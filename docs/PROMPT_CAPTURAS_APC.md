# Prompt actualizado para Copilot - Mapeo APC

Copilot, necesito que me ayudes a relevar la plataforma APC para continuar el desarrollo de una herramienta desktop local llamada `APC Reclamos Agente`.

La herramienta va a funcionar en paralelo con APC. Yo ingreso a APC manualmente con mi credencial. La herramienta no debe guardar credenciales, no debe modificar APC sin validacion humana y no debe subir informacion confidencial a ningun repositorio.

## Objetivo del relevamiento

Necesito capturas y notas tecnicas para mapear las acciones de estos botones de la app:

1. `Cargar Base`
2. `Pegar Nro en APC`
3. `Leer y Analizar`
4. `Documentacion`
5. `Informar Resolucion`
6. `Limpiar`

La interfaz actual esta organizada asi:

- Barra lateral izquierda con los botones, uno debajo del otro, cada uno con su check de validacion.
- Panel `Caso actual`, con campos bloqueados porque vienen del incidente APC o de la Base de Reclamos.
- Panel `Resolucion actual`, con `Tema` y `Detalle`, editables solo al tocar `Editar`.
- Boton `Limpiar`, que pide confirmar: `Desea borrar el incidente actual?`, con respuestas `Borrar` y `Cancelar`.

## Regla estricta de confidencialidad

Antes de guardar o compartir capturas:

- Tapar DNI, CUIL, CUIT, nombre, apellido, telefono, email, domicilio, numero de cuenta, CBU, CVU, tarjeta, usuario interno, legajo, token, QR, IDs internos sensibles, observaciones personales y cualquier dato identificable.
- No compartir credenciales, cookies, URL con tokens, datos de sesion ni pantallas de login con usuario visible.
- No subir capturas, bases, documentos, PDFs, Excel o datos reales a GitHub.
- Usar datos ficticios o anonimizados cuando sea posible.
- Si una captura no se puede anonimizar con seguridad, no compartirla.

Tu tarea es relevar ubicaciones, nombres visibles, flujos y comportamiento. No debes ejecutar cambios reales en APC salvo acciones de navegacion/consulta necesarias y autorizadas por mi.

## Contexto general a documentar

Completar estas notas:

```text
NAVEGADOR USADO:
VERSION / SISTEMA:
ZOOM DEL NAVEGADOR:
RESOLUCION DE PANTALLA:
APC ABRE EN MISMA PESTANA / NUEVA PESTANA / POPUP:
EL CAMPO NRO OPERACION ACEPTA CTRL+V: SI/NO
ENTER EJECUTA BUSQUEDA: SI/NO
BOTON VISIBLE PARA BUSCAR:
TIEMPO PROMEDIO DE CARGA:
DESCARGAS VAN A CARPETA DEFAULT O PREGUNTA DESTINO:
OBSERVACIONES:
```

## 1. Base de Reclamos

Objetivo: identificar exactamente de donde se toma el incidente.

Necesito:

- Captura de encabezados completos del archivo `Base de Reclamos`.
- Captura de una fila de ejemplo, con datos sensibles tapados.
- Confirmar nombre exacto de la columna `Incidente`.
- Confirmar si el valor tiene ceros a la izquierda o formato especial.
- Confirmar si la base trae mas de un identificador posible.
- Confirmar si existen columnas utiles para `Cliente`, `Canal`, `Motivo`, `Importe`, `Moneda` y `Cuenta`.

Notas a completar:

```text
COLUMNA INCIDENTE:
FORMATO DEL INCIDENTE:
HAY CEROS A LA IZQUIERDA: SI/NO
COLUMNA CLIENTE:
COLUMNA CANAL:
COLUMNA MOTIVO:
COLUMNA IMPORTE:
COLUMNA MONEDA:
COLUMNA CUENTA:
OTRAS COLUMNAS UTILES:
```

## 2. Boton Cargar Base

Funcion esperada:

- Al hacer click, la app toma el numero de una celda de la columna `Incidente` del archivo `Base de Reclamos`.
- Completa `Caso actual`.
- Copia ese numero al portapapeles.
- Marca el check del boton.

