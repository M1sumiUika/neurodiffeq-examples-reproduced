"""使用与训练/验证独立的固定随机数流验收；边界单独评估。"""
import numpy as np
import torch
from neurodiffeq import diff
from .math import errors, reference, residual
from .geometry import star_sample, star_boundary


def tensors(points):
    return [torch.tensor(points[:, i:i+1], requires_grad=True) for i in range(points.shape[1])]


def as_list(values):
    return list(values) if isinstance(values, (list, tuple)) else [values]


def to_array(values):
    return np.column_stack([v.detach().cpu().numpy().ravel() for v in as_list(values)])


def boundary(solution, cfg):
    p = cfg["problem"]
    rng = np.random.default_rng(20230404)
    if len(cfg["domain"]) == 1:
        t = torch.zeros((1, 1), requires_grad=True)
        values = as_list(solution(t))
        targets = [1.] if p == "decay" else [0.] if p == "oscillator" else [1.5, 1.] if p == "lotka" else [0., 1.]
        errors_ = [(u-v).detach().cpu().numpy().ravel() for u, v in zip(values, targets)]
        if p == "oscillator":
            errors_.append((diff(values[0], t)-1).detach().cpu().numpy().ravel())
        return np.concatenate(errors_), {"initial_max_abs": float(np.max(np.abs(np.concatenate(errors_))))}
    if p == "heat":
        x = rng.uniform(0, 2, 257)
        initial = np.column_stack([x, np.zeros_like(x)])
        initial_error = to_array(solution(*tensors(initial)))[:, 0]-np.sin(np.pi*x/2)
        t = rng.uniform(0, 3, 257)
        edges = []
        for endpoint, sign in [(0., 1.), (2., -1.)]:
            coords = tensors(np.column_stack([np.full_like(t, endpoint), t]))
            derivative = diff(solution(*coords), coords[0]).detach().cpu().numpy().ravel()
            edges.append(derivative-sign*np.pi/2*np.exp(-0.3*np.pi**2*t/4))
        return np.concatenate([initial_error, *edges]), dict(
            initial_max_abs=float(np.abs(initial_error).max()),
            neumann_max_abs=float(np.abs(np.concatenate(edges)).max()))
    if p == "star":
        # 用控制点之间的新点检验整条边，不能只检验拟合过的控制点。
        pts = star_boundary(53, 0.5)
        control = star_boundary()
        ref, _ = reference(p, control)
        cp_error = to_array(solution(*tensors(control)))-ref
        extra = {"control_point_max_abs": float(np.abs(cp_error).max())}
    else:
        v = rng.uniform(0, 1, 257)
        pts = np.vstack([np.column_stack([0*v, v]), np.column_stack([0*v+1, v]),
                         np.column_stack([v, 0*v]), np.column_stack([v, 0*v+1])])
        extra = {}
    ref, _ = reference(p, pts)
    e = (to_array(solution(*tensors(pts)))-ref).ravel()
    return e, {**extra, "boundary_max_abs": float(np.abs(e).max())}


def evaluate(solution, cfg):
    rng = np.random.default_rng(20230403)  # 与网络/训练种子无关，各模式共用基准测试流
    n = cfg["test_size"]
    if cfg["problem"] == "star":
        points = star_sample(n, rng)
    else:
        bounds = np.array(cfg.get("test_domain", cfg["domain"]))
        points = rng.uniform(bounds[:, 0], bounds[:, 1], (n, len(bounds)))
    if points.shape[1] == 1:
        points = points[np.argsort(points[:, 0])]
    preds, residuals = [], []
    for batch in np.array_split(points, max(1, (n+255)//256)):
        coords = tensors(batch)
        values = as_list(solution(*coords))
        preds.append(to_array(values))
        residuals.append(to_array(residual(cfg["problem"], values, coords)))
    pred, res = np.concatenate(preds), np.concatenate(residuals)
    ref, ref_info = reference(cfg["problem"], points)
    bc, bc_info = boundary(solution, cfg)
    metrics = {**errors(pred, ref), **bc_info,
        "condition_max_abs": float(np.abs(bc).max()),
        "residual_rmse": float(np.sqrt(np.mean(res**2))),
        "residual_max_abs": float(np.abs(res).max()),
        "per_component": [errors(pred[:, i], ref[:, i]) for i in range(pred.shape[1])],
        "reference": ref_info, "test_size": n, "test_seed": 20230403}
    # 多指标同时通过；smoke 永远不能获得数值复现通过状态。
    limits = cfg["acceptance"]
    checks = {k: metrics[k] is not None and metrics[k] <= v for k, v in limits.items()}
    metrics.update(acceptance=limits, acceptance_checks=checks,
                   numerical_pass=bool(all(checks.values()) and cfg["mode"] != "smoke"))
    data = dict(points=points, prediction=pred, reference=ref, residual=res, boundary_error=bc)
    if cfg["problem"] in ("oscillator", "circle"):
        if cfg["problem"] == "oscillator":
            c = tensors(points)
            velocity = to_array(diff(solution(*c), c[0]))[:, 0]
        else:
            velocity = pred[:, 1]
        energy = 0.5*(pred[:, 0]**2+velocity**2)
        data.update(velocity=velocity, energy=energy)
        metrics["energy_max_drift"] = float(np.abs(energy-0.5).max())
    return metrics, data

