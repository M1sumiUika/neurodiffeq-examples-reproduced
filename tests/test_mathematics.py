import numpy as np
import pytest
import torch
from neurodiffeq import diff
from neurodiffeq.conditions import IVP
from neurodiffeq.networks import FCNN
from ndeq_examples.runner import setup
from ndeq_examples.math import analytic, residual, errors, reference
from ndeq_examples.config import resolve
from ndeq_examples.models import build
from ndeq_examples.evaluate import boundary
from ndeq_examples.geometry import in_star, star_sample, star_vertices, star_boundary


@pytest.fixture(autouse=True)
def cpu_double():
    setup(123)


@pytest.mark.parametrize("problem", ["decay","oscillator","circle","poisson","laplace","heat","star"])
def test_analytic_satisfies_equation(problem):
    x = torch.linspace(.13, .79, 31).reshape(-1,1).requires_grad_()
    y = torch.linspace(.21, .88, 31).reshape(-1,1).requires_grad_()
    coords = [x] if problem in ("decay","oscillator","circle") else [x,y]
    values = analytic(problem, *coords, backend=torch)
    r = residual(problem, values, coords)
    assert max(v.abs().max().item() for v in r) < 1e-12


@pytest.mark.parametrize("problem", ["decay","oscillator","circle","poisson","laplace","heat","star"])
def test_analytic_satisfies_conditions(problem):
    cfg = resolve(problem if problem != "star" else "star")
    def solution(*coords):
        values = analytic(problem, *coords, backend=torch)
        return values[0] if len(values)==1 else values
    error, _ = boundary(solution, cfg)
    assert np.abs(error).max() < 1e-12


def test_hard_initial_value_and_derivative_for_arbitrary_network():
    net = FCNN()
    t = torch.zeros(5,1,requires_grad=True)
    u = IVP(0, 2, u_0_prime=-3).enforce(net,t)
    assert torch.equal(u,torch.full_like(t,2))
    assert torch.equal(diff(u,t),torch.full_like(t,-3))


@pytest.mark.parametrize("example", ["poisson","laplace","heat"])
def test_hard_pde_conditions_before_training(example):
    solver = build(resolve(example))
    solution = solver.get_solution(best=False)
    err, _ = boundary(solution, resolve(example))
    assert np.abs(err).max() < 1e-10


def test_error_metrics_and_shape_guard():
    p, t = np.array([2.,4.]), np.array([1.,2.])
    e = errors(p,t)
    assert e["max_abs"]==2
    assert e["rmse"]==pytest.approx(np.sqrt(2.5))
    assert e["relative_l2"]==1
    assert errors(np.array([1.,0.]),np.array([0.,0.]))["relative_l2"] is None
    with pytest.raises(ValueError): errors(p[:,None],t)


def test_star_sampling_and_reentrant_notches():
    points = star_sample(1000,np.random.default_rng(2))
    assert in_star(points).all()
    assert in_star(np.array([[0,0]])).all()
    assert not in_star(np.array([[.85,.85],[0.9,0.],[0.,1.01]])).any()
    v = star_vertices()
    assert len(v)==12
    assert np.isclose(np.abs(v[:,1]).max(),1)
    assert not in_star(star_boundary()).any()
    assert in_star(star_boundary(),include_boundary=True).all()


def test_lotka_numerical_reference_tolerance_check():
    values, info = reference("lotka",np.linspace(0,12,101)[:,None])
    assert np.allclose(values[0],[1.5,1.])
    assert info["convergence_max_abs"] < 1e-7
    h = (values-np.log(values)).sum(axis=1)
    assert np.max(np.abs(h-h[0])) < 1e-9

