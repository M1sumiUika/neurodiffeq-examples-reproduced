"""在独立内核中执行每份 Notebook，成功后保存真实输出。"""
from pathlib import Path
import nbformat
from nbclient import NotebookClient
import argparse
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument("--pattern",default="*.ipynb")
args=p.parse_args()
for path in sorted((root/"notebooks").glob(args.pattern)):
    nb=nbformat.read(path,as_version=4)
    NotebookClient(nb,timeout=300,kernel_name="python3",resources={"metadata":{"path":str(root)}}).execute()
    # 去除运行路径里的私人用户名；保留可复核的相对运行路径。
    for cell in nb.cells:
        for output in cell.get("outputs",[]):
            if "text" in output:
                output["text"]=output["text"].replace(str(root),"<PROJECT_ROOT>")
    nbformat.write(nb,path)
    print("EXECUTED",path.name,flush=True)

