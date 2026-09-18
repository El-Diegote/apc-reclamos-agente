# APC RECLAMOS AGENTE

## CONTEXTO GENERAL

Proyecto de automatización asistida para el equipo APC (Atención de Reclamos y Consultas).

El objetivo NO es reemplazar APC ni automatizar credenciales.

El objetivo es construir una aplicación desktop que asista al analista durante la investigación, análisis y resolución de incidentes.

El usuario se autentica manualmente en APC y en los sistemas corporativos.

El sistema funciona como una segunda pantalla inteligente.

---

# OBJETIVO FINAL

Construir una aplicación desktop denominada:

APC Reclamos Agente

capaz de:

1. Analizar reclamos APC.
2. Analizar documentación asociada.
3. Analizar movimientos Smart Console.
4. Detectar operaciones reclamadas.
5. Sugerir tratamiento operativo.
6. Generar texto para Diario APC.
7. Preparar futuras integraciones con APC.

---

# ALCANCE MVP

La primera versión debe:

✅ Cargar documentación.

✅ Analizar F60330.

✅ Analizar movimientos Smart Console.

✅ Detectar canales.

✅ Clasificar operaciones.

✅ Generar resolución sugerida.

✅ Generar Diario APC.

✅ Exportar informe.

No debe:

❌ Automatizar credenciales.

❌ Publicar automáticamente en APC.

❌ Modificar incidentes sin validación humana.

---

# SISTEMAS RELEVADOS

## APC

Flujo:

Base Reclamos
↓
N° Operación
↓
ENTER
↓
Lista resultados
↓
Abrir incidente

### Solapas críticas

Detalle

Diario

Documentación

Auditoría

---

## Diario

Modelo:

Tema

Nota

Cada entrada se crea mediante:

Nuevo
↓
Tema
↓
Nota

La aplicación debe generar ambas cosas.

---

## Documentación

Modelo:

Categoría

Tipo Documento

Subtipo

Archivo

Los documentos se cargan mediante:

Nuevo
↓
Categoría
↓
Seleccionar archivo
↓
Agregar

---

## Auditoría

Columnas:

Fecha

Usuario

Campo

Operación

Valor anterior

Nuevo valor

Campo más importante:

Puesto Propietario

Permite reconstruir derivaciones.

---

# DOCUMENT MAP

## DOC-001

Comprobante Reclamo/Consulta APC

Extraer:

- incidente
- motivo
- origen
- sucursal
- fecha
- operaciones reclamadas

---

## DOC-002

Formulario F60330

IMPORTANTE:

NO asumir que contiene todas las operaciones.

Pueden existir:

- múltiples formularios
- anexos
- denuncias
- notas complementarias

El F60330 puede:

- estar incompleto
- estar mal completado
- contener información inconsistente

Por lo tanto debe contrastarse contra:

Detalle APC

Diario APC

Extractos

Movimientos

---

# CONCEPTO DE CLAIM UNIVERSE

No analizar documentos individualmente.

Construir un expediente completo.

Concepto:

Claim Universe

Fuentes:

F60330

Detalle APC

Diario APC

Documentación

Smart Console

La aplicación debe consolidar todas las operaciones reclamadas.

---

# SMART CONSOLE

Fuente principal de evidencia transaccional.

Búsqueda posible por:

- cuenta
- tarjeta
- fecha
- hora

Exporta un Excel crudo.

---

# MACRO CHANI

Actualmente los analistas utilizan una macro denominada:

DETALLE_OPERACIONES_CHANI_FINAL

La macro:

- reorganiza columnas
- facilita lectura
- agrega columnas operativas

La aplicación NO debe replicar visualmente la macro.

Debe replicar la lógica.

---

# COLUMNAS OPERATIVAS

## CHECK

Marca operaciones seleccionadas para el reclamo.

## ROBO

Marca operaciones con:

- robo
- hurto
- extravío

## LINK GO

Puede contener:

Número Gestión

Número Pedido

PAGAR

CIRCUITO

---

# REGLAS DE NEGOCIO

## RULE-001

Analizar únicamente operaciones:

Aprobada.

No utilizar:

Aprobada

como criterio principal.

---

## RULE-002

También tener en cuenta:

Reversos

Devoluciones

Contrapartidas

---

## RULE-003

LINK GO solo debe utilizarse para operaciones CHECK.

---

## RULE-004

LINK GO se utiliza principalmente para:

e-Commerce

e-Commerce Recurrente

POS

mPOS

con indicios de fraude.

---

## RULE-005

La condición ROBO puede provenir de:

Denuncia Policial

F60330

Documentación

Diario

---

## RULE-006

CIRCUITO

Operaciones menores al umbral definido operativamente.

Inicialmente considerar:

USD 15

o equivalente en pesos.

Este valor debe parametrizarse.

---

## RULE-007

PAGAR

Operaciones que no pueden trazarse mediante LINK GO.

---

# SMART CONSOLE ANALYZER

Debe extraer:

fecha

hora

importe

tarjeta

cuenta origen

cuenta destino

canal

respuesta

comercio

IP

país

moneda

---

# RECONSTRUCCIÓN DE COMERCIO

NO utilizar únicamente una columna.

Combinar:

Cuenta Hasta

+

Denominación de Establecimiento

para reconstruir comercio.

---

# CANALES RELEVANTES

ATM

POS

mPOS

e-Commerce

e-Commerce Recurrente

BNA+

MODO

Coelsa

Transferencia

DEBIN

Mobile Banking

---

# MOTORES DEL SISTEMA

## DocumentClassifier

Clasifica:

F60330

Denuncia

Extracto

Comprobante

Dictamen

Nota

---

## ClaimUniverseBuilder

Consolida información proveniente de:

APC

Documentos

Movimientos

---

## SmartConsoleAnalyzer

Analiza transacciones.

---

## FraudAssessmentEngine

Evalúa:

ROBO

Denuncia

Ingeniería Social

Fraude

Estafa

---

## OperationDecisionEngine

Debe sugerir:

LINK GO

PAGAR

CIRCUITO

OTRA RESOLUCIÓN

---

## ResolutionEngine

Utiliza:

RESOLUCIONES APC

para generar:

Tema

Nota

---

# INTERFAZ OBJETIVO

Tecnología:

CustomTkinter

Modo oscuro

Vista principal:

[ Cargar Caso ]

[ Analizar Smart Console ]

[ Analizar Documentación ]

[ Generar Diario ]

[ Exportar Informe ]

Panel de resultados:

Incidente

Cuenta

Tarjeta

Canal

Operaciones

Resolución

Tema APC

Nota APC

---

# ESTRUCTURA DEL PROYECTO

app/

ui/

core/

knowledge/

documents/

smart_console/

decision_engine/

automation/

data/

logs/

---

# PRÓXIMO DESARROLLO

Implementar:

1. SmartConsoleAnalyzer.

2. DocumentClassifier.

3. ClaimUniverseBuilder.

4. ResolutionEngine.

5. Interfaz Desktop MVP.

No generar todavía integraciones automáticas con APC.