Necesito confirmar:

- Si la base es CSV, XLSX o ambos.
- Si la columna siempre se llama exactamente `Incidente`.
- Si hay que seleccionar manualmente el archivo o si conviene usar una ruta fija local.
- Si el orden de procesamiento es de arriba hacia abajo.
- Como identificar reclamos ya procesados, si existe esa marca.

## 3. Busqueda en APC

Objetivo: mapear el flujo de `Pegar Nro en APC`.

Capturas necesarias:

- Pantalla donde aparece el campo `Nro Operacion:`.
- Campo `Nro Operacion:` vacio.
- Campo con valor pegado, usando un valor ficticio o tapado.
- Boton `Ir` o boton equivalente.
- Resultado de busqueda cuando encuentra el incidente.
- Numero azul clickeable que coincide con el incidente.
- Resultado cuando no encuentra el incidente, si existe ese escenario.

Notas a completar:

```text
NOMBRE EXACTO DEL CAMPO:
EL CAMPO SE LLAMA NRO OPERACION / NRO DE OPERACION / OTRO:
HAY QUE LIMPIAR EL CAMPO ANTES: SI/NO
ENTER FUNCIONA IGUAL QUE IR: SI/NO
NOMBRE EXACTO DEL BOTON IR:
EL RESULTADO AZUL ES LINK / BOTON / TEXTO CLICKEABLE:
EL INCIDENTE SE ABRE EN MISMA PANTALLA / NUEVA PESTANA / POPUP:
DEMORA PROMEDIO HASTA VER RESULTADO:
```

## 4. Boton Pegar Nro en APC

Funcion esperada:

- Pega el incidente copiado en `Nro Operacion:`.
- Presiona `Ir` o `Enter/Intro`.
- Espera el resultado.
- Da click en el numero azul igual al incidente.
- Marca el check del boton si el incidente queda abierto.

Necesito que identifiques:

- Coordenadas aproximadas del campo `Nro Operacion:` con la pantalla maximizada.
- Coordenadas aproximadas del boton `Ir`.
- Coordenadas aproximadas del link azul del incidente.
- Si el link azul cambia de posicion segun cantidad de resultados.
- Si se puede tabular hasta el campo o boton.
- Si hay algun indicador de carga.

## 5. Incidente abierto

Objetivo: confirmar que APC quedo en el caso correcto.

Capturas necesarias:

- Pantalla inicial del incidente abierto.
- Zona donde se ve el numero de incidente/operacion.
- Barra o menu donde aparecen las solapas.
- Cualquier mensaje de estado del reclamo.

Notas:

```text
DONDE SE VE EL INCIDENTE ABIERTO:
COMO CONFIRMAR QUE ES EL INCIDENTE CORRECTO:
SOLAPAS VISIBLES:
HAY BOTON VOLVER / NUEVA BUSQUEDA:
```

## 6. Solapa Detalle

Objetivo: mapear lo que debe leer `Leer y Analizar`.

Capturas necesarias:

- Solapa `Detalle` completa.
- Si hay scroll, capturas de parte superior, media e inferior.
- Campos donde figuren datos de `Cliente`, `Canal`, `Motivo`, `Importe`, `Moneda`, `Cuenta`, fecha y hora.

Notas:

```text
NOMBRE EXACTO DE LA SOLAPA:
CAMPO CLIENTE:
CAMPO CANAL:
CAMPO MOTIVO:
CAMPO IMPORTE:
CAMPO MONEDA:
CAMPO CUENTA:
CAMPO FECHA:
CAMPO HORA:
HAY TABLAS O SOLO CAMPOS:
HAY SCROLL: SI/NO
```

## 7. Boton Leer y Analizar

Funcion esperada:

- Lee el cuadro o contenido de la solapa `Detalle`.
- Entra a la solapa `Documentacion`.
- Descarga los archivos disponibles del incidente.
- Lee los archivos descargados.
- Analiza el caso y devuelve una resolucion que sea igual o similar a la fila correspondiente del archivo `RESOLUCIONES APC`.
- Completa `Resolucion actual` con:
  - `Tema`
  - `Detalle`
