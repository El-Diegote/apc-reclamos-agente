"""Generacion de Tema y Detalle para la solapa Diario APC."""

from __future__ import annotations

import logging
from typing import Any

from src.decision_engine import FraudAssessmentEngine, OperationDecisionEngine


class ResolutionEngine:
    """Genera una resolucion sugerida basada en expediente y reglas."""

    def __init__(
        self,
        decision_engine: OperationDecisionEngine | None = None,
        fraud_engine: FraudAssessmentEngine | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Inicializa el generador de resoluciones.

        Args:
            decision_engine: Motor de decision opcional.
            fraud_engine: Evaluador de fraude opcional.
            logger: Logger opcional.
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.decision_engine = decision_engine or OperationDecisionEngine(logger=self.logger)
        self.fraud_engine = fraud_engine or FraudAssessmentEngine(logger=self.logger)

    def generar(
        self,
        universo: dict[str, Any],
        resoluciones_entrenadas: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Genera Tema y Detalle revisables para Diario APC.

        Args:
            universo: Expediente consolidado.
            resoluciones_entrenadas: Resoluciones APC cargadas desde base local.

        Returns:
            Resolucion estructurada con tema, detalle y fundamentos.
        """
        decision = self.decision_engine.decidir(universo)
        fraude = self.fraud_engine.evaluar(universo)
        plantilla = self._buscar_plantilla(universo, decision, resoluciones_entrenadas or [])

        if plantilla:
            tema = str(plantilla.get("motivo") or plantilla.get("tema") or decision["decision"])
            detalle = str(
                plantilla.get("texto_diario")
                or plantilla.get("texto_resolucion")
                or self._detalle_base(universo, decision, fraude)
            )
            fuente = f"resolucion_entrenada:{plantilla.get('id', 'sin_id')}"
        else:
            tema = self._tema_base(universo, decision)
            detalle = self._detalle_base(universo, decision, fraude)
            fuente = "reglas_operativas_mvp"

        resultado = {
            "tema": tema,
            "detalle": detalle,
            "decision": decision,
            "evaluacion_fraude": fraude,
            "fuente": fuente,
            "requiere_aprobacion_humana": True,
        }
        self.logger.info("Resolucion sugerida generada para tema %s", tema)
        return resultado

    def _buscar_plantilla(
        self,
        universo: dict[str, Any],
        decision: dict[str, Any],
        resoluciones: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Busca una resolucion entrenada compatible con el universo."""
        canales = {str(canal).lower() for canal in universo.get("canales", []) or []}
        motivo = str(universo.get("motivo", "")).lower()
        decision_texto = str(decision.get("decision", "")).lower()

        for resolucion in resoluciones:
            canal = str(resolucion.get("canal", "")).lower()
            patron = str(resolucion.get("motivo", "")).lower()
            if canal and canal not in canales and canal != "otros":
                continue
            if patron and (patron in motivo or patron in decision_texto or decision_texto in patron):
                return resolucion
        return None

    def _tema_base(self, universo: dict[str, Any], decision: dict[str, Any]) -> str:
        """Construye un Tema base para APC."""
        canales = universo.get("canales", []) or ["Otros"]
        return f"{canales[0]} - {decision.get('decision', 'REVISION_MANUAL')}"

    def _detalle_base(
        self,
        universo: dict[str, Any],
        decision: dict[str, Any],
        fraude: dict[str, Any],
    ) -> str:
        """Construye un Detalle base para revision humana."""
        incidente = universo.get("incidente", "")
        total = universo.get("importe_total_reclamado", 0)
        cuentas = ", ".join(universo.get("cuentas", []) or [])
        return (
            f"Se analiza el incidente {incidente}. "
            f"Operaciones reclamadas consolidadas: {len(universo.get('operaciones_reclamadas', []) or [])}. "
            f"Importe total reclamado: {total}. "
            f"Cuentas detectadas: {cuentas}. "
            f"Decision sugerida: {decision.get('decision')}. "
            f"Fundamento: {decision.get('fundamento')} "
            f"Evaluacion de fraude: {fraude.get('riesgo_fraude')}. "
            "Texto sujeto a revision y aprobacion del analista antes de informar en APC."
        )
