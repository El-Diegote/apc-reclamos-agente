"""Motor de negocio para el MVP APC Reclamos."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from config.config import BASE_RECLAMOS_EXTENSIONS, EXPORTS_DIR
from src.database import RepositorioAPC
from src.utils import parsear_importe, timestamp_actual


class MotorAPC:
    """Coordina carga, entrenamiento, analisis y exportacion de casos APC."""

    def __init__(
        self,
        repositorio: RepositorioAPC | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Inicializa el motor.

        Args:
            repositorio: Repositorio SQLite opcional.
            logger: Logger opcional.
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.repositorio = repositorio or RepositorioAPC(logger=self.logger)

    def cargar_base_reclamos(self, archivo: Path) -> int:
        """Carga una base de reclamos desde CSV o Excel.

        Args:
            archivo: Ruta del archivo de base.

        Returns:
            Cantidad de registros persistidos.

        Raises:
            ValueError: Si el formato no esta soportado.
        """
        if archivo.suffix.lower() not in BASE_RECLAMOS_EXTENSIONS:
            raise ValueError(f"Formato no soportado para base de reclamos: {archivo.suffix}")

        if archivo.suffix.lower() == ".csv":
            dataframe = pd.read_csv(archivo)
        else:
            dataframe = pd.read_excel(archivo)

        filas = [self._normalizar_registro(fila) for fila in dataframe.to_dict("records")]
        cantidad = self.repositorio.guardar_base_reclamos(filas, archivo.name)
        self.logger.info("Base cargada desde %s", archivo)
        return cantidad

    def entrenar_resolucion(
        self,
        canal: str,
        motivo: str,
        texto_resolucion: str,
        texto_diario: str,
    ) -> int:
        """Entrena una resolucion APC reutilizable.

        Args:
            canal: Canal APC.
            motivo: Motivo del reclamo o patron textual.
            texto_resolucion: Resolucion sugerida.
            texto_diario: Texto diario sugerido.

        Returns:
            ID de la resolucion creada.
        """
        return self.repositorio.entrenar_resolucion(
            canal=canal.strip(),
            motivo=motivo.strip(),
            texto_resolucion=texto_resolucion.strip(),
            texto_diario=texto_diario.strip(),
        )

    def entrenar_desde_excel_resoluciones(self, archivo: Path) -> int:
        """Entrena resoluciones desde un Excel local con columnas TEMA y NOTA.

        Args:
            archivo: Ruta local del archivo de resoluciones APC.

        Returns:
            Cantidad de resoluciones entrenadas.

        Raises:
            ValueError: Si el archivo no contiene hojas aprovechables.
        """
        entrenadas = 0
        excel = pd.ExcelFile(archivo)

        for hoja in excel.sheet_names:
            dataframe = pd.read_excel(archivo, sheet_name=hoja)
            dataframe = dataframe.dropna(how="all").dropna(axis=1, how="all")
            columnas = {str(columna).strip().upper(): columna for columna in dataframe.columns}

            if "TEMA" not in columnas or "NOTA" not in columnas:
                self.logger.info("Hoja omitida sin TEMA/NOTA: %s", hoja)
                continue

            for _, fila in dataframe.iterrows():
                tema = str(fila.get(columnas["TEMA"], "") or "").strip()
                nota = str(fila.get(columnas["NOTA"], "") or "").strip()
                if not tema or not nota or tema.lower() == "nan" or nota.lower() == "nan":
                    continue

                self.repositorio.entrenar_resolucion(
                    canal=self._inferir_canal_desde_tema(tema),
                    motivo=tema,
                    texto_resolucion=nota,
                    texto_diario=self._generar_diario_desde_nota(tema, nota),
                )
                entrenadas += 1

        if entrenadas == 0:
            raise ValueError("No se encontraron resoluciones con columnas TEMA y NOTA.")

        self.logger.info("Resoluciones entrenadas desde Excel: %s", entrenadas)
        return entrenadas

    def analizar_caso(self, caso: dict[str, Any]) -> dict[str, Any]:
        """Analiza un caso y genera sugerencias revisables.

        Args:
            caso: Datos ingresados por el analista.

        Returns:
            Caso enriquecido con resolucion sugerida y texto diario.
        """
        caso_normalizado = self._normalizar_registro(caso)
        resolucion = self._buscar_mejor_resolucion(caso_normalizado)

        if resolucion:
            resolucion_sugerida = resolucion["texto_resolucion"]
            texto_diario = resolucion["texto_diario"]
            fuente = f"resolucion_entrenada:{resolucion['id']}"
        else:
            resolucion_sugerida = self.generar_resolucion_sugerida(caso_normalizado)
            texto_diario = self.generar_texto_diario(caso_normalizado, resolucion_sugerida)
            fuente = "regla_base_mvp"

        resultado = {
            **caso_normalizado,
            "resolucion_sugerida": resolucion_sugerida,
            "texto_diario": texto_diario,
            "fuente_sugerencia": fuente,
            "requiere_aprobacion_humana": True,
            "aprobado": False,
            "timestamp_analisis": timestamp_actual(),
        }
        self.logger.info("Caso analizado: %s", resultado.get("numero_incidente"))
        return resultado

    def generar_resolucion_sugerida(self, caso: dict[str, Any]) -> str:
        """Genera una resolucion base cuando no hay entrenamiento especifico.

        Args:
            caso: Datos del caso.

        Returns:
            Texto de resolucion sugerida.
        """
        return (
            f"Se analizo el reclamo {caso.get('numero_incidente', '')} "
            f"correspondiente al canal {caso.get('canal', '')}. "
            f"Motivo informado: {caso.get('motivo', '')}. "
            "La resolucion queda sujeta a revision y aprobacion del analista APC."
        )

    def generar_texto_diario(self, caso: dict[str, Any], resolucion: str) -> str:
        """Genera texto sugerido para la solapa Diario.

        Args:
            caso: Datos del caso.
            resolucion: Resolucion sugerida.

        Returns:
            Texto diario sugerido.
        """
        importe = float(caso.get("importe") or 0)
        return (
            f"Analisis APC - Incidente {caso.get('numero_incidente', '')}. "
            f"Canal: {caso.get('canal', '')}. "
            f"Cuenta: {caso.get('numero_cuenta', '')}. "
            f"Importe reclamado: {importe:.2f}. "
            f"Resultado sugerido: {resolucion}"
        )

    def guardar_caso_aprobado(
        self,
        caso: dict[str, Any],
        aprobado: bool,
        analista: str,
    ) -> int:
        """Guarda un caso luego de la revision humana.

        Args:
            caso: Caso analizado.
            aprobado: Indica si el analista aprobo la sugerencia.
            analista: Nombre o identificador del analista.

        Returns:
            ID del caso guardado.
        """
        caso_guardar = {**caso, "aprobado": aprobado, "analista": analista}
        return self.repositorio.guardar_caso(caso_guardar)

    def exportar_informe(self, destino: Path | None = None) -> Path:
        """Exporta informe JSON de casos analizados.

        Args:
            destino: Ruta opcional del archivo de salida.

        Returns:
            Ruta del informe generado.
        """
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        destino = destino or EXPORTS_DIR / f"informe_apc_{timestamp_actual().replace(':', '-')}.json"
        casos = self.repositorio.listar_casos()
        informe = {
            "generado_en": timestamp_actual(),
            "total_casos": len(casos),
            "casos_aprobados": sum(1 for caso in casos if caso.get("aprobado")),
            "principio_operativo": (
                "Toda resolucion debe ser revisada y aprobada por un analista humano "
                "antes de publicarse."
            ),
            "casos": casos,
        }
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
        self.logger.info("Informe exportado: %s", destino)
        return destino

    def exportar_texto_diario(self, texto_diario: str, formato: str = "txt") -> Path:
        """Exporta el texto Diario editado por el analista.

        Args:
            texto_diario: Texto final revisado.
            formato: Formato de salida, `txt` o `docx`.

        Returns:
            Ruta del archivo exportado.

        Raises:
            ValueError: Si el formato no esta soportado.
        """
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = timestamp_actual().replace(":", "-")

        if formato == "txt":
            destino = EXPORTS_DIR / f"texto_diario_{timestamp}.txt"
            destino.write_text(texto_diario, encoding="utf-8")
            return destino

        if formato == "docx":
            from docx import Document

            destino = EXPORTS_DIR / f"texto_diario_{timestamp}.docx"
            documento = Document()
            documento.add_heading("Texto Diario APC", level=1)
            documento.add_paragraph(texto_diario)
            documento.save(destino)
            return destino

        raise ValueError(f"Formato no soportado: {formato}")

    def listar_resoluciones(self) -> list[dict[str, Any]]:
        """Lista resoluciones entrenadas.

        Returns:
            Resoluciones disponibles.
        """
        return self.repositorio.listar_resoluciones()

    def normalizar_registro_publico(self, fila: dict[str, Any]) -> dict[str, Any]:
        """Normaliza un registro para usarlo desde la interfaz.

        Args:
            fila: Registro original.

        Returns:
            Registro normalizado.
        """
        return self._normalizar_registro(fila)

    def _buscar_mejor_resolucion(self, caso: dict[str, Any]) -> dict[str, Any] | None:
        """Busca una resolucion entrenada compatible con el caso.

        Args:
            caso: Caso normalizado.

        Returns:
            Resolucion encontrada o `None`.
        """
        canal_caso = str(caso.get("canal", "")).lower()
        motivo_caso = str(caso.get("motivo", "")).lower()

        for resolucion in self.repositorio.listar_resoluciones():
            canal_resolucion = str(resolucion.get("canal", "")).lower()
            motivo_resolucion = str(resolucion.get("motivo", "")).lower()
            canal_match = canal_resolucion in {"", "otros"} or canal_resolucion == canal_caso
            motivo_match = motivo_resolucion in motivo_caso or motivo_caso in motivo_resolucion
            if canal_match and motivo_match:
                return resolucion
        return None

    def _normalizar_registro(self, fila: dict[str, Any]) -> dict[str, Any]:
        """Normaliza nombres de campos frecuentes.

        Args:
            fila: Registro original.

        Returns:
            Registro normalizado para el motor.
        """
        normalizado = {str(clave).lower().strip(): valor for clave, valor in fila.items()}
        return {
            "numero_incidente": str(
                normalizado.get("numero_incidente")
                or normalizado.get("incidente")
                or normalizado.get("nro_incidente")
                or normalizado.get("nro de operacion")
                or normalizado.get("nro de operación")
                or normalizado.get("nro_operacion")
                or normalizado.get("numero_operacion")
                or normalizado.get("numero de operacion")
                or ""
            ),
            "canal": str(normalizado.get("canal") or "Otros"),
            "motivo": str(normalizado.get("motivo") or normalizado.get("descripcion") or ""),
            "fecha": str(normalizado.get("fecha") or ""),
            "hora": str(normalizado.get("hora") or ""),
            "importe": parsear_importe(normalizado.get("importe") or normalizado.get("monto")),
            "numero_cuenta": str(
                normalizado.get("numero_cuenta")
                or normalizado.get("cuenta")
                or normalizado.get("nro_cuenta")
                or ""
            ),
        }

    def _inferir_canal_desde_tema(self, tema: str) -> str:
        """Infiere canal APC a partir del tema de una resolucion.

        Args:
            tema: Tema textual de la resolucion.

        Returns:
            Canal normalizado.
        """
        tema_upper = tema.upper()
        if "ATM" in tema_upper:
            return "ATM"
        if "MPOS" in tema_upper:
            return "mPOS"
        if "POS" in tema_upper:
            return "POS"
        if "BNA" in tema_upper:
            return "BNA+"
        if "MODO" in tema_upper:
            return "MODO"
        if "CASH" in tema_upper:
            return "Cash In"
        if "ECOMMERCE" in tema_upper or "LINKGO" in tema_upper:
            return "eCommerce"
        return "Otros"

    def _generar_diario_desde_nota(self, tema: str, nota: str) -> str:
        """Genera una base editable para Diario a partir de una nota.

        Args:
            tema: Tema de resolucion.
            nota: Nota de resolucion.

        Returns:
            Texto Diario sugerido.
        """
        return f"Se analiza caso APC bajo tema '{tema}'. Resolucion sugerida: {nota}"
