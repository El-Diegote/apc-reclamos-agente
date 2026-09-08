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

- `Cargar Base`: selecciona `Base de Reclamos`, toma el valor de la columna `Incidente`, completa `Caso actual` y copia ese numero al portapapeles.
- `Pegar Nro en APC`: pega el incidente copiado en `Nro Operacion:`, presiona `Enter` para buscar y deja pendiente el click exacto sobre el resultado azul hasta contar con el mapeo de APC.
- `Leer y Analizar`: lee la solapa `Detalle`, prepara descarga/lectura de `Documentacion` y genera una respuesta comparable con `RESOLUCIONES APC`.
- `Documentacion`: valida que la documentacion descargada exista, no este vacia y sea legible.
- `Informar Resolución`: informa primero `Tema` y luego `Detalle` en la solapa `Diario`; el pegado exacto en APC requiere el mapeo de campos.

Cada boton tiene un indicador de validacion al costado. El check aparece cuando la accion pudo completarse o quedar preparada correctamente dentro del alcance del prototipo.

## Limite actual

La descarga automatica directa desde la solapa `Documentacion` queda pendiente hasta conocer los selectores o el comportamiento exacto de APC. Mientras tanto, el boton prepara la carpeta local segura.

## Seguridad aplicada al prototipo

- No se suben datos reales a GitHub.
- Los archivos de `notebook bna/` quedan excluidos.
- Bases, documentos, capturas, SQLite local y exports quedan ignorados por Git.
- La vista Seguridad documenta el proximo paso: PIN local, TOTP y auditoria local.
