"""Clasificacion documental inicial para expedientes APC."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from src.extractor import Extractor
from src.utils import normalizar_texto


@dataclass(slots=True)
class DocumentClassification:
    """Resultado de clasificar un documento del expediente."""

    archivo: str
    tipo_documento: str
    confianza: float
    senales: list[str]
    requiere_ocr: bool


class DocumentClassifier:
    """Clasifica documentos APC por reglas transparentes y auditables."""

    RULES: dict[str, tuple[str, ...]] = {
        "F60330": ("f60330", "60330", "formulario", "form "),
        "Denuncia": ("denuncia", "policial", "robo", "hurto", "extrav"),
        "Extracto": ("extracto", "movimientos", "saldo", "cuenta desde"),
        "Comprobante": ("comprobante", "reclamo", "consulta apc", "nro operacion"),
        "Dictamen": ("dictamen", "resolucion", "resolución", "procedente", "improcedente"),
        "Nota": ("nota", "carta", "presentacion", "presentación"),
    }

    OCR_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}

    def __init__(
        self,
        extractor: Extractor | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Inicializa el clasificador.

        Args:
            extractor: Extractor documental opcional.
            logger: Logger opcional.
        """
        self.extractor = extractor or Extractor(logger=logger)
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def clasificar_archivo(self, archivo: Path) -> DocumentClassification:
        """Clasifica un archivo local del expediente.

        Args:
            archivo: Ruta local del documento.

        Returns:
            Clasificacion del documento.
        """
        texto = self._leer_texto_posible(archivo)
        clasificacion = self.clasificar_texto(texto, nombre_archivo=archivo.name)
        self.logger.info("Documento clasificado: %s -> %s", archivo.name, clasificacion.tipo_documento)
        return clasificacion

    def clasificar_texto(self, texto: str, nombre_archivo: str = "") -> DocumentClassification:
        """Clasifica texto extraido o nombre de archivo.

        Args:
            texto: Texto disponible del documento.
            nombre_archivo: Nombre del archivo para usar como senal adicional.

        Returns:
            Clasificacion con tipo, confianza y senales.
        """
        contenido = normalizar_texto(f"{nombre_archivo} {texto}").lower()
        puntajes: dict[str, list[str]] = {}

        for tipo, senales in self.RULES.items():
            halladas = [senal for senal in senales if senal in contenido]
            if halladas:
                puntajes[tipo] = halladas

        if not puntajes:
            return DocumentClassification(
                archivo=nombre_archivo,
                tipo_documento="Otro",
                confianza=0.15,
                senales=[],
                requiere_ocr=self._requiere_ocr(nombre_archivo, texto),
            )

        tipo_documento, senales = max(puntajes.items(), key=lambda item: len(item[1]))
        confianza = min(0.95, 0.35 + (0.15 * len(senales)))
        return DocumentClassification(
            archivo=nombre_archivo,
            tipo_documento=tipo_documento,
            confianza=round(confianza, 2),
            senales=senales,
            requiere_ocr=self._requiere_ocr(nombre_archivo, texto),
        )

    def clasificar_lote(self, archivos: Iterable[Path]) -> list[dict[str, Any]]:
        """Clasifica una coleccion de documentos.

        Args:
            archivos: Rutas locales a documentos descargados o aportados.

        Returns:
            Lista serializable de clasificaciones.
        """
        return [asdict(self.clasificar_archivo(archivo)) for archivo in archivos]

    def _leer_texto_posible(self, archivo: Path) -> str:
        """Extrae texto cuando el formato ya esta soportado por el MVP."""
        try:
            extension = archivo.suffix.lower()
            if extension == ".txt":
                return self.extractor.leer_txt(str(archivo))
            if extension == ".pdf":
                return self.extractor.leer_pdf(str(archivo))
            if extension in {".xlsx", ".xlsm", ".xls", ".csv"}:
                datos = self.extractor.leer_excel(str(archivo)) if extension != ".csv" else {}
                return normalizar_texto(str(datos))
        except Exception as exc:  # pragma: no cover - logging defensivo
            self.logger.warning("No se pudo leer texto de %s: %s", archivo, exc)
        return ""

    def _requiere_ocr(self, nombre_archivo: str, texto: str) -> bool:
        """Detecta si podria requerirse OCR por falta de texto extraible."""
        extension = Path(nombre_archivo).suffix.lower()
        return extension in self.OCR_EXTENSIONS and not texto.strip()
