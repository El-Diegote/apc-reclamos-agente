"""Interfaz desktop simple para operar junto a APC."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any

import customtkinter as ctk
import pandas as pd

from config.config import CORRIDAS_DIR, DEFAULT_CORRIDA
from src.extractor import Extractor
from src.motor_apc import MotorAPC
from src.utils import parsear_importe


class APCDesktopApp(ctk.CTk):
    """Ventana companera para trabajar en paralelo con APC."""

    def __init__(self, motor: MotorAPC | None = None) -> None:
        """Inicializa la aplicacion.

        Args:
            motor: Motor APC opcional para pruebas.
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.motor = motor or MotorAPC(logger=self.logger)
        self.registros: list[dict[str, Any]] = []
        self.indice_actual = 0
        self.caso_actual: dict[str, Any] | None = None
        self.ultimo_analisis: dict[str, Any] | None = None
        self.documentos_dir = CORRIDAS_DIR / DEFAULT_CORRIDA / "documentos"
        self.importe_base = 0.0
        self.moneda_previa = "Peso"
        self.resolucion_editable = False
        self.resolucion_historial: list[tuple[str, str]] = []

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("APC Reclamos Agente")
        self.geometry("1020x680")
        self.minsize(920, 620)

        self._crear_layout()
        self._actualizar_estado("Cargue una base o ingrese un caso manual.")

    def _crear_layout(self) -> None:
        """Construye una unica vista con botones operativos."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#111827")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="APC Reclamos Agente",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")
        ctk.CTkLabel(
            header,
            text="Ventana simple para usar en paralelo con APC. No guarda credenciales.",
            text_color="#B8C2CC",
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")

        actions = ctk.CTkFrame(self, fg_color="#172033")
        actions.grid(row=1, column=0, padx=16, pady=16, sticky="ew")
        actions.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        botones = [
            ("Cargar Base", self._cargar_base),
            ("Pegar Nro en APC", self._copiar_y_pegar_en_apc),
            ("Leer y Analizar", self._leer_y_analizar),
            ("Documentacion", self._preparar_documentacion),
            ("Copiar Diario", self._copiar_diario),
        ]
        for columna, (texto, comando) in enumerate(botones):
            ctk.CTkButton(actions, text=texto, height=48, command=comando).grid(
                row=0, column=columna, padx=8, pady=12, sticky="ew"
            )

        body = ctk.CTkFrame(self, fg_color="#0F172A")
        body.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        caso = ctk.CTkFrame(body, fg_color="#172033")
        caso.grid(row=0, column=0, padx=(12, 6), pady=12, sticky="nsew")
        caso.grid_columnconfigure(1, weight=1)

        self.incidente_var = ctk.StringVar(value="")
        self.cliente_var = ctk.StringVar(value="")
        self.canal_var = ctk.StringVar(value="")
        self.motivo_var = ctk.StringVar(value="")
        self.importe_var = ctk.StringVar(value="")
        self.moneda_var = ctk.StringVar(value="Peso")
        self.cuenta_var = ctk.StringVar(value="")
        self.tema_diario_var = ctk.StringVar(value="")

        ctk.CTkLabel(caso, text="Caso actual", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=14, pady=(14, 8), sticky="w"
        )
        self._campo(caso, "Incidente", self.incidente_var, 1)
        self._campo(caso, "Cliente", self.cliente_var, 2)
        self._campo(caso, "Canal", self.canal_var, 3)
        self._campo(caso, "Motivo", self.motivo_var, 4)
        self._campo_importe_moneda(caso, 5)
        self._campo(caso, "Cuenta", self.cuenta_var, 6)
        ctk.CTkButton(caso, text="Siguiente reclamo", command=self._siguiente_reclamo).grid(
            row=7, column=1, padx=14, pady=(10, 14), sticky="e"
        )

        salida = ctk.CTkFrame(body, fg_color="#172033")
        salida.grid(row=0, column=1, padx=(6, 12), pady=12, sticky="nsew")
        salida.grid_columnconfigure(0, weight=1)
        salida.grid_rowconfigure(4, weight=1)
        resolucion_header = ctk.CTkFrame(salida, fg_color="transparent")
        resolucion_header.grid(row=0, column=0, padx=14, pady=(14, 8), sticky="ew")
        resolucion_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            resolucion_header,
            text="Resolucion actual",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            resolucion_header,
            text="Editar",
            width=80,
            height=30,
            command=self._habilitar_edicion_resolucion,
        ).grid(row=0, column=1, padx=(8, 0), sticky="e")
        ctk.CTkButton(
            resolucion_header,
            text="Deshacer",
            width=90,
            height=30,
            command=self._deshacer_resolucion,
        ).grid(row=0, column=2, padx=(8, 0), sticky="e")
        ctk.CTkLabel(salida, text="Tema").grid(row=1, column=0, padx=14, pady=(4, 4), sticky="w")
        self.tema_diario_entry = ctk.CTkEntry(salida, textvariable=self.tema_diario_var)
        self.tema_diario_entry.grid(
            row=2, column=0, padx=14, pady=(0, 10), sticky="ew"
        )
        self.tema_diario_entry.bind("<KeyRelease>", self._registrar_cambio_resolucion)
        ctk.CTkLabel(salida, text="Detalle").grid(row=3, column=0, padx=14, pady=(0, 4), sticky="w")
        self.resultado_text = ctk.CTkTextbox(salida, height=300)
        self.resultado_text.grid(row=4, column=0, padx=14, pady=(0, 14), sticky="nsew")
        self.resultado_text.bind("<KeyRelease>", self._registrar_cambio_resolucion)
        self.resultado_text.insert(
            "1.0",
            "Esperando accion.\n\n"
            "1. Cargue la Base de Reclamos.\n"
            "2. Pegue el Nro en APC.\n"
            "3. Busque el incidente en APC.\n"
            "4. Use Leer y Analizar para completar Tema y Detalle.",
        )
        self.tema_diario_entry.configure(state="disabled")
        self.resultado_text.configure(state="disabled")
        self.resolucion_historial = [self._snapshot_resolucion()]

        footer = ctk.CTkFrame(self, fg_color="#111827")
        footer.grid(row=3, column=0, padx=16, pady=(0, 16), sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        self.estado_label = ctk.CTkLabel(
            footer,
            text="",
            text_color="#A7F3D0",
            anchor="w",
            justify="left",
        )
        self.estado_label.grid(row=0, column=0, padx=14, pady=10, sticky="ew")

    def _campo(
        self,
        parent: ctk.CTkFrame,
        label: str,
        variable: ctk.StringVar,
        row: int,
    ) -> None:
        """Crea una etiqueta y entrada."""
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=14, pady=8, sticky="w")
        ctk.CTkEntry(parent, textvariable=variable).grid(
            row=row, column=1, padx=14, pady=8, sticky="ew"
        )

    def _campo_importe_moneda(self, parent: ctk.CTkFrame, row: int) -> None:
        """Crea el campo de importe con selector de moneda."""
        ctk.CTkLabel(parent, text="Importe").grid(row=row, column=0, padx=14, pady=8, sticky="w")
        contenedor = ctk.CTkFrame(parent, fg_color="transparent")
        contenedor.grid(row=row, column=1, padx=14, pady=8, sticky="ew")
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_columnconfigure(1, weight=0)
        ctk.CTkLabel(contenedor, text="").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(contenedor, text="Moneda").grid(row=0, column=1, sticky="w")
        ctk.CTkEntry(contenedor, textvariable=self.importe_var).grid(
            row=1, column=0, padx=(0, 8), sticky="ew"
        )
        ctk.CTkOptionMenu(
            contenedor,
            values=["Peso", "Dolar"],
            variable=self.moneda_var,
            width=120,
            command=self._cambiar_moneda,
        ).grid(row=1, column=1, sticky="e")

    def _cargar_base(self) -> None:
        """Carga una base local y toma el primer reclamo."""
        archivo = filedialog.askopenfilename(
            title="Seleccionar Base de Reclamos",
            filetypes=[("Bases APC", "*.csv *.xlsx *.xlsm"), ("Todos", "*.*")],
        )
        if not archivo:
            return

        try:
            path = Path(archivo)
            dataframe = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
            self.registros = self.motor.normalizar_base_reclamos(dataframe)
            self.indice_actual = 0
            self._mostrar_registro_actual()
            self._actualizar_estado(f"Base cargada: {len(self.registros)} reclamos. Archivo local.")
        except Exception as exc:
            self.logger.exception("No se pudo cargar la base")
            messagebox.showerror("Error", str(exc))

    def _mostrar_registro_actual(self) -> None:
        """Muestra el reclamo actual en pantalla."""
        if not self.registros:
            return
        self.caso_actual = self.registros[self.indice_actual]
        self.incidente_var.set(str(self.caso_actual.get("numero_incidente", "")))
        self.cliente_var.set(str(self.caso_actual.get("nombre_apellido", "")))
        self.canal_var.set(str(self.caso_actual.get("canal", "Otros")))
        self.motivo_var.set(str(self.caso_actual.get("motivo", "")))
        self.importe_base = float(self.caso_actual.get("importe") or 0)
        self.moneda_var.set(str(self.caso_actual.get("moneda", "Peso") or "Peso"))
        self._actualizar_importe_por_moneda()
        self.moneda_previa = self.moneda_var.get()
        self.cuenta_var.set(str(self.caso_actual.get("numero_cuenta", "")))
        self.tema_diario_var.set("")
        self._set_text("Resolucion pendiente. Use Leer y Analizar cuando el incidente este abierto en APC.")

    def _siguiente_reclamo(self) -> None:
        """Avanza al siguiente reclamo de la base cargada."""
        if not self.registros:
            messagebox.showwarning("Sin base", "Primero cargue una Base de Reclamos.")
            return
        self.indice_actual = min(self.indice_actual + 1, len(self.registros) - 1)
        self._mostrar_registro_actual()
        self._actualizar_estado(
            f"Reclamo {self.indice_actual + 1} de {len(self.registros)} listo."
        )

    def _copiar_y_pegar_en_apc(self) -> None:
        """Copia el numero y lo pega en APC despues de una pausa breve."""
        numero = self.incidente_var.get().strip()
        if not numero:
            messagebox.showwarning("Sin numero", "Ingrese o cargue un numero de reclamo.")
            return

        self.clipboard_clear()
        self.clipboard_append(numero)
        self.update()
        self._actualizar_estado(
            "Numero copiado. Haga click en el campo 'Nro de Operacion' de APC; "
            "se pegara automaticamente en 3 segundos."
        )
        self.after(3000, self._pegar_clipboard_en_ventana_activa)

    def _pegar_clipboard_en_ventana_activa(self) -> None:
        """Envia Ctrl+V a la ventana o campo activo."""
        try:
            import pyautogui

            pyautogui.hotkey("ctrl", "v")
            self._actualizar_estado("Numero pegado en la ventana activa.")
        except ModuleNotFoundError:
            self._actualizar_estado(
                "Numero copiado al portapapeles. Instale pyautogui para pegado automatico."
            )
        except Exception as exc:
            self.logger.exception("No se pudo pegar automaticamente")
            self._actualizar_estado(f"No se pudo pegar automaticamente: {exc}")

    def _leer_y_analizar(self) -> None:
        """Lee documentos locales y genera analisis sugerido."""
        caso = self._caso_desde_campos()
        textos = self._leer_documentos_locales()
        if textos and not caso["motivo"]:
            caso["motivo"] = "Informacion complementada desde documentos locales"

        self.ultimo_analisis = self.motor.analizar_caso(caso)
        self.tema_diario_var.set(str(self.ultimo_analisis.get("tema_diario", "")))
        self._set_text(str(self.ultimo_analisis.get("detalle_diario", "")))
        self._actualizar_estado("Analisis generado localmente. Revise antes de usar en APC.")

    def _preparar_documentacion(self) -> None:
        """Prepara carpeta local para descargar documentacion desde APC."""
        self.documentos_dir.mkdir(parents=True, exist_ok=True)
        self.clipboard_clear()
        self.clipboard_append(str(self.documentos_dir))
        self.update()
        try:
            os.startfile(self.documentos_dir)
        except OSError:
            pass
        self._actualizar_estado(
            "Carpeta de documentacion abierta y ruta copiada. "
            "Descargue desde la solapa Documentacion de APC en esa carpeta."
        )

    def _copiar_diario(self) -> None:
        """Copia el texto Diario sugerido para pegarlo manualmente en APC."""
        if not self.ultimo_analisis:
            messagebox.showwarning("Sin analisis", "Primero ejecute Leer y Analizar.")
            return
        tema = self.tema_diario_var.get().strip()
        detalle = self.resultado_text.get("1.0", "end").strip()
        texto = f"Tema: {tema}\nDetalle: {detalle}" if tema else detalle
        self.clipboard_clear()
        self.clipboard_append(texto)
        self.update()
        self._actualizar_estado("Tema y Detalle Diario copiados. Pegarlos manualmente en APC luego de revisar.")

    def _caso_desde_campos(self) -> dict[str, Any]:
        """Construye un caso desde los campos visibles."""
        return {
            "numero_incidente": self.incidente_var.get().strip(),
            "nombre_apellido": self.cliente_var.get().strip(),
            "canal": self.canal_var.get().strip(),
            "motivo": self.motivo_var.get().strip(),
            "importe": self.importe_var.get().strip(),
            "moneda": self.moneda_var.get().strip(),
            "numero_cuenta": self.cuenta_var.get().strip(),
        }

    def _leer_documentos_locales(self) -> list[str]:
        """Lee documentos descargados localmente."""
        extractor = Extractor(logger=self.logger)
        textos: list[str] = []
        if not self.documentos_dir.exists():
            return textos

        for archivo in sorted(self.documentos_dir.iterdir()):
            if not archivo.is_file():
                continue
            try:
                if archivo.suffix.lower() == ".txt":
                    textos.append(extractor.leer_txt(str(archivo)))
                elif archivo.suffix.lower() == ".pdf":
                    textos.append(extractor.leer_pdf(str(archivo)))
                elif archivo.suffix.lower() in {".xlsx", ".xlsm"}:
                    textos.append(str(extractor.leer_excel(str(archivo))))
            except Exception as exc:
                self.logger.warning("Documento omitido %s: %s", archivo.name, exc)
        return textos

    def _actualizar_estado(self, mensaje: str) -> None:
        """Actualiza el estado inferior."""
        self.estado_label.configure(text=mensaje)

    def _set_text(self, texto: str) -> None:
        """Reemplaza el panel de resultado."""
        self.resultado_text.configure(state="normal")
        self.resultado_text.delete("1.0", "end")
        self.resultado_text.insert("1.0", texto)
        self.resolucion_editable = False
        self.tema_diario_entry.configure(state="disabled")
        self.resultado_text.configure(state="disabled")
        self.resolucion_historial = [self._snapshot_resolucion()]

    def _habilitar_edicion_resolucion(self) -> None:
        """Permite editar manualmente tema y detalle sugeridos."""
        self.resolucion_editable = True
        self.tema_diario_entry.configure(state="normal")
        self.resultado_text.configure(state="normal")
        snapshot_actual = self._snapshot_resolucion()
        if not self.resolucion_historial or self.resolucion_historial[-1] != snapshot_actual:
            self.resolucion_historial.append(snapshot_actual)
        self._actualizar_estado("Tema y Detalle habilitados para edicion manual.")

    def _registrar_cambio_resolucion(self, _event: Any = None) -> None:
        """Guarda cambios de tema y detalle para poder deshacer."""
        if not self.resolucion_editable:
            return
        snapshot_actual = self._snapshot_resolucion()
        if not self.resolucion_historial or self.resolucion_historial[-1] != snapshot_actual:
            self.resolucion_historial.append(snapshot_actual)

    def _deshacer_resolucion(self) -> None:
        """Revierte el ultimo cambio manual de tema o detalle."""
        if len(self.resolucion_historial) <= 1:
            self._actualizar_estado("No hay cambios de Tema o Detalle para deshacer.")
            return
        self.resolucion_historial.pop()
        tema_anterior, detalle_anterior = self.resolucion_historial[-1]
        estado_tema = self.tema_diario_entry.cget("state")
        if estado_tema == "disabled":
            self.tema_diario_entry.configure(state="normal")
        self.tema_diario_var.set(tema_anterior)
        self.resultado_text.configure(state="normal")
        self.resultado_text.delete("1.0", "end")
        self.resultado_text.insert("1.0", detalle_anterior)
        if not self.resolucion_editable:
            self.tema_diario_entry.configure(state="disabled")
            self.resultado_text.configure(state="disabled")
        self._actualizar_estado("Ultimo cambio de Tema o Detalle deshecho.")

    def _cambiar_moneda(self, moneda: str) -> None:
        """Aplica conversion al cambiar la moneda visible."""
        importe_actual = parsear_importe(self.importe_var.get())
        if importe_actual > 0 and self.moneda_previa == "Peso":
            self.importe_base = importe_actual
        self._actualizar_importe_por_moneda()
        self.moneda_previa = moneda

    def _actualizar_importe_por_moneda(self) -> None:
        """Actualiza el importe visible segun la moneda seleccionada."""
        moneda = self.moneda_var.get()
        if moneda == "Dolar":
            convertido = self.motor.convertir_dolar_a_peso(self.importe_base)
            self.importe_var.set(self._formatear_importe(convertido, moneda))
            self._actualizar_estado(
                f"Importe convertido desde Dolar con coeficiente {self.motor.coeficiente_dolar:.4f}."
            )
            return
        self.importe_var.set(self._formatear_importe(self.importe_base, moneda) if self.importe_base else "")

    def _formatear_importe(self, importe: float, moneda: str) -> str:
        """Formatea un importe visible con simbolo de moneda."""
        simbolo = "US$" if moneda == "Dolar" else "$"
        return f"{simbolo} {importe:.2f}"

    def _snapshot_resolucion(self) -> tuple[str, str]:
        """Devuelve tema y detalle actuales para historial."""
        return (
            self.tema_diario_var.get().strip(),
            self.resultado_text.get("1.0", "end").strip(),
        )


def ejecutar_app() -> None:
    """Ejecuta la aplicacion desktop."""
    app = APCDesktopApp()
    app.mainloop()
