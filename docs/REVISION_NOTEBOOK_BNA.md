# Revision de carpeta notebook bna

Fecha de revision: 2026-09-07

## Alcance

Se reviso la carpeta local `C:\apc-reclamos-agente\notebook bna` como insumo proveniente de una conversacion con Copilot en la notebook laboral. Esta carpeta se considera material de trabajo local y no debe subirse al repositorio sin una limpieza previa de datos.

## Inventario detectado

- Archivos de definicion funcional en texto y Markdown.
- Tres planillas Excel:
  - `5443060.xlsx`
  - `5632220.xlsx`
  - `RESOLUCIONES APC.xlsx`
- Cuatro documentos Word:
  - `APC_Reclamos_Agente_Minuta_Integral.docx`
  - `MINUTA GENERAL DEL PROYECTO.docx`
  - `pantallas bna+.docx`
  - `pantallas compra pos - borrar datos reales.docx`

## Hallazgos utiles para el proyecto

- La definicion vigente del proyecto es operativa e interna, no academica.
- El MVP debe concentrarse en:
  - Cargar Base de Reclamos.
  - Entrenar Resoluciones APC.
  - Analizar Casos.
  - Generar Resolucion Sugerida.
  - Generar Texto Diario editable.
  - Exportar Informe.
- El flujo funcional propuesto es:
  - Base de Reclamos.
  - Desktop App.
  - Entrenador.
  - Motor APC.
  - Resolucion sugerida.
  - Diario.
  - Validacion humana.
  - Publicacion manual en APC.
- La planilla `RESOLUCIONES APC.xlsx` sirve como fuente para un `ResolutionTrainer`.
  - Las hojas `Nuevo` y `Hoja1` contienen campos `TEMA` y `NOTA` aprovechables.
  - La hoja `Resoluciones viejas o sin uso` requiere limpieza antes de usarla como fuente.

## Riesgos de datos

- `5443060.xlsx` y `5632220.xlsx` contienen columnas operativas sensibles como `Tarjeta` y `CBU`.
- Los documentos `pantallas bna+.docx` y `pantallas compra pos - borrar datos reales.docx` contienen capturas embebidas. Aunque no tengan texto extraible, pueden incluir datos visibles en imagen.
- `RESUMEN_COMPLETO.md` conserva referencias academicas o de trabajo final que ya no representan el objetivo real del proyecto.
- Por seguridad, la carpeta completa `notebook bna/` queda excluida en `.gitignore`.

## Decision

No se incorpora ningun archivo real de la carpeta `notebook bna` al repositorio. Solo se incorporan aprendizajes estructurales y decisiones tecnicas sanitizadas.

## Proximos pasos sugeridos

- Implementar importacion controlada de resoluciones desde Excel.
- Crear un proceso de anonimizado para bases y capturas antes de usarlas como fixtures.
- Mantener datos reales solo en entorno local autorizado.
- Agregar autenticacion local antes de habilitar uso extendido del programa.
