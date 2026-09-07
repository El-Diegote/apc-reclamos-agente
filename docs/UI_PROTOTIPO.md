# Prototipo simple de producto desktop

## Objetivo

Preparar una ventana simple para usar en paralelo con APC. El analista ingresa con su credencial en APC y mantiene abierta esta app como apoyo operativo.

## Vistas incluidas

La primera version vuelve a una unica vista con el caso actual, un panel de resolucion y cinco botones.

## Caso actual

El panel izquierdo muestra el incidente APC sobre el que esta trabajando el analista. Todos sus campos quedan bloqueados porque son datos fuente tomados del incidente y no deben editarse manualmente desde la app:

- `Incidente`: numero de operacion/incidente APC.
- `Cliente`: persona afectada en el reclamo.
- `Canal`: valor que surge del campo `TEMA` del Excel `RESOLUCIONES APC` o del canal detectado en la base.
- `Motivo`: detalle asociado al tema o motivo operativo del reclamo.
- `Importe`: suma de transacciones marcadas en la base local, tomando la columna `Importe $` cuando existe.
- `Moneda`: selector entre `Peso` y `Dolar`; el importe muestra el simbolo correspondiente y, cuando se elige `Dolar`, se convierte con el `COEFICIENTE DOLAR` leido desde `RESOLUCIONES APC`.
- `Cuenta`: cuenta desde normalizada a 14 digitos.

## Resolucion actual

El panel derecho muestra lo que se va a completar en la solapa `Diario` de APC:

- `Tema`: se completa con el `TEMA` entrenado desde `RESOLUCIONES APC`.
- `Detalle`: se completa con la `NOTA` equivalente a la fila elegida del Excel de resoluciones.
- `Editar`: habilita cambios manuales sobre `Tema` y `Detalle`.
- `Deshacer`: revierte el ultimo cambio realizado sobre `Tema` o `Detalle`.

## Botones funcionales

- `Cargar Base`: selecciona una base CSV/XLSX local y toma el primer incidente.
- `Pegar Nro en APC`: copia el incidente y, luego de 3 segundos, envia `Ctrl+V` al campo activo para pegar en `Nro de Operacion`.
- `Leer y Analizar`: lee documentos locales ya descargados y completa `Tema` y `Detalle`.
- `Documentacion`: abre la carpeta local de documentos y copia la ruta para descargar alli desde APC.
- `Copiar Diario`: copia `Tema` y `Detalle` para pegarlos manualmente en APC luego de revisarlos.

## Limite actual

La descarga automatica directa desde la solapa `Documentacion` queda pendiente hasta conocer los selectores o el comportamiento exacto de APC. Mientras tanto, el boton prepara la carpeta local segura.

## Seguridad aplicada al prototipo

- No se suben datos reales a GitHub.
- Los archivos de `notebook bna/` quedan excluidos.
- Bases, documentos, capturas, SQLite local y exports quedan ignorados por Git.
- La vista Seguridad documenta el proximo paso: PIN local, TOTP y auditoria local.