- Marca el check del boton.

Necesito relevar:

- Como abrir la solapa `Detalle`.
- Como copiar o leer el texto visible de `Detalle`.
- Como abrir la solapa `Documentacion`.
- Si la plataforma permite seleccionar texto.
- Si las tablas son HTML, imagen, PDF incrustado o controles especiales.
- Que datos de Detalle alcanzan para buscar una resolucion equivalente.

## 8. RESOLUCIONES APC

Objetivo: entender como empatar el incidente con la resolucion sugerida.

Necesito:

- Captura solo de encabezados del archivo `RESOLUCIONES APC`.
- Confirmar columna exacta de `TEMA`.
- Confirmar columna exacta de `MOTIVO` o detalle equivalente.
- Confirmar columna exacta de `NOTA`.
- Confirmar donde aparece `COEFICIENTE DOLAR`.
- Confirmar si el coeficiente esta en una columna, celda fija, hoja separada o texto.
- No compartir filas reales completas si contienen informacion sensible.

Notas:

```text
HOJAS DEL EXCEL:
COLUMNA TEMA:
COLUMNA MOTIVO/DETALLE:
COLUMNA NOTA:
UBICACION COEFICIENTE DOLAR:
FORMATO DEL COEFICIENTE DOLAR:
COMO ELEGIR LA FILA CORRECTA:
```

## 9. Solapa Documentacion

Objetivo: descargar y validar archivos.

Capturas necesarias:

- Solapa `Documentacion` abierta.
- Lista completa de documentos disponibles.
- Encabezados de la tabla.
- Boton, link o icono de descarga por documento.
- Pantalla posterior al click de descarga.
- Mensajes de error o confirmacion, si existen.

Notas:

```text
NOMBRE EXACTO DE LA SOLAPA:
TIPOS DE ARCHIVO DISPONIBLES:
HAY DESCARGA INDIVIDUAL POR FILA: SI/NO
HAY DESCARGA MASIVA: SI/NO
HAY QUE SELECCIONAR FILA ANTES: SI/NO
EL NOMBRE DEL ARCHIVO LO DEFINE APC: SI/NO
APARECE DIALOGO DE DESCARGA: SI/NO
COMO SABER QUE TERMINO LA DESCARGA:
```

## 10. Boton Documentacion

Funcion esperada:

- Confirma que toda la documentacion descargada se haya descargado bien.
- Valida que existan archivos.
- Valida que no esten vacios.
- Valida que sean legibles.
- Marca el check del boton.

Necesito que identifiques:

- Cuantos documentos deberian descargarse para un caso normal.
- Como saber desde APC cuantos documentos hay.
- Como comparar cantidad esperada vs cantidad descargada.
- Si hay documentos obligatorios.
- Si hay archivos que APC descarga con nombres repetidos.
- Si algun archivo queda bloqueado mientras descarga.

## 11. Solapa Diario

Objetivo: mapear `Informar Resolucion`.

Capturas necesarias:

- Solapa `Diario` completa.
- Campo visible donde se carga `Tema`.
- Campo visible donde se carga `Detalle`.
- Boton para guardar/agregar/aceptar la nota.
- Mensaje posterior a guardar, si existe.
- Entradas previas del Diario, con datos sensibles tapados.

Notas:

```text
NOMBRE EXACTO DE LA SOLAPA:
CAMPO TEMA:
CAMPO DETALLE:
EL CAMPO TEMA ES INPUT / SELECT / COMBO:
EL CAMPO DETALLE ES TEXTAREA / EDITOR / OTRO:
ACEPTA PEGAR TEXTO PLANO: SI/NO
LIMITE DE CARACTERES:
BOTON GUARDAR / AGREGAR / ACEPTAR:
HAY CONFIRMACION POSTERIOR: SI/NO
COMO SABER QUE SE GUARDO:
```

## 12. Boton Informar Resolucion

Funcion esperada:

- Primero copia el contenido del item `Tema`.
- Lo pega en el campo `Tema` de la solapa `Diario`.
- Luego copia el contenido del item `Detalle`.
- Lo pega en el campo de detalle de esa nota en la solapa `Diario`.
- La publicacion debe quedar bajo validacion humana.
- Marca el check del boton cuando queda informado/preparado.

