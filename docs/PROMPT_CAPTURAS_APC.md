# Prompt para relevar pantallas APC

## Objetivo

Relevar las pantallas necesarias para convertir el prototipo simple en una herramienta desktop que funcione en paralelo con APC. El analista ingresa manualmente con su credencial en APC; la aplicacion solo asiste con copia, lectura local, descarga asistida, analisis y texto Diario.

## Regla de confidencialidad

Antes de compartir cualquier captura o archivo:

- Tapar DNI, CUIL, CUIT, nombre, apellido, telefono, email, domicilio, numero de cuenta, CBU, CVU, tarjeta, usuario interno, token, QR o cualquier dato identificable.
- No compartir credenciales, cookies, URL con tokens, datos de sesion ni pantallas de login con usuario visible.
- No subir capturas, bases, documentos o planillas reales a GitHub.
- Usar datos ficticios o anonimizados cuando sea posible.
- Si una captura no se puede anonimizar con confianza, no compartirla.

## Contexto que necesito

Responder o documentar:

- Navegador usado para APC: Chrome, Edge u otro.
- Resolucion aproximada de pantalla y zoom del navegador.
- Si APC abre en una sola pestana o abre ventanas emergentes.
- Si el campo `Nro de Operacion` acepta pegar con `Ctrl+V`.
- Si luego de buscar se abre el incidente en la misma pantalla, nueva ventana o nueva pestana.
- Si las descargas se hacen con un click directo o aparece un dialogo de descarga.
- Carpeta local donde conviene guardar documentacion descargada.

## Capturas necesarias

### 1. Base de Reclamos

Objetivo: conocer el nombre exacto de las columnas y donde esta el numero que debe copiarse.

Capturas:

- Encabezados completos del CSV/XLSX `Base de Reclamos`.
- Una fila de ejemplo con todos los datos sensibles tapados.
- Columna exacta que contiene el numero para buscar en APC.

Detalles a anotar:

- Nombre exacto de la columna del incidente.
- Si el numero tiene ceros a la izquierda.
- Si hay mas de un identificador posible.
- Si hay columnas utiles para canal, motivo, fecha, importe o cuenta.

### 2. Busqueda en APC

Objetivo: automatizar o asistir el pegado del numero.

Capturas:

- Pantalla donde aparece el campo `Nro de Operacion`.
- Campo `Nro de Operacion` vacio.
- Campo `Nro de Operacion` con un valor ficticio o tapado.
- Boton usado para buscar.
- Resultado cuando APC encuentra el incidente.
- Resultado cuando APC no encuentra el incidente, si existe ese caso.

Detalles a anotar:

- Nombre visible exacto del campo.
- Si hace falta seleccionar algun filtro antes de buscar.
- Si el boton se llama `Buscar`, `Consultar`, `Aceptar` u otro.
- Si Enter ejecuta la busqueda.
- Tiempo aproximado que tarda en cargar el resultado.

### 3. Incidente encontrado

Objetivo: entender donde queda ubicado el caso y que datos estan disponibles.

Capturas:

- Pantalla inicial del incidente abierto.
- Zona donde se ve el numero de incidente u operacion.
- Menu o barra donde se ven las solapas disponibles.

Detalles a anotar:

- Nombres exactos de las solapas.
- Si las solapas cargan sin recargar toda la pagina.
- Si hay botones de volver, cerrar o nueva busqueda.

### 4. Solapa Detalle

Objetivo: mapear campos para lectura y analisis.

Capturas:

- Solapa `Detalle` completa, con datos sensibles tapados.
- Si hay scroll, tomar capturas de arriba, medio y abajo.

Detalles a anotar:

- Campos que aparecen siempre.
- Campo donde figura motivo/sintesis/resumen.
- Campo donde figura canal u origen.
- Campo donde figura importe, fecha, hora o cuenta.

### 5. Solapa Diario

Objetivo: generar texto Diario y preparar copia manual.

Capturas:

- Solapa `Diario` completa.
- Area donde se leen entradas previas.
- Area donde se cargaria un nuevo texto, si existe.

Detalles a anotar:

- Si el Diario es solo lectura o permite cargar texto.
- Si se pega texto plano sin perder formato.
- Si hay limite de caracteres.
- Si requiere guardar, aceptar o confirmar.

### 6. Solapa Documentacion

Objetivo: descargar archivos del incidente de forma segura o asistida.

