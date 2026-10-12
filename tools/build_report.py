"""从已完成的结果生成报告，不修改训练配置、验收线或数值。"""
import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ndeq_examples.config import catalog
from ndeq_examples.runner import write_json

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument("--root",default="results/runs")
p.add_argument("--select",action="store_true",help="复制精选真实结果（排除权重）")
args=p.parse_args()
source=ROOT/args.root
cat=catalog()
records=[]
for path in sorted(source.glob("*/status.json")):
    status=json.loads(path.read_text(encoding="utf-8"))
    m=path.parent/"metrics.json"
    records.append(dict(**status,path=str(path.parent.relative_to(ROOT)).replace("\\","/"),
                        metrics=json.loads(m.read_text(encoding="utf-8")) if m.exists() else {}))
last={}
for r in records:
    if r["status"] in ("full_training_finished","snippet_verified","smoke_passed"):
        last[(r["example"],r["mode"],r["seed"],r.get("variant","default"))]=r
if args.select:
    selected=ROOT/"results/selected"
    selected.mkdir(exist_ok=True)
    # 每个独立完整配置保留最近完成项；原始运行目录依然保留所有历史。
    for r in last.values():
        if r["mode"] not in ("reproduction","benchmark"): continue
        src=ROOT/r["path"]
        dst=selected/src.name
        shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns("*.pt","*.tmp","*.pth"))
        if "problem" in json.loads((src/"config.json").read_text(encoding="utf-8")):
            problem=json.loads((src/"config.json").read_text(encoding="utf-8"))["problem"]
            definitions=json.loads((ROOT/"src/ndeq_examples/problems.json").read_text(encoding="utf-8"))
            write_json(dst/"problem.json",definitions[problem])
    # 原始失败也有公开记录，去掉机器本地绝对路径。
    failures=[r for r in records if r["status"]=="failed"]
    write_json(ROOT/"results/failure_history.json",failures)
    index=["# 精选真实结果", "", "每个目录包含原始数据、指标、训练历史和图。出于体积考虑不发布模型权重；本地 results/runs 保留检查点。数值未达标结果同样保留。", "",
           "|示例|模式/变体/种子|状态|文件夹|", "|---|---|---|---|"]
    for r in last.values():
        if r["mode"] not in ("reproduction","benchmark"): continue
        folder=Path(r["path"]).name
        status="片段断言通过" if r["status"]=="snippet_verified" else "数值通过" if r.get("numerical_pass") else "完整训练，数值未达标"
        index.append(f"|{r['example']}|{r['mode']}/{r['variant']}/{r['seed']}|{status}|[结果](selected/{folder})|")
    (ROOT/"results/README.md").write_text("\n".join(index)+"\n",encoding="utf-8")
write_json(ROOT/"results/run_manifest.json",records)

def state(key):
    r=last.get((key,"reproduction",42,"default"))
    if r:
        if r["status"]=="snippet_verified": return "片段已运行，断言通过（不适用完整训练）"
        return "完整训练已运行；"+("数值验证通过" if r.get("numerical_pass") else "未达到数值目标")
    if any(k[0]==key for k in last): return "流程验证通过"
    return "已实现但未运行"

lines=["# 覆盖清单", "", "基准：2023-04-03 PDF，共138页。以下页码为PDF页面，不是印刷页码。主入口相同问题共享实现；单元格清单在本页后半部分。状态由实际结果生成。", "",
       "|章节|示例|实现文件|验证方法|完成状态|", "|---|---|---|---|---|"]
for key,c in cat.items():
    chapter=c["chapters"][-1]
    method="独立测试残差、条件及解析解" if c.get("problem") else "可执行断言及输出"
    if c.get("problem")=="lotka": method="DOP853双容差数值参考、残差、初值、不变量"
    lines.append(f"|{c['section']} (PDF {','.join(map(str,c['pdf_pages']))})|{key}: {c['title']}|[入口](../examples/chapter{chapter}/{key}.py)|{method}|{state(key)}|")
