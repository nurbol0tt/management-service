import json
import psycopg2
import psycopg2.extras

from typing import List, Optional, Dict, Any, Protocol
from twisted.internet import defer, threads

from app.services.exceptions import DatabaseError, VersionNotFoundError, ServiceNotFoundError
from app.repo.models import Configuration, ConfigurationHistory
from app.settings import settings


class IDatabaseManager(Protocol):
    def save_configuration(self, service: str, payload: Dict[str, Any]) -> int:
        ...

    def get_configuration(self, service: str, version: Optional[int] = None) -> defer.Deferred:
        ...

    def get_configuration_history(self, service: str) -> defer.Deferred:
        ...

class DatabaseManager(IDatabaseManager):
    def _get_connection(self):
        """Получить соединение с базой данных."""
        try:
            conn = psycopg2.connect(
                host=settings.db_host,
                port=settings.db_port,
                database=settings.db_name,
                user=settings.db_user,
                password=settings.db_password,
            )
            conn.autocommit = True
            return conn
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}")

    @defer.inlineCallbacks
    def save_configuration(self, service: str, payload: Dict[str, Any]) -> int:

        def _save_in_thread():
            conn = self._get_connection()
            try:
                with conn.cursor() as cursor:
                    version = payload.get('version')
                    if version is None:
                        cursor.execute(
                            "SELECT COALESCE(MAX(version), 0) FROM configurations WHERE service = %s",
                            (service,)
                        )
                        max_version = cursor.fetchone()[0]
                        version = max_version + 1
                        payload['version'] = version

                    cursor.execute(
                        """
                        INSERT INTO configurations (service, version, payload)
                        VALUES (%s, %s, %s)
                        """,
                        (service, version, json.dumps(payload))
                    )

                    return version
            finally:
                conn.close()

        try:
            version = yield threads.deferToThread(_save_in_thread)
            defer.returnValue(version)
        except psycopg2.IntegrityError:
            raise DatabaseError(f"Configuration version {payload.get('version')} already exists for service {service}")
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to save configuration: {e}")

    @defer.inlineCallbacks
    def get_configuration(self, service: str, version: Optional[int] = None) -> Configuration:
        """Получить конфигурацию."""

        def _get_in_thread():
            conn = self._get_connection()
            try:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    if version is None:
                        # Получаем последнюю версию
                        cursor.execute(
                            """
                            SELECT * FROM configurations
                            WHERE service = %s
                            ORDER BY version DESC
                            LIMIT 1
                            """,
                            (service,)
                        )
                    else:
                        # Получаем конкретную версию
                        cursor.execute(
                            """
                            SELECT * FROM configurations
                            WHERE service = %s AND version = %s
                            """,
                            (service, version)
                        )

                    row = cursor.fetchone()
                    if not row:
                        if version is None:
                            raise ServiceNotFoundError(service)
                        else:
                            raise VersionNotFoundError(service, version)

                    return Configuration(
                        id=row['id'],
                        service=row['service'],
                        version=row['version'],
                        payload=row['payload'],
                        created_at=row['created_at']
                    )
            finally:
                conn.close()

        try:
            config = yield threads.deferToThread(_get_in_thread)
            defer.returnValue(config)
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to get configuration: {e}")

    @defer.inlineCallbacks
    def get_configuration_history(self, service: str) -> List[ConfigurationHistory]:
        """Получить историю конфигураций для сервиса."""

        def _get_history_in_thread():
            conn = self._get_connection()
            try:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT version, created_at
                        FROM configurations
                        WHERE service = %s
                        ORDER BY version DESC
                        """,
                        (service,)
                    )

                    rows = cursor.fetchall()
                    if not rows:
                        raise ServiceNotFoundError(service)

                    return [
                        ConfigurationHistory(
                            version=row['version'],
                            created_at=row['created_at']
                        )
                        for row in rows
                    ]
            finally:
                conn.close()

        try:
            history = yield threads.deferToThread(_get_history_in_thread)
            defer.returnValue(history)
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to get configuration history: {e}")


db_manager = DatabaseManager()
