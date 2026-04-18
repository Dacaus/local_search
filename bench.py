import subprocess
import csv
import os

# 创建输出文件夹
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

configs = [
    ("base", f"clang -O3 matmul.c -o {OUTPUT_DIR}/base"),
    ("p1",   f"clang -O3 -mllvm -polly matmul.c -o {OUTPUT_DIR}/p1"),
    ("p2",   f"clang -O3 -mllvm -polly -mllvm -polly-reschedule matmul.c -o {OUTPUT_DIR}/p2")
]

results = []

for name, compile_cmd in configs:
    print(f"\n🔨 Compiling {name}...")
    subprocess.run(compile_cmd, shell=True, check=True)
    
    print(f"🏃 Running {name}...")
    exe_path = f"{OUTPUT_DIR}/{name}"
    times = []
    for _ in range(5):
        output = subprocess.run(exe_path, capture_output=True, text=True, shell=True)
        runtime = float(output.stdout.strip())
        times.append(runtime)
    median = sorted(times)[2]
    results.append((name, median))
    print(f"   median runtime: {median:.4f} s")

# 保存 CSV 到 output 文件夹
csv_path = f"{OUTPUT_DIR}/results.csv"
with open(csv_path, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["config", "runtime_seconds"])
    writer.writerows(results)

print(f"\n✅ Results saved to {csv_path}")