lines += ["", "## Notebook 单元格逐条映射", "", "导入和绘图单元也列出；同一单元跨页或重复的输出编号不重复计数。空单元、HTML显示对象不是可执行示例。原文没有[33]，不能凭空补成一项。", "", "|章节/单元|内容|共享实现/独立配置|状态|", "|---|---|---|---|"]
mapping2={1:("导入与Notebook绘图后端","decay"),2:("diff/solve/IVP导入","decay"),3:("指数方程、初值、求解","decay"),4:("解析解比较曲线","decay"),5:("训练/验证损失图","decay"),6:("Monitor1D导入","decay_monitor"),7:("附加Monitor的指数求解","decay_monitor"),8:("二阶残差和初始导数","oscillator"),9:("3000轮和监视器","oscillator"),10:("振子解曲线","oscillator"),11:("solve_system导入","circle"),12:("一阶方程组及5000轮训练","circle"),13:("两分量解析曲线","circle"),14:("FCNN/SinActv导入","lotka"),15:("LV及sin网络","lotka"),16:("Solver迁移、t_min=.1、复用权重","migration"),17:("数值对照与误差图","migration"),18:("PDE条件、Solver、采样和监视器导入","laplace"),19:("Laplace方程和200轮","laplace"),20:("plt_surf辅助函数：用现代绘图接口和并排热图展示","laplace"),21:("规则网格预测解可视化","laplace"),22:("解析解及误差；修正residual标签","laplace"),23:("IBVP1D和动画功能","heat"),24:("L=2、Neumann热方程","heat"),25:("动态过程；共享求解结果输出GIF","heat"),26:("热方程解析解和误差图","heat"),27:("不规则域依赖导入","star"),28:("get_grid/create_contour/compare_contour：几何掩膜热图与共享色标","star"),29:("星形解析解","star"),30:("120个唯一边界控制点","star"),31:("32x32及100x100域内生成器、采样展示","star"),32:("mse定义、非线性方程和网络；修正对象传递","star"),34:("星形解与误差图","star")}
mapping3={1:("基础导入","solver_config"),2:("振子方程和条件","solver_config"),3:("FCNN/nn导入","network"),4:("自定义16x16x16网络","network"),5:("Generator1D导入","sampling"),6:("训练64/验证128","sampling"),7:("SGD导入","optimizer"),8:("SGD网络参数绑定与训练","optimizer"),9:("L1Loss导入","loss"),10:("loss_fn兼容修正","loss"),11:("旧return_internal","legacy_internals"),12:("检查旧接口返回内部对象","legacy_internals"),13:("Solver训练及get_internals","internals"),14:("检查Solver内部对象","internals")}
for ch,mapping in [(2,mapping2),(3,mapping3)]:
    for cell,(label,key) in mapping.items(): lines.append(f"|{ch}章 [{cell}]|{label}|`{key}`|{state(key)}|")
lines += ["", "## 第4章逐条 API 片段", "", "|API位置|片段|对应实现|状态|", "|---|---|---|---|"]
for name,page in [("BaseSolver",61),("BundleSolver1D",65),("GenericSolver",68),("Solver1D",72),("Solver2D",75),("SolverSpherical",79)]:
    lines.append(f"|§4.4 {name}，PDF {page}|get_solution → get_examples → 求值；补全上下文与多坐标展开|`api_solution`（合并相同用法，不宣称运行独立球面/Bundle实验）|{state('api_solution')}|")
for label in ["嵌套MeshGenerator与平铺构造等价","MeshGenerator与g1 ^ g2 ^ g3等价"]:
    lines.append(f"|§4.11 PDF108|{label}|`api_mesh`|{state('api_mesh')}|")
for page,label in [(114,"AndCallback 与 &"),(117,"NotCallback 与 ~"),(117,"OrCallback 与 |"),(122,"XorCallback 与 ^")]:
    lines.append(f"|§4.13 PDF{page}|{label.replace('|','&#124;')}|`api_callbacks`，八行真值表|{state('api_callbacks')}|")
