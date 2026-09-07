# Prototipo simple de producto desktop

## Objetivo

Preparar una ventana simple para usar en paralelo con APC. El analista ingresa con su credencial en APC y mantiene abierta esta app como apoyo operativo.

## Vistas incluidas

La primera version vuelve a una unica vista con el caso actual, un panel de resultado y cinco botones.

## Botones funcionales

- `Cargar Base`: selecciona una base CSV/XLSX local y toma el primer reclamo.
- `Pegar Nro en APC`: copia el numero y, luego de 3 segundos, envia `Ctrl+V` al campo activo para pegar en `Nro de Operacion`.
- `Leer y Analizar`: lee documentos locales ya descargados y genera resolucion sugerida y texto Diario.
- `Documentacion`: abre la carpeta local de documentos y copia la ruta para descargar alli desde APC.
- `Copiar Diario`: copia el texto Diario sugerido para pegarlo manualmente en APC luego de revisarlo.

## Limite actual

La descarga automatica directa desde la solapa `Documentacion` queda pendiente hasta conocer los selectores o el comportamiento exacto de APC. Mientras tanto, el boton prepara la carpeta local segura.

## Seguridad aplicada al prototipo

- No se suben datos reales a GitHub.
- Los archivos de `notebook bna/` quedan excluidos.
- Bases, documentos, capturas, SQLite local y exports quedan ignorados por Git.
- La vista Seguridad documenta el proximo paso: PIN local, TOTP y auditoria local.
