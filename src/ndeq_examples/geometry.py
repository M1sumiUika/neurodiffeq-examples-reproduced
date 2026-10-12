"""按 PDF 的十二条边构造六角星；几何判断不依赖边界插值的符号。"""
import numpy as np
from matplotlib.path import Path


def star_vertices():
    point = np.array([0., -1.])
    theta = 2*np.pi/3
    length = 2/np.sin(np.pi/3)/4
    vertices = []
    for edge in range(12):
        vertices.append(point.copy())
        point += length*np.array([np.cos(theta), np.sin(theta)])
        theta += np.pi/3 if edge % 2 == 0 else -2*np.pi/3
    assert np.allclose(point, vertices[0])
    return np.array(vertices)


def star_boundary(n_per_edge=10, offset=0.):
    v = star_vertices()
    f = (np.arange(n_per_edge)+offset)/n_per_edge
    return np.concatenate([a[None, :]+f[:, None]*(b-a) for a, b in zip(v, np.roll(v, -1, axis=0))])


def in_star(points, include_boundary=False):
    # 显式首尾闭合，不将凹星形误当成凸包。
    # 原文顺序为顺时针；Path 的负 radius 对逆时针轮廓才表示向内缩。
    # 反转后明确排除边界本身，边界在 evaluate.boundary 中独立检验。
    v = star_vertices()[::-1]
    radius = 1e-12 if include_boundary else -1e-12
    return Path(np.vstack([v, v[0]])).contains_points(np.asarray(points), radius=radius)


def star_sample(n, rng):
    parts = []
    while sum(len(p) for p in parts) < n:
        p = rng.uniform(-1, 1, (max(n*2, 128), 2))
        parts.append(p[in_star(p)])
    return np.concatenate(parts)[:n]

