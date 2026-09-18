"""Analisis de exportaciones Smart Console para reclamos APC."""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from src.utils import parsear_importe


@dataclass(slots=True)
class SmartConsoleOperation:
    """Operacion normalizada desde una fila de Smart Console."""

    fecha: str
    hora: str
    importe: float
    moneda: str
    tarjeta: str
    cuenta_origen: str
    cuenta_destino: str
    canal: str
    respuesta: str
    comercio: str
    ip: str
    pais: str
    check: bool
    robo: bool
    link_go: str
    aprobada: bool


class SmartConsoleAnalyzer:
    """Normaliza y resume movimientos exportados desde Smart Console."""

    TRUE_VALUES = {"1", "1.0", "x", "si", "sí", "true", "ok", "marcado", "resaltado", "check"}

    COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
        "fecha": ("fecha", "fecha trx", "fecha operacion", "dia"),
        "hora": ("hora", "hora trx", "hora operacion"),
        "importe": ("importe $", "importe", "monto", "monto operacion"),
        "moneda": ("moneda", "divisa"),
        "tarjeta": ("tarjeta", "nro tarjeta", "numero tarjeta", "pan"),
        "cuenta_origen": ("cuenta desde", "cta desde", "cta dde", "cuenta origen", "cta origen"),
        "cuenta_destino": ("cuenta hasta", "cta hasta", "cta hta", "cuenta destino", "cta destino"),
        "canal": ("canal", "tipo canal", "origen", "tema"),
        "respuesta": ("respuesta", "estado", "codigo respuesta", "cod rta", "descripcion respuesta"),
        "denominacion": (
            "denominacion de establecimiento",
            "den establecimiento",
            "establecimiento",
            "comercio",
        ),
        "ip": ("ip", "direccion ip"),
        "pais": ("pais", "país"),
        "check": ("check", "seleccionado", "seleccionada", "resaltado", "marcado"),
        "robo": ("robo", "hurto", "extravio", "extravío"),
        "link_go": ("link go", "linkgo", "numero gestion", "numero pedido", "gestion"),
    }

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Inicializa el analizador.

        Args:
            logger: Logger opcional para registrar acciones y errores.
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def cargar_archivo(self, archivo: Path) -> pd.DataFrame:
        """Carga un archivo CSV o Excel exportado desde Smart Console.

        Args:
            archivo: Ruta local del archivo.

        Returns:
            DataFrame con los movimientos originales.

        Raises:
            ValueError: Si la extension no esta soportada.
        """
        extension = archivo.suffix.lower()
        if extension == ".csv":
            return pd.read_csv(archivo)
        if extension in {".xlsx", ".xlsm", ".xls"}:
            return pd.read_excel(archivo)
        raise ValueError(f"Formato Smart Console no soportado: {archivo.suffix}")

    def analizar_archivo(self, archivo: Path) -> dict[str, Any]:
        """Carga y analiza un archivo Smart Console.

        Args:
            archivo: Ruta local del archivo CSV o Excel.

        Returns:
            Resumen estructurado de operaciones.
        """
        dataframe = self.cargar_archivo(archivo)
        return self.analizar_dataframe(dataframe, fuente=archivo.name)

    def analizar_dataframe(self, dataframe: pd.DataFrame, fuente: str = "") -> dict[str, Any]:
        """Analiza un DataFrame de movimientos.

        Args:
            dataframe: Datos tabulares exportados desde Smart Console.
            fuente: Nombre opcional del origen para trazabilidad.

        Returns:
            Resumen con operaciones normalizadas, totales y banderas.
        """
        operaciones = self.extraer_operaciones(dataframe)
        operaciones_check = [operacion for operacion in operaciones if operacion.check]
        operaciones_base = operaciones_check or operaciones
        total_check = sum(operacion.importe for operacion in operaciones_check)

        resumen = {
            "fuente": fuente,
            "total_operaciones": len(operaciones),
            "total_operaciones_check": len(operaciones_check),
            "total_importe_check": round(total_check, 2),
            "canales_detectados": self._valores_unicos(operacion.canal for operacion in operaciones_base),
            "monedas_detectadas": self._valores_unicos(operacion.moneda for operacion in operaciones_base),
            "cuentas_origen": self._valores_unicos(operacion.cuenta_origen for operacion in operaciones_base),
            "cuentas_destino": self._valores_unicos(operacion.cuenta_destino for operacion in operaciones_base),
            "tiene_robo": any(operacion.robo for operacion in operaciones_base),
            "tiene_link_go": any(bool(operacion.link_go) for operacion in operaciones_base),
            "operaciones_aprobadas": sum(1 for operacion in operaciones_base if operacion.aprobada),
            "operaciones": [asdict(operacion) for operacion in operaciones],
        }
        self.logger.info("Smart Console analizada: %s operaciones", len(operaciones))
        return resumen

    def extraer_operaciones(self, dataframe: pd.DataFrame) -> list[SmartConsoleOperation]:
        """Convierte filas Smart Console a operaciones normalizadas.

        Args:
            dataframe: Datos tabulares originales.

        Returns:
            Lista de operaciones normalizadas.
        """
        columnas = {self._normalizar_clave(columna): columna for columna in dataframe.columns}
        operaciones: list[SmartConsoleOperation] = []

        for fila in dataframe.to_dict("records"):
            cuenta_destino = self._texto(self._valor(fila, columnas, "cuenta_destino"))
            denominacion = self._texto(self._valor(fila, columnas, "denominacion"))
            respuesta = self._texto(self._valor(fila, columnas, "respuesta"))
            link_go = self._texto(self._valor(fila, columnas, "link_go"))

            operaciones.append(
                SmartConsoleOperation(
                    fecha=self._texto(self._valor(fila, columnas, "fecha")),
                    hora=self._texto(self._valor(fila, columnas, "hora")),
                    importe=parsear_importe(self._valor(fila, columnas, "importe")),
                    moneda=self._texto(self._valor(fila, columnas, "moneda")) or "Peso",
                    tarjeta=self._texto(self._valor(fila, columnas, "tarjeta")),
                    cuenta_origen=self._normalizar_cuenta(self._valor(fila, columnas, "cuenta_origen")),
                    cuenta_destino=self._normalizar_cuenta(cuenta_destino),
                    canal=self._texto(self._valor(fila, columnas, "canal")),
                    respuesta=respuesta,
                    comercio=self._componer_comercio(cuenta_destino, denominacion),
                    ip=self._texto(self._valor(fila, columnas, "ip")),
                    pais=self._texto(self._valor(fila, columnas, "pais")),
                    check=self._es_verdadero(self._valor(fila, columnas, "check")),
                    robo=self._es_verdadero(self._valor(fila, columnas, "robo")),
                    link_go=link_go,
                    aprobada=self._es_aprobada(respuesta),
                )
            )

        return operaciones

    def _valor(self, fila: dict[str, Any], columnas: dict[str, Any], campo: str) -> Any:
        """Obtiene el primer valor disponible para un campo normalizado."""
        for alias in self.COLUMN_ALIASES[campo]:
            columna = columnas.get(self._normalizar_clave(alias))
            if columna is not None:
                valor = fila.get(columna)
                if not self._esta_vacio(valor):
                    return valor
        return ""

    def _normalizar_clave(self, clave: Any) -> str:
        """Normaliza encabezados para comparar columnas."""
        texto = unicodedata.normalize("NFKD", str(clave))
        texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
        texto = re.sub(r"[^a-zA-Z0-9$]+", " ", texto).strip().lower()
        return re.sub(r"\s+", " ", texto)

    def _texto(self, valor: Any) -> str:
        """Convierte valores tabulares a texto seguro."""
        if self._esta_vacio(valor):
            return ""
        return str(valor).strip()

    def _esta_vacio(self, valor: Any) -> bool:
        """Indica si un valor tabular esta vacio."""
        if valor is None:
            return True
        try:
            if pd.isna(valor):
                return True
        except TypeError:
            pass
        return str(valor).strip().lower() in {"", "nan", "none"}

    def _es_verdadero(self, valor: Any) -> bool:
        """Detecta marcas manuales como CHECK o ROBO."""
        if isinstance(valor, bool):
            return valor
        return self._texto(valor).lower() in self.TRUE_VALUES

    def _es_aprobada(self, respuesta: str) -> bool:
        """Detecta aprobacion como dato auxiliar, no como criterio unico."""
        texto = respuesta.lower()
        return "aprob" in texto or texto in {"00", "0", "approved"}

    def _normalizar_cuenta(self, valor: Any) -> str:
        """Normaliza cuentas a 14 digitos cuando es posible."""
        digitos = re.sub(r"\D", "", self._texto(valor))
        if not digitos:
            return ""
        return digitos[-14:].zfill(14)

    def _componer_comercio(self, cuenta_hasta: str, denominacion: str) -> str:
        """Reconstruye comercio combinando cuenta destino y denominacion."""
        partes = [parte for parte in (self._normalizar_cuenta(cuenta_hasta), denominacion.strip()) if parte]
        return " - ".join(partes)

    def _valores_unicos(self, valores: Iterable[str]) -> list[str]:
        """Devuelve valores unicos preservando el orden."""
        vistos: set[str] = set()
        resultado: list[str] = []
        for valor in valores:
            limpio = str(valor or "").strip()
            if limpio and limpio not in vistos:
                vistos.add(limpio)
                resultado.append(limpio)
        return resultado
