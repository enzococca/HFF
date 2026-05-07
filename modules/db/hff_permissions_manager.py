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
        'media_to_entity_table',
        'divers',
        'diver_segments'
    ]

    # Child tables of dive_log. Saving a dive_log record rewrites these
    # via DELETE + INSERT, so any role allowed to UPDATE dive_log must
    # also be allowed to DELETE rows here, otherwise the save aborts.
    DIVE_CHILD_TABLES = ['divers', 'diver_segments']

    def __init__(self, engine):
        """Initialize the permissions manager.

        Args:
            engine: SQLAlchemy engine connected to the database
        """
        self.engine = engine
        self._current_user = None
        self._current_role = None
        self._permissions_cache = {}
        self._is_pg_superuser = None

    def is_pg_superuser(self) -> bool:
        """Check if the connected PostgreSQL user has superuser privileges."""
        if self._is_pg_superuser is not None:
            return self._is_pg_superuser

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT usesuper, current_user FROM pg_user WHERE usename = current_user"
                ))
                row = result.fetchone()
                self._is_pg_superuser = bool(row and row[0])
                from qgis.core import QgsMessageLog, Qgis
                QgsMessageLog.logMessage(
                    f"HFF User Management: PG user='{row[1] if row else '?'}', "
                    f"superuser={self._is_pg_superuser}",
                    'HFF', Qgis.Info
                )
        except Exception as e:
            self._is_pg_superuser = False
            from qgis.core import QgsMessageLog, Qgis
            QgsMessageLog.logMessage(
                f"HFF User Management: superuser check failed: {e}",
                'HFF', Qgis.Warning
            )

        return self._is_pg_superuser

    def _is_admin(self) -> bool:
        """Check if current session has admin privileges.

        Returns True if logged in as admin OR if connected as PG superuser.
        """
        return self._current_role == 'admin' or self.is_pg_superuser()

    def ensure_tables_exist(self) -> bool:
        """Create user management tables if they don't exist.

        Returns:
            True if tables exist (or were created), False on error.
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                    "WHERE table_name = 'hff_users')"
                ))
                if result.fetchone()[0]:
                    return True
        except Exception:
            return False

        # Tables don't exist, create them
        create_sql = [
            """CREATE TABLE IF NOT EXISTS hff_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                email VARCHAR(100),
                role VARCHAR(20) NOT NULL DEFAULT 'guest',
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                notes TEXT,
                CONSTRAINT chk_role CHECK (role IN ('admin', 'archaeologist', 'student', 'guest'))
            )""",
            """CREATE TABLE IF NOT EXISTS hff_permissions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES hff_users(id) ON DELETE CASCADE,
                table_name VARCHAR(100) NOT NULL,
                can_view BOOLEAN DEFAULT true,
                can_insert BOOLEAN DEFAULT false,
                can_update BOOLEAN DEFAULT false,
                can_delete BOOLEAN DEFAULT false,
                UNIQUE(user_id, table_name)
            )""",
            """CREATE TABLE IF NOT EXISTS hff_access_log (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100),
                action VARCHAR(20),
                table_name VARCHAR(100),
                record_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                details TEXT
            )""",
            "CREATE INDEX IF NOT EXISTS idx_hff_users_username ON hff_users(username)",
            "CREATE INDEX IF NOT EXISTS idx_hff_users_role ON hff_users(role)",
            "CREATE INDEX IF NOT EXISTS idx_hff_permissions_user_id ON hff_permissions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_hff_permissions_table ON hff_permissions(table_name)",
            "CREATE INDEX IF NOT EXISTS idx_hff_access_log_username ON hff_access_log(username)",
            "CREATE INDEX IF NOT EXISTS idx_hff_access_log_timestamp ON hff_access_log(timestamp)",
        ]

        try:
            with self.engine.begin() as conn:
                for stmt in create_sql:
                    conn.execute(text(stmt))

            # Create default admin user
            self._create_initial_admin()
            return True
        except Exception:
            return False

    def _create_initial_admin(self):
        """Create the default admin user if no users exist."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM hff_users"))
                if result.fetchone()[0] > 0:
                    return

            password_hash = self.hash_password('admin')
            with self.engine.begin() as conn:
                result = conn.execute(text("""
                    INSERT INTO hff_users (username, password_hash, full_name, role, is_active)
                    VALUES (:username, :password_hash, :full_name, :role, true)
                    RETURNING id
                """), {
                    "username": "admin",
                    "password_hash": password_hash,
                    "full_name": "Administrator",
                    "role": "admin"
                })
                user_id = result.fetchone()[0]
                self._create_default_permissions(conn, user_id, 'admin')
        except Exception:
            pass

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
    # User Management (Admin / PG Superuser only)
    # =========================================================================

    def _get_db_name(self):
        """Get current database name from engine URL."""
        try:
            return self.engine.url.database
        except Exception:
            return None

    def _create_pg_role(self, conn, username: str, password: str, role: str):
        """Create a PostgreSQL role with LOGIN and grant permissions.

        Args:
            conn: Active SQLAlchemy connection (inside transaction)
            username: PG role name
            password: PG login password
            role: HFF role for determining grant level
        """
        from sqlalchemy import text as sa_text

        # Check if PG role already exists
        result = conn.execute(sa_text(
            "SELECT 1 FROM pg_roles WHERE rolname = :username"
        ), {"username": username})
        if result.fetchone():
            # Role exists, just update password
            conn.execute(sa_text(
                f'ALTER ROLE "{username}" WITH LOGIN PASSWORD :password'
            ), {"password": password})
        else:
            # Create new role
            conn.execute(sa_text(
                f'CREATE ROLE "{username}" WITH LOGIN PASSWORD :password'
            ), {"password": password})

        # Grant CONNECT on current database
        db_name = self._get_db_name()
        if db_name:
            conn.execute(sa_text(f'GRANT CONNECT ON DATABASE "{db_name}" TO "{username}"'))

        # Grant USAGE on public schema
        conn.execute(sa_text(f'GRANT USAGE ON SCHEMA public TO "{username}"'))

        # Grant table permissions based on role
        self._grant_pg_permissions(conn, username, role)

    def _grant_pg_permissions(self, conn, username: str, role: str):
        """Grant PostgreSQL table-level permissions based on HFF role."""
        from sqlalchemy import text as sa_text

        # Get all public tables
        result = conn.execute(sa_text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
        ))
        all_tables = [row[0] for row in result]

        # Also include views
        result = conn.execute(sa_text(
            "SELECT table_name FROM information_schema.views "
            "WHERE table_schema = 'public'"
        ))
        all_views = [row[0] for row in result]

        # Revoke existing grants first
        for table in all_tables + all_views:
            try:
                conn.execute(sa_text(
                    f'REVOKE ALL PRIVILEGES ON TABLE public."{table}" FROM "{username}"'
                ))
            except Exception:
                pass

        # Grant based on role
        role_grants = {
            'admin': 'ALL PRIVILEGES',
            'archaeologist': 'SELECT, INSERT, UPDATE',
            'student': 'SELECT, INSERT',
            'guest': 'SELECT'
        }
        grant = role_grants.get(role, 'SELECT')

        for table in all_tables:
            conn.execute(sa_text(
                f'GRANT {grant} ON TABLE public."{table}" TO "{username}"'
            ))

        # Child tables of dive_log require DELETE for any role that can
        # UPDATE dive_log, because _save_divers does a DELETE + INSERT
        # on every save. Without this, archaeologists hit a permission
        # error when saving a divelog they're allowed to update.
        if role in ('admin', 'archaeologist'):
            for table in self.DIVE_CHILD_TABLES:
                if table in all_tables:
                    try:
                        conn.execute(sa_text(
                            f'GRANT DELETE ON TABLE public."{table}" '
                            f'TO "{username}"'
                        ))
                    except Exception:
                        pass

        # Views: always SELECT
        for view in all_views:
            try:
                conn.execute(sa_text(
                    f'GRANT SELECT ON TABLE public."{view}" TO "{username}"'
                ))
            except Exception:
                pass

        # Grant USAGE on sequences for roles that can INSERT
        if role in ('admin', 'archaeologist', 'student'):
            result = conn.execute(sa_text(
                "SELECT sequence_name FROM information_schema.sequences "
                "WHERE sequence_schema = 'public'"
            ))
            for row in result:
                try:
                    conn.execute(sa_text(
                        f'GRANT USAGE, SELECT ON SEQUENCE public."{row[0]}" TO "{username}"'
                    ))
                except Exception:
                    pass

    def create_user(self, username: str, password: str, full_name: str = None,
                   email: str = None, role: str = 'guest') -> bool:
        """Create a new user.

        Creates both an HFF application user and a PostgreSQL login role.
        Requires admin role or PostgreSQL superuser privileges.

        Args:
            username: Username (must be unique)
            password: Plain text password
            full_name: User's full name
            email: Email address
            role: User role ('admin', 'archaeologist', 'student', 'guest')

        Returns:
            True if user created successfully

        Raises:
            PermissionDeniedError: If not admin/superuser
            Exception: On database errors
        """
        if not self._is_admin():
            raise PermissionDeniedError(
                self.current_user or 'anonymous', 'create_user',
                'hff_users'
            )

        if role not in self.ROLES:
            role = 'guest'

        password_hash = self.hash_password(password)

        with self.engine.begin() as conn:
            # Create HFF application user
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

            # Create default HFF permissions
            self._create_default_permissions(conn, user_id, role)

            # Create PostgreSQL role with LOGIN
            self._create_pg_role(conn, username, password, role)

        self._log_access(
            self.current_user or 'superuser', 'CREATE_USER',
            'hff_users', username, True,
            f"Created user '{username}' with role '{role}'"
        )
        return True

    def update_user(self, username: str, full_name: str = None,
                   email: str = None, role: str = None,
                   password: str = None, is_active: bool = None) -> bool:
        """Update an existing user.

        Requires admin role or PostgreSQL superuser privileges.

        Args:
            username: Username to update
            full_name: New full name (None to keep current)
            email: New email (None to keep current)
            role: New role (None to keep current)
            password: New password (None to keep current)
            is_active: Active status (None to keep current)

        Returns:
            True if updated successfully

        Raises:
            PermissionDeniedError: If not admin/superuser
            Exception: On database errors
        """
        if not self._is_admin():
            raise PermissionDeniedError(
                self.current_user or 'anonymous', 'update_user',
                'hff_users'
            )

        updates = []
        params = {"username": username}

        if full_name is not None:
            updates.append("full_name = :full_name")
            params["full_name"] = full_name
        if email is not None:
            updates.append("email = :email")
            params["email"] = email
        if role is not None and role in self.ROLES:
            updates.append("role = :role")
            params["role"] = role
        if password:
            updates.append("password_hash = :password_hash")
            params["password_hash"] = self.hash_password(password)
        if is_active is not None:
            updates.append("is_active = :is_active")
            params["is_active"] = is_active

        if not updates:
            return True

        with self.engine.begin() as conn:
            conn.execute(text(
                f"UPDATE hff_users SET {', '.join(updates)} WHERE username = :username"
            ), params)

            # If role changed, update default permissions and PG grants
            if role is not None:
                result = conn.execute(text(
                    "SELECT id FROM hff_users WHERE username = :username"
                ), {"username": username})
                row = result.fetchone()
                if row:
                    self._create_default_permissions(conn, row[0], role)
                self._grant_pg_permissions(conn, username, role)

            # If password changed, update PG role password
            if password:
                try:
                    conn.execute(text(
                        f'ALTER ROLE "{username}" WITH PASSWORD :password'
                    ), {"password": password})
                except Exception:
                    pass  # PG role might not exist for legacy users

            # If deactivated, revoke PG LOGIN
            if is_active is not None:
                try:
                    if is_active:
                        conn.execute(text(f'ALTER ROLE "{username}" WITH LOGIN'))
                    else:
                        conn.execute(text(f'ALTER ROLE "{username}" WITH NOLOGIN'))
                except Exception:
                    pass

        self._log_access(
            self.current_user or 'superuser', 'UPDATE_USER',
            'hff_users', username, True,
            f"Updated user '{username}': {', '.join(updates)}"
        )
        return True

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
            row = dict(perms)
            # Dive_log child tables follow the parent's update permission:
            # if you can UPDATE dive_log, you can rewrite its diver list,
            # which requires DELETE on these child rows.
            if table in self.DIVE_CHILD_TABLES and perms['update']:
                row['delete'] = True
            conn.execute(text("""
                INSERT INTO hff_permissions (user_id, table_name, can_view, can_insert, can_update, can_delete)
                VALUES (:user_id, :table_name, :can_view, :can_insert, :can_update, :can_delete)
                ON CONFLICT (user_id, table_name) DO UPDATE
                SET can_view = :can_view, can_insert = :can_insert,
                    can_update = :can_update, can_delete = :can_delete
            """), {
                "user_id": user_id,
                "table_name": table,
                "can_view": row['view'],
                "can_insert": row['insert'],
                "can_update": row['update'],
                "can_delete": row['delete']
            })

    def update_user_permissions(self, username: str, table_name: str,
                               can_view: bool = True, can_insert: bool = False,
                               can_update: bool = False, can_delete: bool = False) -> bool:
        """Update permissions for a user on a specific table.

        Requires admin role or PostgreSQL superuser privileges.

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
        if not self._is_admin():
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

                # Sync PostgreSQL GRANT for this table
                try:
                    conn.execute(text(
                        f'REVOKE ALL PRIVILEGES ON TABLE public."{table_name}" FROM "{username}"'
                    ))
                    grants = []
                    if can_view:
                        grants.append('SELECT')
                    if can_insert:
                        grants.append('INSERT')
                    if can_update:
                        grants.append('UPDATE')
                    if can_delete:
                        grants.append('DELETE')
                    if grants:
                        conn.execute(text(
                            f'GRANT {", ".join(grants)} ON TABLE public."{table_name}" TO "{username}"'
                        ))
                except Exception:
                    pass  # PG role might not exist for legacy users

            return True
        except Exception:
            return False

    def resync_all_pg_grants(self) -> int:
        """Re-apply role-based PG grants for every active HFF user.

        Useful after MANAGED_TABLES grows or grant logic changes (e.g. when
        adding the divers / diver_segments DELETE grant): existing users
        keep their stale grants until their role is changed via
        update_user, so this method explicitly rewrites them.

        Requires admin / PG superuser. Failures on individual users are
        swallowed so one bad PG role doesn't abort the rest.

        Returns the number of users successfully resynced.
        """
        if not self._is_admin():
            return 0

        count = 0
        try:
            with self.engine.begin() as conn:
                rows = conn.execute(text(
                    "SELECT username, role FROM hff_users WHERE is_active = TRUE"
                )).fetchall()
                for username, role in rows:
                    try:
                        self._grant_pg_permissions(conn, username, role)
                        count += 1
                    except Exception:
                        continue
        except Exception:
            return count
        return count

    def list_users(self) -> List[Dict[str, Any]]:
        """List all users.

        Requires admin role or PostgreSQL superuser privileges.

        Returns:
            List of user dictionaries
        """
        if not self._is_admin():
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
        """Deactivate a user account.

        Requires admin role or PostgreSQL superuser privileges.

        Args:
            username: Username to deactivate

        Returns:
            True if deactivated successfully

        Raises:
            PermissionDeniedError: If not admin/superuser
            ValueError: If trying to deactivate yourself
            Exception: On database errors
        """
        if not self._is_admin():
            raise PermissionDeniedError(
                self.current_user or 'anonymous', 'deactivate_user',
                'hff_users'
            )

        if username == self.current_user:
            raise ValueError("Cannot deactivate your own account")

        with self.engine.begin() as conn:
            conn.execute(text("""
                UPDATE hff_users
                SET is_active = false
                WHERE username = :username
            """), {"username": username})

            # Revoke LOGIN from PG role
            try:
                conn.execute(text(f'ALTER ROLE "{username}" WITH NOLOGIN'))
            except Exception:
                pass  # PG role might not exist for legacy users

        self._log_access(
            self.current_user or 'superuser', 'DEACTIVATE_USER',
            'hff_users', username, True,
            f"Deactivated user '{username}'"
        )
        return True

    def get_access_log(self, username: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get access log entries.

        Requires admin role or PostgreSQL superuser privileges.

        Args:
            username: Filter by username (all users if None)
            limit: Maximum entries to return

        Returns:
            List of log entry dictionaries
        """
        if not self._is_admin():
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