lines += ["", "### 其余 API 范围的扫描结论", "", "|节|PDF页|扫描结论|", "|---|---|---|"]
for sec,pages,note in [("4.1","39–40","diff/safe_diff/unsafe_diff签名和参数；第5章自动微分短例覆盖相关概念"),("4.2","40","只有networks节标题，没有独立可执行例"),("4.3","40–58","条件类、重参数化公式及参数，无独立代码块；IVP/Dirichlet/IBVP的实际用法映射已有方程例"),("4.4","58–79","发现上述6个重复片段；其余签名不扩成新实验"),("4.5","80–87","Monitor签名，实际回调在decay_monitor和api_solution"),("4.6","87–89","旧ODE接口签名，映射legacy_internals和迁移说明"),("4.7","90–94","不规则边界与旧PDE接口签名；星形与热动画映射现有例"),("4.8","94–97","球面旧求解器签名，无独立示例，不新增球面训练"),("4.9","97–101","temporal类与生成器参数，无独立示例"),("4.10","102–103","函数基类API，无独立示例"),("4.11","103–109","2个MeshGenerator内嵌用法已列出；其余构造签名不是实验"),("4.12","109–114","算子函数签名及数学说明，无独立可执行代码块"),("4.13","114–122","4个布尔组合片段已逐项映射"),("4.14","123–124","set_seed/set_tensor_type参数说明，项目setup实际使用；无独立示例")]:
    lines.append(f"|{sec}|{pages}|{note}|")
