"""全部图来自实际计算。英文轴标保证不同系统无中文字体也可读。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
from .geometry import in_star, star_boundary, star_vertices
from .math import reference
from .evaluate import tensors, to_array

plt.rcParams.update({"figure.dpi": 120, "axes.grid": True, "grid.alpha": 0.2,
                     "savefig.bbox": "tight", "font.size": 10})


def save(fig, path):
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plots(out, solution, cfg, metrics, data, history):
    fig, ax = plt.subplots(figsize=(7, 4))
    for key in ("train_loss", "valid_loss"):
        ax.semilogy(np.arange(1, len(history[key])+1), history[key], label=key)
    ax.set(xlabel="Epoch", ylabel="Loss (training objective)", title=f"{cfg['id']} / {cfg['mode']} / seed {cfg['seed']}")
    ax.legend()
    save(fig, out/"loss.png")
    p = cfg["problem"]
    pts, pred, ref = [data[k] for k in ("points", "prediction", "reference")]
    if pts.shape[1] == 1:
        t = pts[:, 0]
        fig, axes = plt.subplots(1, 3, figsize=(14, 4))
        for i in range(pred.shape[1]):
            axes[0].plot(t, pred[:, i], label=f"NN {i+1}")
            axes[0].plot(t, ref[:, i], "--", label=f"Reference {i+1}")
            axes[1].plot(t, pred[:, i]-ref[:, i], label=f"error {i+1}")
            axes[2].plot(t, data["residual"][:, i], label=f"residual {i+1}")
        for ax, title in zip(axes, ("Solution", "Solution error", "Equation residual")):
            ax.set(xlabel="t", title=title)
            ax.legend()
        save(fig, out/"solution.png")
        if p in ("oscillator", "circle", "lotka"):
            fig, axes = plt.subplots(1, 2, figsize=(10, 4))
            v = data.get("velocity", pred[:, -1])
            axes[0].plot(pred[:, 0], v, label="NN")
            vr = np.cos(t) if p == "oscillator" else ref[:, 1]
            axes[0].plot(ref[:, 0], vr, "--", label="Reference")
            axes[0].set(xlabel="u / prey", ylabel="velocity / predator", title="Phase portrait")
            axes[0].legend()
            if p == "lotka":
                # H=u-log(u)+v-log(v)；非正预测值不能取对数。
                h = np.full(len(t), np.nan)
                good = (pred > 0).all(axis=1)
                h[good] = (pred[good]-np.log(pred[good])).sum(axis=1)
                axes[1].plot(t, h-(2.5-np.log(1.5)))
                axes[1].set(ylabel="H(t)-H(0)", title="Population invariant drift")
            else:
                axes[1].plot(t, data["energy"]-0.5)
                axes[1].set(ylabel="E(t)-0.5", title="Energy drift")
            axes[1].set_xlabel("t")
            save(fig, out/"phase_energy.png")
        return
    n = 65
    bounds = np.array(cfg["domain"])
    xx, yy = np.meshgrid(np.linspace(*bounds[0], n), np.linspace(*bounds[1], n))
    grid = np.column_stack([xx.ravel(), yy.ravel()])
    mask = in_star(grid) if p == "star" else np.ones(len(grid), dtype=bool)
    active = grid[mask]
    z = np.concatenate([to_array(solution(*tensors(chunk)))[:, 0]
                        for chunk in np.array_split(active, max(1, len(active)//256))])
    exact, _ = reference(p, active)
    fields = []
    for values in (z, exact[:, 0], np.abs(z-exact[:, 0])):
        a = np.full(len(grid), np.nan)
        a[mask] = values
        fields.append(a.reshape(xx.shape))
    np.savez_compressed(out/"plot_grid.npz", x=xx, y=yy, prediction=fields[0], reference=fields[1], absolute_error=fields[2])
    lo, hi = min(z.min(), exact.min()), max(z.max(), exact.max())
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), constrained_layout=True)
    for i, (ax, f, title) in enumerate(zip(axes, fields, ("NN prediction", "Analytical reference", "Absolute solution error"))):
        im = ax.pcolormesh(xx, yy, f, shading="auto", cmap="viridis" if i < 2 else "magma",
                           vmin=lo if i < 2 else 0, vmax=hi if i < 2 else None)
        fig.colorbar(im, ax=ax)
        ax.set(xlabel="x", ylabel="t" if p == "heat" else "y", title=title)
        ax.grid(False)
        if p == "star":
            v = star_vertices()
            ax.plot(*np.vstack([v, v[0]]).T, color="black", lw=0.8)
            ax.set_aspect("equal")
    fig.savefig(out/"solution.png")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 5))
    sc = ax.scatter(*pts.T, c=np.abs(data["residual"][:, 0]), s=6, cmap="magma")
    fig.colorbar(sc, ax=ax, label="Absolute equation residual")
    ax.set(xlabel="x", ylabel="t" if p == "heat" else "y", title="Independent interior test points")
    save(fig, out/"residual.png")
    if p == "star":
        fig, ax = plt.subplots(figsize=(6, 6))
        samples = np.load(out/"sampling.npz")
        ax.scatter(*samples["train"].T, s=8, label="Training points")
        ax.scatter(*star_boundary().T, s=9, label="Boundary controls")
        v = star_vertices()
        ax.plot(*np.vstack([v, v[0]]).T, color="black", lw=1)
        ax.set(xlabel="x", ylabel="y", title="Hexagram domain and actual samples", aspect="equal")
        ax.legend()
        save(fig, out/"domain.png")
    if p == "heat":
        # 31 帧，使用 Pillow 写 GIF，避免依赖 FFmpeg。
        xs, ts = np.linspace(0, 2, 101), np.linspace(0, 3, 31)
        frames = []
        for t in ts:
            points = np.column_stack([xs, np.full_like(xs, t)])
            frames.append(to_array(solution(*tensors(points)))[:, 0])
        frames = np.array(frames)
        refs = np.sin(np.pi*xs[None, :]/2)*np.exp(-0.3*np.pi**2*ts[:, None]/4)
        np.savez_compressed(out/"animation_data.npz", x=xs, t=ts, prediction=frames, reference=refs)
        fig, ax = plt.subplots(figsize=(7, 4))
        a, = ax.plot([], [], label="NN")
        b, = ax.plot([], [], "--", label="Analytical")
        ax.set(xlim=(0, 2), ylim=(min(-0.05, frames.min()), max(1.05, frames.max())), xlabel="x", ylabel="u")
        ax.legend()
        def update(i):
            a.set_data(xs, frames[i]); b.set_data(xs, refs[i])
            ax.set_title(f"Heat equation: t={ts[i]:.2f}")
            return a, b
        anim = FuncAnimation(fig, update, frames=len(ts), interval=100)
        anim.save(out/"heat.gif", writer=PillowWriter(fps=10))
        plt.close(fig)

