"""方程和参考解。残差是微分算子的输出，解误差是预测与参考之差。"""
import numpy as np
import torch
from neurodiffeq import diff
from scipy.integrate import solve_ivp


def residual(problem, values, coords):
    u = values[0]
    x = coords[0]
    if problem == "decay":
        return [diff(u, x) + u]
    if problem == "oscillator":
        return [diff(u, x, order=2) + u]
    if problem == "circle":
        return [diff(u, x) - values[1], diff(values[1], x) + u]
    if problem == "lotka":
        v = values[1]
        return [diff(u, x) - u + u*v, diff(v, x) - u*v + v]
    y = coords[1]
    if problem == "heat":
        return [diff(u, y) - 0.3*diff(u, x, order=2)]
    lap = diff(u, x, order=2) + diff(u, y, order=2)
    if problem == "laplace":
        return [lap]
    if problem == "poisson":
        forcing = 2*x*(y-1)*(y-2*x+x*y+2)*torch.exp(x-y)
        return [lap - forcing]
    if problem == "star":
        return [lap + torch.exp(u) - 1 - x*x - y*y - 4/(1+x*x+y*y)**2]
    raise ValueError(problem)


def analytic(problem, *coords, backend=np):
    """同一公式支持 numpy 作图和 torch 自动微分验算。"""
    x = coords[0]
    if problem == "decay":
        return [backend.exp(-x)]
    if problem == "oscillator":
        return [backend.sin(x)]
    if problem == "circle":
        return [backend.sin(x), backend.cos(x)]
    y = coords[1]
    if problem == "laplace":
        return [backend.sin(np.pi*y)*backend.sinh(np.pi*(1-x))/np.sinh(np.pi)]
    if problem == "poisson":
        return [x*(1-x)*y*(1-y)*backend.exp(x-y)]
    if problem == "heat":
        return [backend.sin(np.pi*x/2)*backend.exp(-0.3*np.pi**2*y/4)]
    if problem == "star":
        return [backend.log(1+x*x+y*y)]
    raise ValueError(problem)


def reference(problem, coords):
    if problem != "lotka":
        return np.column_stack(analytic(problem, *coords.T)), {"kind": "analytic"}
    def rhs(t, z):
        u, v = z
        return [u-u*v, u*v-v]
    # 独立的两组容差；不能将数值积分称为精确解。
    coarse = solve_ivp(rhs, (0, 12), [1.5, 1.0], method="DOP853",
                       rtol=1e-9, atol=1e-11, dense_output=True)
    fine = solve_ivp(rhs, (0, 12), [1.5, 1.0], method="DOP853",
                     rtol=1e-11, atol=1e-13, dense_output=True)
    if not (coarse.success and fine.success):
        raise RuntimeError("数值参考积分失败")
    delta = float(np.max(np.abs(coarse.sol(coords[:, 0])-fine.sol(coords[:, 0]))))
    if delta > 1e-7:
        raise RuntimeError("数值参考解的容差收敛检查未通过")
    return fine.sol(coords[:, 0]).T, dict(kind="numerical DOP853", rtol=1e-11,
             atol=1e-13, check_rtol=1e-9, check_atol=1e-11, convergence_max_abs=delta)


def errors(prediction, target):
    p, t = np.asarray(prediction), np.asarray(target)
    if p.shape != t.shape:
        raise ValueError(f"形状不一致，禁止广播误算: {p.shape} != {t.shape}")
    d = p-t
    norm = np.linalg.norm(t)
    return dict(max_abs=float(np.max(np.abs(d))), rmse=float(np.sqrt(np.mean(d*d))),
                relative_l2=float(np.linalg.norm(d)/norm) if norm else None)

