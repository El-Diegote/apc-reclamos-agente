# Seguridad y resguardo

## Principio rector

APC Reclamos Agente es una herramienta operativa pensada para asistir al analista. No debe reemplazar la revision humana, no debe modificar APC automaticamente y no debe almacenar credenciales.

## Objetivos de seguridad

- Que el acceso al programa dependa de autorizacion del titular del proyecto.
- Que los datos reales permanezcan fuera de GitHub.
- Que toda salida sensible quede en almacenamiento local controlado.
- Que toda resolucion sugerida requiera aprobacion humana antes de publicarse.
- Que las futuras integraciones con APC sean de solo lectura salvo aprobacion explicita.

## Politicas iniciales

- No versionar bases reales, capturas, PDFs, DOCX, XLSX ni analisis manuales con datos identificables.
- No guardar usuarios, claves, cookies, tokens ni secretos en archivos del proyecto.
- No incluir credenciales en logs.
- Registrar acciones relevantes sin registrar datos personales innecesarios.
- Usar datos ficticios o anonimizados para pruebas compartibles.

## Autenticacion propuesta

La primera version protegida deberia incluir autenticacion local antes de abrir la app:

- PIN local definido por el titular.
- Segundo factor basado en TOTP compatible con aplicaciones autenticadoras.
- Bloqueo temporal ante intentos fallidos.
- Hash de secretos, nunca almacenamiento en texto plano.
- Recuperacion manual controlada, sin backdoors ocultos.

## Componentes futuros

- `auth/`: modulo de autenticacion local.
- `security/`: utilidades de hashing, TOTP y control de intentos.
- `audit/`: registro de eventos sin datos sensibles.
- `settings/`: configuracion local no versionada.

## Fase recomendada

Primero afianzar el MVP funcional. Luego implementar seguridad local antes de ampliar uso o distribuir la herramienta.
