"""Persistencia SQLite para el MVP APC Reclamos."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

from config.config import SQLITE_DB_PATH


class RepositorioAPC:
    """Repositorio SQLite para casos, resoluciones e informes APC."""

    def __init__(
        self,
        db_path: Path = SQLITE_DB_PATH,
        logger: logging.Logger | None = None,
    ) -> None:
        """Inicializa el repositorio.

        Args:
            db_path: Ruta del archivo SQLite.
            logger: Logger opcional.
        """
        self.db_path = db_path
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.inicializar()

    def _conectar(self) -> sqlite3.Connection:
        """Abre una conexion SQLite con filas tipo diccionario.

        Returns:
            Conexion SQLite configurada.
        """
        conexion = sqlite3.connect(self.db_path)
        conexion.row_factory = sqlite3.Row
        return conexion

    def inicializar(self) -> None:
        """Crea tablas necesarias si no existen."""
        with self._conectar() as conexion:
            conexion.executescript(
                """
                CREATE TABLE IF NOT EXISTS resoluciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    canal TEXT NOT NULL,
                    motivo TEXT NOT NULL,
                    texto_resolucion TEXT NOT NULL,
                    texto_diario TEXT NOT NULL,
                    prioridad INTEGER DEFAULT 1,
                    activa INTEGER DEFAULT 1,
                    creado_en TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS casos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_incidente TEXT NOT NULL,
                    canal TEXT NOT NULL,
                    motivo TEXT NOT NULL,
                    importe REAL DEFAULT 0,
                    numero_cuenta TEXT DEFAULT '',
                    resolucion_sugerida TEXT DEFAULT '',
                    texto_diario TEXT DEFAULT '',
                    aprobado INTEGER DEFAULT 0,
                    analista TEXT DEFAULT '',
                    creado_en TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS base_reclamos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_incidente TEXT,
                    canal TEXT,
                    motivo TEXT,
                    fecha TEXT,
                    hora TEXT,
                    importe REAL,
                    numero_cuenta TEXT,
                    origen_archivo TEXT,
                    creado_en TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        self.logger.info("Base SQLite inicializada en %s", self.db_path)

    def entrenar_resolucion(
        self,
        canal: str,
        motivo: str,
        texto_resolucion: str,
        texto_diario: str,
        prioridad: int = 1,
    ) -> int:
        """Guarda una resolucion modelo.

        Args:
            canal: Canal APC al que aplica la resolucion.
            motivo: Motivo o patron de reclamo.
            texto_resolucion: Texto sugerido para resolver el caso.
            texto_diario: Texto sugerido para cargar en Diario.
            prioridad: Prioridad de coincidencia.

        Returns:
            ID de la resolucion creada.
        """
        with self._conectar() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO resoluciones
                    (canal, motivo, texto_resolucion, texto_diario, prioridad)
                VALUES (?, ?, ?, ?, ?)
                """,
                (canal, motivo, texto_resolucion, texto_diario, prioridad),
            )
            resolucion_id = int(cursor.lastrowid)
        self.logger.info("Resolucion entrenada: %s", resolucion_id)
        return resolucion_id

    def listar_resoluciones(self) -> list[dict[str, Any]]:
        """Lista resoluciones activas.

        Returns:
            Resoluciones guardadas como diccionarios.
        """
        with self._conectar() as conexion:
            filas = conexion.execute(
                """
                SELECT id, canal, motivo, texto_resolucion, texto_diario, prioridad
                FROM resoluciones
                WHERE activa = 1
                ORDER BY prioridad DESC, id DESC
                """
            ).fetchall()
        return [dict(fila) for fila in filas]

    def guardar_base_reclamos(
        self,
        filas: list[dict[str, Any]],
        origen_archivo: str,
    ) -> int:
        """Persiste filas de una base de reclamos.

        Args:
            filas: Registros normalizados de reclamos.
            origen_archivo: Nombre del archivo cargado.

        Returns:
            Cantidad de filas guardadas.
        """
        if not filas:
            return 0

        registros = [
            (
                fila.get("numero_incidente", ""),
                fila.get("canal", ""),
                fila.get("motivo", ""),
                fila.get("fecha", ""),
                fila.get("hora", ""),
                float(fila.get("importe") or 0),
                fila.get("numero_cuenta", ""),
                origen_archivo,
            )
            for fila in filas
        ]

        with self._conectar() as conexion:
            conexion.executemany(
                """
                INSERT INTO base_reclamos
                    (numero_incidente, canal, motivo, fecha, hora, importe,
                     numero_cuenta, origen_archivo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                registros,
            )
        self.logger.info("Base de reclamos cargada: %s filas", len(registros))
        return len(registros)

    def guardar_caso(self, caso: dict[str, Any]) -> int:
        """Guarda un caso analizado.

        Args:
            caso: Datos del caso y sugerencias.

        Returns:
            ID del caso guardado.
        """
        with self._conectar() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO casos
                    (numero_incidente, canal, motivo, importe, numero_cuenta,
                     resolucion_sugerida, texto_diario, aprobado, analista)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    caso.get("numero_incidente", ""),
                    caso.get("canal", ""),
                    caso.get("motivo", ""),
                    float(caso.get("importe") or 0),
                    caso.get("numero_cuenta", ""),
                    caso.get("resolucion_sugerida", ""),
                    caso.get("texto_diario", ""),
                    1 if caso.get("aprobado") else 0,
                    caso.get("analista", ""),
                ),
            )
            caso_id = int(cursor.lastrowid)
        self.logger.info("Caso guardado: %s", caso_id)
        return caso_id

    def actualizar_aprobacion(self, caso_id: int, aprobado: bool, analista: str) -> None:
        """Actualiza aprobacion humana de un caso.

        Args:
            caso_id: ID del caso.
            aprobado: Estado aprobado/rechazado.
            analista: Nombre o identificador del analista.
        """
        with self._conectar() as conexion:
            conexion.execute(
                """
                UPDATE casos
                SET aprobado = ?, analista = ?
                WHERE id = ?
                """,
                (1 if aprobado else 0, analista, caso_id),
            )
        self.logger.info("Aprobacion actualizada para caso %s", caso_id)

    def listar_casos(self) -> list[dict[str, Any]]:
        """Lista casos analizados.

        Returns:
            Casos guardados como diccionarios.
        """
        with self._conectar() as conexion:
            filas = conexion.execute(
                """
                SELECT id, numero_incidente, canal, motivo, importe,
                       numero_cuenta, resolucion_sugerida, texto_diario,
                       aprobado, analista, creado_en
                FROM casos
                ORDER BY id DESC
                """
            ).fetchall()
        return [dict(fila) for fila in filas]
