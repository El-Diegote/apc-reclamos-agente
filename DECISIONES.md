# Decisiones del Proyecto

## Iteracion 1 - Estructura base

- Se creo una estructura modular con separacion entre agente, analizador, extractor, utilidades y configuracion.
- Se eligio `pathlib.Path` para evitar hardcoding de rutas y mejorar la portabilidad entre sistemas operativos.
- Se agrego una corrida de ejemplo (`corrida_1`) para permitir una ejecucion inmediata.

## Iteracion 2 - Simulacion APC

- La integracion con APC se implementa como simulacion controlada porque no hay credenciales ni acceso real a la plataforma.
- Las cuatro solapas APC se representan como diccionarios: `detalle`, `diario`, `documentacion` y `auditoria`.
- El timeout de sesion se simula comparando el tiempo transcurrido desde la creacion del agente.

## Iteracion 3 - Seguridad

- No se almacenan credenciales en codigo ni en archivos de ejemplo.
- `.gitignore` excluye `.env`, llaves, tokens, logs y PDFs potencialmente sensibles.
- Los datos de ejemplo son ficticios y no deben reemplazar politicas internas de anonimizado.

## Errores encontrados

- Sin errores tecnicos conocidos en la version inicial.
- Riesgo esperado: si se intenta leer PDF o Excel sin instalar dependencias opcionales, el extractor registra el error e informa la causa.

## Cambios de alcance

- La descarga de documentacion se simula leyendo archivos ya presentes en `corridas/corrida_X/documentos`.
- La busqueda en APC se simula con el archivo `csv_diario.csv` y datos generados localmente.

## Justificaciones tecnicas

- Se evita hardcoding centralizando rutas y constantes en `config/config.py`.
- Se usa logging en todos los puntos de accion o error para facilitar auditoria.
- La salida JSON sigue un template versionado en `templates/output_template.json`.
- El codigo prioriza legibilidad y trazabilidad por encima de optimizaciones prematuras.

## Iteracion 4 - MVP desktop

- Se agrego una aplicacion de escritorio con CustomTkinter para que el analista pueda operar sin consola.
- Se incorporo `MotorAPC` como capa de negocio para cargar bases, entrenar resoluciones, analizar casos, generar textos y exportar informes.
- Se agrego `RepositorioAPC` con SQLite para persistir resoluciones entrenadas, bases cargadas y casos revisados.
- `main.py` abre la app desktop por defecto y mantiene `--cli` para la corrida simulada.

## Restricciones operativas del MVP

- La app no modifica informacion en APC.
- La app no ejecuta acciones automaticas sin validacion humana.
- La app no almacena credenciales.
- La resolucion sugerida se guarda como revisada solo cuando el analista completa la revision en pantalla.
