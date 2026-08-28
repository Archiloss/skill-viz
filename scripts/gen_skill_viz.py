#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键生成 skill-viz 全部可视化(树状图+突触图+入口页)并推送 GitHub Pages。

用法: python3 ~/.hermes/scripts/gen_skill_viz.py
本脚本是权威源; repo scripts/ 中是备份快照(手动同步,勿直接改 repo 份)。
""" 
import datetime
import subprocess
import sys
import os

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
REPO = "/Users/huangqixuan/hermes_output/skill-viz"


def run(cmd, cwd=REPO):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout, end="")
    if r.stderr.strip():
        print(r.stderr, end="", file=sys.stderr)
    return r.returncode


print("== 1/3 生成树状图 + 入口页(index/skill-tree) ==")
run(f"{sys.executable} {os.path.join(SCRIPTS, 'gen_skill_tree.py')}")

print("\n== 2/3 生成突触图(skill-synapse-network) ==")
run(f"{sys.executable} {os.path.join(SCRIPTS, 'gen_skill_synapse.py')}")

print("\n== 3/3 推送 GitHub Pages ==")
date = datetime.date.today().isoformat()
git_status = subprocess.run(["git", "-C", REPO, "status", "--short"],
                            capture_output=True, text=True).stdout.strip()
if git_status:
    print("检测到改动，提交并推送…")
    run("git add -A")
    run(f"git commit -m 'feat: auto-regenerate skill-viz visualizations {date}'")
    run("git push origin main")
else:
    print("无可提交改动(skill 无变化，各图未变)")
