from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_LOCAL_DIR = PROJECT_ROOT / "output_local"
OUTPUT_LOCAL_BIN_DIR = OUTPUT_LOCAL_DIR / "bin"

MATMUL_PATH = OUTPUT_LOCAL_DIR / "matmul.c"
RESULTS_CSV_PATH = OUTPUT_LOCAL_DIR / "results.csv"
PLOT_DATA_PATH = OUTPUT_LOCAL_DIR / "plot_data.json"
DISTANCE_RUNTIME_PNG = OUTPUT_LOCAL_DIR / "distance_vs_runtime.png"
SPEEDUP_BAR_PNG = OUTPUT_LOCAL_DIR / "speedup_bar.png"
BOXPLOT_PNG = OUTPUT_LOCAL_DIR / "boxplot.png"
HEATMAP_PNG = OUTPUT_LOCAL_DIR / "heatmap_vec_tile.png"

OUTPUT_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_LOCAL_BIN_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_TEMPLATE_DIR = PROJECT_ROOT / "prompts" 
analysis_prompt_path = PROMPT_TEMPLATE_DIR / "analysis_prompt.txt"