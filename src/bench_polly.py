# search_local.py
# -----------------------------------------
# Real Research Prototype:
# Local Search Around Polly Schedules
#
# Usage:
#   python3 search_local.py
#
# Need:
#   clang with Polly enabled
#   matmul.c (prints runtime in seconds)
# -----------------------------------------


import csv
import statistics
import subprocess
import sys
from itertools import product
from pathlib import Path

LOCAL_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(LOCAL_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(LOCAL_PROJECT_ROOT))

from config import PROJECT_ROOT, MATMUL_PATH

OUTPUT_LOCAL_DIR = PROJECT_ROOT / "output_local"
OUTPUT_LOCAL_BIN_DIR = OUTPUT_LOCAL_DIR / "bin"
RESULTS_CSV_PATH = OUTPUT_LOCAL_DIR / "results.csv"

# =====================================
# Baseline config (center point)
# =====================================

BASE = {
    "polly": "on",
    "reschedule": "off",
    "vectorize": "off",
    "parallel": "off",
    "tile": "16"
}

# =====================================
# Neighborhood candidates
# distance = changed flags count
# =====================================

configs = [BASE]

for reschedule, vectorize, parallel, tile in product(
    ["off", "on"],
    ["off", "on"],
    ["off", "on"],
    ["16", "32", "64"],
):
    cfg = {
        "polly": "on",
        "reschedule": reschedule,
        "vectorize": vectorize,
        "parallel": parallel,
        "tile": tile,
    }
    if cfg != BASE:
        configs.append(cfg)

print(f"✅ Generated {len(configs)} benchmark configurations around BASE")

# =====================================
# Helpers
# =====================================

def config_name(cfg):
    return (
        f"rs_{cfg['reschedule']}_"
        f"vec_{cfg['vectorize']}_"
        f"par_{cfg['parallel']}_"
        f"tile_{cfg['tile']}"
    )


def distance_from_base(cfg):
    d = 0
    for k in BASE:
        if cfg[k] != BASE[k]:
            d += 1
    return d


def build_compile_cmd(cfg, exe_path):
    cmd = ["clang", "-O3", str(MATMUL_PATH), "-o", str(exe_path)]

    if cfg["polly"] == "on":
        cmd += ["-mllvm", "-polly"]

    if cfg["reschedule"] == "on":
        cmd += ["-mllvm", "-polly-reschedule"]

    if cfg["vectorize"] == "on":
        cmd += ["-mllvm", "-polly-vectorizer=stripmine"]

    if cfg["parallel"] == "on":
        cmd += ["-mllvm", "-polly-parallel"]
        cmd.append("-fopenmp") # parallel 需要 OpenMP 支持
    if cfg["tile"] != "16":
        cmd += ["-mllvm", f"-polly-tile-sizes={cfg['tile']}"]

    return cmd


def compile_and_run(cfg):
    name = config_name(cfg)
    exe = OUTPUT_LOCAL_BIN_DIR / name

    # compile
    cmd = build_compile_cmd(cfg, exe)
    print("\n🔨 Compiling:", name)
    subprocess.run(cmd, check=True)

    # run 5 times
    print("🏃 Running:", name)

    runs = []
    for _ in range(5):
        out = subprocess.run(
            str(exe),
            capture_output=True,
            text=True,
            check=True
        )
        t = float(out.stdout.strip())
        runs.append(t)

    median = statistics.median(runs)
    mean = statistics.mean(runs)

    return runs, mean, median


# =====================================
# Main experiment
# =====================================

rows = []

for cfg in configs:
    dist = distance_from_base(cfg)

    try:
        runs, mean, median = compile_and_run(cfg)

        for r in runs:
            rows.append({
                "config": config_name(cfg),
                "distance": dist,
                "runtime": r,
                "mean": mean,
                "median": median,
                "reschedule": cfg["reschedule"],
                "vectorize": cfg["vectorize"],
                "parallel": cfg["parallel"],
                "tile": cfg["tile"]
            })

        print(f"   distance={dist}, median={median:.6f}")

    except Exception as e:
        print("❌ Failed:", cfg, e)

# =====================================
# Save CSV
# =====================================

csv_path = RESULTS_CSV_PATH

with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "config",
            "distance",
            "runtime",
            "mean",
            "median",
            "reschedule",
            "vectorize",
            "parallel",
            "tile"
        ]
    )
    writer.writeheader()
    writer.writerows(rows)

print("\n✅ Saved:", csv_path)
print("Next step: analyze_local.py")