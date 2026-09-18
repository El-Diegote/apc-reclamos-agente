"""Analisis de adjuntos de la solapa Documentacion APC."""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import asdict, dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

import pandas as pd

from src.document_classifier import DocumentClassifier
from src.extractor import Extractor
from src.utils import normalizar_texto, parsear_importe


@dataclass(slots=True)
class DocumentationOperation:
    """Operacion reclamada o consultada extraida de un adjunto."""

    archivo: str
    tipo_documento: str
    fecha: str
    hora: str
    importe: float
    moneda: str
    cuenta: str
    canal: str
    motivo: str
    descripcion: str
    referencia: str


class DocumentationAnalyzer:
    """Valida adjuntos y arma el listado de operaciones reclamadas."""

    COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
        "fecha": ("fecha", "fecha trx", "fecha operacion", "fecha operación", "dia"),
        "hora": ("hora", "hora trx", "hora operacion", "hora operación"),
        "importe": ("importe $", "importe", "monto", "monto reclamado", "importe reclamado"),
        "moneda": ("moneda", "divisa"),
        "cuenta": ("cuenta desde", "cuenta", "numero cuenta", "nro cuenta", "cta dde", "cta desde"),
        "canal": ("canal", "tema", "origen"),
        "motivo": ("motivo", "detalle", "descripcion", "descripción", "concepto"),
        "descripcion": ("descripcion", "descripción", "comercio", "establecimiento", "detalle"),
    }

    def __init__(
        self,
        classifier: DocumentClassifier | None = None,
        extractor: Extractor | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Inicializa el analizador documental.

        Args:
            classifier: Clasificador documental opcional.
            extractor: Extractor textual opcional.
            logger: Logger opcional.
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.extractor = extractor or Extractor(logger=self.logger)
        self.classifier = classifier or DocumentClassifier(
            extractor=self.extractor,
            logger=self.logger,
        )

    def analizar(self, archivos: list[Path]) -> dict[str, Any]:
        """Valida y analiza adjuntos documentales.

        Args:
            archivos: Adjuntos descargados desde la solapa Documentacion APC.

        Returns:
            Resultado serializable con clasificaciones, operaciones y faltantes.
        """
        if not archivos:
            return self._resultado(
                total_archivos=0,
                archivos_validos=0,
                clasificaciones=[],
                operaciones=[],
                faltantes=["No se encontraron adjuntos en la solapa Documentacion."],
                advertencias=[],
            )

        clasificaciones: list[dict[str, Any]] = []
        operaciones: list[DocumentationOperation] = []
        faltantes: list[str] = []
        advertencias: list[str] = []
        archivos_validos = 0

        for archivo in archivos:
            if not self._archivo_legible(archivo):
                faltantes.append(f"{archivo.name}: archivo vacio o no legible.")
                continue

            archivos_validos += 1
            try:
                clasificacion = self.classifier.clasificar_archivo(archivo)
                clasificacion_dict = asdict(clasificacion)
                clasificaciones.append(clasificacion_dict)
                if clasificacion.requiere_ocr:
                    faltantes.append(f"{archivo.name}: requiere OCR o tiene letra ilegible.")
                    continue

                extraidas = self._extraer_operaciones_archivo(archivo, clasificacion.tipo_documento)
                if not extraidas:
                    advertencias.append(
                        f"{archivo.name}: no se pudo traducir el adjunto a operaciones."
                    )
                operaciones.extend(extraidas)
            except Exception as exc:
                self.logger.warning("No se pudo analizar documentacion %s: %s", archivo.name, exc)
                faltantes.append(f"{archivo.name}: error de formato o lectura ({exc}).")

        operaciones_dict = [asdict(operacion) for operacion in operaciones]
        faltantes.extend(self._validar_operaciones(operaciones_dict))
        return self._resultado(
            total_archivos=len(archivos),
            archivos_validos=archivos_validos,
            clasificaciones=clasificaciones,
            operaciones=operaciones_dict,
            faltantes=faltantes,
            advertencias=advertencias,
        )

    def _resultado(
        self,
        total_archivos: int,
        archivos_validos: int,
        clasificaciones: list[dict[str, Any]],
        operaciones: list[dict[str, Any]],
        faltantes: list[str],
        advertencias: list[str],
    ) -> dict[str, Any]:
        """Arma el resultado documental normalizado."""
        operaciones_completas = [
            operacion for operacion in operaciones if self._operacion_completa(operacion)
        ]
        return {
            "total_archivos": total_archivos,
            "archivos_validos": archivos_validos,
            "documentacion_valida": total_archivos > 0
            and archivos_validos > 0
            and bool(operaciones_completas)
            and not faltantes,
            "clasificaciones": clasificaciones,
            "operaciones": operaciones,
            "operaciones_completas": operaciones_completas,
            "faltantes": list(dict.fromkeys(faltantes)),
            "advertencias": list(dict.fromkeys(advertencias)),
        }

    def _extraer_operaciones_archivo(
        self,
        archivo: Path,
        tipo_documento: str,
    ) -> list[DocumentationOperation]:
        """Extrae operaciones desde un archivo soportado."""
        extension = archivo.suffix.lower()
        if extension in {".xlsx", ".xlsm", ".xls"}:
            return self._extraer_operaciones_excel(archivo, tipo_documento)
        if extension == ".csv":
            return self._extraer_operaciones_dataframe(
                pd.read_csv(archivo),
                archivo.name,
                tipo_documento,
            )
        texto = self._leer_texto(archivo, extension)
        return self._extraer_operaciones_texto(texto, archivo.name, tipo_documento)

    def _extraer_operaciones_excel(
        self,
        archivo: Path,
        tipo_documento: str,
    ) -> list[DocumentationOperation]:
        """Extrae operaciones desde todas las hojas tabulares de un Excel."""
        operaciones: list[DocumentationOperation] = []
        excel = pd.ExcelFile(archivo)
        for hoja in excel.sheet_names:
            dataframe = pd.read_excel(archivo, sheet_name=hoja)
            operaciones.extend(
                self._extraer_operaciones_dataframe(
                    dataframe,
                    archivo.name,
                    tipo_documento,
                    hoja,
                )
            )
        return operaciones

    def _extraer_operaciones_dataframe(
        self,
        dataframe: pd.DataFrame,
        archivo: str,
        tipo_documento: str,
        hoja: str = "",
    ) -> list[DocumentationOperation]:
        """Extrae operaciones desde filas tabulares."""
        if dataframe.empty:
            return []

        columnas = {self._normalizar_clave(columna): columna for columna in dataframe.columns}
        operaciones: list[DocumentationOperation] = []
        for indice, fila in dataframe.iterrows():
            fecha = self._texto_valor(self._valor(fila, columnas, "fecha"))
            hora = self._texto_valor(self._valor(fila, columnas, "hora"))
            importe = parsear_importe(self._valor(fila, columnas, "importe"))
            cuenta = self._normalizar_cuenta(self._valor(fila, columnas, "cuenta"))
            motivo = self._texto_valor(self._valor(fila, columnas, "motivo"))
            descripcion = self._texto_valor(self._valor(fila, columnas, "descripcion"))
            if not any([fecha, hora, importe, cuenta, motivo, descripcion]):
                continue
            operaciones.append(
                DocumentationOperation(
                    archivo=archivo,
                    tipo_documento=tipo_documento,
                    fecha=self._normalizar_fecha(fecha),
                    hora=self._normalizar_hora(hora),
                    importe=importe,
                    moneda=self._texto_valor(self._valor(fila, columnas, "moneda")) or "Peso",
                    cuenta=cuenta,
                    canal=self._texto_valor(self._valor(fila, columnas, "canal")),
                    motivo=motivo,
                    descripcion=descripcion,
                    referencia=f"{hoja or 'Hoja'} fila {indice + 2}",
                )
            )
        return operaciones

    def _extraer_operaciones_texto(
        self,
        texto: str,
        archivo: str,
        tipo_documento: str,
    ) -> list[DocumentationOperation]:
        """Extrae una operacion desde texto libre cuando hay datos suficientes."""
        if not texto.strip():
            return []
        fecha = self._buscar_regex(
            [r"\b(\d{4}-\d{2}-\d{2})\b", r"\b(\d{2}/\d{2}/\d{4})\b"],
            texto,
        )
        hora = self._buscar_regex([r"\b(([01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?)\b"], texto)
        importe_texto = self._buscar_regex(
            [r"(?:importe|monto)[:\s$ARS]*([\d.,]+)", r"\$[\s]*([\d.,]+)"],
            texto,
        )
        cuenta = self._buscar_regex(
            [
                r"(?:numero de cuenta|n[uú]mero de cuenta|cuenta)[:\s]+([A-Z0-9-]{6,})",
                r"\b(\d{10,22})\b",
            ],
            texto,
        )
        motivo = self._buscar_regex([r"motivo[:\s]+(.+?)(?:\.|$)"], texto)
        if not any([fecha, hora, importe_texto, cuenta, motivo]):
            return []
        return [
            DocumentationOperation(
                archivo=archivo,
                tipo_documento=tipo_documento,
                fecha=self._normalizar_fecha(fecha),
                hora=self._normalizar_hora(hora),
                importe=parsear_importe(importe_texto),
                moneda="Peso",
                cuenta=self._normalizar_cuenta(cuenta),
                canal="",
                motivo=normalizar_texto(motivo),
                descripcion=normalizar_texto(texto[:180]),
                referencia="Texto extraido",
            )
        ]

    def _validar_operaciones(self, operaciones: list[dict[str, Any]]) -> list[str]:
        """Devuelve faltantes que impiden armar el listado operativo."""
        if not operaciones:
            return ["No se pudo reconstruir un listado de operaciones reclamadas."]

        faltantes: list[str] = []
        completas = [operacion for operacion in operaciones if self._operacion_completa(operacion)]
        if not completas:
            faltantes.append(
                "Las operaciones detectadas no tienen fecha, hora e importe suficientes."
            )
        for indice, operacion in enumerate(operaciones, start=1):
            campos = [
                campo
                for campo in ("fecha", "hora", "importe")
                if not operacion.get(campo)
            ]
            if campos:
                faltantes.append(
                    f"Operacion documental {indice}: falta {', '.join(campos)}."
                )
        return faltantes

    def _operacion_completa(self, operacion: dict[str, Any]) -> bool:
        """Indica si una operacion tiene campos minimos para analizar."""
        return bool(operacion.get("fecha")) and bool(operacion.get("hora")) and bool(
            operacion.get("importe")
        )

    def _leer_texto(self, archivo: Path, extension: str) -> str:
        """Lee texto segun extension."""
        if extension == ".txt":
            return self.extractor.leer_txt(str(archivo))
        if extension == ".pdf":
            return self.extractor.leer_pdf(str(archivo))
        return ""

    def _archivo_legible(self, archivo: Path) -> bool:
        """Valida existencia, peso y lectura minima."""
        try:
            return archivo.is_file() and archivo.stat().st_size > 0
        except OSError:
            return False

    def _valor(self, fila: pd.Series, columnas: dict[str, Any], campo: str) -> Any:
        """Obtiene el primer valor de una fila segun aliases."""
        for alias in self.COLUMN_ALIASES[campo]:
            columna = columnas.get(self._normalizar_clave(alias))
            if columna is not None:
                valor = fila.get(columna)
                if not self._vacio(valor):
                    return valor
        return ""

    def _texto_valor(self, valor: Any) -> str:
        """Convierte valores a texto, preservando fechas y horas utiles."""
        if self._vacio(valor):
            return ""
        if isinstance(valor, datetime):
            return valor.isoformat(sep=" ")
        if isinstance(valor, date):
            return valor.isoformat()
        if isinstance(valor, time):
            return valor.strftime("%H:%M:%S")
        return str(valor).strip()

    def _normalizar_fecha(self, valor: str) -> str:
        """Normaliza fechas detectadas a texto estable."""
        texto = self._texto_valor(valor)
        if " " in texto and re.match(r"\d{4}-\d{2}-\d{2}", texto):
            return texto.split(" ", maxsplit=1)[0]
        return texto

    def _normalizar_hora(self, valor: str) -> str:
        """Normaliza horas detectadas."""
        texto = self._texto_valor(valor)
        match = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)(?::([0-5]\d))?\b", texto)
        return match.group(0) if match else texto

    def _normalizar_cuenta(self, valor: Any) -> str:
        """Normaliza cuentas a ultimos 14 digitos cuando aplica."""
        texto = self._texto_valor(valor)
        digitos = re.sub(r"\D", "", texto)
        if not digitos:
            return ""
        return digitos[-14:].zfill(14)

    def _normalizar_clave(self, clave: Any) -> str:
        """Normaliza encabezados tabulares."""
        texto = unicodedata.normalize("NFKD", str(clave))
        texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
        texto = re.sub(r"[^a-zA-Z0-9$]+", " ", texto).strip().lower()
        return re.sub(r"\s+", " ", texto)

    def _buscar_regex(self, patrones: list[str], texto: str) -> str:
        """Busca el primer patron en texto libre."""
        for patron in patrones:
            match = re.search(patron, texto, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip().rstrip(".,")
        return ""

    def _vacio(self, valor: Any) -> bool:
        """Indica si un valor tabular esta vacio."""
        if valor is None:
            return True
        try:
            if pd.isna(valor):
                return True
        except TypeError:
            pass
        return str(valor).strip().lower() in {"", "nan", "none"}
