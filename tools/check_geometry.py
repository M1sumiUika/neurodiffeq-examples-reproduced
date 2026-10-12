"""量化原文插值域与真正六角星的差异；不修改问题。"""
from pathlib import Path
import numpy as np
import torch
from ndeq_examples.runner import setup,write_json
from ndeq_examples.models import star_condition
from ndeq_examples.geometry import in_star

root=Path(__file__).resolve().parents[1]
setup(42)
condition=star_condition()
rows=[]
for n in [32,100,201]:
    x,y=np.meshgrid(np.linspace(-1,1,n),np.linspace(-1,1,n))
    p=np.column_stack([x.ravel(),y.ravel()])
    exact=in_star(p)
    closure=in_star(p,include_boundary=True)
    parts=[]
    for batch in np.array_split(p,max(1,len(p)//1024)):
        a,b=[torch.tensor(batch[:,i:i+1]) for i in range(2)]
        parts.append(condition.in_domain(a,b).detach().cpu().numpy().ravel())
    approximate=np.concatenate(parts)
    rows.append(dict(grid=n,polygon_interior=int(exact.sum()),interpolated_interior=int(approximate.sum()),
                     interpolated_outside_polygon=int((approximate&~closure).sum()),
                     interpolated_boundary_points=int((approximate&closure&~exact).sum()),
                     polygon_missed_by_interpolant=int((exact&~approximate).sum()),
                     intersection=int((exact&approximate).sum())))
write_json(root/"results/star_geometry_audit.json",rows)
print(rows)

