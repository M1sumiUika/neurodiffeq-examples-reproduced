# 从 solve 迁移到 Solver

主项目使用 NeuroDiffEq 发行包0.7.0的 `Solver1D`、`Solver2D`。0.7.0仍保留旧函数，因此无需降级主环境。仅 `legacy_internals` 为教学目的实际调用废弃的 `solve_system`，警告保存到文件；它没有被静默屏蔽成“无问题”。

|旧用法|推荐用法|
|---|---|
|`solve(ode=f, condition=ivp, ...)`|`Solver1D(ode_system=lambda u,t:[f(u,t)], conditions=[ivp], ...)`|
|`solve_system(ode_system=f, conditions=cs, ...)`|`Solver1D(f, cs, ...)`|
|`solve2D` / `solve2D_system`|`Solver2D(pde_system=f, conditions=[...], ...)`|
|`net=net`（单方程）|`nets=[net]`|
|`criterion=L1Loss()`|`loss_fn=L1Loss()`|
|`max_epochs` 在构造调用内|`solver.fit(max_epochs=...)`|
|`monitor=monitor`|`solver.fit(..., callbacks=[monitor.to_callback()])`|
|返回 `(solution, loss)`|`solver.get_solution()` 和 `solver.metrics_history`|
|`return_internal=True`|`solver.get_internals()`|
|`return_best=False`（旧默认）|`solver.get_solution(best=False)`；新默认 best=True|

一个可独立理解的最小迁移：

```python
import numpy as np
from neurodiffeq import diff
from neurodiffeq.conditions import IVP
from neurodiffeq.solvers import Solver1D
from neurodiffeq.utils import set_tensor_type

set_tensor_type(device="cpu", float_bits=64)
solver = Solver1D(lambda u, t: [diff(u, t) + u],
                  [IVP(t_0=0, u_0=1)], t_min=0, t_max=2)
solver.fit(max_epochs=1000)
solution = solver.get_solution(best=False)
print(solution(np.array([0., 1., 2.]), to_numpy=True))
```

完整数值验收请运行 `python -m ndeq_examples run --example decay --mode reproduction`。上面只帮助理解接口，不代替统一实验入口。

注意三个容易出错的点：

1. 新求解器需要“残差列表”，即使只有一个方程。未知量、条件、网络的顺序必须相同。
2. 自定义优化器必须绑定传入求解器的那些网络。单独建立 Adam 却不传 `optimizer=`，并不会改变 Solver 的默认优化器。
3. `get_solution(best=True)` 取验证损失最小的模型，并不等于最后一轮。对旧函数的迁移配置保留其 `best=False` 行为。历史损失来自每轮训练，最终测试来自配置指定的权重。

API参考中的重复片段被合并为 `api_solution`，使用原来的指数衰减和Laplace问题演示单/多坐标，不因此增加新的球面求解实验。它只检查接口，不作新的数值精度结论。

0.7.0 的旧 `solve_system` 仍要求提供 `t_min` 和 `t_max` 位置/关键字参数，即使提供了训练与验证生成器。项目第一次 smoke 捕获了遗漏，修复后重跑，原始失败记录保留在运行历史中。

GPU 可选：命令加 `--device cuda`。安装相应官方 CUDA wheel；不要把CPU训练时间与GPU训练时间混为一谈。当前精选结果在 CPU、float64、单PyTorch线程下运行。`CustomBoundaryCondition` 的内部插值与设备兼容性只以实际执行为准，GPU未列入已验证范围。

