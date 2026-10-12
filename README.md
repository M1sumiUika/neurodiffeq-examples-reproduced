# NeuroDiffEq 文档示例复现与数值验证

**neurodiffeq-examples-reproduced** 是软件文档示例复现项目，不是原创求解器，也不是整篇论文复现。以用户提供的 **2023-04-03 NeuroDiffEq PDF** 为基准，补全可执行代码、修正兼容性问题，并用独立测试点进行数值验证。

**当前成果：25个独立配置/片段组均已运行；其中18个训练配置跑完指定轮数，6个通过全部数值标准，另外7个短片段组断言通过。新增15次三种子对照训练。** 未达标结果没有隐藏，也没有把两轮 smoke 当作数值成功。`大创1.py`尚未找到，相关核查仍待补充。

从这里开始：[中文学习指南](docs/learning_guide_zh.md) · [逐条覆盖表](docs/coverage.md) · [实际实验报告](docs/experiment_report.md) · [精选结果](results/README.md) · [English](README_EN.md)

## 这个项目包含什么

|来源|内容|处理原则|
|---|---|---|
|PDF第1–2章|指数衰减、两种振子形式、Lotka–Volterra、Poisson、Laplace、热传导、星形非线性PDE|保持方程、参数、区域与条件；重复示例共享实现|
|PDF第3章|自定义网络/激活、采样、SGD、L1损失、旧接口和Solver内部信息|保留独立配置；明确网络与优化器绑定|
|PDF第4章|6处重复solution调用、2处采样器组合、4处回调组合|逐条定位；相同用法合并；不把无例子的API条目扩大为新实验|
|PDF第5章原理|残差、初值硬约束、自动微分|补全可运行教学短例|
|项目新增|硬/软约束对照、网络大小与采样方式对照、独立数值验收|显式标注，至少3个种子；不冒充原文实验|

第1章Poisson只有公式和图，训练网络及轮数由本项目补全。`migration`保留原文复用已训练网络的行为：先训练3000轮，再在t≥0.1上继续3000轮。详见[勘误与决策](docs/errata.md)。

## 安装：Windows PowerShell

已验证 Python **3.12.6**。使用 Python 3.12 安装最方便；默认只需要CPU，不需要显卡。

```powershell
cd "你的路径\neurodiffeq-examples-reproduced"
py -3.12 -m venv .venv
# 不必激活环境，不必修改系统执行策略：
.\.venv\Scripts\python.exe -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m ndeq_examples list
```

以下命令中的 `python` 均指该虚拟环境的解释器。可激活环境：`.\.venv\Scripts\Activate.ps1`；若系统不允许，继续使用完整解释器路径即可。Linux/macOS对应 `python3 -m venv .venv`、`source .venv/bin/activate`，然后执行相同pip命令。

