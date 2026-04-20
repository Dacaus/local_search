# analyze_local.py
# -----------------------------------------
# Analysis script for local search experiment
# Generates visualizations to test local smoothness hypothesis
# -----------------------------------------

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    PROJECT_ROOT,
    BOXPLOT_PNG,
    DISTANCE_RUNTIME_PNG,
    HEATMAP_PNG,
    PLOT_DATA_PATH,
    RESULTS_CSV_PATH,
    SPEEDUP_BAR_PNG,
)

# 与 benchmark 脚本保持一致的输出目录
csv_path = RESULTS_CSV_PATH

# 读取数据
df = pd.read_csv(csv_path)

# 从原始数据中提取每个配置的摘要信息（避免重复绘图时多行干扰）
# 注意：median 和 mean 在原始 CSV 中每行都相同，取第一条即可
summary = df.groupby(["config", "distance"]).agg(
    median_runtime=("median", "first"),
    mean_runtime=("mean", "first"),
    vectorize=("vectorize", "first"),
    reschedule=("reschedule", "first"),
    parallel=("parallel", "first"),
    tile=("tile", "first")
).reset_index()

# 计算相对于 baseline (distance=0) 的加速比
baseline_mask = summary["distance"] == 0
if baseline_mask.any():
    baseline_median = summary.loc[baseline_mask, "median_runtime"].values[0]
else:
    # 如果没有 baseline（不应该发生），取所有配置的最小中位数作为参考
    baseline_median = summary["median_runtime"].min()
summary["speedup"] = baseline_median / summary["median_runtime"]

# 设置绘图风格
sns.set_theme(style="whitegrid")

# ------------------------------------------------------------
# 1. 距离 vs 性能散点图（验证局部平滑性的核心图）
# ------------------------------------------------------------
plt.figure(figsize=(8, 5))
# 用颜色区分向量化状态，用标记区分重调度状态
sns.scatterplot(
    data=summary,
    x="distance",
    y="median_runtime",
    hue="vectorize",
    style="reschedule",
    s=120,
    palette={"off": "blue", "on": "red"}
)
plt.title("Local Smoothness: Distance from Baseline vs Runtime")
plt.xlabel("Hamming Distance from Baseline")
plt.ylabel("Median Runtime (s)")
plt.grid(True, alpha=0.3)

# 添加水平线表示 baseline 性能
plt.axhline(y=baseline_median, color='gray', linestyle='--', alpha=0.7, label=f'Baseline ({baseline_median:.3f}s)')
plt.legend(title="Vectorize / Reschedule")
plt.tight_layout()
scatter_path = DISTANCE_RUNTIME_PNG
plt.savefig(scatter_path, dpi=150)
print(f"✅ Scatter plot saved to {scatter_path}")

# ------------------------------------------------------------
# 2. 加速比条形图（展示各配置相对 baseline 的提升）
# ------------------------------------------------------------
plt.figure(figsize=(12, 5))
# 按加速比降序排列
ordered_summary = summary.sort_values("speedup", ascending=False)
order = ordered_summary["config"].tolist()
colors = ["#2ecc71" if s >= 1.0 else "#e74c3c" for s in ordered_summary["speedup"]]
plt.bar(order, ordered_summary["speedup"], color=colors)
plt.axhline(y=1.0, color='black', linestyle='--', linewidth=1, label='baseline (speedup=1.0)')
plt.xticks(rotation=45, ha='right')
plt.title("Speedup over Baseline Configuration")
plt.ylabel("Speedup (×)")
plt.xlabel("Configuration")
plt.legend()
plt.tight_layout()
bar_path = SPEEDUP_BAR_PNG
plt.savefig(bar_path, dpi=150)
print(f"✅ Speedup bar chart saved to {bar_path}")

# ------------------------------------------------------------
# 3. 箱线图（展示 5 次运行的波动，验证测量稳定性）
# ------------------------------------------------------------
plt.figure(figsize=(12, 5))
# 使用原始数据 df，其中包含每次运行的 runtime
# 按中位数排序以保持与条形图一致
order_configs = summary.sort_values("median_runtime")["config"].tolist()
sns.boxplot(
    data=df,
    x="config",
    y="runtime",
    order=order_configs,
    palette="Set3",
    hue="config",
    legend=False
)
plt.xticks(rotation=45, ha='right')
plt.title("Runtime Distribution Across 5 Runs per Configuration")
plt.ylabel("Runtime (s)")
plt.xlabel("Configuration")
plt.tight_layout()
box_path = BOXPLOT_PNG
plt.savefig(box_path, dpi=150)
print(f"✅ Boxplot saved to {box_path}")

# ------------------------------------------------------------
# 4. 可选：参数影响热力图（向量化 vs 分块大小）
# ------------------------------------------------------------
# 只选取 parallel=off 的子集，因为可能数据不全
subset = summary[(summary["parallel"] == "off")].copy()
if not subset.empty:
    pivot = subset.pivot_table(
        index="vectorize",
        columns="tile",
        values="median_runtime",
        aggfunc="mean",
        dropna=False
    )
    plt.figure(figsize=(6, 4))
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap="YlOrRd_r", cbar_kws={'label': 'Runtime (s)'})
    plt.title("Heatmap: Vectorize × Tile Size (parallel=off)")
    plt.tight_layout()
    heat_path = HEATMAP_PNG
    plt.savefig(heat_path, dpi=150)
    print(f"✅ Heatmap saved to {heat_path}")

print("\n🎉 All analyses complete. Check the output_local/ directory for figures.")

# 散点图数据：每条记录对应一个配置的摘要信息
scatter_data = summary[["config", "distance", "median_runtime", "vectorize", "reschedule"]].to_dict(orient="records")

# 加速比条形图数据：config 和 speedup（按 speedup 降序排列）
bar_data = summary[["config", "speedup"]].sort_values("speedup", ascending=False).to_dict(orient="records")

# 箱线图数据：每个 config 对应的 5 次 runtime 值列表
box_data = df.groupby("config")["runtime"].apply(list).reset_index().to_dict(orient="records")

# 热力图数据：向量化 × tile 的二维矩阵（只保留 parallel=off 的子集）
subset = summary[summary["parallel"] == "off"]
if not subset.empty:
    pivot = subset.pivot_table(index="vectorize", columns="tile", values="median_runtime", aggfunc="mean")
    heatmap_data = {
        "rows": pivot.index.tolist(),
        "columns": pivot.columns.tolist(),
        "values": pivot.values.tolist()
    }
else:
    heatmap_data = None

plot_data = {
    "scatter": scatter_data,
    "bar": bar_data,
    "box": box_data,
    "heatmap": heatmap_data
}

json_path = PLOT_DATA_PATH
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(plot_data, f, indent=2)

print(f"📄 Minimal plot data saved to {json_path}")