Necesito relevar:

- Coordenadas o comportamiento para llegar al campo `Tema`.
- Coordenadas o comportamiento para llegar al campo `Detalle`.
- Si conviene usar click, Tab o atajos de teclado.
- Si se debe presionar algun boton para agregar la nota.
- Si existe riesgo de guardar automaticamente sin confirmacion.
- Que paso debe quedar reservado para validacion humana.

## 13. Boton Limpiar

Funcion esperada:

- Al hacer click, aparece el cuadro: `Desea borrar el incidente actual?`
- Boton `Borrar`: limpia incidente encontrado/copiado, limpia `Caso actual`, limpia `Resolucion actual`, reinicia checks y limpia portapapeles.
- Boton `Cancelar`: cierra el cuadro y no ejecuta la limpieza.
- No borra archivos descargados ni documentos reales.

Necesito validar desde el uso:

- Si el texto del cuadro resulta claro.
- Si conviene agregar advertencia de que no borra archivos.
- Si el flujo debe limpiar tambien la carpeta de documentacion o no. Por ahora, no debe borrarla.

## 14. Formato de entrega del relevamiento

Crear una carpeta local en la notebook del trabajo:

```text
C:\apc-reclamos-agente\mapeo_apc\
├── 01_base_reclamos_encabezados.png
├── 02_base_reclamos_fila_anonimizada.png
├── 03_apc_busqueda_nro_operacion_vacio.png
├── 04_apc_busqueda_nro_operacion_con_valor.png
├── 05_apc_boton_ir.png
├── 06_apc_resultado_link_azul.png
├── 07_incidente_abierto.png
├── 08_solapa_detalle_arriba.png
├── 09_solapa_detalle_medio.png
├── 10_solapa_detalle_abajo.png
├── 11_resoluciones_apc_encabezados.png
├── 12_resoluciones_apc_coeficiente_dolar.png
├── 13_solapa_documentacion_lista.png
├── 14_solapa_documentacion_descarga.png
├── 15_carpeta_descargas_documentacion.png
├── 16_solapa_diario_campos.png
├── 17_solapa_diario_guardar.png
└── notas_mapeo_apc.txt
```

Contenido sugerido para `notas_mapeo_apc.txt`:

```text
NAVEGADOR:
ZOOM:
RESOLUCION:

BASE DE RECLAMOS:
COLUMNA INCIDENTE:
COLUMNAS UTILES:

BUSQUEDA APC:
CAMPO NRO OPERACION:
BOTON IR:
ENTER BUSCA:
RESULTADO AZUL:
COMO ABRE INCIDENTE:

DETALLE:
CAMPOS IMPORTANTES:
FORMA DE LECTURA:

RESOLUCIONES APC:
COLUMNA TEMA:
COLUMNA MOTIVO/DETALLE:
COLUMNA NOTA:
COEFICIENTE DOLAR:

DOCUMENTACION:
CANTIDAD ESPERADA:
BOTONES DESCARGA:
CARPETA DESCARGA:
VALIDACION DE DESCARGA:

DIARIO:
CAMPO TEMA:
CAMPO DETALLE:
BOTON GUARDAR:
VALIDACION HUMANA:

LIMPIAR:
CONFIRMACION CLARA:
NO BORRA ARCHIVOS:

OBSERVACIONES:
```

## Resultado esperado de Copilot

Al finalizar, necesito que Copilot me devuelva:

- Lista de capturas generadas y nombre de cada archivo.
- `notas_mapeo_apc.txt` completo.
- Resumen de acciones que ya se pueden automatizar con seguridad.
- Lista de acciones que todavia requieren confirmacion humana.
- Riesgos detectados de seguridad/confidencialidad.
- Recomendacion sobre si usar coordenadas, teclado, Playwright, Selenium o lectura manual asistida para cada boton.

Recordatorio: no subir ningun archivo real, captura ni dato sensible a GitHub. Todo el relevamiento queda local hasta que sea revisado y autorizado.
