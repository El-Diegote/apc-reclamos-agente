# APC Reclamos Agente

Proyecto Python para procesar y analizar reclamos de una plataforma bancaria APC. El agente simula la busqueda de incidentes, la lectura de solapas operativas, la descarga/logica de documentacion y la generacion de una salida JSON estructurada para auditoria o revision posterior.

## Caso de uso

El caso de uso principal es asistir a un equipo de operaciones, back office o auditoria bancaria en el analisis inicial de reclamos. A partir de un numero de incidente ingresado manualmente o disponible en un CSV diario, el agente:

- Simula la lectura de las cuatro solapas APC: Detalle, Diario, Documentacion y Auditoria.
- Revisa documentos descargados en la carpeta de la corrida.
- Valida tres requisitos previos configurados como reglas de negocio.
- Extrae datos criticos: fecha, hora, importe, numero de cuenta y motivo.
- Genera un archivo `resultado.json` en la carpeta de salida de la corrida.

## Requisitos previos

- Python 3.10 o superior.
- Entorno virtual recomendado.
- Dependencias instaladas desde `requirements.txt` si se desea leer PDF o Excel.

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

## Como ejecutar

Ejecutar una corrida de ejemplo:

```bash
python main.py
```

Ejecutar con un incidente especifico:

```bash
python main.py --incidente INC-2026-0001 --corrida corrida_1
```

La salida se guarda en:

```text
corridas/corrida_1/salida/resultado.json
```

## Ejemplo de entrada

Archivo `corridas/corrida_1/entrada/csv_diario.csv`:

```csv
numero_incidente,fecha,hora,importe,numero_cuenta,motivo
INC-2026-0001,2026-09-06,10:15,12500.50,001234567890,Desconocimiento de consumo
```

## Ejemplo de salida

```json
{
  "numero_incidente": "INC-2026-0001",
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
│   ├── extractor.py
│   └── utils.py
├── config/
│   └── config.py
└── templates/
    └── output_template.json
```

## Notas de seguridad

El proyecto no almacena credenciales. Los datos reales, PDFs sensibles, logs y archivos `.env` deben mantenerse fuera del repositorio.