Capturas:

- Lista de documentos disponibles.
- Columnas de la lista, con nombres visibles.
- Boton, link o icono exacto de descarga.
- Pantalla posterior al click de descarga.
- Si aparece dialogo del navegador o descarga directa.

Detalles a anotar:

- Tipos de archivo que aparecen: PDF, XLSX, DOCX, imagen, otros.
- Si cada archivo se descarga con un boton por fila.
- Si hay que seleccionar una fila antes de descargar.
- Si el nombre del archivo viene desde APC o lo define el usuario.
- Si APC permite descargar todo junto.

### 7. Solapa Auditoria

Objetivo: entender recorrido, derivaciones y estados.

Capturas:

- Solapa `Auditoria` completa.
- Si hay scroll, tomar capturas de todo el recorrido.

Detalles a anotar:

- Campos de usuario, sector, estado y fecha.
- Como identificar si el caso corresponde procesar o derivar.
- Estados importantes que deba reconocer el analizador.

### 8. Descarga local y lectura de archivos

Objetivo: definir que hara el programa una vez descargada la documentacion.

Capturas:

- Carpeta local con archivos descargados, con nombres sensibles tapados si hiciera falta.
- Ejemplo de documento PDF abierto, con datos reales tapados.
- Ejemplo de Excel descargado, mostrando solo encabezados o datos anonimizados.

Detalles a anotar:

- Que archivos son obligatorios para resolver.
- Que campos se buscan en cada documento.
- Como detectar si falta documentacion.
- Como detectar si el PDF es escaneado y requiere OCR.

## Mapeo por boton del prototipo

### Boton Cargar Base

Necesita:

- Encabezados reales de la base.
- Columna exacta del numero de incidente/operacion.
- Columnas opcionales para canal, motivo, importe, fecha, hora y cuenta.

Resultado esperado:

- La app muestra el primer reclamo y permite avanzar al siguiente.

### Boton Pegar Nro en APC

Necesita:

- Saber si el campo `Nro de Operacion` acepta foco manual y `Ctrl+V`.
- Saber si hace falta limpiar el campo antes.
- Saber si Enter ejecuta la busqueda o hay que presionar boton.

Resultado esperado:

- La app copia el numero y lo pega en el campo activo de APC sin guardar credenciales.

### Boton Leer y Analizar

Necesita:

- Campos visibles en Detalle, Diario y Auditoria.
- Documentos descargados localmente.
- Reglas para decidir canal, motivo y resolucion sugerida.

Resultado esperado:

- La app genera resolucion sugerida, texto Diario y alertas de faltantes.

### Boton Documentacion

Necesita:

- Ubicacion de la solapa `Documentacion`.
- Botones o links de descarga.
- Comportamiento real de descarga.

Resultado esperado:

- Fase actual: abre carpeta local y copia ruta.
- Fase siguiente: descarga asistida/automatizada con Playwright cuando el mapeo este validado.

### Boton Copiar Diario

Necesita:

- Confirmar donde se pega el texto Diario en APC.
- Confirmar limite de caracteres y si se admite texto plano.

Resultado esperado:

- Copia el texto revisado para que el analista lo pegue manualmente.

## Formato recomendado para enviar el relevamiento

Crear una carpeta local, sin subirla a GitHub:

```text
C:\apc-reclamos-agente\mapeo_apc\
├── 01_base_reclamos_encabezados.png
├── 02_apc_busqueda_nro_operacion_vacio.png
├── 03_apc_busqueda_nro_operacion_completo.png
├── 04_apc_resultado_encontrado.png
├── 05_incidente_abierto.png
├── 06_solapa_detalle_1.png
├── 07_solapa_diario_1.png
├── 08_solapa_documentacion_lista.png
├── 09_solapa_documentacion_descarga.png
├── 10_solapa_auditoria_1.png
└── notas_mapeo_apc.txt
```

Contenido sugerido para `notas_mapeo_apc.txt`:

```text
NAVEGADOR:
ZOOM:
CAMPO BUSQUEDA:
BOTON BUSCAR:
ENTER BUSCA: SI/NO
ABRE NUEVA PESTANA: SI/NO
SOLAPAS:
COLUMNA INCIDENTE EN BASE:
COLUMNAS UTILES EN BASE:
DESCARGA DOCUMENTACION:
LIMITE TEXTO DIARIO:
OBSERVACIONES:
```
