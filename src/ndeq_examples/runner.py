"""独立运行目录、原子状态写入、定期检查点、真实失败日志。"""
import copy
import hashlib
import importlib.metadata
import json
import platform
import random
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from importlib.resources import files
import numpy as np
import torch
import neurodiffeq
from neurodiffeq.utils import set_tensor_type
from .config import resolve
from .models import build
from .evaluate import evaluate, to_array, tensors
from .plotting import plots


def write_json(path, obj):
    path = Path(path)
    temp = path.with_suffix(path.suffix+".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    temp.replace(path)


def environment():
    names = ["torch", "neurodiffeq", "numpy", "scipy", "matplotlib", "pandas", "pillow"]
    return {"python": platform.python_version(), "platform": platform.platform(),
            "packages": {n: importlib.metadata.version(n) for n in names},
            "neurodiffeq_module_version": neurodiffeq.__version__}


def setup(seed, device="cpu"):
    set_tensor_type(device=device, float_bits=64)
    torch.set_num_threads(1)
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if device == "cuda":
        torch.cuda.manual_seed_all(seed)


def checkpoint(out, solver, cfg):
    state = dict(config=cfg, epoch=solver.global_epoch,
        nets=[n.state_dict() for n in solver.nets],
        best_nets=[n.state_dict() for n in (solver.best_nets or solver.nets)],
        optimizer=solver.optimizer.state_dict(), history=solver.metrics_history,
        lowest_loss=solver.lowest_loss, rng_torch=torch.get_rng_state(),
        rng_numpy=np.random.get_state(), rng_python=random.getstate())
    temp = out/"checkpoint.tmp"
    torch.save(state, temp)
    temp.replace(out/"checkpoint.pt")
    write_json(out/"history.json", solver.metrics_history)
    write_json(out/"progress.json", {"epoch": solver.global_epoch, "target": cfg["epochs"]})


def fingerprint(cfg):
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()


def run(example, mode="smoke", seed=42, root="results/runs", variant="default", device="cpu", resume_from=None):
    cfg = resolve(example, mode, seed, variant)
    cfg["device"] = device
    setup(seed, device)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out = Path(root)/f"{stamp}_{example}_{mode}_s{seed}_{variant}_{uuid.uuid4().hex[:6]}"
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    state = dict(example=example, mode=mode, seed=seed, variant=variant, status="running",
                 started_utc=stamp, config_hash=fingerprint(cfg), environment=environment())
    write_json(out/"config.json", cfg)  # 训练前先落盘，包括验收阈值
    if "problem" in cfg:
        problems = json.loads(files("ndeq_examples").joinpath("problems.json").read_text(encoding="utf-8"))
        write_json(out/"problem.json", problems[cfg["problem"]])
    write_json(out/"status.json", state)
    try:
        if cfg.get("kind") == "snippet":
            from .snippets import run_snippet
            report = run_snippet(cfg, out)
            write_json(out/"metrics.json", report)
            state.update(status="snippet_verified", numerical_pass=None)
        else:
            warmup = None
            if cfg["warmup_epochs"] and not resume_from:
                warmcfg = copy.deepcopy(cfg)
                warmcfg.update(domain=[[0, 12]], epochs=cfg["warmup_epochs"], warmup_epochs=0)
                warmup = build(warmcfg)
                warmdir = out/"warmup"
                warmdir.mkdir()
                write_json(warmdir/"config.json", warmcfg)
                def warm_cb(s):
                    if s.global_epoch % cfg["checkpoint_every"] == 0:
                        checkpoint(warmdir, s, warmcfg)
                warmup.fit(cfg["warmup_epochs"], callbacks=[warm_cb], tqdm_file=None)
                checkpoint(warmdir, warmup, warmcfg)
            solver = build(cfg, existing_nets=warmup.nets if warmup else None)
            if resume_from:
                # 只加载自己生成的本地检查点；不接受网上下载的不可信 pickle。
                saved = torch.load(Path(resume_from)/"checkpoint.pt", map_location=device, weights_only=False)
                if saved["config"] != cfg:
                    raise ValueError("检查点配置不一致，拒绝混合实验")
                for net, weights in zip(solver.nets, saved["nets"]): net.load_state_dict(weights)
                solver.best_nets = copy.deepcopy(solver.nets)
                for net, weights in zip(solver.best_nets, saved["best_nets"]): net.load_state_dict(weights)
                solver.optimizer.load_state_dict(saved["optimizer"])
                solver.metrics_history = saved["history"]
                solver.lowest_loss = saved["lowest_loss"]
                torch.set_rng_state(saved["rng_torch"].cpu())
                np.random.set_state(saved["rng_numpy"]); random.setstate(saved["rng_python"])
                state["resumed_from"] = str(resume_from)
            # 采样快照不改变训练随机数流。
            rngstate = torch.get_rng_state()
            samples = {}
            for phase in ("train", "valid"):
                values = solver.generator[phase].get_examples()
                samples[phase] = to_array(values)
            torch.set_rng_state(rngstate)
            np.savez_compressed(out/"sampling.npz", **samples)
            def cb(s):
                if not np.isfinite(s.metrics_history["train_loss"][-1]):
                    raise FloatingPointError("训练损失非有限数")
                if s.global_epoch % cfg["checkpoint_every"] == 0:
                    checkpoint(out, s, cfg)
            train_start = time.perf_counter()
            if cfg.get("legacy"):
                from neurodiffeq.ode import solve_system
                import warnings
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    solution, history, internal = solve_system(
                        solver.diff_eqs, solver.conditions, t_min=cfg["domain"][0][0],
                        t_max=cfg["domain"][0][1], nets=solver.nets, optimizer=solver.optimizer,
                        train_generator=solver.generator["train"], valid_generator=solver.generator["valid"],
                        n_batches_valid=cfg["valid_batches"], max_epochs=cfg["epochs"],
                        return_internal=True, return_best=False)
                write_json(out/"legacy_warnings.json", sorted(set(str(w.message) for w in caught)))
                write_json(out/"internals.json", {k: type(v).__name__ for k, v in internal.items()})
                solver.metrics_history = history
                solver.best_nets = copy.deepcopy(solver.nets)
            else:
                callbacks = [cb]
                if cfg.get("monitor"):
                    from neurodiffeq.monitors import Monitor1D
                    monitor = Monitor1D(t_min=0., t_max=2., check_every=100)
                    callbacks.append(monitor.to_callback(fig_dir=str(out/"monitor")))
                solver.fit(max(0, cfg["epochs"]-solver.global_epoch), callbacks=callbacks, tqdm_file=None)
                solution = solver.get_solution(best=cfg["best"])
                history = solver.metrics_history
                write_json(out/"internals.json", {k: type(v).__name__ for k, v in solver.get_internals().items()})
            state["training_seconds"] = time.perf_counter()-train_start
            checkpoint(out, solver, cfg)
            metrics, data = evaluate(solution, cfg)
            write_json(out/"metrics.json", metrics)
            np.savez_compressed(out/"test_data.npz", **data)
            plots(out, solution, cfg, metrics, data, history)
            state.update(status="smoke_passed" if mode == "smoke" else "full_training_finished",
                         numerical_pass=metrics["numerical_pass"], epochs_completed=solver.global_epoch)
        state["elapsed_seconds"] = time.perf_counter()-started
        write_json(out/"status.json", state)
        print(f"{example}: {state['status']}; numerical_pass={state.get('numerical_pass')}; {out}", flush=True)
        return out
    except BaseException as exc:
        state.update(status="interrupted" if isinstance(exc, KeyboardInterrupt) else "failed",
                     elapsed_seconds=time.perf_counter()-started, error=f"{type(exc).__name__}: {exc}")
        write_json(out/"status.json", state)
        (out/"failure.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
