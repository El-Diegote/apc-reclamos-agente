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

## Iteracion 5 - Reencuadre operativo

- Se confirma que el proyecto no es academico ni corresponde a un trabajo final.
- El objetivo pasa a quedar formulado como iniciativa operativa para construir una herramienta de asistencia en el banco.
- Se revisa la carpeta local `C:\apc-reclamos-agente\notebook bna` como insumo privado, sin incorporar archivos reales al repo.
- Se documentan hallazgos sanitizados en `docs/REVISION_NOTEBOOK_BNA.md`.
- Se agrega `docs/SEGURIDAD.md` para planificar autenticacion local, resguardo de datos y control de acceso.
- Se refuerza `.gitignore` para evitar subir capturas, documentos, planillas y analisis manuales con datos reales.

## Iteracion 6 - Cierre V1 prototipo simple

- Se aprueba una primera version simple de la aplicacion como ventana companera de APC.
- La app queda en una sola vista con cinco botones: `Cargar Base`, `Pegar Nro en APC`, `Leer y Analizar`, `Documentacion` y `Copiar Diario`.
- El pegado en APC se implementa como asistencia controlada: copia al portapapeles y pega en el campo activo despues de una pausa breve.
- La descarga automatica desde APC queda fuera de esta version hasta mapear con capturas la solapa `Documentacion`.
- Se agrega `docs/PROMPT_CAPTURAS_APC.md` para relevar pantallas y detalles necesarios sin exponer informacion confidencial.
- Regla operativa: no se sube ningun dato real o archivo confidencial sin autorizacion y validacion previa del titular.

## Iteracion 7 - Ajuste de campos operativos

- Se renombran campos de la vista simple: `Cliente`, `Canal`, `Motivo` y `Detalle`.
- Se agrega selector `Moneda` junto a `Importe`, con conversion de `Dolar` mediante `COEFICIENTE DOLAR` del Excel `RESOLUCIONES APC`.
- El campo `Detalle` queda bloqueado por defecto y se habilita con `Editar`.
- Se agrega `Deshacer` para revertir cambios manuales sobre el detalle antes de copiarlo a APC.
