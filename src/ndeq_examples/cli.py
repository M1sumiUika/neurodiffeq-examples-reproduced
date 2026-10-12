"""python -m ndeq_examples 或安装后的 ndeq 命令。"""
import argparse
import json
from pathlib import Path
from .config import catalog, resolve
from .runner import run, fingerprint, write_json


def summarize(root):
    rows = []
    for p in sorted(Path(root).glob("*/status.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        mpath = p.parent/"metrics.json"
        m = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else {}
        rows.append({**s, "directory": str(p.parent), "metrics": m})
    write_json(Path(root)/"summary.json", rows)
    lines = ["# 实际运行清单", "", "smoke 只表示流程通过；数值通过须同时满足预先写入配置的验收线。", "",
             "|示例|模式|种子|对照|状态|数值通过|RMSE|残差 RMSE|条件误差|秒|", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        m = r["metrics"]
        def fmt(k):
            v = m.get(k)
            return f"{v:.3g}" if isinstance(v, (int, float)) else "—"
        lines.append(f"|{r['example']}|{r['mode']}|{r['seed']}|{r.get('variant')}|{r['status']}|{r.get('numerical_pass')}|{fmt('rmse')}|{fmt('residual_rmse')}|{fmt('condition_max_abs')}|{r.get('elapsed_seconds',0):.1f}|")
    (Path(root)/"summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("\n".join(lines))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description="NeuroDiffEq 文档示例复现与数值验证")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="列出全部独立配置")
    s = sub.add_parser("summarize", help="汇总已有真实结果")
    s.add_argument("--root", default="results/runs")
    r = sub.add_parser("run", help="运行一个示例、一章或全部示例")
    sel = r.add_mutually_exclusive_group(required=True)
    sel.add_argument("--example", choices=list(catalog()))
    sel.add_argument("--chapter", type=int, choices=range(1,6))
    sel.add_argument("--all", action="store_true")
    r.add_argument("--mode", choices=["smoke","reproduction","benchmark"], default="smoke")
    r.add_argument("--seeds", nargs="+", type=int, default=None)
    r.add_argument("--variants", nargs="+", choices=["default","wide","uniform","soft"], default=["default"])
    r.add_argument("--root", default="results/runs")
    r.add_argument("--device", choices=["cpu","cuda"], default="cpu")
    r.add_argument("--resume", action="store_true", help="跳过相同配置的已完成项；失败项重跑")
    r.add_argument("--resume-from", help="从自己生成的本地检查点续训，输出仍保存到新目录")
    args = parser.parse_args(argv)
    if args.command == "list":
        for key, c in catalog().items():
            print(f"{key:22} ch{','.join(map(str,c['chapters'])):6} {c['title']}")
        return 0
    if args.command == "summarize":
        Path(args.root).mkdir(parents=True, exist_ok=True)
        summarize(args.root)
        return 0
    seeds = args.seeds or ([42,43,44] if args.mode == "benchmark" else [42])
    if args.mode == "benchmark" and len(set(seeds)) < 3:
        parser.error("benchmark 必须至少有 3 个不同随机种子")
    selected = [args.example] if args.example else [k for k,c in catalog().items() if args.all or args.chapter in c["chapters"]]
    if args.resume_from and (len(selected)!=1 or len(seeds)!=1 or len(args.variants)!=1):
        parser.error("--resume-from 只用于单个实验")
    failures = []
    for name in selected:
        for variant in args.variants:
            for seed in seeds:
                if args.resume:
                    cfg = resolve(name, args.mode, seed, variant); cfg["device"] = args.device
                    done = False
                    for p in Path(args.root).glob("*/status.json"):
                        state = json.loads(p.read_text(encoding="utf-8"))
                        if state.get("config_hash") == fingerprint(cfg) and state["status"] in ("smoke_passed","full_training_finished","snippet_verified"):
                            done = True; break
                    if done:
                        print(f"跳过已完成配置: {name}/{variant}/{seed}"); continue
                try:
                    run(name, args.mode, seed, args.root, variant, args.device, args.resume_from)
                except Exception as exc:
                    failures.append(f"{name}: {exc}")
                    print(f"FAILED {failures[-1]}", flush=True)
    summarize(args.root)
    return 1 if failures else 0

