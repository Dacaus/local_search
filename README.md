# 尝试探究利用深度学习方法学习程序结构与优化决策之间的映射关系

## 最终 ideal 流程
1. 由 Polly 给一个给定的调度 $\phi$
2. 生成一个随机扰动 $\Delta$，生成新的调度 $\phi'$，$\phi' = \phi + \Delta$
3. 检查合法性
4. 过滤掉不合法的调度
5. 测试性能
6. 观察局部领域是否平滑
   - gradient-free search
   - Bayesian optimization
   - RL warm start
   - MCTS

## 当前状态
### 理论研究与模拟环境
- 使用 Python 建立二维 loop iteration space
- 使用矩阵表示调度变换：$\theta(i,j)=\Theta[i,j]^T$
- 枚举局部调度矩阵
- 实现合法性检查
- 构建局部性代理得分
- 绘制调度景观热力图

### 实证研究：Polly 优化空间自动基准测试（新增）
为了将理论验证落地到真实编译器与硬件，本项目搭建了面向 Polly 的自动基准测试框架：

- **多参数配置搜索**：不再局限于 `-polly` 开关，而是系统探索 Polly 的多个优化维度：
  - `-polly` on/off
  - `-polly-reschedule` on/off
  - 向量化（`-polly-vectorizer`）on/off
  - 并行化（`-polly-parallel`）on/off
  - 分块大小（tile size）：16 / 32 / 64
- **自动化实验流程**（`bench.py`）：
  - 自动生成 20+ 种编译配置组合
  - 每种配置编译一次，运行 5 次并记录全部原始耗时
  - 输出结构化 CSV 数据（`output/results_detailed.csv`）
- **结果可视化**（`plot.py`）：
  - 以 `-O3`（无 Polly）为基线计算各配置的加速比条形图
  - 绘制箱线图展示运行时波动，验证测量可靠性
  - 生成热力图展示部分参数切片下的性能景观

### 初步观察（基于 1024×1024 双精度矩阵乘法）
- Polly 默认调度较纯 `-O3` 可获得约 1.2× 加速
- 结合 reschedule 与显式 tiling 后，加速比可达 1.5× 以上
- 多次运行的中位数非常稳定，表明测量数据适合后续建模

## 尝试验证（进行中）
1. ✅ 邻近合法调度是否具有相近性能？  
   *已在模拟环境中观察到局部平滑性；真实调度空间的平滑性分析正在进行。*
2. ⏳ 调度空间是否呈现连续结构，而非完全随机黑盒？  
   *通过热力图初步观察到 tile size 与 Polly 标志之间存在结构化趋势。*
3. ⏳ 是否存在低维流形结构，可供学习模型逼近？  
   *计划在收集更多真实性能数据后，使用降维与代理模型进行分析。*

## 下一步
- ✅ 接入真实测试：matmul（已完成基本框架）
- ⬜ 扩展至更多 kernel：jacobi / stencil / 2D convolution
- ⬜ 将调度评分从代理得分切换为实测运行时间
- ⬜ 在真实性能景观上实现一个简单的局部搜索算法，验证“邻近调度平滑性”
- ⬜ 若平滑性成立，则进一步引入贝叶斯优化或简单神经网络作为调度性能预测器

---

## 本仓库文件说明

| 文件 | 作用 |
|------|------|
| `matmul.c` | 固定规模（N=1024）的矩阵乘法基准程序，输出纯数字运行时间（秒） |
| `bench.py` | 自动生成 Polly 参数组合、编译、多次运行并记录详细 CSV |
| `plot.py` | 读取 CSV 生成加速比条形图、箱线图和热力图 |
| `output/` | 所有编译产物、原始数据与图片的存放目录 |

### 运行方式
```bash
# 1. 运行基准测试（需安装 clang 并确保 Polly 可用）
python bench.py

# 2. 生成可视化图表
python plot.py
```

<!-- # 尝试探究利用深度学习方法学习程序结构与优化决策之间的映射关系

## 最终ideal流程
1. 由polly给一个给定的调度 $\phi$
2. 生成一个随机扰动 $\Delta$，生成新的调度 $\phi '$ , $\phi ' = \phi + \Delta$
3. 检查合法性
4. 过滤掉不合法的调度
5. 测试性能
6. 观察局部领域是否平滑
    * gradient-free search
    * Bayesian optimization
    * RL warm start
    * MCTS

## 当前状态
* 使用 Python 建立二维 loop iteration space
* 使用矩阵表示调度变换： $θ(i,j)=Θ[i,j]^T$
* 枚举局部调度矩阵
* 实现合法性检查
* 构建局部性代理得分
* 绘制调度景观热力图

## 尝试验证

1. 邻近合法调度是否具有相近性能？

2. 调度空间是否呈现连续结构，而非完全随机黑盒？

3. 是否存在低维流形结构，可供学习模型逼近？


## 下一步
* 接入真实测试： matmul jacobi stencil
* 使用 clang + Polly 获取真实调度
* 测量真实运行时间
* 将评分标准替换为真实性能


# 尝试探究利用深度学习方法学习程序结构与优化决策之间的映射关系

## 最终 ideal 流程
1. 由 Polly 给一个给定的调度 $\phi$
2. 生成一个随机扰动 $\Delta$，生成新的调度 $\phi'$，$\phi' = \phi + \Delta$
3. 检查合法性
4. 过滤掉不合法的调度
5. 测试性能
6. 观察局部领域是否平滑
   - gradient-free search
   - Bayesian optimization
   - RL warm start
   - MCTS

## 当前状态
- 使用 Python 建立二维 loop iteration space
- 使用矩阵表示调度变换：$\theta(i,j)=\Theta[i,j]^T$
- 枚举局部调度矩阵
- 实现合法性检查
- 构建局部性代理得分
- 绘制调度景观热力图

## 尝试验证
1. 邻近合法调度是否具有相近性能？
2. 调度空间是否呈现连续结构，而非完全随机黑盒？
3. 是否存在低维流形结构，可供学习模型逼近？

## 下一步
- 接入真实测试：matmul / jacobi / stencil
- 使用 clang + Polly 获取真实调度
- 测量真实运行时间
- 将评分标准替换为真实性能

---

## 本仓库新增：matmul + Polly 编译/测量脚本（用于“真实测试”）

为了将“代理得分”逐步替换为真实性能测量，目前仓库包含一个简单的 `matmul.c` 基准程序，以及一个 Python 脚本用于在不同 Polly 配置下编译、运行并记录耗时。

### 文件说明
- `matmul.c`  
  - `N=1024`、`double` 矩阵乘（naive 三重循环）
  - 程序会输出一次运行的耗时（秒，纯数字），便于脚本解析

- `benchmark.py`（如果你的脚本文件名不是这个，请按实际名称替换）  
  - 自动创建 `output/`
  - 编译三种配置：`base` / `p1` / `p2`
  - 每种配置运行 5 次，取中位数（median）
  - 输出 `output/results.csv`

### 依赖
- Python 3
- `clang`
- LLVM Polly（能识别 `-mllvm -polly` 等参数）

### 运行方式
```bash
python3 benchmark.py
```

运行后产物：
- `output/base`, `output/p1`, `output/p2`
- `output/results.csv`

`results.csv` 格式：
```csv
config,runtime_seconds
base,0.123456
p1,0.101234
p2,0.098765
```

### 可配置项（可选）
如需增加编译参数（例如 `-march=native`），可直接编辑脚本中的 `configs` 列表。 -->