"""Interfaz desktop CustomTkinter para APC Reclamos."""

from __future__ import annotations

import logging
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any

import customtkinter as ctk

from config.config import CANALES_APC
from src.motor_apc import MotorAPC


class APCDesktopApp(ctk.CTk):
    """Aplicacion desktop para analistas APC."""

    def __init__(self, motor: MotorAPC | None = None) -> None:
        """Inicializa la interfaz.

        Args:
            motor: Motor APC opcional para inyeccion o pruebas.
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.motor = motor or MotorAPC(logger=self.logger)
        self.caso_actual: dict[str, Any] | None = None

        self.title("APC Reclamos Agente")
        self.geometry("1120x720")
        self.minsize(980, 640)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self._crear_layout()

    def _crear_layout(self) -> None:
        """Construye la pantalla principal."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(self, corner_radius=0)
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            encabezado,
            text="APC Reclamos Agente",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        titulo.grid(row=0, column=0, padx=20, pady=(16, 2), sticky="w")

        subtitulo = ctk.CTkLabel(
            encabezado,
            text=(
                "MVP desktop para analizar reclamos ATM, POS, mPOS, BNA+, MODO, "
                "Cash In, eCommerce y otros canales."
            ),
            font=ctk.CTkFont(size=13),
        )
        subtitulo.grid(row=1, column=0, padx=20, pady=(0, 14), sticky="w")

        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=1, column=0, padx=16, pady=16, sticky="nsew")
        self.tabs.add("Base de Reclamos")
        self.tabs.add("Entrenamiento APC")
        self.tabs.add("Analisis de Caso")
        self.tabs.add("Exportacion")

        self._tab_base()
        self._tab_entrenamiento()
        self._tab_analisis()
        self._tab_exportacion()

    def _tab_base(self) -> None:
        """Crea controles para cargar base de reclamos."""
        tab = self.tabs.tab("Base de Reclamos")
        tab.grid_columnconfigure(0, weight=1)

        panel = ctk.CTkFrame(tab)
        panel.grid(row=0, column=0, padx=16, pady=16, sticky="ew")
        panel.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(panel, text="Archivo CSV/XLSX").grid(row=0, column=0, padx=12, pady=12)
        self.base_path_var = ctk.StringVar(value="")
        ctk.CTkEntry(panel, textvariable=self.base_path_var).grid(
            row=0, column=1, padx=12, pady=12, sticky="ew"
        )
        ctk.CTkButton(panel, text="Seleccionar", command=self._seleccionar_base).grid(
            row=0, column=2, padx=12, pady=12
        )
        ctk.CTkButton(panel, text="Cargar Base", command=self._cargar_base).grid(
            row=1, column=2, padx=12, pady=(0, 12)
        )

        self.base_estado = ctk.CTkTextbox(tab, height=220)
        self.base_estado.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.base_estado.insert("1.0", "Seleccione una base de reclamos para cargarla en SQLite.")

    def _tab_entrenamiento(self) -> None:
        """Crea controles para entrenar resoluciones APC."""
        tab = self.tabs.tab("Entrenamiento APC")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        formulario = ctk.CTkFrame(tab)
        formulario.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")
        formulario.grid_columnconfigure(1, weight=1)

        self.train_canal = ctk.StringVar(value=CANALES_APC[0])
        self.train_motivo = ctk.StringVar(value="")

        ctk.CTkLabel(formulario, text="Canal").grid(row=0, column=0, padx=12, pady=10, sticky="w")
        ctk.CTkOptionMenu(formulario, values=list(CANALES_APC), variable=self.train_canal).grid(
            row=0, column=1, padx=12, pady=10, sticky="ew"
        )
        ctk.CTkLabel(formulario, text="Motivo").grid(row=1, column=0, padx=12, pady=10, sticky="w")
        ctk.CTkEntry(formulario, textvariable=self.train_motivo).grid(
            row=1, column=1, padx=12, pady=10, sticky="ew"
        )
        ctk.CTkLabel(formulario, text="Resolucion sugerida").grid(
            row=2, column=0, padx=12, pady=10, sticky="nw"
        )
        self.train_resolucion = ctk.CTkTextbox(formulario, height=150)
        self.train_resolucion.grid(row=2, column=1, padx=12, pady=10, sticky="ew")
        ctk.CTkLabel(formulario, text="Texto Diario").grid(
            row=3, column=0, padx=12, pady=10, sticky="nw"
        )
        self.train_diario = ctk.CTkTextbox(formulario, height=120)
        self.train_diario.grid(row=3, column=1, padx=12, pady=10, sticky="ew")
        ctk.CTkButton(formulario, text="Entrenar Resolucion", command=self._entrenar).grid(
            row=4, column=1, padx=12, pady=14, sticky="e"
        )

        self.resoluciones_text = ctk.CTkTextbox(tab)
        self.resoluciones_text.grid(row=0, column=1, padx=(0, 16), pady=16, sticky="nsew")
        self._refrescar_resoluciones()

    def _tab_analisis(self) -> None:
        """Crea controles de analisis y aprobacion humana."""
        tab = self.tabs.tab("Analisis de Caso")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        formulario = ctk.CTkFrame(tab)
        formulario.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")
        formulario.grid_columnconfigure(1, weight=1)

        self.incidente_var = ctk.StringVar(value="INC-2026-0001")
        self.canal_var = ctk.StringVar(value=CANALES_APC[0])
        self.motivo_var = ctk.StringVar(value="Desconocimiento de consumo")
        self.importe_var = ctk.StringVar(value="12500.50")
        self.cuenta_var = ctk.StringVar(value="001234567890")
        self.analista_var = ctk.StringVar(value="")
        self.aprobado_var = ctk.BooleanVar(value=False)

        campos = [
            ("Numero incidente", self.incidente_var),
            ("Motivo", self.motivo_var),
            ("Importe", self.importe_var),
            ("Numero cuenta", self.cuenta_var),
            ("Analista", self.analista_var),
        ]
        ctk.CTkLabel(formulario, text="Canal").grid(row=0, column=0, padx=12, pady=8, sticky="w")
        ctk.CTkOptionMenu(formulario, values=list(CANALES_APC), variable=self.canal_var).grid(
            row=0, column=1, padx=12, pady=8, sticky="ew"
        )
        for indice, (label, variable) in enumerate(campos, start=1):
            ctk.CTkLabel(formulario, text=label).grid(
                row=indice, column=0, padx=12, pady=8, sticky="w"
            )
            ctk.CTkEntry(formulario, textvariable=variable).grid(
                row=indice, column=1, padx=12, pady=8, sticky="ew"
            )

        ctk.CTkButton(formulario, text="Analizar Caso", command=self._analizar_caso).grid(
            row=6, column=1, padx=12, pady=12, sticky="e"
        )
        ctk.CTkCheckBox(
            formulario,
            text="Resolucion revisada y aprobada por analista humano",
            variable=self.aprobado_var,
        ).grid(row=7, column=1, padx=12, pady=8, sticky="w")
        ctk.CTkButton(formulario, text="Guardar Revision", command=self._guardar_revision).grid(
            row=8, column=1, padx=12, pady=12, sticky="e"
        )

        self.resultado_text = ctk.CTkTextbox(tab)
        self.resultado_text.grid(row=0, column=1, padx=(0, 16), pady=16, sticky="nsew")
        self.resultado_text.insert(
            "1.0",
            "Analice un caso para generar resolucion sugerida y texto Diario.",
        )

    def _tab_exportacion(self) -> None:
        """Crea controles para exportar informe."""
        tab = self.tabs.tab("Exportacion")
        tab.grid_columnconfigure(0, weight=1)

        panel = ctk.CTkFrame(tab)
        panel.grid(row=0, column=0, padx=16, pady=16, sticky="ew")
        ctk.CTkButton(panel, text="Exportar Informe JSON", command=self._exportar).grid(
            row=0, column=0, padx=12, pady=12
        )
        self.export_estado = ctk.CTkTextbox(tab, height=260)
        self.export_estado.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.export_estado.insert("1.0", "Los informes se exportan desde casos revisados.")

    def _seleccionar_base(self) -> None:
        """Abre selector de archivo para base de reclamos."""
        archivo = filedialog.askopenfilename(
            title="Seleccionar Base de Reclamos",
            filetypes=[("Bases APC", "*.csv *.xlsx *.xlsm"), ("Todos", "*.*")],
        )
        if archivo:
            self.base_path_var.set(archivo)

    def _cargar_base(self) -> None:
        """Carga base seleccionada en SQLite."""
        try:
            cantidad = self.motor.cargar_base_reclamos(Path(self.base_path_var.get()))
            self._set_text(self.base_estado, f"Base cargada correctamente: {cantidad} filas.")
        except Exception as exc:
            self.logger.exception("No se pudo cargar la base")
            messagebox.showerror("Error", str(exc))

    def _entrenar(self) -> None:
        """Entrena una resolucion desde el formulario."""
        try:
            resolucion_id = self.motor.entrenar_resolucion(
                canal=self.train_canal.get(),
                motivo=self.train_motivo.get(),
                texto_resolucion=self.train_resolucion.get("1.0", "end").strip(),
                texto_diario=self.train_diario.get("1.0", "end").strip(),
            )
            messagebox.showinfo("Entrenamiento", f"Resolucion entrenada: #{resolucion_id}")
            self._refrescar_resoluciones()
        except Exception as exc:
            self.logger.exception("No se pudo entrenar resolucion")
            messagebox.showerror("Error", str(exc))

    def _analizar_caso(self) -> None:
        """Analiza el caso ingresado en pantalla."""
        caso = {
            "numero_incidente": self.incidente_var.get(),
            "canal": self.canal_var.get(),
            "motivo": self.motivo_var.get(),
            "importe": self.importe_var.get(),
            "numero_cuenta": self.cuenta_var.get(),
        }
        self.caso_actual = self.motor.analizar_caso(caso)
        texto = (
            f"Resolucion sugerida:\n{self.caso_actual['resolucion_sugerida']}\n\n"
            f"Texto Diario:\n{self.caso_actual['texto_diario']}\n\n"
            "Estado: pendiente de aprobacion humana."
        )
        self._set_text(self.resultado_text, texto)

    def _guardar_revision(self) -> None:
        """Guarda el caso luego de la revision humana."""
        if not self.caso_actual:
            messagebox.showwarning("Sin caso", "Primero analice un caso.")
            return
        if not self.analista_var.get().strip():
            messagebox.showwarning("Analista requerido", "Ingrese el analista revisor.")
            return
        caso_id = self.motor.guardar_caso_aprobado(
            self.caso_actual,
            aprobado=self.aprobado_var.get(),
            analista=self.analista_var.get().strip(),
        )
        messagebox.showinfo("Revision guardada", f"Caso guardado: #{caso_id}")

    def _exportar(self) -> None:
        """Exporta informe consolidado."""
        try:
            destino = self.motor.exportar_informe()
            self._set_text(self.export_estado, f"Informe exportado:\n{destino}")
        except Exception as exc:
            self.logger.exception("No se pudo exportar informe")
            messagebox.showerror("Error", str(exc))

    def _refrescar_resoluciones(self) -> None:
        """Actualiza listado de resoluciones entrenadas."""
        resoluciones = self.motor.listar_resoluciones()
        if not resoluciones:
            texto = "No hay resoluciones entrenadas todavia."
        else:
            texto = "\n\n".join(
                (
                    f"#{item['id']} | {item['canal']} | {item['motivo']}\n"
                    f"Resolucion: {item['texto_resolucion']}\n"
                    f"Diario: {item['texto_diario']}"
                )
                for item in resoluciones
            )
        self._set_text(self.resoluciones_text, texto)

    def _set_text(self, widget: ctk.CTkTextbox, texto: str) -> None:
        """Reemplaza el contenido de un textbox.

        Args:
            widget: Textbox destino.
            texto: Texto a mostrar.
        """
        widget.delete("1.0", "end")
        widget.insert("1.0", texto)


def ejecutar_app() -> None:
    """Ejecuta la aplicacion desktop."""
    app = APCDesktopApp()
    app.mainloop()
