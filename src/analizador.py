"""Logica de validacion para reclamos APC."""

from __future__ import annotations

import logging
from typing import Any

from src.extractor import Extractor
from src.utils import parsear_importe


class Analizador:
    """Analiza solapas APC simuladas y documentos asociados."""

    def __init__(
        self,
        solapas: dict[str, Any],
        textos_documentos: list[str],
        logger: logging.Logger | None = None,
    ) -> None:
        """Inicializa el analizador.

        Args:
            solapas: Datos simulados de las solapas APC.
            textos_documentos: Textos extraidos desde documentos.
            logger: Logger opcional.
        """
        self.solapas = solapas
        self.textos_documentos = textos_documentos
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def validar_requisito_1(self) -> bool:
        """Valida que exista detalle minimo del incidente.

        Returns:
            `True` si el incidente tiene numero, motivo y cuenta.
        """
        detalle = self.solapas.get("detalle", {})
        valido = bool(
            detalle.get("numero_incidente")
            and detalle.get("motivo")
            and detalle.get("numero_cuenta")
        )
        self.logger.info("Requisito 1 validado: %s", valido)
        return valido

    def validar_requisito_2(self) -> bool:
        """Valida que exista registro diario con fecha, hora e importe.

        Returns:
            `True` si el diario contiene los campos operativos minimos.
        """
        diario = self.solapas.get("diario", {})
        importe = parsear_importe(diario.get("importe"))
        valido = bool(diario.get("fecha") and diario.get("hora") and importe > 0)
        self.logger.info("Requisito 2 validado: %s", valido)
        return valido

    def validar_requisito_3(self) -> bool:
        """Valida que haya documentacion o evidencia asociada.

        Returns:
            `True` si existe al menos un documento o evidencia declarada.
        """
        documentacion = self.solapas.get("documentacion", {})
        documentos = documentacion.get("archivos", [])
        valido = bool(documentos or self.textos_documentos)
        self.logger.info("Requisito 3 validado: %s", valido)
        return valido

    def validar_todos(self) -> dict[str, bool]:
        """Ejecuta todas las validaciones.

        Returns:
            Diccionario con resultado por requisito y resultado general.
        """
        resultados = {
            "requisito_1": self.validar_requisito_1(),
            "requisito_2": self.validar_requisito_2(),
            "requisito_3": self.validar_requisito_3(),
        }
        resultados["resultado_general"] = all(resultados.values())
        return resultados

    def extraer_datos_criticos(self) -> dict[str, str | float]:
        """Extrae datos criticos desde solapas y documentos.

        Returns:
            Diccionario con fecha, hora, importe, numero de cuenta y motivo.
        """
        detalle = self.solapas.get("detalle", {})
        diario = self.solapas.get("diario", {})
        datos: dict[str, str | float] = {
            "fecha": str(diario.get("fecha") or ""),
            "hora": str(diario.get("hora") or ""),
            "importe": parsear_importe(diario.get("importe")),
            "numero_cuenta": str(detalle.get("numero_cuenta") or ""),
            "motivo": str(detalle.get("motivo") or ""),
        }

        # Completa faltantes usando el texto documental consolidado.
        texto_consolidado = "\n".join(self.textos_documentos)
        if texto_consolidado:
            extractor = Extractor(logger=self.logger)
            extractor._contenido_reciente = texto_consolidado
            datos["fecha"] = datos["fecha"] or extractor.extraer_fecha()
            datos["hora"] = datos["hora"] or extractor.extraer_hora()
            datos["importe"] = datos["importe"] or extractor.extraer_importe()
            datos["numero_cuenta"] = datos["numero_cuenta"] or extractor.extraer_numero_cuenta()
            datos["motivo"] = datos["motivo"] or extractor.extraer_motivo()

        self.logger.info("Datos criticos extraidos: %s", datos)
        return datos
