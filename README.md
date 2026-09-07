# APC Reclamos Agente

Proyecto Python para asistir a analistas APC en la gestion de reclamos y consultas vinculados a operaciones ATM, POS, mPOS, BNA+, MODO, Cash In, eCommerce y otros canales. El MVP combina una aplicacion desktop en CustomTkinter, un motor APC en Python, persistencia SQLite y exportacion de informes.

## Caso de uso

El caso de uso principal es asistir a un equipo de operaciones, back office o auditoria bancaria en el analisis inicial de reclamos. A partir de una base de reclamos o de un caso ingresado manualmente, la aplicacion:

- Carga Base de Reclamos desde CSV o Excel.
- Entrena resoluciones APC reutilizables.
- Analiza casos por canal, motivo, importe y cuenta.
- Genera una resolucion sugerida.
- Genera texto sugerido para Diario.
- Exporta un informe JSON.

Toda resolucion debe ser revisada y aprobada por un analista humano antes de publicarse.

## Alcance MVP

Incluido:

- Aplicacion desktop con CustomTkinter.
- Backend Python modular.
- Carga de CSV/XLSX con Pandas y OpenPyXL.
- Persistencia local SQLite.
- Motor de sugerencias por resoluciones entrenadas y reglas base.
- Modo CLI para corrida simulada.

No incluido:

- Modificacion de informacion en APC.
- Acciones automaticas sin validacion humana.
- Almacenamiento de credenciales.
- Web scraping real con Playwright o Selenium.

## Requisitos previos

- Python 3.11 recomendado.
- Entorno virtual recomendado.
- Dependencias instaladas desde `requirements.txt`.

Las librerias estandar como `json`, `logging`, `pathlib`, `csv`, `re` y `datetime` no requieren instalacion adicional.

## Instalacion

```bash
cd apc-reclamos-agente
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

En macOS o Linux:

```bash
source .venv/bin/activate
```

## Como ejecutar la app desktop

```bash
python main.py
```

Si falta CustomTkinter o Pandas:

```bash
pip install -r requirements.txt
```

## Como ejecutar modo CLI

Ejecutar una corrida de ejemplo:

```bash
python main.py --cli
```

Ejecutar con un incidente especifico:

```bash
python main.py --cli --incidente INC-2026-0001 --corrida corrida_1
```

La salida se guarda en:

```text
corridas/corrida_1/salida/resultado.json
```

## Ejemplo de entrada

Archivo `corridas/corrida_1/entrada/csv_diario.csv`:

```csv
numero_incidente,canal,fecha,hora,importe,numero_cuenta,motivo
INC-2026-0001,ATM,2026-09-06,10:15,12500.50,001234567890,Desconocimiento de consumo
```

Para cargar una base desde la app desktop, el archivo puede incluir columnas como:

```csv
numero_incidente,canal,fecha,hora,importe,numero_cuenta,motivo
INC-2026-0001,ATM,2026-09-06,10:15,12500.50,001234567890,Desconocimiento de consumo
```

## Ejemplo de salida

```json
{
  "numero_incidente": "INC-2026-0001",
  "canal": "ATM",
  "estado": "analizado",
  "validaciones": {
    "requisito_1": true,
    "requisito_2": true,
    "requisito_3": true,
    "resultado_general": true
  },
  "datos_criticos": {
    "fecha": "2026-09-06",
    "hora": "10:15",
    "importe": 12500.5,
    "numero_cuenta": "001234567890",
    "motivo": "Desconocimiento de consumo"
  }
}
```

## Estructura del repo

```text
apc-reclamos-agente/
├── README.md
├── .gitignore
├── DECISIONES.md
├── main.py
├── requirements.txt
├── data/
├── exports/
├── prompts/
│   ├── system_prompt.md
│   └── user_prompt.md
├── corridas/
│   ├── corrida_1/
│   │   ├── entrada/
│   │   │   ├── csv_diario.csv
│   │   │   └── screenshots/
│   │   ├── documentos/
│   │   └── salida/
│   │       └── resultado.json
│   ├── corrida_2/
│   └── corrida_3/
├── src/
│   ├── __init__.py
│   ├── agente.py
│   ├── analizador.py
│   ├── app_desktop.py
│   ├── database.py
│   ├── extractor.py
│   ├── motor_apc.py
│   └── utils.py
├── config/
│   └── config.py
└── templates/
    └── output_template.json
```

## Notas de seguridad

El proyecto no almacena credenciales. Los datos reales, PDFs sensibles, logs y archivos `.env` deben mantenerse fuera del repositorio.

## Futuro

- Integracion Playwright para lectura asistida de APC.
- Lectura de PDFs reales con reglas documentadas.
- Base vectorial ChromaDB para resoluciones historicas.
- Integracion con APIs de analisis inteligente, manteniendo revision humana obligatoria.
