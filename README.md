# 尝试探究利用深度学习方法学习程序结构与优化决策之间的映射关系

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
如需增加编译参数（例如 `-march=native`），可直接编辑脚本中的 `configs` 列表。