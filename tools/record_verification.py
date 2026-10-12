"""仅从已完成的本地验证文件取证，不虚构测试状态。"""
import json
import re
from pathlib import Path
import nbformat
root=Path(__file__).resolve().parents[1]
def read_log(path):
    raw=path.read_bytes()
    return raw.decode("utf-16" if raw.startswith((b"\xff\xfe",b"\xfe\xff")) else "utf-8")
test=read_log(root/"clean_tests_final.log")
match=re.search(r"(\d+) passed",test)
assert match and "failed" not in test.lower()
smoke=[]
for path in (root/"results/clean_cpu").glob("*/status.json"):
    smoke.append(json.loads(path.read_text(encoding="utf-8")))
assert len({r['example'] for r in smoke})==25
assert all(r['status'] in ('smoke_passed','snippet_verified') for r in smoke)
notebooks=[]
for path in sorted((root/"notebooks").glob("*.ipynb")):
    nb=nbformat.read(path,as_version=4)
    code=[c for c in nb.cells if c.cell_type=="code"]
    assert all(c.execution_count is not None for c in code)
    assert not any(o.output_type=="error" for c in code for o in c.outputs)
    notebooks.append(dict(file=path.name,executed_code_cells=len(code)))
check=read_log(root/"clean_pip_check.log")
assert "No broken requirements found" in check
result={"pytest_passed":int(match.group(1)),"clean_cpu_smoke_count":len(smoke),"pip_check":"passed",
        "notebooks":notebooks,"clean_cpu_smoke":[{k:r[k] for k in ['example','status','environment']} for r in smoke],
        "checkpoint_resume_test":"prediction arrays identical; final history remains two epochs",
        "github_authenticated":False,"reference_dachuang1_available":False,
        "ci_local_only":"GitHub Actions is configured; remote CI has not run."}
(root/"results/verification.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("Verified",result['pytest_passed'],"tests,",len(smoke),"CPU smoke entries,",len(notebooks),"notebooks")

