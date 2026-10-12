# 覆盖清单

基准：2023-04-03 PDF，共138页。以下页码为PDF页面，不是印刷页码。主入口相同问题共享实现；单元格清单在本页后半部分。状态由实际结果生成。

|章节|示例|实现文件|验证方法|完成状态|
|---|---|---|---|---|
|2.1.1 (PDF 13,14,15)|decay: 指数衰减（Solver 迁移）|[入口](../examples/chapter2/decay.py)|独立测试残差、条件及解析解|完整训练已运行；数值验证通过|
|2.1.1 [6]-[7] (PDF 15)|decay_monitor: 指数衰减与 Monitor1D 回调|[入口](../examples/chapter2/decay_monitor.py)|独立测试残差、条件及解析解|完整训练已运行；数值验证通过|
|2.1.2 (PDF 16)|oscillator: 二阶简谐振子|[入口](../examples/chapter2/oscillator.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|2.2.1 (PDF 17,18)|circle: 一阶振子方程组|[入口](../examples/chapter2/circle.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|1.4.1; 2.2.2 (PDF 7,8,9,10,19)|lotka: Lotka–Volterra|[入口](../examples/chapter2/lotka.py)|DOP853双容差数值参考、残差、初值、不变量|完整训练已运行；数值验证通过|
|2.2.3 (PDF 20,21)|migration: LV 的旧接口到 Solver 迁移（显式前置训练）|[入口](../examples/chapter2/migration.py)|DOP853双容差数值参考、残差、初值、不变量|完整训练已运行；数值验证通过|
|1.4.2 (PDF 10,11)|poisson: 二维 Poisson（补全代码）|[入口](../examples/chapter1/poisson.py)|独立测试残差、条件及解析解|完整训练已运行；数值验证通过|
|2.3.1 (PDF 21,22,23,24)|laplace: 二维 Laplace|[入口](../examples/chapter2/laplace.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|2.3.2 (PDF 24,25,26)|heat: 热传导：L=2、非齐次 Neumann、GIF|[入口](../examples/chapter2/heat.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|2.4 (PDF 26,27,28,29)|star: 星形区域非线性 PDE|[入口](../examples/chapter2/star.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|3.1;3.1.1 (PDF 31,32)|solver_config: 振子求解器配置|[入口](../examples/chapter3/solver_config.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|3.1.2 (PDF 32,33)|network: 16x16x16 Tanh 网络|[入口](../examples/chapter3/network.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|3.1.2 (PDF 32)|activations: 网络与 Tanh/Sigmoid/Sin/Swish 激活|[入口](../examples/chapter3/activations.py)|可执行断言及输出|片段已运行，断言通过（不适用完整训练）|
|3.1.3 (PDF 33,34)|sampling: 训练64点均匀采样/验证128点等距|[入口](../examples/chapter3/sampling.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|3.1.4 (PDF 34,35)|optimizer: SGD + momentum=0.99|[入口](../examples/chapter3/optimizer.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|3.1.5 (PDF 35)|loss: L1 自定义损失|[入口](../examples/chapter3/loss.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|3.2.1 (PDF 36,37)|legacy_internals: 旧 solve_system 内部信息|[入口](../examples/chapter3/legacy_internals.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|3.2.2 (PDF 37,38)|internals: Solver 内部信息|[入口](../examples/chapter3/internals.py)|独立测试残差、条件及解析解|完整训练已运行；未达到数值目标|
|4.4 (PDF 61,65,68,72,75,79)|api_solution: 六处 get_solution 调用短片段|[入口](../examples/chapter4/api_solution.py)|可执行断言及输出|片段已运行，断言通过（不适用完整训练）|
|4.11 (PDF 108)|api_mesh: MeshGenerator 嵌套与 ^ 运算符|[入口](../examples/chapter4/api_mesh.py)|可执行断言及输出|片段已运行，断言通过（不适用完整训练）|
|4.13 (PDF 114,117,122)|api_callbacks: And/Not/Or/Xor 回调组合|[入口](../examples/chapter4/api_callbacks.py)|可执行断言及输出|片段已运行，断言通过（不适用完整训练）|
|5.1 (PDF 125)|residual_demo: 残差为零不意味着满足初值|[入口](../examples/chapter5/residual_demo.py)|可执行断言及输出|片段已运行，断言通过（不适用完整训练）|
|5.2 (PDF 126)|hard_constraint: 初值硬约束及导数约束|[入口](../examples/chapter5/hard_constraint.py)|可执行断言及输出|片段已运行，断言通过（不适用完整训练）|
|5.3 (PDF 126,127)|autodiff: 自动微分一阶与二阶导数|[入口](../examples/chapter5/autodiff.py)|可执行断言及输出|片段已运行，断言通过（不适用完整训练）|
|项目新增；对应5.2原理 (PDF 126)|hard_soft: 新增：硬约束与初值惩罚项对照|[入口](../examples/chapter5/hard_soft.py)|独立测试残差、条件及解析解|完整训练已运行；数值验证通过|

## Notebook 单元格逐条映射

导入和绘图单元也列出；同一单元跨页或重复的输出编号不重复计数。空单元、HTML显示对象不是可执行示例。原文没有[33]，不能凭空补成一项。

|章节/单元|内容|共享实现/独立配置|状态|
|---|---|---|---|
|2章 [1]|导入与Notebook绘图后端|`decay`|完整训练已运行；数值验证通过|
|2章 [2]|diff/solve/IVP导入|`decay`|完整训练已运行；数值验证通过|
|2章 [3]|指数方程、初值、求解|`decay`|完整训练已运行；数值验证通过|
|2章 [4]|解析解比较曲线|`decay`|完整训练已运行；数值验证通过|
|2章 [5]|训练/验证损失图|`decay`|完整训练已运行；数值验证通过|
|2章 [6]|Monitor1D导入|`decay_monitor`|完整训练已运行；数值验证通过|
|2章 [7]|附加Monitor的指数求解|`decay_monitor`|完整训练已运行；数值验证通过|
|2章 [8]|二阶残差和初始导数|`oscillator`|完整训练已运行；未达到数值目标|
|2章 [9]|3000轮和监视器|`oscillator`|完整训练已运行；未达到数值目标|
|2章 [10]|振子解曲线|`oscillator`|完整训练已运行；未达到数值目标|
|2章 [11]|solve_system导入|`circle`|完整训练已运行；未达到数值目标|
|2章 [12]|一阶方程组及5000轮训练|`circle`|完整训练已运行；未达到数值目标|
|2章 [13]|两分量解析曲线|`circle`|完整训练已运行；未达到数值目标|
|2章 [14]|FCNN/SinActv导入|`lotka`|完整训练已运行；数值验证通过|
|2章 [15]|LV及sin网络|`lotka`|完整训练已运行；数值验证通过|
|2章 [16]|Solver迁移、t_min=.1、复用权重|`migration`|完整训练已运行；数值验证通过|
|2章 [17]|数值对照与误差图|`migration`|完整训练已运行；数值验证通过|
|2章 [18]|PDE条件、Solver、采样和监视器导入|`laplace`|完整训练已运行；未达到数值目标|
|2章 [19]|Laplace方程和200轮|`laplace`|完整训练已运行；未达到数值目标|
|2章 [20]|plt_surf辅助函数：用现代绘图接口和并排热图展示|`laplace`|完整训练已运行；未达到数值目标|
|2章 [21]|规则网格预测解可视化|`laplace`|完整训练已运行；未达到数值目标|
|2章 [22]|解析解及误差；修正residual标签|`laplace`|完整训练已运行；未达到数值目标|
|2章 [23]|IBVP1D和动画功能|`heat`|完整训练已运行；未达到数值目标|
|2章 [24]|L=2、Neumann热方程|`heat`|完整训练已运行；未达到数值目标|
|2章 [25]|动态过程；共享求解结果输出GIF|`heat`|完整训练已运行；未达到数值目标|
|2章 [26]|热方程解析解和误差图|`heat`|完整训练已运行；未达到数值目标|
|2章 [27]|不规则域依赖导入|`star`|完整训练已运行；未达到数值目标|
|2章 [28]|get_grid/create_contour/compare_contour：几何掩膜热图与共享色标|`star`|完整训练已运行；未达到数值目标|
|2章 [29]|星形解析解|`star`|完整训练已运行；未达到数值目标|
|2章 [30]|120个唯一边界控制点|`star`|完整训练已运行；未达到数值目标|
|2章 [31]|32x32及100x100域内生成器、采样展示|`star`|完整训练已运行；未达到数值目标|
|2章 [32]|mse定义、非线性方程和网络；修正对象传递|`star`|完整训练已运行；未达到数值目标|
|2章 [34]|星形解与误差图|`star`|完整训练已运行；未达到数值目标|
|3章 [1]|基础导入|`solver_config`|完整训练已运行；未达到数值目标|
|3章 [2]|振子方程和条件|`solver_config`|完整训练已运行；未达到数值目标|
|3章 [3]|FCNN/nn导入|`network`|完整训练已运行；未达到数值目标|
|3章 [4]|自定义16x16x16网络|`network`|完整训练已运行；未达到数值目标|
|3章 [5]|Generator1D导入|`sampling`|完整训练已运行；未达到数值目标|
|3章 [6]|训练64/验证128|`sampling`|完整训练已运行；未达到数值目标|
|3章 [7]|SGD导入|`optimizer`|完整训练已运行；未达到数值目标|
|3章 [8]|SGD网络参数绑定与训练|`optimizer`|完整训练已运行；未达到数值目标|
|3章 [9]|L1Loss导入|`loss`|完整训练已运行；未达到数值目标|
|3章 [10]|loss_fn兼容修正|`loss`|完整训练已运行；未达到数值目标|
|3章 [11]|旧return_internal|`legacy_internals`|完整训练已运行；未达到数值目标|
|3章 [12]|检查旧接口返回内部对象|`legacy_internals`|完整训练已运行；未达到数值目标|
|3章 [13]|Solver训练及get_internals|`internals`|完整训练已运行；未达到数值目标|
|3章 [14]|检查Solver内部对象|`internals`|完整训练已运行；未达到数值目标|

## 第4章逐条 API 片段

|API位置|片段|对应实现|状态|
|---|---|---|---|
|§4.4 BaseSolver，PDF 61|get_solution → get_examples → 求值；补全上下文与多坐标展开|`api_solution`（合并相同用法，不宣称运行独立球面/Bundle实验）|片段已运行，断言通过（不适用完整训练）|
|§4.4 BundleSolver1D，PDF 65|get_solution → get_examples → 求值；补全上下文与多坐标展开|`api_solution`（合并相同用法，不宣称运行独立球面/Bundle实验）|片段已运行，断言通过（不适用完整训练）|
|§4.4 GenericSolver，PDF 68|get_solution → get_examples → 求值；补全上下文与多坐标展开|`api_solution`（合并相同用法，不宣称运行独立球面/Bundle实验）|片段已运行，断言通过（不适用完整训练）|
|§4.4 Solver1D，PDF 72|get_solution → get_examples → 求值；补全上下文与多坐标展开|`api_solution`（合并相同用法，不宣称运行独立球面/Bundle实验）|片段已运行，断言通过（不适用完整训练）|
|§4.4 Solver2D，PDF 75|get_solution → get_examples → 求值；补全上下文与多坐标展开|`api_solution`（合并相同用法，不宣称运行独立球面/Bundle实验）|片段已运行，断言通过（不适用完整训练）|
|§4.4 SolverSpherical，PDF 79|get_solution → get_examples → 求值；补全上下文与多坐标展开|`api_solution`（合并相同用法，不宣称运行独立球面/Bundle实验）|片段已运行，断言通过（不适用完整训练）|
|§4.11 PDF108|嵌套MeshGenerator与平铺构造等价|`api_mesh`|片段已运行，断言通过（不适用完整训练）|
|§4.11 PDF108|MeshGenerator与g1 ^ g2 ^ g3等价|`api_mesh`|片段已运行，断言通过（不适用完整训练）|
|§4.13 PDF114|AndCallback 与 &|`api_callbacks`，八行真值表|片段已运行，断言通过（不适用完整训练）|
|§4.13 PDF117|NotCallback 与 ~|`api_callbacks`，八行真值表|片段已运行，断言通过（不适用完整训练）|
|§4.13 PDF117|OrCallback 与 &#124;|`api_callbacks`，八行真值表|片段已运行，断言通过（不适用完整训练）|
|§4.13 PDF122|XorCallback 与 ^|`api_callbacks`，八行真值表|片段已运行，断言通过（不适用完整训练）|

### 其余 API 范围的扫描结论

|节|PDF页|扫描结论|
|---|---|---|
|4.1|39–40|diff/safe_diff/unsafe_diff签名和参数；第5章自动微分短例覆盖相关概念|
|4.2|40|只有networks节标题，没有独立可执行例|
|4.3|40–58|条件类、重参数化公式及参数，无独立代码块；IVP/Dirichlet/IBVP的实际用法映射已有方程例|
|4.4|58–79|发现上述6个重复片段；其余签名不扩成新实验|
|4.5|80–87|Monitor签名，实际回调在decay_monitor和api_solution|
|4.6|87–89|旧ODE接口签名，映射legacy_internals和迁移说明|
|4.7|90–94|不规则边界与旧PDE接口签名；星形与热动画映射现有例|
|4.8|94–97|球面旧求解器签名，无独立示例，不新增球面训练|
|4.9|97–101|temporal类与生成器参数，无独立示例|
|4.10|102–103|函数基类API，无独立示例|
|4.11|103–109|2个MeshGenerator内嵌用法已列出；其余构造签名不是实验|
|4.12|109–114|算子函数签名及数学说明，无独立可执行代码块|
|4.13|114–122|4个布尔组合片段已逐项映射|
|4.14|123–124|set_seed/set_tensor_type参数说明，项目setup实际使用；无独立示例|

第5章没有原始可执行代码单元；`residual_demo`、`hard_constraint`、`autodiff`是根据原理补全的教学短例，`hard_soft`是明确标注的项目新增训练对照。

参考代码 `大创1.py`：未提供可访问路径，内容和许可证核查未完成。当前目录的test.py仅作本地比对，不冒充缺失文件。
