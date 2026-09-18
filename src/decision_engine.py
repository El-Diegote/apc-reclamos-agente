"""Motor inicial de evaluacion y decision para operaciones APC."""

from __future__ import annotations

import logging
from typing import Any

from config.config import CIRCUITO_USD_THRESHOLD, DEFAULT_COEFICIENTE_DOLAR
from src.utils import normalizar_texto, parsear_importe


class FraudAssessmentEngine:
    """Evalua senales de fraude, robo o faltantes documentales."""

    FRAUD_TERMS = ("robo", "hurto", "extrav", "fraude", "estafa", "ingenieria social")

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Inicializa el evaluador.

        Args:
            logger: Logger opcional.
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def evaluar(self, universo: dict[str, Any]) -> dict[str, Any]:
        """Evalua riesgo y evidencias del expediente.

        Args:
            universo: Reclamo consolidado por ClaimUniverseBuilder.

        Returns:
            Resultado de evaluacion de fraude.
        """
        texto = normalizar_texto(
            " ".join(
                [
                    str(universo.get("motivo", "")),
                    " ".join(str(nota) for nota in universo.get("diario_apc", []) or []),
                ]
            )
        ).lower()
        banderas = universo.get("banderas", {}) or {}
        senales_texto = [termino for termino in self.FRAUD_TERMS if termino in texto]
        tiene_senal = bool(senales_texto) or bool(banderas.get("robo_hurto_extravio"))
        return {
            "riesgo_fraude": "alto" if tiene_senal else "medio",
            "senales": senales_texto,
            "denuncia_policial": bool(banderas.get("denuncia_policial")),
            "robo_hurto_extravio": bool(banderas.get("robo_hurto_extravio")),
            "requiere_revision_documental": bool(banderas.get("requiere_ocr")),
        }


class OperationDecisionEngine:
    """Sugiere tratamiento operativo para operaciones reclamadas."""

    def __init__(
        self,
        circuito_usd_threshold: float = CIRCUITO_USD_THRESHOLD,
        coeficiente_dolar: float = DEFAULT_COEFICIENTE_DOLAR,
        logger: logging.Logger | None = None,
    ) -> None:
        """Inicializa el motor de decision.

        Args:
            circuito_usd_threshold: Umbral inicial para circuito.
            coeficiente_dolar: Coeficiente de conversion peso/dolar.
            logger: Logger opcional.
        """
        self.circuito_usd_threshold = circuito_usd_threshold
        self.coeficiente_dolar = coeficiente_dolar
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def decidir(self, universo: dict[str, Any]) -> dict[str, Any]:
        """Sugiere una decision operativa revisable.

        Args:
            universo: Reclamo consolidado por ClaimUniverseBuilder.

        Returns:
            Decision sugerida con fundamentos.
        """
        operaciones = universo.get("operaciones_reclamadas", []) or []
        total = parsear_importe(universo.get("importe_total_reclamado"))
        total_usd = self._total_equivalente_usd(operaciones, total)
        tiene_link_go = any(bool(op.get("link_go")) for op in operaciones) or bool(
            universo.get("smart_console", {}).get("tiene_link_go")
        )

        if not operaciones:
            decision = "REVISION_MANUAL"
            fundamento = "No hay operaciones reclamadas consolidadas."
        elif tiene_link_go:
            decision = "LINK_GO"
            fundamento = "Hay operaciones con referencia LINK GO o gestion asociada."
        elif 0 < total_usd <= self.circuito_usd_threshold:
            decision = "CIRCUITO"
            fundamento = f"Importe equivalente estimado dentro del umbral USD {self.circuito_usd_threshold:.2f}."
        else:
            decision = "PAGAR"
            fundamento = "No se detecto trazabilidad LINK GO y requiere tratamiento operativo."

        resultado = {
            "decision": decision,
            "fundamento": fundamento,
            "total_equivalente_usd": round(total_usd, 2),
            "requiere_aprobacion_humana": True,
        }
        self.logger.info("Decision sugerida: %s", decision)
        return resultado

    def _total_equivalente_usd(self, operaciones: list[dict[str, Any]], total: float) -> float:
        """Calcula total equivalente en USD para reglas de circuito."""
        if not operaciones:
            return total / self.coeficiente_dolar if self.coeficiente_dolar else total

        acumulado = 0.0
        for operacion in operaciones:
            importe = parsear_importe(operacion.get("importe"))
            moneda = str(operacion.get("moneda", "Peso")).lower()
            if "dolar" in moneda or "usd" in moneda or "u$s" in moneda:
                acumulado += importe
            else:
                acumulado += importe / self.coeficiente_dolar if self.coeficiente_dolar else importe
        return acumulado
