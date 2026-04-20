#!/usr/bin/env python3
"""
使用 DeepSeek API 分析 Polly 调度实验数据（plot_data.json）
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI  # DeepSeek API 兼容 OpenAI SDK

# ---------- 路径配置 ----------
LOCAL_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(LOCAL_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(LOCAL_PROJECT_ROOT))

from config import PLOT_DATA_PATH, PROJECT_ROOT
from config import OUTPUT_LOCAL_DIR

# 显式从项目根目录加载 .env
load_dotenv(PROJECT_ROOT / ".env")

DATA_FILE = PLOT_DATA_PATH
PROMPT_DEBUG_FILE = OUTPUT_LOCAL_DIR / "analysis_prompt.txt"

OUTPUT_LOCAL_DIR.mkdir(parents=True, exist_ok=True)

# ---------- API 配置 ----------
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("请在 .env 文件中设置 DEEPSEEK_API_KEY")

# 初始化 DeepSeek 客户端（使用 OpenAI 兼容接口）
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1",  # DeepSeek 官方 endpoint
)

# ---------- 读取 JSON 数据 ----------
def load_experiment_data(json_path: Path) -> dict:
    if not json_path.exists():
        raise FileNotFoundError(
            f"未找到实验数据文件: {json_path}。请先运行 `python3 ./src/analyze_locality.py` 生成 plot_data.json。"
        )
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# ---------- 构造分析提示词 ----------
def build_prompt(data: dict) -> str:
    # 提取关键信息，避免超出上下文长度
    scatter = data.get("scatter", [])[:20]      # 只取前20条
    bar = data.get("bar", [])[:20]
    heatmap = data.get("heatmap", {})
    box_preview = data.get("box", [])[:3]       # 箱线图数据量较大，只取前3个配置预览

    prompt = f"""
你是一个编译器优化与性能分析专家。以下是针对矩阵乘法（1024×1024）在不同 Polly 调度配置下的性能测试结果。
你是系统优化研究员。




数据说明：
- rs: reschedule (on/off)
- vec: vectorize (on/off)
- par: parallel (on/off)
- tile: 分块大小 (16/32/64)
- median_runtime: 多次运行的中位耗时（秒）
- speedup: 相对于 baseline (rs_off_vec_off_par_off_tile_16) 的加速比

我提出假设：

“编译优化空间不是随机黑箱，而具有局部平滑性和可预测结构。”

请根据实验数据判断：

1. 数据支持程度（强/中/弱）
2. 支持证据有哪些
3. 反例有哪些
4. 还缺什么实验才能发表论文
5. 如何设计统计检验验证该假设

实验数据：
- 散点/距离数据（配置，距离，中位耗时）：
{json.dumps(scatter, indent=2)}

- 加速比排行（部分）：
{json.dumps(bar, indent=2)}

- 热力图矩阵（vectorize vs tile size，中位耗时）：
{json.dumps(heatmap, indent=2)}

- 箱线图样例（前3个配置的原始运行时间序列）：
{json.dumps(box_preview, indent=2)}

请用中文回答，重点突出，避免冗长。
"""
    return prompt

# ---------- 调用 DeepSeek API ----------
def analyze_with_deepseek(prompt: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",  # 或者 "deepseek-reasoner" 如果需要深度推理
        messages=[
            {"role": "system", "content": "你是一个性能分析和编译器优化专家。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,   # 较低温度使输出更确定
        max_tokens=2000,
    )
    return response.choices[0].message.content

# ---------- 主函数 ----------
def main():
    print("正在加载实验数据...")
    data = load_experiment_data(DATA_FILE)
    
    print("正在构造分析提示词...")
    prompt = build_prompt(data)
    
    # 可选：将提示词保存到文件，便于调试
    PROMPT_DEBUG_FILE.write_text(prompt, encoding="utf-8")
    
    print("正在调用 DeepSeek API，请稍候...")
    analysis = analyze_with_deepseek(prompt)
    
    # 输出到控制台
    print("\n" + "="*60)
    print("DeepSeek 分析结果")
    print("="*60)
    print(analysis)
    
    # 保存结果到文件
    output_file = OUTPUT_LOCAL_DIR / "analysis_result.txt"
    output_file.write_text(analysis, encoding="utf-8")
    print(f"\n分析结果已保存至：{output_file}")

if __name__ == "__main__":
    main()