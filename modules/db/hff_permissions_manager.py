# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - Permissions Manager for User Access Control
                             -------------------
    begin                : 2024
    copyright            : (C) 2024 by HFF Team
    email                : enzo.ccc@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import hashlib
import os
from datetime import datetime
from typing import Optional, Dict, List, Any

from sqlalchemy import text
from qgis.core import QgsSettings


class PermissionDeniedError(Exception):
    """Raised when a user doesn't have permission for an action."""
    def __init__(self, username: str, action: str, table: str):
        self.username = username
        self.action = action
        self.table = table
        super().__init__(f"User '{username}' does not have {action} permission on {table}")


class HffPermissionsManager:
    """Manages user authentication and permissions for HFF plugin.

    This class provides:
    - User authentication (login/logout)
    - Permission checking (view, insert, update, delete)
    - User management (create, update, delete users)
    - Role-based access control

    Roles:
    - admin: Full access to all tables and user management
    - archaeologist: Can view, insert, update (no delete)
    - student: Can view and insert (no update/delete)
    - guest: View only

    Usage:
        manager = HffPermissionsManager(db_manager.engine)

        # Login
        if manager.login('username', 'password'):
            # Check permission before action
            if manager.check_permission('anchor_table', 'update'):
                # Perform update
            else:
                # Show permission denied message
    """

    # Available roles
    ROLES = ['admin', 'archaeologist', 'student', 'guest']

    # Tables to manage permissions for
    MANAGED_TABLES = [
        'anchor_table',
        'artefact_log',
        'dive_log',
        'pottery_table',
        'shipwreck_table',
        'site_table',
        'media_table',
        'media_thumb_table',
        'media_to_entity_table'
    ]

    def __init__(self, engine):
        """Initialize the permissions manager.

        Args:
            engine: SQLAlchemy engine connected to the database
        """
        self.engine = engine
        self._current_user = None
        self._current_role = None
        self._permissions_cache = {}

    @property
    def current_user(self) -> Optional[str]:
        """Get the currently logged in username."""
        if self._current_user:
            return self._current_user
        # Try to restore from settings
        settings = QgsSettings()
        return settings.value("HFF/current_user", None)

    @property
    def current_role(self) -> Optional[str]:
        """Get the current user's role."""
        if self._current_role:
            return self._current_role
        settings = QgsSettings()
        return settings.value("HFF/current_role", None)

    @property
    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in."""
        return self.current_user is not None

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """Hash a password using PBKDF2.

        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)

        Returns:
            Hash string in format 'pbkdf2:sha256:iterations$salt$hash'
        """
        if salt is None:
            salt = os.urandom(16).hex()

        iterations = 260000
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), iterations)

        return f"pbkdf2:sha256:{iterations}${salt}${dk.hex()}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against a hash.

        Args:
            password: Plain text password to verify
            password_hash: Stored hash string

        Returns:
            True if password matches
        """
        try:
            parts = password_hash.split('$')
            if len(parts) != 3:
                return False

            method_info = parts[0]
            salt = parts[1]
            stored_hash = parts[2]

            # Parse method info
            method_parts = method_info.split(':')
            if len(method_parts) != 3 or method_parts[0] != 'pbkdf2':
                return False

            algorithm = method_parts[1]
            iterations = int(method_parts[2])

            # Compute hash
            dk = hashlib.pbkdf2_hmac(algorithm, password.encode(), salt.encode(), iterations)

            return dk.hex() == stored_hash
        except Exception:
            return False

    def login(self, username: str, password: str) -> bool:
        """Authenticate a user.

        Args:
            username: Username
            password: Plain text password

        Returns:
            True if authentication successful
        """
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, password_hash, role, is_active
                FROM hff_users
                WHERE username = :username
            """), {"username": username})

            row = result.fetchone()
            if not row:
                return False

            user_id, password_hash, role, is_active = row

            if not is_active:
                return False

            if not self.verify_password(password, password_hash):
                self._log_access(username, 'LOGIN', None, None, False, 'Invalid password')
                return False

            # Update last login
            with self.engine.begin() as conn:
                conn.execute(text("""
                    UPDATE hff_users
                    SET last_login = :now
                    WHERE id = :user_id
                """), {"now": datetime.now(), "user_id": user_id})

            # Store session
            self._current_user = username
            self._current_role = role
            self._permissions_cache = {}

            # Save to QGIS settings
            settings = QgsSettings()
            settings.setValue("HFF/current_user", username)
            settings.setValue("HFF/current_role", role)

            # Load permissions
            self._load_permissions(user_id)

            self._log_access(username, 'LOGIN', None, None, True)
            return True

    def logout(self):
        """Log out the current user."""
        if self._current_user:
            self._log_access(self._current_user, 'LOGOUT', None, None, True)

        self._current_user = None
        self._current_role = None
        self._permissions_cache = {}

        settings = QgsSettings()
        settings.remove("HFF/current_user")
        settings.remove("HFF/current_role")

    def _load_permissions(self, user_id: int):
        """Load permissions for a user into cache."""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name, can_view, can_insert, can_update, can_delete
                FROM hff_permissions
                WHERE user_id = :user_id
            """), {"user_id": user_id})

            for row in result:
                table_name, can_view, can_insert, can_update, can_delete = row
                self._permissions_cache[table_name] = {
                    'view': can_view,
                    'insert': can_insert,
                    'update': can_update,
                    'delete': can_delete
                }

    def check_permission(self, table_name: str, action: str) -> bool:
        """Check if current user has permission for an action.

        Args:
            table_name: Database table name
            action: 'view', 'insert', 'update', or 'delete'

        Returns:
            True if permission granted
        """
        if not self.is_logged_in:
            return False

        # Admin has all permissions
        if self._current_role == 'admin':
            return True

        # Check cache
        if table_name in self._permissions_cache:
            return self._permissions_cache[table_name].get(action, False)

        # Default permissions by role
        role_defaults = {
            'archaeologist': {'view': True, 'insert': True, 'update': True, 'delete': False},
            'student': {'view': True, 'insert': True, 'update': False, 'delete': False},
            'guest': {'view': True, 'insert': False, 'update': False, 'delete': False}
        }

        role_perms = role_defaults.get(self._current_role, role_defaults['guest'])
        return role_perms.get(action, False)

    def require_permission(self, table_name: str, action: str):
        """Require permission or raise PermissionDeniedError.

        Args:
            table_name: Database table name
            action: 'view', 'insert', 'update', or 'delete'

        Raises:
            PermissionDeniedError: If permission denied
        """
        if not self.check_permission(table_name, action):
            raise PermissionDeniedError(self.current_user or 'anonymous', action, table_name)

    def get_user_permissions(self, username: Optional[str] = None) -> Dict[str, Dict[str, bool]]:
        """Get all permissions for a user.

        Args:
            username: Username (current user if None)

        Returns:
            Dictionary of {table_name: {action: bool}}
        """
        user = username or self.current_user
        if not user:
            return {}

        permissions = {}

        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT p.table_name, p.can_view, p.can_insert, p.can_update, p.can_delete
                FROM hff_permissions p
                JOIN hff_users u ON p.user_id = u.id
                WHERE u.username = :username
            """), {"username": user})

            for row in result:
                table_name, can_view, can_insert, can_update, can_delete = row
                permissions[table_name] = {
                    'view': can_view,
                    'insert': can_insert,
                    'update': can_update,
                    'delete': can_delete
                }

        return permissions

    def _log_access(self, username: str, action: str, table_name: Optional[str],
                   record_id: Optional[Any], success: bool, details: Optional[str] = None):
        """Log an access event to the audit log."""
        try:
            with self.engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO hff_access_log (username, action, table_name, record_id, success, details)
                    VALUES (:username, :action, :table_name, :record_id, :success, :details)
                """), {
                    "username": username,
                    "action": action,
                    "table_name": table_name,
                    "record_id": str(record_id) if record_id else None,
                    "success": success,
                    "details": details
                })
        except Exception:
            pass  # Don't fail if logging fails

    # =========================================================================
    # User Management (Admin only)
    # =========================================================================

    def create_user(self, username: str, password: str, full_name: str = None,
                   email: str = None, role: str = 'guest') -> bool:
        """Create a new user (admin only).

        Args:
            username: Username (must be unique)
            password: Plain text password
            full_name: User's full name
            email: Email address
            role: User role ('admin', 'archaeologist', 'student', 'guest')

        Returns:
            True if user created successfully
        """
        if self._current_role != 'admin':
            return False

        if role not in self.ROLES:
            role = 'guest'

        password_hash = self.hash_password(password)

        try:
            with self.engine.begin() as conn:
                result = conn.execute(text("""
                    INSERT INTO hff_users (username, password_hash, full_name, email, role)
                    VALUES (:username, :password_hash, :full_name, :email, :role)
                    RETURNING id
                """), {
                    "username": username,
                    "password_hash": password_hash,
                    "full_name": full_name,
                    "email": email,
                    "role": role
                })

                user_id = result.fetchone()[0]

                # Create default permissions
                self._create_default_permissions(conn, user_id, role)

            return True
        except Exception:
            return False

    def _create_default_permissions(self, conn, user_id: int, role: str):
        """Create default permissions for a new user."""
        role_defaults = {
            'admin': {'view': True, 'insert': True, 'update': True, 'delete': True},
            'archaeologist': {'view': True, 'insert': True, 'update': True, 'delete': False},
            'student': {'view': True, 'insert': True, 'update': False, 'delete': False},
            'guest': {'view': True, 'insert': False, 'update': False, 'delete': False}
        }

        perms = role_defaults.get(role, role_defaults['guest'])

        for table in self.MANAGED_TABLES:
            conn.execute(text("""
                INSERT INTO hff_permissions (user_id, table_name, can_view, can_insert, can_update, can_delete)
                VALUES (:user_id, :table_name, :can_view, :can_insert, :can_update, :can_delete)
                ON CONFLICT (user_id, table_name) DO UPDATE
                SET can_view = :can_view, can_insert = :can_insert,
                    can_update = :can_update, can_delete = :can_delete
            """), {
                "user_id": user_id,
                "table_name": table,
                "can_view": perms['view'],
                "can_insert": perms['insert'],
                "can_update": perms['update'],
                "can_delete": perms['delete']
            })

    def update_user_permissions(self, username: str, table_name: str,
                               can_view: bool = True, can_insert: bool = False,
                               can_update: bool = False, can_delete: bool = False) -> bool:
        """Update permissions for a user on a specific table (admin only).

        Args:
            username: Username to update
            table_name: Table to set permissions for
            can_view: View permission
            can_insert: Insert permission
            can_update: Update permission
            can_delete: Delete permission

        Returns:
            True if updated successfully
        """
        if self._current_role != 'admin':
            return False

        try:
            with self.engine.begin() as conn:
                conn.execute(text("""
                    UPDATE hff_permissions p
                    SET can_view = :can_view, can_insert = :can_insert,
                        can_update = :can_update, can_delete = :can_delete
                    FROM hff_users u
                    WHERE p.user_id = u.id AND u.username = :username AND p.table_name = :table_name
                """), {
                    "username": username,
                    "table_name": table_name,
                    "can_view": can_view,
                    "can_insert": can_insert,
                    "can_update": can_update,
                    "can_delete": can_delete
                })
            return True
        except Exception:
            return False

    def list_users(self) -> List[Dict[str, Any]]:
        """List all users (admin only).

        Returns:
            List of user dictionaries
        """
        if self._current_role != 'admin':
            return []

        users = []
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, username, full_name, email, role, is_active, created_at, last_login
                FROM hff_users
                ORDER BY username
            """))

            for row in result:
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'full_name': row[2],
                    'email': row[3],
                    'role': row[4],
                    'is_active': row[5],
                    'created_at': row[6],
                    'last_login': row[7]
                })

        return users

    def deactivate_user(self, username: str) -> bool:
        """Deactivate a user account (admin only).

        Args:
            username: Username to deactivate

        Returns:
            True if deactivated successfully
        """
        if self._current_role != 'admin':
            return False

        if username == self.current_user:
            return False  # Can't deactivate yourself

        try:
            with self.engine.begin() as conn:
                conn.execute(text("""
                    UPDATE hff_users
                    SET is_active = false
                    WHERE username = :username
                """), {"username": username})
            return True
        except Exception:
            return False

    def get_access_log(self, username: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get access log entries (admin only).

        Args:
            username: Filter by username (all users if None)
            limit: Maximum entries to return

        Returns:
            List of log entry dictionaries
        """
        if self._current_role != 'admin':
            return []

        logs = []
        with self.engine.connect() as conn:
            if username:
                result = conn.execute(text("""
                    SELECT username, action, table_name, record_id, timestamp, success, details
                    FROM hff_access_log
                    WHERE username = :username
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """), {"username": username, "limit": limit})
            else:
                result = conn.execute(text("""
                    SELECT username, action, table_name, record_id, timestamp, success, details
                    FROM hff_access_log
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """), {"limit": limit})

            for row in result:
                logs.append({
                    'username': row[0],
                    'action': row[1],
                    'table_name': row[2],
                    'record_id': row[3],
                    'timestamp': row[4],
                    'success': row[5],
                    'details': row[6]
                })

        return logs
