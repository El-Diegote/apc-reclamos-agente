"""Construccion del expediente consolidado de un reclamo APC."""

from __future__ import annotations

import logging
from typing import Any

from src.utils import normalizar_texto, parsear_importe


class ClaimUniverseBuilder:
    """Consolida APC, documentacion y Smart Console en una vista unica."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Inicializa el constructor.

        Args:
            logger: Logger opcional.
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def construir(
        self,
        detalle_apc: dict[str, Any] | None = None,
        diario_apc: list[str] | None = None,
        documentacion: list[dict[str, Any]] | None = None,
        smart_console: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Construye el universo del reclamo desde fuentes parciales.

        Args:
            detalle_apc: Datos leidos de la solapa Detalle.
            diario_apc: Notas leidas de la solapa Diario.
            documentacion: Clasificaciones documentales.
            smart_console: Resumen generado por SmartConsoleAnalyzer.

        Returns:
            Diccionario consolidado para decisiones y resolucion.
        """
        detalle = detalle_apc or {}
        diario = diario_apc or []
        docs = documentacion or []
        smart = smart_console or {}

        operaciones = self.extraer_operaciones_reclamadas(detalle, smart)
        universo = {
            "incidente": self._primer_texto(detalle, ["incidente", "numero_incidente", "nro_operacion"]),
            "cliente": self._primer_texto(detalle, ["cliente", "nombre_apellido", "nombre y apellido"]),
            "cuentas": self._consolidar_cuentas(detalle, smart, operaciones),
            "canales": self._consolidar_canales(detalle, smart, operaciones),
            "motivo": self._primer_texto(detalle, ["motivo", "detalle", "descripcion"]),
            "diario_apc": diario,
            "documentos": docs,
            "smart_console": smart,
            "operaciones_reclamadas": operaciones,
            "importe_total_reclamado": round(sum(parsear_importe(op.get("importe")) for op in operaciones), 2),
            "banderas": self._detectar_banderas(diario, docs, smart),
            "fuentes": self._fuentes_presentes(detalle, diario, docs, smart),
            "requiere_aprobacion_humana": True,
        }
        self.logger.info("Universo APC construido para incidente %s", universo.get("incidente"))
        return universo

    def extraer_operaciones_reclamadas(
        self,
        detalle_apc: dict[str, Any],
        smart_console: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Obtiene operaciones reclamadas desde Smart Console y detalle APC.

        Args:
            detalle_apc: Datos leidos de APC.
            smart_console: Resumen Smart Console.

        Returns:
            Lista de operaciones candidatas a decision.
        """
        operaciones = list(smart_console.get("operaciones", []) or [])
        operaciones_check = [op for op in operaciones if op.get("check")]
        if operaciones_check:
            return operaciones_check

        importe_detalle = parsear_importe(detalle_apc.get("importe"))
        if importe_detalle:
            return [
                {
                    "fecha": detalle_apc.get("fecha", ""),
                    "hora": detalle_apc.get("hora", ""),
                    "importe": importe_detalle,
                    "moneda": detalle_apc.get("moneda", "Peso"),
                    "cuenta_origen": detalle_apc.get("numero_cuenta", ""),
                    "canal": detalle_apc.get("canal", ""),
                    "check": True,
                    "fuente": "detalle_apc",
                }
            ]
        return []

    def _consolidar_cuentas(
        self,
        detalle_apc: dict[str, Any],
        smart_console: dict[str, Any],
        operaciones: list[dict[str, Any]],
    ) -> list[str]:
        """Consolida cuentas detectadas en todas las fuentes."""
        cuentas = [str(detalle_apc.get("numero_cuenta", "") or "")]
        cuentas.extend(str(cuenta) for cuenta in smart_console.get("cuentas_origen", []) or [])
        cuentas.extend(str(op.get("cuenta_origen", "") or "") for op in operaciones)
        return self._unicos(cuentas)

    def _consolidar_canales(
        self,
        detalle_apc: dict[str, Any],
        smart_console: dict[str, Any],
        operaciones: list[dict[str, Any]],
    ) -> list[str]:
        """Consolida canales detectados en todas las fuentes."""
        canales = [str(detalle_apc.get("canal", "") or "")]
        canales.extend(str(canal) for canal in smart_console.get("canales_detectados", []) or [])
        canales.extend(str(op.get("canal", "") or "") for op in operaciones)
        return self._unicos(canales)

    def _detectar_banderas(
        self,
        diario_apc: list[str],
        documentacion: list[dict[str, Any]],
        smart_console: dict[str, Any],
    ) -> dict[str, bool]:
        """Detecta banderas de fraude o faltantes documentales."""
        texto_diario = normalizar_texto(" ".join(diario_apc)).lower()
        tipos_docs = {str(doc.get("tipo_documento", "")) for doc in documentacion}
        return {
            "robo_hurto_extravio": bool(smart_console.get("tiene_robo"))
            or any(palabra in texto_diario for palabra in ("robo", "hurto", "extrav")),
            "denuncia_policial": "Denuncia" in tipos_docs,
            "f60330_presente": "F60330" in tipos_docs,
            "requiere_ocr": any(bool(doc.get("requiere_ocr")) for doc in documentacion),
        }

    def _fuentes_presentes(
        self,
        detalle_apc: dict[str, Any],
        diario_apc: list[str],
        documentacion: list[dict[str, Any]],
        smart_console: dict[str, Any],
    ) -> list[str]:
        """Lista las fuentes efectivamente disponibles."""
        fuentes: list[str] = []
        if detalle_apc:
            fuentes.append("Detalle APC")
        if diario_apc:
            fuentes.append("Diario APC")
        if documentacion:
            fuentes.append("Documentacion APC")
        if smart_console:
            fuentes.append("Smart Console")
        return fuentes

    def _primer_texto(self, datos: dict[str, Any], claves: list[str]) -> str:
        """Obtiene el primer texto no vacio entre varias claves."""
        for clave in claves:
            valor = datos.get(clave)
            if valor is not None and str(valor).strip():
                return str(valor).strip()
        return ""

    def _unicos(self, valores: list[str]) -> list[str]:
        """Devuelve valores unicos preservando orden."""
        resultado: list[str] = []
        vistos: set[str] = set()
        for valor in valores:
            limpio = valor.strip()
            if limpio and limpio not in vistos:
                vistos.add(limpio)
                resultado.append(limpio)
        return resultado
