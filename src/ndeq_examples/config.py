"""明确记录原文配置和模式变更，不根据训练结果改变验收线。"""
import copy
import json
from importlib.resources import files


def catalog():
    return json.loads(files("ndeq_examples").joinpath("catalog.json").read_text(encoding="utf-8"))


def resolve(example, mode="smoke", seed=42, variant="default"):
    cfg = copy.deepcopy(catalog()[example])
    cfg.update(id=example, mode=mode, seed=seed, variant=variant)
    cfg.setdefault("hidden", [32, 32])
    cfg.setdefault("activation", "Tanh")
    cfg.setdefault("lr", 0.001)
    cfg.setdefault("optimizer", "Adam")
    cfg.setdefault("loss", "mse")
    cfg.setdefault("train_size", 32)
    cfg.setdefault("valid_size", 32)
    cfg.setdefault("sampling", "equally-spaced-noisy")
    cfg.setdefault("valid_batches", 4)
    cfg.setdefault("best", True)
    cfg.setdefault("grid", 32)
    cfg.setdefault("valid_grid", cfg["grid"])
    cfg.setdefault("warmup_epochs", 0)
    cfg.setdefault("test_size", 2048)
    cfg.setdefault("checkpoint_every", 100)
    if mode == "smoke":
        cfg.update(epochs=2, warmup_epochs=min(2, cfg["warmup_epochs"]),
                   train_size=16, valid_size=16, grid=8, valid_grid=10,
                   valid_batches=1, test_size=256)
    if mode == "benchmark":
        if variant == "wide":
            cfg["hidden"] = [64, 64]
        elif variant == "uniform":
            cfg.update(sampling="uniform", train_size=64, valid_size=128)
        elif variant == "soft":
            if cfg.get("problem") != "decay":
                raise ValueError("soft 对照仅用于指数衰减")
            cfg.update(soft=True, penalty_weight=1.0)
        elif variant != "default":
            raise ValueError(f"未知对照 {variant}")
    elif variant != "default":
        raise ValueError("variant 仅用于 benchmark")
    return cfg

