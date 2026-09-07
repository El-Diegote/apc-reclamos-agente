# Revision de carpeta notebook bna

Fecha de revision: 2026-09-07

## Alcance

Se reviso la carpeta local `C:\apc-reclamos-agente\notebook bna` como insumo proveniente de una conversacion con Copilot en la notebook laboral. Esta carpeta se considera material de trabajo local y no debe subirse al repositorio sin una limpieza previa de datos.

## Inventario detectado

- Archivos de definicion funcional en texto y Markdown.
- Tres planillas Excel, incluyendo una base de resoluciones y archivos operativos.
- Cuatro documentos Word, incluyendo minutas y capturas de pantallas.

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
- La planilla local de resoluciones sirve como fuente para un `ResolutionTrainer`.
  - Hay hojas con campos de tema y nota aprovechables.
  - Hay material historico que requiere limpieza antes de usarlo como fuente.

## Riesgos de datos

- Algunas planillas contienen columnas operativas sensibles.
- Algunos documentos contienen capturas embebidas. Aunque no tengan texto extraible, pueden incluir datos visibles en imagen.
- Algunas notas previas conservan referencias academicas o de trabajo final que ya no representan el objetivo real del proyecto.
- Por seguridad, la carpeta completa `notebook bna/` queda excluida en `.gitignore`.

## Decision

No se incorpora ningun archivo real de la carpeta `notebook bna` al repositorio. Solo se incorporan aprendizajes estructurales y decisiones tecnicas sanitizadas.

## Proximos pasos sugeridos

- Implementar importacion controlada de resoluciones desde Excel.
- Crear un proceso de anonimizado para bases y capturas antes de usarlas como fixtures.
- Mantener datos reales solo en entorno local autorizado.
- Agregar autenticacion local antes de habilitar uso extendido del programa.
