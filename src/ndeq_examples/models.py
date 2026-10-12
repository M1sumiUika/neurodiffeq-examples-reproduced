"""构造官方 Solver；显式传入网络及优化器，避免 Notebook 隐藏状态。"""
from itertools import chain
import numpy as np
import torch
from neurodiffeq.conditions import IVP, DirichletBVP2D, IBVP1D, NoCondition
from neurodiffeq.generators import Generator1D, Generator2D, PredefinedGenerator
from neurodiffeq.networks import FCNN, SinActv, Swish
from neurodiffeq.solvers import Solver1D, Solver2D
from .math import residual
from .geometry import star_boundary, in_star


def star_condition():
    from neurodiffeq.pde import CustomBoundaryCondition, Point, DirichletControlPoint
    points = star_boundary()
    return CustomBoundaryCondition(Point((0., 0.)), [
        DirichletControlPoint(tuple(p), float(np.log(1+sum(p*p)))) for p in points])


def build(cfg, existing_nets=None):
    p = cfg["problem"]
    dim = 1 if p in ("decay", "oscillator", "circle", "lotka") else 2
    n_funcs = 2 if p in ("circle", "lotka") else 1
    activation = {"SinActv": SinActv, "Swish": Swish}.get(cfg["activation"], getattr(torch.nn, cfg["activation"], None))
    nets = existing_nets or [FCNN(n_input_units=dim, n_output_units=1,
                                hidden_units=tuple(cfg["hidden"]), actv=activation) for _ in range(n_funcs)]
    if cfg["optimizer"] == "SGD":
        optimizer = torch.optim.SGD(chain.from_iterable(n.parameters() for n in nets), lr=cfg["lr"], momentum=0.99)
    else:
        optimizer = torch.optim.Adam(chain.from_iterable(n.parameters() for n in nets), lr=cfg["lr"])
    if dim == 1:
        if p == "decay":
            conditions = [IVP(0., 1.)]
        elif p == "oscillator":
            conditions = [IVP(0., 0., u_0_prime=1.)]
        else:
            conditions = [IVP(0., 1.5 if p == "lotka" else 0.), IVP(0., 1.)]
        if cfg.get("soft"):
            conditions = [NoCondition()]
        low, high = cfg["domain"][0]
        train = Generator1D(cfg["train_size"], low, high, method=cfg["sampling"])
        valid = Generator1D(cfg["valid_size"], low, high, method="equally-spaced")
        cls, ranges = Solver1D, dict(t_min=low, t_max=high)
    else:
        low, high = tuple(d[0] for d in cfg["domain"]), tuple(d[1] for d in cfg["domain"])
        if p in ("laplace", "poisson"):
            conditions = [DirichletBVP2D(x_min=0., x_max=1., y_min=0., y_max=1.,
                x_min_val=(lambda y: torch.sin(np.pi*y)) if p == "laplace" else (lambda y: 0*y),
                x_max_val=lambda y: 0*y, y_min_val=lambda x: 0*x, y_max_val=lambda x: 0*x)]
        elif p == "heat":
            conditions = [IBVP1D(t_min=0., t_min_val=lambda x: torch.sin(np.pi*x/2),
                x_min=0., x_max=2.,
                x_min_prime=lambda t: np.pi/2*torch.exp(-0.3*np.pi**2*t/4),
                x_max_prime=lambda t: -np.pi/2*torch.exp(-0.3*np.pi**2*t/4))]
        else:
            conditions = [star_condition()]
        if p == "star":
            def grid(n):
                a, b = np.meshgrid(np.linspace(-1, 1, n), np.linspace(-1, 1, n))
                pts = np.column_stack([a.ravel(), b.ravel()])
                # 原文插值域和严格六角星的交集：防止域外点污染 PDE 训练。
                tx, ty = [torch.tensor(pts[:, i:i+1]) for i in range(2)]
                m = conditions[0].in_domain(tx, ty).detach().cpu().numpy().ravel() & in_star(pts)
                pts = pts[m]
                return PredefinedGenerator(*pts.T)
            train, valid = grid(cfg["grid"]), grid(cfg["valid_grid"])
        else:
            train = Generator2D((cfg["grid"],)*2, low, high, method="equally-spaced-noisy")
            valid = Generator2D((cfg["valid_grid"],)*2, low, high, method="equally-spaced")
        cls, ranges = Solver2D, dict(xy_min=low, xy_max=high)
    def equation(*args):
        return residual(p, args[:n_funcs], args[n_funcs:])
    loss = torch.nn.L1Loss() if cfg["loss"] == "l1" else "l2"
    if cfg.get("soft"):
        # 项目新增实验：直接输出 N(t)，通过惩罚项学习 u(0)=1。
        def loss(r, funcs, coords):
            origin = torch.zeros((1, 1), device=next(nets[0].parameters()).device)
            return (r*r).mean()+cfg["penalty_weight"]*((nets[0](origin)-1)**2).mean()
    solver = cls(equation, conditions, nets=nets, optimizer=optimizer, loss_fn=loss,
                 train_generator=train, valid_generator=valid,
                 n_batches_train=1, n_batches_valid=cfg["valid_batches"], **ranges)
    # 同时检查对象身份和参数身份：尤其针对 PDF 的星形区域错误。
    assert all(a is b for a, b in zip(solver.nets, nets))
    assert {id(p) for n in nets for p in n.parameters()} == {
        id(p) for g in optimizer.param_groups for p in g["params"]}
    return solver