复建本次纯CPU依赖快照可用：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-lock-cpu.txt
```

核心版本：NeuroDiffEq发行包0.7.0、PyTorch2.6.0、NumPy1.26.4、SciPy1.15.2、Matplotlib3.9.2、Pillow10.4.0。每次运行保存实际版本。原始完整实验使用本机2.6.0+cu126 wheel但明确运行在CPU；另建2.6.0+cpu干净环境通过全部smoke及测试。模块 `neurodiffeq.__version__` 的0.6.3-dev标识与发行元数据不一致，项目同时记录，见[环境快照](docs/environment_cpu.json)。

## 从第一个示例开始

```powershell
python -m ndeq_examples run --example decay --mode smoke
python -m ndeq_examples run --example decay --mode reproduction
```

第一条只训练2轮，检查安装、求导和文件输出。第二条训练1000轮，完成数值验收。在输出目录打开 `solution.png`，应看到神经网络曲线与exp(-t)比较；再看 `metrics.json`，不要只看曲线“像不像”。

也可独立执行脚本：

```powershell
python examples/chapter2/decay.py --mode reproduction
```

代码不依赖Notebook之前运行过什么。学习顺序建议：指数衰减 → 二阶振子 → 一阶方程组 → LV → Laplace → 热方程 → 星形区域。六份[教学Notebook](notebooks/)只调用同一共享实现，均已在独立内核执行。默认是smoke；修改 `MODE` 可运行完整配置。在VS Code选择虚拟环境内核即可；使用JupyterLab可另装 `python -m pip install jupyterlab`。

## 统一运行命令

```powershell
python -m ndeq_examples list
python -m ndeq_examples run --example lotka --mode reproduction
python -m ndeq_examples run --chapter 2 --mode reproduction
python -m ndeq_examples run --all --mode smoke
python -m ndeq_examples run --all --mode reproduction --resume
python -m ndeq_examples summarize
```

`--resume`会跳过配置一致且已完成的项目，对失败项目重跑；“完整训练但精度未达标”仍属于已完成实验，不会擅自换超参数。每次新运行生成带UTC时间、示例、模式、种子和唯一后缀的目录。

从本地检查点续训（保存到新目录，配置必须一致）：

```powershell
python -m ndeq_examples run --example oscillator --mode reproduction --resume-from "results/runs/你的运行目录"
```

三个运行模式：

|模式|用途|是否可称数值复现通过|
|---|---|---|
|smoke|2轮、较少采样点，检查流程和输出|不能|
|reproduction|原文明示的网络、参数和轮数，必要补全/修正均有记录|仅在所有预定指标通过时|
|benchmark|明确新增的对照，默认种子42、43、44|仅代表该对照配置达到标准|

新增对照命令：

```powershell
python -m ndeq_examples run --example hard_soft --mode benchmark --variants default soft
python -m ndeq_examples run --example decay --mode benchmark --variants default wide uniform
python tools/build_report.py --select
```

`default`为原配置，`soft`增加初值惩罚项λ=1，`wide`用64×64网络，`uniform`用64训练点和128验证点。每个变体至少3种子。CPU/float64/单PyTorch线程为默认；GPU可选 `--device cuda`，需相应PyTorch wheel，GPU尚未验证。

## 精选真实结果

完整配置种子42，独立测试2048点。标准在训练前确定，见[验证协议](docs/validation_protocol.md)。

|例子|最大解误差|整体相对L2|残差RMSE|结论|
|---|---:|---:|---:|---|
|指数衰减|1.05e-3|1.05e-3|2.88e-3|通过|
|Lotka–Volterra|8.79e-3|3.22e-3|2.26e-3|通过；DOP853数值参考|
|Poisson（补全训练配置）|5.02e-5|5.38e-4|2.45e-3|通过；与原文图示误差同量级|
|一阶振子方程组|6.09e-2|3.47e-2|1.33e-2|残差达标，解误差未达标|
|Laplace，200轮|1.64e-2|2.62e-2|9.86e-1|未达标|
|热方程，200轮|1.24e-1|1.52e-1|1.54e-1|未达标；Neumann条件仍满足|
|星形PDE，100轮|1.75e-3|3.02e-3|1.08e-1|解误差达标，残差略超0.1|

完整18项训练配置和15次benchmark的指标都在[实验报告](docs/experiment_report.md)，图像和GIF在[结果索引](results/README.md)。6项通过包含指数监视器、迁移和新增硬约束基线等配置，不代表6种互不相关的方程全部成功。

![三种子对照](results/benchmark_comparison.png)

原文热传导保留L=2、k=.3、T=3及非齐次Neumann条件；没有换成更容易的零Dirichlet题目。星形仍为十二边六角星，严格域内评价，边界另测。Poisson没有原文训练参数，所以只能声称补全配置重现相近误差量级，不能声称恢复原作者训练过程。

## 文件结构和如何读结果

```text
src/ndeq_examples/  方程、条件、求解器、独立评价、绘图与CLI
examples/chapter*/ 各章可独立执行的轻量入口
configs/           原文/补全配置与各运行模式快照
notebooks/         六份中文教学Notebook（共享算法）
tests/             数学、条件、指标、几何和关键smoke测试
docs/              覆盖、勘误、迁移、学习指南及实际报告
results/selected/  可发布真实数据、图表、GIF及失败精度结果
results/runs/      本地所有原始运行与检查点（Git忽略）
tools/             PDF定位、报告、环境记录及发布检查
.github/workflows/ CPU数学测试与smoke持续集成
```

每次方程运行包含 `config.json`（种子、配置与验收线）、`problem.json`（方程、参数与条件）、`status.json`（状态、环境及时间）、`history.json`、`metrics.json`、`sampling.npz`、`test_data.npz`和图。完整训练的最终测试使用配置指定的最后权重或最佳验证权重。局部采样的方程残差与解对参考的误差分别保存；有零点的解不用逐点相对误差。热方程输出Pillow GIF，无需FFmpeg。

`configs`是由 `tools/create_catalog.py` 生成的可读快照；运行时读取包内 `catalog.json`，统一默认值在 `config.py`。修改新实验时应新增独立配置，再生成快照，避免同时维护两套不同参数。

## 测试、局限与未完成项

```powershell
python -m pytest -q
python -m ndeq_examples run --all --mode smoke --root results/ci
```

GitHub Actions只执行数学/接口检查和CPU smoke，不在每次提交时重复完整训练。预设阈值适用于这些无量纲教学例题，不是工程精度保证。

主要局限：完整复现配置只有一个主种子；原文轮数不保证收敛；星形薄板样条在控制点之间只有近似约束；ELU二阶导正则性可能影响PDE残差；GPU和Linux完整训练未在本机验证。干净CPU环境已单独验证安装、全部入口与测试。训练时间含其他并行本地检查的影响，不能当作严格性能排行榜。

**缺失材料：** `大创1.py`未找到，内容和许可证核查尚未完成。本地仅发现 `test.py`，与指数衰减旧接口例相符，但不把它冒充缺失文件。项目没有附个人材料或整本第三方PDF。

当前无可用GitHub认证，未创建远程仓库；完整项目已可本地运行。[私有仓库上传步骤](docs/github_upload.md)包括首次发布检查。项目不虚构个人身份、导师、学校、项目经历或Git历史。

## 参考与许可证

复现基准：NeuroDiffGym，*neurodiffeq Documentation*，PDF封面2023-04-03，138页，文件SHA256见[基准审计](docs/baseline_audit.json)。在线资料查阅于2026-10-12，文档标识为`latest`，发行包选择0.7.0。

- [官方项目](https://github.com/NeuroDiffGym/neurodiffeq) · [官方文档](https://neurodiffeq.readthedocs.io/en/latest/)
- [Chen等，2020，JOSS](https://doi.org/10.21105/joss.01931)
- [Liu等，2025，Recent Advances of NeuroDiffEq](https://arxiv.org/abs/2502.12177)（当前官方补充引用，不取代2023基准）

采用MIT条款并保留第三方原始声明，详见 [LICENSE](LICENSE)、[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)及 [NeuroDiffEq原始许可证](LICENSES/NeuroDiffEq-MIT.txt)。
