"""补全 API 短片段上下文；不将每个 API 条目扩成大型 PDE 实验。"""
from types import SimpleNamespace
import numpy as np
import torch
import matplotlib.pyplot as plt
from neurodiffeq import diff
from neurodiffeq.conditions import IVP
from neurodiffeq.networks import FCNN, Swish, SinActv
from neurodiffeq.generators import Generator1D, MeshGenerator
from .config import resolve
from .models import build
from .plotting import save


def run_snippet(cfg, out):
    name = cfg["id"]
    if name == "api_solution":
        reports = {}
        for identifier in ("decay", "laplace"):
            solver = build(resolve(identifier, "smoke", cfg["seed"]))
            from neurodiffeq.monitors import Monitor1D, Monitor2D
            monitor = Monitor1D(0.,2.,check_every=2) if identifier == "decay" else Monitor2D(xy_min=(0,0),xy_max=(1,1),check_every=2)
            solver.fit(2, callbacks=[monitor.to_callback(fig_dir=str(out/identifier))], tqdm_file=None)
            solution = solver.get_solution()
            coords = solver.generator["train"].get_examples()
            # Solver 的 SamplerGenerator 总是给坐标列表；必须展开。
            value = solution(*coords)
            copied = solver.get_solution(copy=True)
            old = copied(*coords).detach().clone()
            solver.fit(1, tqdm_file=None)
            assert torch.equal(copied(*coords), old)
            reports[identifier] = {"shape": list(value.shape), "copy_isolated": True}
        return {"checks_passed": True, "solution_calls": reports,
                "scope": "六处重复片段统一用 1D/2D 展示单坐标和多坐标调用；不宣称新增球面训练实验"}
    if name == "api_mesh":
        gs = [Generator1D(3, i, i+1, method="equally-spaced") for i in range(3)]
        a = MeshGenerator(MeshGenerator(gs[0], gs[1]), gs[2]).get_examples()
        b = MeshGenerator(*gs).get_examples()
        c = (gs[0] ^ gs[1] ^ gs[2]).get_examples()
        assert all(torch.equal(x, y) and torch.equal(y, z) for x, y, z in zip(a, b, c))
        points = np.column_stack([x.detach().cpu().numpy().ravel() for x in a])
        np.savez_compressed(out/"samples.npz", points=points)
        return {"checks_passed": True, "mesh_shape": list(points.shape), "two_equivalences": True}
    if name == "api_callbacks":
        from neurodiffeq.callbacks import TrueCallback, FalseCallback, AndCallback, OrCallback, NotCallback, XorCallback
        truth = []
        for av in (False, True):
            for bv in (False, True):
                for cv in (False, True):
                    a, b, c = [(TrueCallback if v else FalseCallback)() for v in (av, bv, cv)]
                    pairs = [(AndCallback([a,b,c]), a&b&c), (OrCallback([a,b,c]), a|b|c),
                             (NotCallback(a), ~a), (XorCallback([a,b,c]), a^b^c)]
                    result = [bool(x.condition(None)) for x, _ in pairs]
                    assert result == [bool(y.condition(None)) for _, y in pairs]
                    assert result == [av and bv and cv, av or bv or cv, not av, av ^ bv ^ cv]
                    truth.append([av,bv,cv,*result])
        return {"checks_passed": True, "truth_table_columns": ["a","b","c","and","or","not_a","xor"], "truth_table": truth}
    if name == "activations":
        t = torch.linspace(-3, 3, 101).reshape(-1, 1).requires_grad_(True)
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for act in (torch.nn.Tanh, torch.nn.Sigmoid, SinActv, Swish):
            y = act()(t)
            dy = diff(y, t)
            net = FCNN(hidden_units=(16,16,16), actv=act)
            assert net(t).shape == t.shape
            axes[0].plot(t.detach().cpu(), y.detach().cpu(), label=act.__name__)
            axes[1].plot(t.detach().cpu(), dy.detach().cpu(), label=act.__name__)
        for ax, title in zip(axes, ("Activation", "Automatic derivative")):
            ax.set_title(title); ax.legend()
        save(fig, out/"activations.png")
        return {"checks_passed": True, "scope": "第 3 章激活函数与网络构造短例，不代表训练效果比较"}
    if name in ("residual_demo", "autodiff", "hard_constraint"):
        t = torch.linspace(0, 2, 101).reshape(-1, 1).requires_grad_(True)
        if name == "autodiff":
            y = t**3 + torch.sin(t)
            first, second = diff(y, t), diff(y, t, order=2)
            e1 = (first-(3*t*t+torch.cos(t))).abs().max().item()
            e2 = (second-(6*t-torch.sin(t))).abs().max().item()
            assert e1 < 1e-12 and e2 < 1e-12
            np.savez_compressed(out/"derivatives.npz", t=t.detach().cpu(), y=y.detach().cpu(),
                                first=first.detach().cpu(), second=second.detach().cpu())
            return {"checks_passed": True, "first_max_error": e1, "second_max_error": e2}
        if name == "hard_constraint":
            net = FCNN()
            origin = torch.zeros((1,1), requires_grad=True)
            u = 1+(1-torch.exp(-t))*net(t)
            official = IVP(0, 1).enforce(net, t)
            assert torch.allclose(u, official)
            err = (IVP(0, 1).enforce(net, origin)-1).abs().max().item()
            second = IVP(0, 0, u_0_prime=1).enforce(net, origin)
            d_err = (diff(second, origin)-1).abs().max().item()
            assert err == 0 and d_err == 0
            return {"checks_passed": True, "initial_error": err, "initial_derivative_error": d_err,
                    "formula": "1 + (1-exp(-t))*N(t)"}
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        report = {}
        for label, u in {"exp(-t)": torch.exp(-t), "2 exp(-t)": 2*torch.exp(-t), "1-t": 1-t}.items():
            r = diff(u, t)+u
            report[label] = {"residual_rmse": torch.sqrt(torch.mean(r*r)).item(), "initial_error": abs(u[0].item()-1)}
            axes[0].plot(t.detach().cpu(), u.detach().cpu(), label=label)
            axes[1].plot(t.detach().cpu(), r.detach().cpu(), label=label)
        for ax, title in zip(axes, ("Candidate solution", "Residual u' + u")):
            ax.set_title(title); ax.legend()
        save(fig, out/"residual_lesson.png")
        assert report["2 exp(-t)"]["residual_rmse"] == 0
        return {"checks_passed": True, "candidates": report}
    raise ValueError(name)

