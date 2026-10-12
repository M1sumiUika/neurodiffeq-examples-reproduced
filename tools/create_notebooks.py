"""生成教学 Notebook；所有求解都调用共享代码，没有第二套算法。"""
from pathlib import Path
import nbformat as nbf

root=Path(__file__).resolve().parents[1]
lessons=[
    ("01_指数衰减与自动微分", "先理解输入 t、输出 u(t)，再看初值如何由条件对象自动满足。", ["decay","autodiff"]),
    ("02_振子与捕食模型", "二阶振子和一阶方程组描述同一运动；LV的参考是数值积分，不能称为精确解。", ["oscillator","circle","lotka"]),
    ("03_规则区域PDE", "Poisson的零值边界、Laplace的非零边界，以及热方程的Neumann导数边界是不同条件。", ["poisson","laplace","heat"]),
    ("04_星形区域", "先看domain.png，再看解和残差。控制点误差小不代表边间误差也为零。", ["star"]),
    ("05_配置和API", "把网络、采样器和优化器看作独立对象，再将正确对象传给Solver。API短例不需要大型训练。", ["network","sampling","optimizer","loss","api_solution","api_mesh","api_callbacks"]),
    ("06_残差与硬软约束", "2exp(-t)的残差为零，但初值错误。新增硬/软约束对照需要至少三个随机种子。", ["residual_demo","hard_constraint"]),
]
for filename,intro,examples in lessons:
    cells=[nbf.v4.new_markdown_cell(f"# {filename.replace('_',' ')}\n\n{intro}\n\n默认仅运行 **smoke**；两轮训练只用于理解流程。把 `MODE` 改成 `reproduction` 才会按文档配置训练。"),
           nbf.v4.new_code_cell('''from pathlib import Path
import sys
import json
from IPython.display import display, Image

# 同时支持从项目根目录或 notebooks 目录启动。
ROOT = Path.cwd()
if not (ROOT / "pyproject.toml").exists():
    ROOT = ROOT.parent
assert (ROOT / "pyproject.toml").exists(), "请从项目目录打开 Notebook"
sys.path.insert(0, str(ROOT / "src"))
from ndeq_examples.runner import run, environment
MODE = "smoke"
SEED = 42
environment()''')]
    for ex in examples:
        cells.append(nbf.v4.new_markdown_cell(f"## {ex}\n\n先预测图像的大致形状，再运行下面的共享实现。"))
        cells.append(nbf.v4.new_code_cell(f'''out = run("{ex}", mode=MODE, seed=SEED, root=ROOT / "results/notebook_runs")
metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
display(metrics)
for name in ("solution.png", "domain.png", "residual_lesson.png", "loss.png"):
    if (out / name).exists():
        display(Image(filename=str(out / name)))'''))
    if filename.startswith("06"):
        cells.append(nbf.v4.new_markdown_cell("## 新增实验：硬约束和惩罚项\n\n以下命令在终端运行，默认三个种子、两种约束。不要将单个种子的好结果推广为普遍结论。\n\n```powershell\npython -m ndeq_examples run --example hard_soft --mode benchmark --variants default soft\n```\n\n完成后运行 `python tools/build_report.py`，读取统计和对照图。"))
    cells.append(nbf.v4.new_markdown_cell("## 自查\n\n- 这里的未知函数和自变量分别是什么？\n- 初始/边界条件如何施加？\n- metrics里哪一项是方程残差，哪一项是解误差？\n- 当前是流程验证，还是完整训练？\n\n详细说明见 `docs/learning_guide_zh.md` 和 `docs/validation_protocol.md`。"))
    nb=nbf.v4.new_notebook(cells=cells,metadata={"kernelspec":{"display_name":"Python 3 (NeuroDiffEq)","language":"python","name":"python3"}})
    nbf.write(nb,root/"notebooks"/(filename+".ipynb"))
print("Created 6 notebooks")

