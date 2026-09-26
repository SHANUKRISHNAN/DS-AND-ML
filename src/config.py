from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DATA = ROOT / "data" / "raw" / "EcoTwin_dataset_raw.csv"
PROCESSED_DATA = ROOT / "data" / "processed" / "EcoTwin_clean.csv"
FEATURE_DATA = ROOT / "data" / "processed" / "EcoTwin_features.csv"
FIGURES = ROOT / "outputs" / "figures"
REPORTS = ROOT / "outputs" / "reports"
MODELS = ROOT / "models"

for folder in [FIGURES, REPORTS, MODELS, PROCESSED_DATA.parent]:
    folder.mkdir(parents=True, exist_ok=True)
