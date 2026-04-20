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

import subprocess
import csv
import os
import statistics

OUTPUT_DIR = "output_local"
BIN_DIR = f"{OUTPUT_DIR}/bin"

os.makedirs(BIN_DIR, exist_ok=True)

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

configs = [
    BASE,

    # distance = 1
    {"polly":"on","reschedule":"on","vectorize":"off","parallel":"off","tile":"16"},
    {"polly":"on","reschedule":"off","vectorize":"on","parallel":"off","tile":"16"},
    {"polly":"on","reschedule":"off","vectorize":"off","parallel":"on","tile":"16"},
    {"polly":"on","reschedule":"off","vectorize":"off","parallel":"off","tile":"32"},
    {"polly":"on","reschedule":"off","vectorize":"off","parallel":"off","tile":"64"},

    # distance = 2
    {"polly":"on","reschedule":"on","vectorize":"on","parallel":"off","tile":"16"},
    {"polly":"on","reschedule":"on","vectorize":"off","parallel":"on","tile":"16"},
    {"polly":"on","reschedule":"on","vectorize":"off","parallel":"off","tile":"32"},
    {"polly":"on","reschedule":"off","vectorize":"on","parallel":"on","tile":"16"},
    {"polly":"on","reschedule":"off","vectorize":"on","parallel":"off","tile":"32"},
]

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
    cmd = ["clang", "-O3", "matmul.c", "-o", exe_path]

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
    exe = f"{BIN_DIR}/{name}"

    # compile
    cmd = build_compile_cmd(cfg, exe)
    print("\n🔨 Compiling:", name)
    subprocess.run(cmd, check=True)

    # run 5 times
    print("🏃 Running:", name)

    runs = []
    for _ in range(5):
        out = subprocess.run(
            exe,
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

csv_path = f"{OUTPUT_DIR}/results.csv"

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