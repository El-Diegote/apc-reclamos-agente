"""Script de ejemplo para ejecutar el agente APC Reclamos."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config.config import CORRIDAS_DIR, DEFAULT_CORRIDA, DEFAULT_CSV_NAME
from src.agente import Agente
from src.utils import SesionExpiradaError, cargar_csv_incidentes, configurar_logging, obtener_logger


def obtener_incidente_desde_csv(corrida: str) -> str:
    """Obtiene el primer incidente disponible en el CSV de la corrida.

    Args:
        corrida: Nombre de la corrida.

    Returns:
        Numero de incidente encontrado o valor de ejemplo.
    """
    csv_path = CORRIDAS_DIR / corrida / "entrada" / DEFAULT_CSV_NAME
    filas = cargar_csv_incidentes(csv_path)
    if filas and filas[0].get("numero_incidente"):
        return filas[0]["numero_incidente"]
    return "INC-2026-0001"


def parse_args() -> argparse.Namespace:
    """Parsea argumentos de linea de comandos.

    Returns:
        Namespace con argumentos de ejecucion.
    """
    parser = argparse.ArgumentParser(description="Procesa reclamos APC simulados.")
    parser.add_argument("--incidente", help="Numero de incidente a procesar.")
    parser.add_argument("--corrida", default=DEFAULT_CORRIDA, help="Carpeta de corrida a usar.")
    return parser.parse_args()


def main() -> int:
    """Ejecuta una corrida completa del agente.

    Returns:
        Codigo de salida del proceso.
    """
    configurar_logging()
    logger = obtener_logger("main")
    args = parse_args()
    numero_incidente = args.incidente or obtener_incidente_desde_csv(args.corrida)

    try:
        agente = Agente(numero_incidente=numero_incidente, corrida=args.corrida, logger=logger)
        if not agente.buscar_incidente(numero_incidente):
            logger.error("No se encontro el incidente %s en el CSV diario.", numero_incidente)
            return 1

        agente.leer_solapas()
        resultado = agente.analizar()
        salida = agente.generar_json()

        print(f"Incidente procesado: {resultado['numero_incidente']}")
        print(f"Estado: {resultado['estado']}")
        print(f"Resultado general: {resultado['validaciones']['resultado_general']}")
        print(f"JSON generado: {Path(salida)}")
        return 0
    except SesionExpiradaError as exc:
        logger.error("Sesion expirada: %s", exc)
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        logger.exception("Error inesperado durante la corrida.")
        print(f"Error inesperado: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
