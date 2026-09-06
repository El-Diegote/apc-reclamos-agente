"""Clase principal del agente de procesamiento APC."""

from __future__ import annotations

import json
import logging
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from config.config import (
    CORRIDAS_DIR,
    DEFAULT_CSV_NAME,
    DEFAULT_CORRIDA,
    DEFAULT_RESULT_NAME,
    DOCUMENT_EXTENSIONS,
    OUTPUT_TEMPLATE_PATH,
    SESSION_TIMEOUT_SECONDS,
)
from src.analizador import Analizador
from src.extractor import Extractor
from src.utils import (
    SesionExpiradaError,
    cargar_csv_incidentes,
    cargar_json,
    guardar_json,
    parsear_importe,
    timestamp_actual,
)


class Agente:
    """Agente principal para buscar, analizar y exportar reclamos APC."""

    def __init__(
        self,
        numero_incidente: str,
        corrida: str = DEFAULT_CORRIDA,
        session_timeout_seconds: int = SESSION_TIMEOUT_SECONDS,
        logger: logging.Logger | None = None,
    ) -> None:
        """Inicializa el agente con una corrida y una sesion simulada.

        Args:
            numero_incidente: Numero de incidente a procesar.
            corrida: Nombre de la carpeta de corrida.
            session_timeout_seconds: Timeout de sesion simulado.
            logger: Logger opcional.
        """
        self.numero_incidente = numero_incidente
        self.corrida = corrida
        self.session_timeout_seconds = session_timeout_seconds
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.session_started_at = datetime.now()
        self.corrida_dir = CORRIDAS_DIR / corrida
        self.entrada_dir = self.corrida_dir / "entrada"
        self.documentos_dir = self.corrida_dir / "documentos"
        self.salida_dir = self.corrida_dir / "salida"
        self.solapas: dict[str, Any] = {}
        self.documentos: list[str] = []
        self.resultado: dict[str, Any] = {}

    def _validar_sesion(self) -> None:
        """Valida que la sesion simulada siga vigente.

        Raises:
            SesionExpiradaError: Si la sesion excedio el timeout configurado.
        """
        segundos = (datetime.now() - self.session_started_at).total_seconds()
        if segundos > self.session_timeout_seconds:
            mensaje = (
                "La sesion APC simulada expiro. "
                "Reinicie el agente y vuelva a ejecutar la corrida."
            )
            self.logger.error(mensaje)
            raise SesionExpiradaError(mensaje)

    def _buscar_fila_csv(self, numero_incidente: str) -> dict[str, str] | None:
        """Busca un incidente dentro del CSV diario.

        Args:
            numero_incidente: Numero de incidente a buscar.

        Returns:
            Fila encontrada o `None`.
        """
        csv_path = self.entrada_dir / DEFAULT_CSV_NAME
        filas = cargar_csv_incidentes(csv_path)
        for fila in filas:
            if fila.get("numero_incidente") == numero_incidente:
                return fila
        return None

    def buscar_incidente(self, numero_incidente: str) -> bool:
        """Busca un incidente en la fuente simulada.

        Args:
            numero_incidente: Numero de incidente APC.

        Returns:
            `True` si el incidente fue encontrado.
        """
        self._validar_sesion()
        self.logger.info("Buscando incidente: %s", numero_incidente)
        self.numero_incidente = numero_incidente
        encontrado = self._buscar_fila_csv(numero_incidente) is not None
        self.logger.info("Incidente encontrado: %s", encontrado)
        return encontrado

    def leer_solapas(self) -> dict[str, Any]:
        """Simula la lectura de las cuatro solapas APC.

        Returns:
            Diccionario con datos de Detalle, Diario, Documentacion y Auditoria.
        """
        self._validar_sesion()
        fila = self._buscar_fila_csv(self.numero_incidente) or {}
        self.logger.info("Leyendo solapas APC simuladas para %s", self.numero_incidente)

        self.solapas = {
            "detalle": {
                "numero_incidente": self.numero_incidente,
                "motivo": fila.get("motivo", "Motivo no informado"),
                "numero_cuenta": fila.get("numero_cuenta", ""),
            },
            "diario": {
                "fecha": fila.get("fecha", ""),
                "hora": fila.get("hora", ""),
                "importe": parsear_importe(fila.get("importe")),
            },
            "documentacion": {
                "archivos": self.descargar_documentacion(),
                "estado": "disponible",
            },
            "auditoria": {
                "usuario_revisor": "agente_simulado",
                "acciones": [
                    "busqueda_incidente",
                    "lectura_solapas",
                    "lectura_documentacion",
                ],
                "observaciones": [],
            },
        }
        return self.solapas

    def descargar_documentacion(self) -> list[str]:
        """Simula descarga buscando documentos en la carpeta de la corrida.

        Returns:
            Lista de rutas de documentos encontrados.
        """
        self._validar_sesion()
        self.documentos_dir.mkdir(parents=True, exist_ok=True)

        documentos = [
            str(path)
            for path in sorted(self.documentos_dir.iterdir())
            if path.is_file() and path.suffix.lower() in DOCUMENT_EXTENSIONS
        ]
        self.documentos = documentos
        self.logger.info("Documentos encontrados: %s", documentos)
        return documentos

    def _leer_documentos(self) -> list[str]:
        """Lee documentos encontrados usando el extractor correspondiente.

        Returns:
            Lista de textos extraidos.
        """
        extractor = Extractor(logger=self.logger)
        textos: list[str] = []

        for archivo in self.documentos:
            path = Path(archivo)
            try:
                if path.suffix.lower() == ".txt":
                    textos.append(extractor.leer_txt(str(path)))
                elif path.suffix.lower() == ".pdf":
                    textos.append(extractor.leer_pdf(str(path)))
                elif path.suffix.lower() in {".xlsx", ".xlsm"}:
                    textos.append(json.dumps(extractor.leer_excel(str(path)), default=str))
                elif path.suffix.lower() == ".csv":
                    textos.append(path.read_text(encoding="utf-8"))
            except Exception as exc:
                self.logger.exception("Error leyendo documento %s", path)
                textos.append(f"ERROR_DOCUMENTO: {path.name}: {exc}")

        return textos

    def analizar(self) -> dict[str, Any]:
        """Ejecuta validaciones y extraccion de datos.

        Returns:
            Resultado estructurado del analisis.
        """
        self._validar_sesion()
        if not self.solapas:
            self.leer_solapas()

        textos_documentos = self._leer_documentos()
        analizador = Analizador(self.solapas, textos_documentos, logger=self.logger)
        validaciones = analizador.validar_todos()
        datos_criticos = analizador.extraer_datos_criticos()

        template = cargar_json(OUTPUT_TEMPLATE_PATH)
        resultado = deepcopy(template)
        resultado.update(
            {
                "numero_incidente": self.numero_incidente,
                "corrida": self.corrida,
                "estado": "analizado",
                "timestamp_procesamiento": timestamp_actual(),
                "validaciones": validaciones,
                "datos_criticos": datos_criticos,
                "documentos": [Path(doc).name for doc in self.documentos],
                "observaciones": self.solapas.get("auditoria", {}).get("observaciones", []),
            }
        )

        self.resultado = resultado
        self.logger.info("Analisis finalizado para %s", self.numero_incidente)
        return resultado

    def generar_json(self) -> str:
        """Genera y guarda el JSON de salida de la corrida.

        Returns:
            Ruta del archivo JSON generado.
        """
        self._validar_sesion()
        if not self.resultado:
            self.analizar()

        salida_path = self.salida_dir / DEFAULT_RESULT_NAME
        guardar_json(salida_path, self.resultado)
        self.logger.info("Resultado guardado en %s", salida_path)
        return str(salida_path)
