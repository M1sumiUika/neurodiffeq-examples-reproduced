"""维护者工具：生成配置快照和仅调用共享实现的独立入口。"""
import json
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]
cat = {}
def add(key, title, chapters, section, pages, problem=None, epochs=1000, **kw):
    item = dict(title=title, chapters=chapters, section=section, pdf_pages=pages, epochs=epochs, **kw)
    if problem:
        item["problem"] = problem
        item.setdefault("domain", [[0,2]] if problem == "decay" else [[0,2*math.pi]] if problem in ("oscillator","circle") else [[0,12]] if problem=="lotka" else [[0,2],[0,3]] if problem=="heat" else [[-1,1],[-1,1]] if problem=="star" else [[0,1],[0,1]])
        # 在第一次训练前确定。主要变量量级约为 1，Poisson 量级约 .06。
        item.setdefault("acceptance", dict(relative_l2=0.02, max_abs=0.03, residual_rmse=0.03, condition_max_abs=1e-8))
        if problem=="poisson": item["acceptance"] = dict(relative_l2=0.02,max_abs=0.002,residual_rmse=0.03,condition_max_abs=1e-8)
        if problem=="star": item["acceptance"] = dict(relative_l2=0.05,max_abs=0.04,residual_rmse=0.1,condition_max_abs=0.01)
    else:
        item["kind"] = "snippet"
    cat[key] = item

add("decay", "指数衰减（Solver 迁移）", [2], "2.1.1", [13,14,15], "decay", best=False)
add("decay_monitor", "指数衰减与 Monitor1D 回调", [2], "2.1.1 [6]-[7]", [15], "decay", best=False, monitor=True)
add("oscillator", "二阶简谐振子", [2], "2.1.2", [16], "oscillator", 3000, best=False)
add("circle", "一阶振子方程组", [2], "2.2.1", [17,18], "circle", 5000, best=False)
add("lotka", "Lotka–Volterra", [1,2], "1.4.1; 2.2.2", [7,8,9,10,19], "lotka", 3000, activation="SinActv", best=False)
add("migration", "LV 的旧接口到 Solver 迁移（显式前置训练）", [2], "2.2.3", [20,21], "lotka", 3000,
    activation="SinActv", domain=[[0.1,12]], test_domain=[[0,12]], warmup_epochs=3000)
add("poisson", "二维 Poisson（补全代码）", [1], "1.4.2", [10,11], "poisson", 2000,
    origin="原文有公式、无训练代码；网络32x32、Adam、32x32采样和2000轮为项目补充")
add("laplace", "二维 Laplace", [2], "2.3.1", [21,22,23,24], "laplace", 200, hidden=[512])
add("heat", "热传导：L=2、非齐次 Neumann、GIF", [2], "2.3.2", [24,25,26], "heat", 200)
add("star", "星形区域非线性 PDE", [2], "2.4", [26,27,28,29], "star", 100,
    hidden=[40,40], activation="ELU", lr=0.01, valid_grid=100,
    corrections=["nets=[net]", "optimizer=adam", "严格多边形与原文插值域取交集"])
add("solver_config", "振子求解器配置", [3], "3.1;3.1.1", [31,32], "oscillator", 1000)
add("network", "16x16x16 Tanh 网络", [3], "3.1.2", [32,33], "oscillator", 1000, hidden=[16,16,16])
add("activations", "网络与 Tanh/Sigmoid/Sin/Swish 激活", [3], "3.1.2", [32])
add("sampling", "训练64点均匀采样/验证128点等距", [3], "3.1.3", [33,34], "oscillator", 1000,
    train_size=64,valid_size=128,sampling="uniform")
add("optimizer", "SGD + momentum=0.99", [3], "3.1.4", [34,35], "oscillator", 1000,
    hidden=[16,16,16],optimizer="SGD")
add("loss", "L1 自定义损失", [3], "3.1.5", [35], "oscillator", 1000, loss="l1")
add("legacy_internals", "旧 solve_system 内部信息", [3], "3.2.1", [36,37], "circle", 1000, legacy=True, best=False)
add("internals", "Solver 内部信息", [3], "3.2.2", [37,38], "circle", 100)
add("api_solution", "六处 get_solution 调用短片段", [4], "4.4", [61,65,68,72,75,79])
add("api_mesh", "MeshGenerator 嵌套与 ^ 运算符", [4], "4.11", [108])
add("api_callbacks", "And/Not/Or/Xor 回调组合", [4], "4.13", [114,117,122])
add("residual_demo", "残差为零不意味着满足初值", [5], "5.1", [125])
add("hard_constraint", "初值硬约束及导数约束", [5], "5.2", [126])
add("autodiff", "自动微分一阶与二阶导数", [5], "5.3", [126,127])
add("hard_soft", "新增：硬约束与初值惩罚项对照", [5], "项目新增；对应5.2原理", [126], "decay", 1000,
    acceptance=dict(relative_l2=0.02,max_abs=0.03,residual_rmse=0.03,condition_max_abs=0.01))

(ROOT/"src/ndeq_examples/catalog.json").write_text(json.dumps(cat,ensure_ascii=False,indent=2),encoding="utf-8")
for folder in ("configs","examples","docs","results","notebooks","tests",".github/workflows"):
    (ROOT/folder).mkdir(parents=True, exist_ok=True)
for key,cfg in cat.items():
    chapter = cfg["chapters"][-1]
    folder = ROOT/f"examples/chapter{chapter}"
    folder.mkdir(exist_ok=True)
    script = f'''"""{cfg['title']}；详细公式和配置见 docs/coverage.md 与 configs。"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from ndeq_examples.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["run", "--example", "{key}", *sys.argv[1:]]))
'''
    (folder/f"{key}.py").write_text(script, encoding="utf-8")
(ROOT/"configs/original.json").write_text(json.dumps(cat,ensure_ascii=False,indent=2),encoding="utf-8")
(ROOT/"configs/smoke.json").write_text(json.dumps(dict(epochs=2,grid=8,valid_grid=10,train_size=16,valid_size=16,valid_batches=1,test_size=256),indent=2),encoding="utf-8")
(ROOT/"configs/benchmark.json").write_text(json.dumps(dict(seeds=[42,43,44],comparisons={"hard_soft":["default","soft"],"decay":["default","wide","uniform"]}),indent=2),encoding="utf-8")
print(f"Created {len(cat)} configurations")

from ndeq_examples.config import resolve
for mode in ("reproduction", "smoke"):
    (ROOT/f"configs/{mode}_resolved.json").write_text(json.dumps(
        {key:resolve(key,mode) for key in cat},ensure_ascii=False,indent=2),encoding="utf-8")

# 第一章复用相同数学实现，保留按章节运行的直观入口。
folder = ROOT/"examples/chapter1"
folder.mkdir(exist_ok=True)
for key in ("lotka","poisson"):
    source = ROOT/f"examples/chapter{cat[key]['chapters'][-1]}/{key}.py"
    target = folder/f"{key}.py"
    if source != target:
        target.write_text(source.read_text(encoding="utf-8"),encoding="utf-8")

