"""Configuracion central del proyecto APC Reclamos."""

from pathlib import Path


ROOT_DIR: Path = Path(__file__).resolve().parents[1]
PROMPTS_DIR: Path = ROOT_DIR / "prompts"
CORRIDAS_DIR: Path = ROOT_DIR / "corridas"
TEMPLATES_DIR: Path = ROOT_DIR / "templates"
LOGS_DIR: Path = ROOT_DIR / "logs"

OUTPUT_TEMPLATE_PATH: Path = TEMPLATES_DIR / "output_template.json"

DEFAULT_CORRIDA: str = "corrida_1"
DEFAULT_CSV_NAME: str = "csv_diario.csv"
DEFAULT_RESULT_NAME: str = "resultado.json"

SESSION_TIMEOUT_SECONDS: int = 300
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT: str = "%Y-%m-%d"
DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"

APC_SOLAPAS: tuple[str, str, str, str] = (
    "Detalle",
    "Diario",
    "Documentacion",
    "Auditoria",
)

DOCUMENT_EXTENSIONS: tuple[str, ...] = (
    ".txt",
    ".pdf",
    ".xlsx",
    ".xlsm",
    ".csv",
)
