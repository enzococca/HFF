# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - Concurrency Manager for Multi-user Support
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

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

from sqlalchemy import text
from qgis.core import QgsSettings


class ConcurrencyError(Exception):
    """Base exception for concurrency errors."""
    pass


class RecordLockError(ConcurrencyError):
    """Raised when a record is locked by another user."""
    def __init__(self, table: str, record_id: Any, locked_by: str, locked_since: datetime):
        self.table = table
        self.record_id = record_id
        self.locked_by = locked_by
        self.locked_since = locked_since
        super().__init__(
            f"Record {record_id} in {table} is locked by {locked_by} since {locked_since}"
        )


class VersionConflictError(ConcurrencyError):
    """Raised when there's a version conflict (optimistic locking failure)."""
    def __init__(self, table: str, record_id: Any, local_version: int, server_version: int):
        self.table = table
        self.record_id = record_id
        self.local_version = local_version
        self.server_version = server_version
        super().__init__(
            f"Version conflict for record {record_id} in {table}: "
            f"local version {local_version}, server version {server_version}"
        )


class HffConcurrencyManager:
    """Manages record locking and version control for multi-user database access.

    This class provides:
    - Pessimistic locking: Lock records while editing to prevent conflicts
    - Optimistic locking: Version checking to detect concurrent modifications
    - Stale lock cleanup: Remove locks from abandoned sessions

    Usage:
        manager = HffConcurrencyManager(db_manager.engine, username)

        # Lock a record before editing
        success = manager.lock_record('anchor_table', record_id)
        if not success:
            # Handle lock failure

        # After editing, save with version check
        if manager.check_version_conflict('anchor_table', record_id, local_version):
            raise VersionConflictError(...)

        # Unlock when done
        manager.unlock_record('anchor_table', record_id)
    """

    # Tables that support concurrency columns
    SUPPORTED_TABLES = [
        'anchor_table',
        'artefact_log',
        'dive_log',
        'pottery_table',
        'shipwreck_table',
        'site_table'
    ]

    # Primary key column names for each table
    PRIMARY_KEYS = {
        'anchor_table': 'id_anc',
        'artefact_log': 'id_art',
        'dive_log': 'id_dive',
        'pottery_table': 'id_rep',
        'shipwreck_table': 'id_shipwreck',
        'site_table': 'id_sito'
    }

    def __init__(self, engine, username: Optional[str] = None):
        """Initialize the concurrency manager.

        Args:
            engine: SQLAlchemy engine connected to the database
            username: Current user's username (loaded from settings if not provided)
        """
        self.engine = engine
        self._username = username

    @property
    def username(self) -> str:
        """Get the current username."""
        if self._username:
            return self._username
        # Try to get from QGIS settings
        settings = QgsSettings()
        return settings.value("HFF/current_user", "anonymous")

    @username.setter
    def username(self, value: str):
        """Set the current username."""
        self._username = value

    def _get_pk_column(self, table_name: str) -> str:
        """Get the primary key column name for a table."""
        return self.PRIMARY_KEYS.get(table_name, 'id')

    def _table_supports_concurrency(self, table_name: str) -> bool:
        """Check if a table has concurrency columns."""
        return table_name in self.SUPPORTED_TABLES

    def lock_record(self, table_name: str, record_id: Any,
                   timeout_minutes: int = 30) -> Tuple[bool, Optional[str]]:
        """Attempt to lock a record for editing.

        Args:
            table_name: Name of the database table
            record_id: Primary key value of the record
            timeout_minutes: Lock timeout (stale locks older than this will be cleared)

        Returns:
            Tuple of (success, error_message)
            - (True, None) if lock acquired
            - (False, "Locked by: username since: timestamp") if already locked
        """
        if not self._table_supports_concurrency(table_name):
            return True, None

        pk_column = self._get_pk_column(table_name)

        with self.engine.begin() as conn:
            # First check if already locked
            result = conn.execute(text(f"""
                SELECT editing_by, editing_since
                FROM {table_name}
                WHERE {pk_column} = :record_id
            """), {"record_id": record_id})

            row = result.fetchone()
            if not row:
                return False, "Record not found"

            editing_by, editing_since = row[0], row[1]

            # Check if locked by another user
            if editing_by and editing_by != self.username:
                # Check if lock is stale
                if editing_since:
                    cutoff = datetime.now() - timedelta(minutes=timeout_minutes)
                    if editing_since < cutoff:
                        # Stale lock, can be overridden
                        pass
                    else:
                        return False, f"Locked by: {editing_by} since: {editing_since}"

            # Acquire or renew lock
            conn.execute(text(f"""
                UPDATE {table_name}
                SET editing_by = :username, editing_since = :now
                WHERE {pk_column} = :record_id
            """), {
                "username": self.username,
                "now": datetime.now(),
                "record_id": record_id
            })

        return True, None

    def unlock_record(self, table_name: str, record_id: Any) -> bool:
        """Release the lock on a record.

        Args:
            table_name: Name of the database table
            record_id: Primary key value of the record

        Returns:
            True if unlocked successfully, False otherwise
        """
        if not self._table_supports_concurrency(table_name):
            return True

        pk_column = self._get_pk_column(table_name)

        with self.engine.begin() as conn:
            result = conn.execute(text(f"""
                UPDATE {table_name}
                SET editing_by = NULL, editing_since = NULL
                WHERE {pk_column} = :record_id AND editing_by = :username
            """), {
                "record_id": record_id,
                "username": self.username
            })

        return result.rowcount > 0

    def check_lock_status(self, table_name: str, record_id: Any) -> Dict[str, Any]:
        """Check the lock status of a record.

        Args:
            table_name: Name of the database table
            record_id: Primary key value of the record

        Returns:
            Dictionary with lock info:
            - 'is_locked': bool
            - 'locked_by': str or None
            - 'locked_since': datetime or None
            - 'is_mine': bool (True if locked by current user)
        """
        if not self._table_supports_concurrency(table_name):
            return {'is_locked': False, 'locked_by': None, 'locked_since': None, 'is_mine': False}

        pk_column = self._get_pk_column(table_name)

        with self.engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT editing_by, editing_since
                FROM {table_name}
                WHERE {pk_column} = :record_id
            """), {"record_id": record_id})

            row = result.fetchone()
            if not row:
                return {'is_locked': False, 'locked_by': None, 'locked_since': None, 'is_mine': False}

            editing_by, editing_since = row[0], row[1]
            is_locked = editing_by is not None
            is_mine = editing_by == self.username if editing_by else False

            return {
                'is_locked': is_locked,
                'locked_by': editing_by,
                'locked_since': editing_since,
                'is_mine': is_mine
            }

    def check_version_conflict(self, table_name: str, record_id: Any,
                               local_version: int) -> Tuple[bool, Optional[int]]:
        """Check if there's a version conflict (optimistic locking).

        Args:
            table_name: Name of the database table
            record_id: Primary key value of the record
            local_version: The version number the client has

        Returns:
            Tuple of (has_conflict, server_version)
            - (False, server_version) if no conflict
            - (True, server_version) if server version is higher
        """
        if not self._table_supports_concurrency(table_name):
            return False, local_version

        pk_column = self._get_pk_column(table_name)

        with self.engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT version_number
                FROM {table_name}
                WHERE {pk_column} = :record_id
            """), {"record_id": record_id})

            row = result.fetchone()
            if not row:
                return False, local_version

            server_version = row[0] or 1

            if server_version > local_version:
                return True, server_version

        return False, server_version

    def get_record_version(self, table_name: str, record_id: Any) -> int:
        """Get the current version number of a record.

        Args:
            table_name: Name of the database table
            record_id: Primary key value of the record

        Returns:
            Version number (1 if not found or table doesn't support versioning)
        """
        if not self._table_supports_concurrency(table_name):
            return 1

        pk_column = self._get_pk_column(table_name)

        with self.engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT version_number
                FROM {table_name}
                WHERE {pk_column} = :record_id
            """), {"record_id": record_id})

            row = result.fetchone()
            if row:
                return row[0] or 1

        return 1

    def set_modified_by(self, table_name: str, record_id: Any) -> bool:
        """Update the last_modified_by field for a record.

        This should be called after a successful save operation.

        Args:
            table_name: Name of the database table
            record_id: Primary key value of the record

        Returns:
            True if updated successfully
        """
        if not self._table_supports_concurrency(table_name):
            return True

        pk_column = self._get_pk_column(table_name)

        with self.engine.begin() as conn:
            conn.execute(text(f"""
                UPDATE {table_name}
                SET last_modified_by = :username, last_modified_timestamp = :now
                WHERE {pk_column} = :record_id
            """), {
                "username": self.username,
                "now": datetime.now(),
                "record_id": record_id
            })

        return True

    def clear_stale_locks(self, timeout_minutes: int = 30) -> int:
        """Clear all stale locks (locks older than timeout).

        Args:
            timeout_minutes: Locks older than this will be cleared

        Returns:
            Number of locks cleared
        """
        cleared_count = 0
        cutoff = datetime.now() - timedelta(minutes=timeout_minutes)

        with self.engine.begin() as conn:
            for table_name in self.SUPPORTED_TABLES:
                result = conn.execute(text(f"""
                    UPDATE {table_name}
                    SET editing_by = NULL, editing_since = NULL
                    WHERE editing_since < :cutoff AND editing_by IS NOT NULL
                """), {"cutoff": cutoff})
                cleared_count += result.rowcount

        return cleared_count

    def clear_user_locks(self, username: Optional[str] = None) -> int:
        """Clear all locks held by a specific user (or current user).

        Useful for cleanup when a user logs out or session ends.

        Args:
            username: Username to clear locks for (current user if None)

        Returns:
            Number of locks cleared
        """
        user = username or self.username
        cleared_count = 0

        with self.engine.begin() as conn:
            for table_name in self.SUPPORTED_TABLES:
                result = conn.execute(text(f"""
                    UPDATE {table_name}
                    SET editing_by = NULL, editing_since = NULL
                    WHERE editing_by = :username
                """), {"username": user})
                cleared_count += result.rowcount

        return cleared_count

    def get_active_locks(self, table_name: Optional[str] = None) -> list:
        """Get a list of all active locks.

        Args:
            table_name: Filter by table (all tables if None)

        Returns:
            List of dictionaries with lock info:
            [{'table': str, 'record_id': Any, 'locked_by': str, 'locked_since': datetime}, ...]
        """
        locks = []
        tables = [table_name] if table_name else self.SUPPORTED_TABLES

        with self.engine.connect() as conn:
            for tbl in tables:
                if tbl not in self.SUPPORTED_TABLES:
                    continue

                pk_column = self._get_pk_column(tbl)
                result = conn.execute(text(f"""
                    SELECT {pk_column}, editing_by, editing_since
                    FROM {tbl}
                    WHERE editing_by IS NOT NULL
                """))

                for row in result:
                    locks.append({
                        'table': tbl,
                        'record_id': row[0],
                        'locked_by': row[1],
                        'locked_since': row[2]
                    })

        return locks
