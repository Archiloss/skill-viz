#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 ~/hermes_output/skill-viz/skill-synapse-network.html — Skill 神经突触网络图

「改数据 → 重新生成」,禁止手动改数据。2026-08-28 恢复被 cleanup 误删的 build_synapse_v2.py。
用法: python3 ~/.hermes/scripts/gen_skill_synapse.py
自包含: 从现有 HTML 提取分类基线,实扫 skills + 重解析 skill 间引用,替换 nodes/links/标题副行。
"""
import datetime, html, os, re, json

SKILLS_ROOT = os.path.expanduser("~/.hermes/skills")
OUT = "/Users/huangqixuan/hermes_output/skill-viz/skill-synapse-network.html"

# 目录顶层 -> 语义域 (无 baseline 的新 skill / 兜底)
DIR_TO_CAT = {
    'galaxy': 'Galaxy 域', 'data-query': '数据/商品域', 'finance': '金融域',
    'openclaw-imports': '金融域', 'creative': '文档/办公域', 'productivity': '文档/办公域',
    'media': '文档/办公域', 'image-processing': '文档/办公域', 'note-taking': '文档/办公域',
    'github': '文档/办公域', 'software-development': '文档/办公域', 'web': '文档/办公域',
    'devops': 'Hermes 运维域', 'autonomous-ai-agents': 'Hermes 运维域',
    'hermes-architecture': 'Hermes 运维域',
}

# 0) 从现有 HTML 提取 v1 分类基线(id -> category)
tpl = open(OUT, encoding='utf-8').read()
BASE_CAT = {}
m = re.search(r'const nodes = (\[.*?\]);', tpl, re.DOTALL)
if m:
    for n in json.loads(m.group(1)):
        BASE_CAT[n['id']] = n['category']

# 1) 扫当前 skills(SKILL.md, 排除归档/缓存)
skills = {}
for root, dirs, files in os.walk(SKILLS_ROOT):
    if '.archive' in root or '/.git' in root or '/.cache' in root:
        continue
    if 'SKILL.md' in files:
        sid = os.path.basename(root)
        rel = os.path.relpath(root, SKILLS_ROOT)
        rdir = os.path.join(root, 'references')
        refs = len([f for f in os.listdir(rdir) if f.endswith('.md')]) if os.path.isdir(rdir) else 0
        cat = BASE_CAT.get(sid) or DIR_TO_CAT.get(rel.split('/')[0], '文档/办公域')
        skills[sid] = {'dir': rel, 'size': os.path.getsize(os.path.join(root, 'SKILL.md')),
                       'refs': refs, 'cat': cat}

nodes = [{'id': sid, 'category': s['cat'], 'refs': s['refs'], 'size': s['size']}
         for sid, s in skills.items()]
nodes.sort(key=lambda n: n['id'])

# 2) links = 基线(现有 HTML 的人工精选突触,过滤失效目标) ∪ 自动解析新增
skill_ids = set(skills.keys())
link_set = set()
ml = re.search(r'const links = (\[.*?\]);', tpl, re.DOTALL)
if ml:
    for l in json.loads(ml.group(1)):
        a, b = l['source'], l['target']
        if a in skill_ids and b in skill_ids:
            link_set.add((a, b))
# 自动解析 SKILL.md 里 `skill X` 引用,补充基线没覆盖的新边
for sid, s in skills.items():
    skfile = os.path.join(SKILLS_ROOT, s['dir'], 'SKILL.md')
    try:
        text = open(skfile, encoding='utf-8').read()
    except Exception:
        continue
    for mt in re.finditer(r'skill\s+`?([a-z][a-z0-9-]{2,})`?', text):
        tgt = mt.group(1)
        if tgt in skill_ids and tgt != sid:
            link_set.add((sid, tgt))
links = [{'source': a, 'target': b} for a, b in sorted(link_set)]

# 3) 统计
nodes_n = len(nodes)
link_directed = len(link_set)
uniq_pairs = len(set((min(a, b), max(a, b)) for a, b in link_set))
deg = {s: 0 for s in skill_ids}
for a, b in link_set:
    deg[a] += 1
    deg[b] += 1
hubs = sum(1 for sid in skills if max(skills[sid]['refs'], deg[sid]) >= 15)
others = nodes_n - hubs
per_cat = {}
for n in nodes:
    per_cat[n['category']] = per_cat.get(n['category'], 0) + 1
sub = (f"{nodes_n} 节点 · {uniq_pairs} 突触连接 · {hubs} 核心 / {others} 其他 · 更新于 {datetime.date.today().isoformat()} · "
       + "｜".join(f"{c} {n}" for c, n in per_cat.items()))

# 4) 替换 nodes/links/标题副行
tpl = re.sub(r'const nodes = \[.*?\];',
             'const nodes = ' + json.dumps(nodes, ensure_ascii=False) + ';',
             tpl, flags=re.DOTALL)
tpl = re.sub(r'const links = \[.*?\];',
             'const links = ' + json.dumps(links, ensure_ascii=False) + ';',
             tpl, flags=re.DOTALL)
tpl = re.sub(r'(<div class="sub">).*?(</div>)',
             lambda mm: mm.group(1) + html.escape(sub) + mm.group(2),
             tpl, flags=re.DOTALL)
open(OUT, 'w', encoding='utf-8').write(tpl)

print(f"written: {OUT}")
print(f"nodes={nodes_n} links(有向)={link_directed} uniq 无向={uniq_pairs} hubs={hubs}/{others}")
print(f"sub: {sub}")
