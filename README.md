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