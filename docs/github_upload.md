# 上传到 GitHub（私有仓库）

本次未检测到可用的 GitHub 认证，未创建任何远程仓库，也未冒用作者信息或生成虚构 Git 历史。你可以先在 GitHub 网页创建名为 `neurodiffeq-examples-reproduced` 的 **Private** 空仓库，不勾选自动生成 README。

在本地项目根目录用 PowerShell 执行：

```powershell
python tools/release_check.py
git init -b main
git add .
git status --short
git diff --cached --stat
# 使用你自己的姓名与邮箱；不要照抄别人的身份。
git config user.name "你的 GitHub 显示名"
git config user.email "你的 GitHub noreply 邮箱"
git commit -m "Add reproduced documentation examples and numerical validation"
git remote add origin https://github.com/你的用户名/neurodiffeq-examples-reproduced.git
git push -u origin main
```

也可以用 GitHub Desktop：Add existing repository → Publish repository → 勾选 Keep this code private。

首次提交只应包含源码、配置、Notebook、文档、依赖锁、许可证、CI及 `results/selected` 的真实图表和小型数据。`.gitignore` 排除 `.venv`、私有参考材料、整本PDF、权重、缓存和原始实验目录。`results/run_manifest.json`保留原始失败的状态，精选结果目录同时保留数值未达标实验。

`release_check.py`检查发布文件中的常见密钥格式、绝对用户路径、PDF和大型文件。它不是安全审计保证；上传前仍应阅读暂存文件列表。不要把 `.env`、Git凭据或“大创1.py”等授权尚未核实的个人材料加入仓库。

