"""Preferencias locales de la aplicacion desktop APC."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from config.config import DEFAULT_RESOLUCIONES_APC_PATH, LOCAL_SETTINGS_PATH


class AppSettings:
    """Administra preferencias locales no versionadas."""

    def __init__(
        self,
        path: Path = LOCAL_SETTINGS_PATH,
        logger: logging.Logger | None = None,
    ) -> None:
        """Inicializa el administrador de preferencias.

        Args:
            path: Ruta del JSON local.
            logger: Logger opcional.
        """
        self.path = path
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def cargar(self) -> dict[str, Any]:
        """Carga preferencias locales.

        Returns:
            Diccionario de preferencias. Si no existe, devuelve valores base.
        """
        if not self.path.exists():
            return self._defaults()
        try:
            with self.path.open("r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            return {**self._defaults(), **datos}
        except (OSError, json.JSONDecodeError) as exc:
            self.logger.warning("No se pudieron leer preferencias locales: %s", exc)
            return self._defaults()

    def guardar(self, datos: dict[str, Any]) -> None:
        """Guarda preferencias locales.

        Args:
            datos: Preferencias a persistir.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as archivo:
            json.dump({**self._defaults(), **datos}, archivo, ensure_ascii=False, indent=2)

    def obtener_ruta_resoluciones_apc(self) -> Path:
        """Obtiene la ruta vigente del Excel de resoluciones.

        Returns:
            Ruta configurada o ruta predeterminada de esta maquina.
        """
        datos = self.cargar()
        return Path(str(datos.get("resoluciones_apc_path") or DEFAULT_RESOLUCIONES_APC_PATH))

    def guardar_ruta_resoluciones_apc(self, ruta: Path) -> None:
        """Actualiza la ruta local del Excel de resoluciones.

        Args:
            ruta: Ruta elegida por el usuario.
        """
        datos = self.cargar()
        datos["resoluciones_apc_path"] = str(ruta)
        self.guardar(datos)

    def _defaults(self) -> dict[str, Any]:
        """Devuelve preferencias predeterminadas."""
        return {
            "resoluciones_apc_path": str(DEFAULT_RESOLUCIONES_APC_PATH),
        }