lines += ["", "第5章没有原始可执行代码单元；`residual_demo`、`hard_constraint`、`autodiff`是根据原理补全的教学短例，`hard_soft`是明确标注的项目新增训练对照。", "", "参考代码 `大创1.py`：未提供可访问路径，内容和许可证核查未完成。当前目录的test.py仅作本地比对，不冒充缺失文件。"]
(ROOT/"docs/coverage.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

full=[r for r in last.values() if r["mode"]=="reproduction" and r["status"]=="full_training_finished"]
bench=[r for r in last.values() if r["mode"]=="benchmark" and r["status"]=="full_training_finished"]
report=["# 实际实验报告", "", "由 `tools/build_report.py` 读取运行文件生成；没有依据结果修改验收线。完整运行清单见 `results/run_manifest.json`。", "",
        f"完整配置训练：{len(full)}项；其中{sum(r.get('numerical_pass',False) for r in full)}项通过全部预设数值标准。另有{len(bench)}次新增对照训练。", "",
        "|例子|轮数|最大绝对误差|RMSE|相对L2|残差RMSE|条件误差|时间(s)|验收|", "|---|---|---|---|---|---|---|---|---|"]
for r in full:
    m=r["metrics"]
    report.append(f"|{r['example']}|{r.get('epochs_completed')}|{m['max_abs']:.3g}|{m['rmse']:.3g}|{m['relative_l2']:.3g}|{m['residual_rmse']:.3g}|{m['condition_max_abs']:.3g}|{r['elapsed_seconds']:.1f}|{'通过' if r['numerical_pass'] else '未达标'}|")
report += ["", "migration 的轮数栏是第二阶段；总训练另加 warmup 3000轮，耗时含该阶段。时间包括初始化、评估和绘图，`training_seconds`另记录主阶段训练。机器同时执行其他检查，因此不能据此声称严格速度排名。", "", "## 三种子对照", "", "同一例子的相同变体使用42、43、44种子。统计为算术均值 ± 样本标准差（ddof=1）。", "", "|例子/变体|种子数|RMSE均值±标准差|相对L2均值±标准差|通过数|", "|---|---|---|---|---|"]
groups=defaultdict(list)
for r in bench: groups[(r["example"],r["variant"])].append(r)
stats=[]
for (example,variant),rs in sorted(groups.items()):
    values=np.array([[r["metrics"]["rmse"],r["metrics"]["relative_l2"],r["metrics"]["condition_max_abs"]] for r in rs])
    unique=len(set(r["seed"] for r in rs))
    mean=values.mean(axis=0); std=values.std(axis=0,ddof=1) if unique>1 else np.zeros(3)
    report.append(f"|{example}/{variant}|{unique}|{mean[0]:.3g} ± {std[0]:.3g}|{mean[1]:.3g} ± {std[1]:.3g}|{sum(r['numerical_pass'] for r in rs)}/{len(rs)}|")
    stats.append(dict(example=example,variant=variant,seeds=[r['seed'] for r in rs],mean=mean.tolist(),std=std.tolist()))
write_json(ROOT/"results/benchmark_statistics.json",dict(columns=["rmse","relative_l2","condition_max_abs"],statistics=stats))
if groups:
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ax,ex in zip(axes,["hard_soft","decay"]):
        keys=sorted(k for k in groups if k[0]==ex)
        for i,k in enumerate(keys):
            rs=groups[k]; vals=[r['metrics']['rmse'] for r in rs]
            ax.scatter(np.full(len(vals),i)+np.linspace(-.1,.1,len(vals)),vals,s=30)
            ax.errorbar(i,np.mean(vals),yerr=np.std(vals,ddof=1),fmt='k_',capsize=5)
        ax.set_xticks(range(len(keys)),[k[1] for k in keys]); ax.set_yscale('log')
        ax.set(title=ex+" / 3 seeds",ylabel="Solution RMSE",xlabel="Variant")
    fig.tight_layout(); fig.savefig(ROOT/"results/benchmark_comparison.png",dpi=140); plt.close(fig)
report += ["", "![三种子对照](../results/benchmark_comparison.png)", "", "## 未达标与解释的边界", "",
"- 二阶振子和一阶方程组的初值严格满足，但长时间区间中的幅度/相位误差仍可积累。一阶形式本次残差通过而解误差未通过，是两种指标不同的真实例子。",
"- Laplace和热方程只运行原文200轮。边界达到浮点精度不能弥补内部残差；不应把边界正确等同于方程求解成功。",
"- 星形例运行原文100轮，解误差较小，残差仍可能受边界插值、二阶导数、凹角邻域和ELU正则性影响。这里只把这些列为可能原因，没有做消融就不能断言因果。控制点误差和边间误差分别报告。",
"- 第3章是接口配置教学，原文100/1000轮并未保证数值收敛；自定义网络、SGD、L1的示例不能因接口能跑就算精度成功。",
"- 3个种子只是最低规模比较，不能给出普遍优劣或统计显著性的结论。宽网络/均匀采样同时有各自配置变化，具体设置以config.json为准。",
"- Poisson有解析解但原文没有训练配置。达到约6e-5量级只表示这套补全配置在该测试集上达到了相近绝对误差，不能推断重现了原作者训练过程。",
"", "如需探索更多轮数或平滑激活，请另建明确标记为新增的benchmark配置，保留这份原文轮数结果。当前任务交付未隐藏未达标项。"]
geometry=ROOT/"results/star_geometry_audit.json"
if geometry.exists():
    report += ["", "## 星形区域几何复核", "", "`tools/check_geometry.py`比较原文插值域与精确多边形。32×32训练网格一致；100×100验证网格中原插值域多含4个域外点，本项目将其排除。更细网格显示两种几何并非完全等价。这是显式记录的修正，不把包围盒当作有效域。边界和真正域外点分开计数。", "", "|网格|严格内部|插值域内部|其中真正域外|其中边界|漏掉严格内部|", "|---|---|---|---|---|---|"]
    for g in json.loads(geometry.read_text()):
        report.append(f"|{g['grid']}²|{g['polygon_interior']}|{g['interpolated_interior']}|{g['interpolated_outside_polygon']}|{g['interpolated_boundary_points']}|{g['polygon_missed_by_interpolant']}|")
(ROOT/"docs/experiment_report.md").write_text("\n".join(report)+"\n",encoding="utf-8")
print(f"Report: {len(full)} full configurations, {len(bench)} benchmark runs, {len(records)} records")

