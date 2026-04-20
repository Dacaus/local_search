# import subprocess
# import csv
# import os

# # 创建输出文件夹
# OUTPUT_DIR = "output"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# COMPILED_DIR = f"{OUTPUT_DIR}/compiled"
# os.makedirs(COMPILED_DIR, exist_ok=True)

# configs = [
#     ("base", f"clang -O3 matmul.c -o {COMPILED_DIR}/base"),
#     ("p1",   f"clang -O3 -mllvm -polly matmul.c -o {COMPILED_DIR}/p1"),
#     ("p2",   f"clang -O3 -mllvm -polly -mllvm -polly-reschedule matmul.c -o {COMPILED_DIR}/p2")
# ]

# results = []

# for name, compile_cmd in configs:
#     print(f"\n🔨 Compiling {name}...")
#     subprocess.run(compile_cmd, shell=True, check=True)
    
#     print(f"🏃 Running {name}...")
#     exe_path = f"{COMPILED_DIR}/{name}"
#     times = []
#     for _ in range(5):
#         output = subprocess.run(exe_path, capture_output=True, text=True, shell=True)
#         runtime = float(output.stdout.strip())
#         times.append(runtime)
#     median = sorted(times)[2]
#     results.append((name, median))
#     print(f"   median runtime: {median:.4f} s")

# # 保存 CSV 到 output 文件夹
# csv_path = f"{OUTPUT_DIR}/results.csv"
# with open(csv_path, "w") as f:
#     writer = csv.writer(f)
#     writer.writerow(["config", "runtime_seconds"])
#     writer.writerows(results)

# print(f"\n✅ Results saved to {csv_path}")

import subprocess
import csv
import os
import itertools

OUTPUT_DIR = "output"
COMPILED_DIR = f"{OUTPUT_DIR}/compiled"
os.makedirs(COMPILED_DIR, exist_ok=True)

# 定义可搜索的参数空间
param_grid = {
    "polly": ["off", "on"],
    "reschedule": ["off", "on"],
    "vectorize": ["off", "on"],
    "parallel": ["off", "on"],
    "tile_size": ["16", "32", "64"]      # 仅当 polly=on 时使用
}

# 生成所有有效组合
configs = []
for polly, resch, vec, par, tile in itertools.product(
    param_grid["polly"],
    param_grid["reschedule"],
    param_grid["vectorize"],
    param_grid["parallel"],
    param_grid["tile_size"]
):
    # 跳过无意义的组合：polly=off 时 tile/reschedule 无效，统一设成 off
    if polly == "off":
        resch = "off"
        tile = "16"
        vec = "off"
        par = "off"
    
    name = f"poly_{polly}_rs_{resch}_vec_{vec}_par_{par}_tile_{tile}"
    exe_path = f"{COMPILED_DIR}/{name}"
    
    # 构建编译命令
    cmd_parts = ["clang", "-O3", "matmul.c", "-o", exe_path]
    if polly == "on":
        cmd_parts.extend(["-mllvm", "-polly"])
    if resch == "on":
        cmd_parts.extend(["-mllvm", "-polly-reschedule"])
    if vec == "on":
        cmd_parts.extend(["-mllvm", "-polly-vectorizer=stripmine"])
    if par == "on":
        cmd_parts.extend(["-mllvm", "-polly-parallel"])
    if polly == "on" and tile != "16":      # 16 是默认，不必显式指定
        cmd_parts.extend(["-mllvm", f"-polly-tile-sizes={tile}"])
    
    compile_cmd = " ".join(cmd_parts)
    
    configs.append({
        "name": name,
        "compile_cmd": compile_cmd,
        "polly": polly,
        "reschedule": resch,
        "vectorize": vec,
        "parallel": par,
        "tile_size": tile
    })

print(f"Generated {len(configs)} configurations.")

results = []
for cfg in configs:
    name = cfg["name"]
    print(f"\n🔨 Compiling {name}...")
    subprocess.run(cfg["compile_cmd"], shell=True, check=True)
    
    print(f"🏃 Running {name}...")
    exe_path = f"{COMPILED_DIR}/{name}"
    times = []
    for _ in range(5):
        output = subprocess.run(exe_path, capture_output=True, text=True, shell=True)
        runtime = float(output.stdout.strip())
        times.append(runtime)
    
    # 记录每一条原始数据（便于后续画箱线图）
    for t in times:
        results.append({
            "config": name,
            "polly": cfg["polly"],
            "reschedule": cfg["reschedule"],
            "vectorize": cfg["vectorize"],
            "parallel": cfg["parallel"],
            "tile_size": cfg["tile_size"],
            "runtime": t
        })
    median = sorted(times)[2]
    print(f"   median runtime: {median:.4f} s")

# 保存详细 CSV
csv_path = f"{OUTPUT_DIR}/results_detailed.csv"
with open(csv_path, "w", newline='') as f:
    fieldnames = ["config", "polly", "reschedule", "vectorize", "parallel", "tile_size", "runtime"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ Detailed results saved to {csv_path}")