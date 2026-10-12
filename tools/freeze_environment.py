"""在选定环境中导出依赖；不把本地 editable 绝对路径写进仓库。"""
import importlib.metadata as metadata
import json
import platform
from pathlib import Path
from ndeq_examples.runner import environment

root=Path(__file__).resolve().parents[1]
rows=[]
for d in metadata.distributions():
    name=d.metadata["Name"]
    if name.lower().replace("_","-")=="neurodiffeq-examples-reproduced": continue
    line=f"{name}=={d.version}"
    if name.lower() in ("pywin32","pywinpty"): line+='; sys_platform == "win32"'
    rows.append(line)
header="# 实际纯CPU环境依赖快照；Python "+platform.python_version()+"\n--extra-index-url https://download.pytorch.org/whl/cpu\n"
(root/"requirements-lock-cpu.txt").write_text(header+"\n".join(sorted(set(rows),key=str.lower))+"\n-e .\n",encoding="utf-8")
(root/"docs/environment_cpu.json").write_text(json.dumps(environment(),ensure_ascii=False,indent=2),encoding="utf-8")
print("Locked",len(rows),"distributions")

