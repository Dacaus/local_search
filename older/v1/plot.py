import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os

OUTPUT_DIR = "output"
csv_path = f"{OUTPUT_DIR}/results.csv"

df = pd.read_csv(csv_path)

# 条形图
plt.figure(figsize=(6, 4))
sns.barplot(data=df, x="config", y="runtime_seconds", hue="config", palette="viridis", legend=False)
plt.title("Matrix Multiplication Runtime (N=1024)")
plt.ylabel("Time (seconds)")
bar_path = f"{OUTPUT_DIR}/runtime_plot.png"
plt.savefig(bar_path, dpi=150)
print(f"✅ 条状图已经保存到 {bar_path}")

# # 热图
# pivot = df.set_index("config").T
# plt.figure()
# sns.heatmap(pivot, annot=True, fmt=".3f", cmap="YlOrRd")
# plt.title("Runtime Heatmap")
# heat_path = f"{OUTPUT_DIR}/heatmap.png"
# plt.savefig(heat_path)
# print(f"✅ 热力图已经保存到 {heat_path}")