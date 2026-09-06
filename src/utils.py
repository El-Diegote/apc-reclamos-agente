"""Utilidades compartidas para el proyecto APC Reclamos."""

from __future__ import annotations

import csv
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from config.config import DATETIME_FORMAT, LOG_FORMAT, LOG_LEVEL, LOGS_DIR


class SesionExpiradaError(RuntimeError):
    """Error controlado para indicar que la sesion simulada expiro."""


def configurar_logging(nombre_log: str = "apc_reclamos.log") -> None:
    """Configura logging en consola y archivo.

    Args:
        nombre_log: Nombre del archivo de log que se guardara en `logs/`.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / nombre_log

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
        force=True,
    )


def obtener_logger(nombre: str) -> logging.Logger:
    """Devuelve un logger con el nombre indicado.

    Args:
        nombre: Nombre logico del componente.

    Returns:
        Logger configurado.
    """
    return logging.getLogger(nombre)


def cargar_json(path: Path) -> dict[str, Any]:
    """Carga un archivo JSON.

    Args:
        path: Ruta del archivo JSON.

    Returns:
        Contenido JSON como diccionario.
    """
    with path.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_json(path: Path, datos: dict[str, Any]) -> None:
    """Guarda un diccionario como JSON formateado.

    Args:
        path: Ruta de salida.
        datos: Datos a serializar.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def cargar_csv_incidentes(path: Path) -> list[dict[str, str]]:
    """Carga incidentes desde un CSV diario.

    Args:
        path: Ruta del archivo CSV.

    Returns:
        Lista de filas del CSV como diccionarios.
    """
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as archivo:
        return [dict(fila) for fila in csv.DictReader(archivo)]


def normalizar_texto(texto: str) -> str:
    """Normaliza espacios para facilitar busquedas y extracciones.

    Args:
        texto: Texto original.

    Returns:
        Texto con espacios normalizados.
    """
    return re.sub(r"\s+", " ", texto).strip()


def parsear_importe(valor: str | float | int | None) -> float:
    """Convierte un importe textual a numero flotante.

    Args:
        valor: Importe como texto o numero.

    Returns:
        Importe convertido. Devuelve `0.0` si no puede parsearse.
    """
    if valor is None:
        return 0.0

    if isinstance(valor, (float, int)):
        return float(valor)

    limpio = valor.strip().replace("$", "").replace("ARS", "").replace(" ", "")
    # Si aparece coma decimal, se retiran puntos de miles y se convierte coma a punto.
    if "," in limpio and "." in limpio:
        limpio = limpio.replace(".", "").replace(",", ".")
    else:
        limpio = limpio.replace(",", ".")

    try:
        return float(limpio)
    except ValueError:
        return 0.0


def timestamp_actual() -> str:
    """Devuelve el timestamp actual en formato configurable.

    Returns:
        Timestamp local como texto.
    """
    return datetime.now().strftime(DATETIME_FORMAT)


def buscar_primer_match(patrones: list[str], texto: str) -> str:
    """Busca el primer match de una lista de patrones regex.

    Args:
        patrones: Patrones regex con un grupo de captura.
        texto: Texto donde buscar.

    Returns:
        Primer valor capturado o cadena vacia.
    """
    for patron in patrones:
        match = re.search(patron, texto, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""
