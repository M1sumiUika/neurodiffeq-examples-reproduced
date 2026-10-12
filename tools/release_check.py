"""发布前扫描及打包。严格排除私有材料、缓存、权重和整本PDF。"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOP={"README.md","README_EN.md","pyproject.toml","requirements-lock-cpu.txt","LICENSE",
     "THIRD_PARTY_NOTICES.md",".gitignore"}
DIRECTORIES={"src","examples","configs","notebooks","tests","docs","tools","LICENSES",".github"}
RESULT_FILES={"README.md","run_manifest.json","failure_history.json","benchmark_statistics.json",
              "benchmark_comparison.png","star_geometry_audit.json","verification.json","publication_audit.json"}
FORBIDDEN_PARTS={"__pycache__",".pytest_cache",".ipynb_checkpoints",".venv",".git","private"}


def publish_files():
    candidates=[ROOT/name for name in TOP if (ROOT/name).is_file()]
    for name in DIRECTORIES:
        candidates.extend(p for p in (ROOT/name).rglob("*") if p.is_file())
    candidates.extend(ROOT/"results"/name for name in RESULT_FILES if (ROOT/"results"/name).is_file())
    candidates.extend(p for p in (ROOT/"results/selected").rglob("*") if p.is_file())
    return sorted(p for p in candidates if not any(part in FORBIDDEN_PARTS or part.endswith(".egg-info") for part in p.relative_to(ROOT).parts))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip",action="store_true",help="生成不含环境、原始PDF和权重的发布ZIP")
    args=parser.parse_args()
    files=publish_files()
    patterns=[r"gh[pousr]_[A-Za-z0-9]{30,}",r"github_pat_[A-Za-z0-9_]{40,}",
              r"sk-[A-Za-z0-9]{30,}",r"AKIA[A-Z0-9]{16}",r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"]
    bad=[]
    for p in files:
        rel=p.relative_to(ROOT).as_posix()
        if p.suffix.lower() in {".pdf",".pt",".pth",".ckpt",".pyc",".pkl",".pickle"} or p.name.startswith(".env"):
            bad.append([rel,"forbidden artifact"])
        if p.stat().st_size>20*1024*1024: bad.append([rel,"file exceeds 20 MiB"])
        if p.suffix in {".py",".md",".json",".ipynb",".txt",".toml",".yml"}:
            text=p.read_text(encoding="utf-8")
            if any(re.search(pattern,text) for pattern in patterns): bad.append([rel,"possible credential"])
            if re.search(r"[A-Za-z]:\\+Users\\+[^\\\s]+",text): bad.append([rel,"personal absolute path"])
    if bad:
        print(json.dumps(bad,ensure_ascii=False,indent=2))
        return 1
    audit={"passed":True,"files":len(files),"total_bytes":sum(p.stat().st_size for p in files),
           "excluded":["third-party PDF","unlicensed private reference code","virtual environments",
                       "model checkpoints","original run caches","credentials","personal absolute paths"],
           "scope":"Common-pattern secret scan and explicit publish allowlist; not a security guarantee."}
    (ROOT/"results/publication_audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(audit,ensure_ascii=False,indent=2))
    if args.zip:
        target=ROOT.parent/(ROOT.name+".zip")
        with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in publish_files():
                z.write(p,arcname=ROOT.name+"/"+p.relative_to(ROOT).as_posix())
        digest=hashlib.sha256(target.read_bytes()).hexdigest()
        target.with_suffix(".zip.sha256").write_text(digest+"  "+target.name+"\n",encoding="ascii")
        print("ZIP",target.name,"bytes",target.stat().st_size,"sha256",digest)
    return 0

if __name__=="__main__":
    raise SystemExit(main())

