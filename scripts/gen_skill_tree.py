#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 ~/hermes_output/skill-tree.html — Hermes Skill 体系树状架构图
用法: python3 ~/.hermes/scripts/gen_skill_tree.py
「改数据 → 重新生成」,禁止手动改 SVG。
"""
import datetime, html, os, re, json

UPDATED = datetime.date.today().isoformat()  # 生成日期,用于图/入口页"更新于"标注

NODE_W, NODE_H, H_GAP, V_GAP = 340, 44, 28, 14
MARGIN = 24

# 颜色: emerald=大索引 / cyan=标准 / amber=待瘦身(当前无) / rose=异常 / slate=普通 / violet=专项
COLORS = {
    "emerald": ("#34d399", "rgba(6,78,59,0.45)"),
    "cyan":    ("#22d3ee", "rgba(8,51,68,0.5)"),
    "amber":   ("#fbbf24", "rgba(120,53,15,0.4)"),
    "rose":    ("#fb7185", "rgba(136,19,55,0.4)"),
    "slate":   ("#94a3b8", "rgba(30,41,59,0.5)"),
    "violet":  ("#a78bfa", "rgba(76,29,149,0.4)"),
}

def N(label, sub="", color="slate", children=None):
    return {"label": label, "sub": sub, "color": color, "children": children or []}

# ============ refs 实扫（点击节点 → 显示该 skill 的 references 列表） ============
SKILLS_ROOT = os.path.expanduser("~/.hermes/skills")
_skill_dirs = {}
for _root, _dirs, _files in os.walk(SKILLS_ROOT):
    if "SKILL.md" in _files:
        _skill_dirs[os.path.basename(_root)] = _root

def _norm_label(s):
    return re.sub(r"[⭐✅🛡️⚠️\s]+", "", s)

def refs_of(label):
    """返回该节点对应 skill 的 references 列表; 无对应 skill 返回 None"""
    key = _norm_label(label)
    d = _skill_dirs.get(key) or _skill_dirs.get(label)
    if not d:
        return None
    rdir = os.path.join(d, "references")
    if not os.path.isdir(rdir):
        return []
    out = []
    for fn in sorted(os.listdir(rdir)):
        if not fn.endswith(".md"):
            continue
        fp = os.path.join(rdir, fn)
        try:
            sz = os.path.getsize(fp)
            lines = sum(1 for _ in open(fp, encoding="utf-8"))
        except Exception:
            sz, lines = 0, 0
        out.append({"name": fn, "size": sz, "lines": lines, "path": fp})
    return out

# ============ 树结构(2026-08-26 修正:活跃 61 skills / 15 分类,排除 .archive) ============
TREE = N("~/hermes/skills/", "61 skills · 15 分类", "slate", [
    # ---------- Galaxy 域 ----------
    N("Galaxy 域", "galaxy-platform + galaxy/ 6 专项", "violet", [
        N("galaxy-platform ⭐", "总索引 21.9KB · 116 refs · 18 scripts", "emerald", [
            N("references/", "116 个 · 商品/订单/审核/底库 模块化", "slate"),
            N("→ 深度专项路由", "6 galaxy + 2 data-query", "violet"),
        ]),
        N("galaxy-stitch ✅", "拼图+修复+排障三合一 14.6KB·13refs", "violet"),
        N("auto-audit-script", "Tampermonkey 审核脚本调试", "violet"),
        N("galaxy-warningcode-query", "内部码查询 8.9KB·9refs ✅", "violet"),
        N("image-upload", "本地图→公开URL 3 条路径", "violet"),
        N("manual-order-identification", "人工/算法结算判定", "violet"),
        N("odin-platform ✅", "Odin 独立认证/查商品/传图(+吸收 galaxy-odin-image-sync)", "violet"),
    ]),
    # ---------- 数据/商品域 ----------
    N("数据/商品域", "data-query/ 2 专项 · 由 galaxy-platform 路由", "violet", [
        N("sku-spu-matching-pipeline ⭐", "总流程 12.6KB·15refs(含6变体)", "violet"),
        N("mysql-large-json-extraction", "大表嵌套 JSON 高效提取", "violet"),
    ]),
    # ---------- 飞书域 ----------
    N("飞书域", "productivity/feishu 系", "cyan", [
        N("feishu-platform ✅", "wiki读取 + IM消息(并回 feishu-im-messaging) 4层级refs", "cyan"),
        N("feishu-doc-optimization", "PRD 文档三维审阅优化", "cyan"),
    ]),
    # ---------- Hermes 运维域 ----------
    N("Hermes 运维域", "7 个瘦身大索引 + 治理", "emerald", [
        N("hermes-agent", "21KB · 16 refs(已瘦身)", "emerald"),
        N("hermes-config-troubleshooting", "20KB · 30 refs(已瘦身)", "emerald"),
        N("cron-troubleshooting", "9KB · 19 refs(已瘦身)", "emerald"),
        N("hermes-gateway-setup", "11KB · 9 refs(已瘦身)", "emerald"),
        N("system-maintenance", "10KB · 14 refs(含索引自循环) ✅", "emerald"),
        N("kibana-es-monitor", "8KB · 11 refs(已瘦身)", "emerald"),
        N("skill-architecture-governance 🛡️", "周检 cron 周一 11:00", "emerald"),
        N("skill-slimming", "大 skill 瘦身/拆分", "slate"),
        N("agent-delegation-orchestration", "子 agent 委派编排", "slate"),
        N("computer-use", "后台桌面控制(不抢焦点)", "slate"),
        N("hermes-session-titles", "会话标题治理", "slate"),
        N("hermes-desktop-features", "桌面端功能版本归属", "slate"),
        N("hermes-session-state-troubleshooting", "会话丢失排查", "slate"),
        N("parallel-session-collaboration", "并行会话/沉淀治理", "slate"),
    ]),
    # ---------- 金融域 ----------
    N("金融域", "finance/ 3 + openclaw-imports/ 4", "cyan", [
        N("eastmoney-trade-scraper", "东方财富成交记录爬取", "slate"),
        N("stock-kline-deep-dive", "K线 MACD/BBI/布林复盘", "slate"),
        N("trading-record-analysis", "交易 CSV FIFO 10.9KB·3refs ✅", "slate"),
        N("mx-data", "东方财富权威行情/财务", "slate"),
        N("mx-search", "妙想金融资讯搜索", "slate"),
        N("mx-xuangu", "智能选股/行业成分", "slate"),
        N("mx-zixuan", "自选股管理", "slate"),
    ]),
    # ---------- 文档/办公域 ----------
    N("文档/办公域", "productivity/ 其余 12", "slate", [
        N("word-documents", ".docx 读改 19.6KB·15refs ✅", "slate"),
        N("xlsx", "Excel/CSV 读写", "slate"),
        N("data-cleaning", "数据清洗/去重/校验", "slate"),
        N("performance-review", "迭代数据→绩效总结 Word", "slate"),
        N("resume-interview-prep", "简历/面试准备", "slate"),
        N("meeting-action-items", "会议纪要→待办/负责人", "slate"),
        N("session-librarian", "会话归档/重命名", "slate"),
        N("safari-extraction", "AppleScript+JS 提取网页", "slate"),
        N("fix-file-extension", "扩展名损坏修复", "slate"),
        N("stock-portfolio-monitor", "持仓监控→飞书 12.4KB·5refs ✅", "slate"),
        N("pdf", "PDF 创建/读取/合并", "slate"),
        N("presentation-decks ✅", "演示deck:HTML优先,pptx兜底(合并 ppt-presentation)", "slate"),
    ]),
    # ---------- devops 其他 ----------
    N("devops 其余", "隧道/同步/估算等 5 个", "slate", [
        N("db-ssh-tunnel", "SSH 隧道连远程 MySQL", "slate"),
        N("dashboard-summary-api", "租户算法占比 API+DB", "slate"),
        N("prod-stage-data-sync", "生产→预发数据同步", "slate"),
        N("cloud-resource-estimation", "正向推导云资源测算", "slate"),
        N("macos-system-management", "macOS 关联/启动项/卸载", "slate"),
    ]),
    # ---------- 创作/媒体/GitHub/其他 ----------
    N("创作/媒体/GitHub/其他", "creative 4 + media 2 + github 1 + 杂项 5", "slate", [
        N("architecture-diagram", "SVG 架构图", "slate"),
        N("data-visualization", "matplotlib/plotly 图表", "slate"),
        N("interactive-network-viz ✅", "D3力导向/突触图(合并 d3-network-visualization)", "slate"),
        N("prd-ui-mockup", "PRD UI 界面设计", "slate"),
        N("audio-processing", "裁剪合并/说话人分离/GPT-SoVITS微调(并回 voice-clone-finetune)", "slate"),
        N("voice-material-pipeline", "语音素材采集与 TTS 合成", "slate"),
        N("github-workflow ⭐", "选题/发布/提PR 三合一(并回 3 个专项)", "slate"),
        N("hermes-architecture", "harness 核心循环", "slate"),
        N("inspecting-hermes-desktop-dom", "CDP 读桌面 DOM", "slate"),
        N("browser-automation", "浏览器自动化通用技巧", "slate"),
        N("obsidian", "Obsidian 笔记读写", "slate"),
        N("image-processing", "PIL 缩放/裁剪/压缩", "slate"),
    ]),
    # ---------- 待处理 ----------
    N("⚠️ 待处理", "26 对 refs 高重叠 · 已裁决:广vs专/误报,非问题", "rose"),
])

# ============ 递归布局 ============
def subtree_height(node):
    if not node["children"]:
        return NODE_H
    return NODE_H + V_GAP + sum(subtree_height(c) + V_GAP for c in node["children"]) - V_GAP

def assign(node, x, y):
    node["x"], node["y"] = x, y
    if not node["children"]:
        return
    cx = x + NODE_W + H_GAP
    cy = y + NODE_H + V_GAP
    for c in node["children"]:
        assign(c, cx, cy)
        cy += subtree_height(c) + V_GAP

def max_depth(node, d=0):
    return max([d] + [max_depth(c, d + 1) for c in node["children"]])

# ============ 自动重建 TREE(扫目录,保留原 TREE 语义域映射,2026-08-28) ============
def _build_tree_from_scan():
    import os as _os
    # 从原 TREE 提取: 纯skill名 -> 域label, 域顺序, 域色 (人工语义基线)
    cls_to_domain, domain_order, domain_color = {}, [], {}
    for top in TREE["children"]:
        domain_order.append(top["label"])
        domain_color[top["label"]] = top["color"]
        for ch in top.get("children", []):
            cls_to_domain[_norm_label(ch["label"])] = top["label"]
    # 扫当前 skills(排除 .archive/.git/.cache)
    skills = {}
    for root, dirs, files in _os.walk(SKILLS_ROOT):
        if ".archive" in root or "/.git" in root or "/.cache" in root:
            continue
        if "SKILL.md" in files:
            sid = _os.path.basename(root)
            rdir = _os.path.join(root, "references")
            refs = len([f for f in _os.listdir(rdir) if f.endswith(".md")]) if _os.path.isdir(rdir) else 0
            skills[sid] = {"root": root, "refs": refs,
                           "size": _os.path.getsize(_os.path.join(root, "SKILL.md"))}
    # 按域收集
    dom = {d: [] for d in domain_order}
    for sid, s in skills.items():
        d = cls_to_domain.get(sid, "其他")
        dom.setdefault(d, []).append((sid, s))
    # 构建新 TREE
    def mk(sid, s):
        color = "emerald" if s["refs"] >= 15 else ("violet" if s["refs"] >= 5 else "slate")
        return N(sid, f"{s['size']/1024:.1f}KB · {s['refs']} refs", color)
    children = []
    for d in domain_order:
        if dom.get(d):
            kids = [mk(s, s2) for s, s2 in sorted(dom[d])]
            children.append(N(d, f"{len(kids)} 个", domain_color.get(d, "slate"), kids))
    for d, lst in dom.items():  # 兜底: 新增 skill 无对应域
        if d not in domain_order and lst:
            kids = [mk(s, s2) for s, s2 in sorted(lst)]
            children.append(N(d, f"{len(kids)} 个", "slate", kids))
    root = N("~/hermes/skills/", f"{len(skills)} skills · {len(children)} 分类", "slate", children)
    return root, len(skills), len(children)

TREE, SKILL_COUNT, CAT_COUNT = _build_tree_from_scan()

assign(TREE, MARGIN, MARGIN)
W = MARGIN + (max_depth(TREE) + 1) * (NODE_W + H_GAP) + MARGIN
H = MARGIN + subtree_height(TREE) + MARGIN

# ============ 无重叠校验 ============
nodes = []
def collect(node):
    nodes.append(node)
    for c in node["children"]:
        collect(c)
collect(TREE)
overlap = []
for i in range(len(nodes)):
    for j in range(i + 1, len(nodes)):
        a, b = nodes[i], nodes[j]
        if abs(a["x"] - b["x"]) < NODE_W and abs(a["y"] - b["y"]) < NODE_H:
            overlap.append((a["label"], b["label"]))
assert not overlap, f"NODE OVERLAP: {overlap}"

# ============ SVG 生成 ============
svg = []
svg.append(f'<svg viewBox="0 0 {W:.0f} {H:.0f}" xmlns="http://www.w3.org/2000/svg">')
svg.append("""
<defs>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
  </pattern>
  <style>
    .lbl { font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; fill: white; }
    .sublbl { font-family: 'JetBrains Mono', monospace; font-size: 8px; fill: #94a3b8; }
    .edge { stroke: #475569; stroke-width: 1.2; fill: none; }
  </style>
</defs>
<rect width="100%" height="100%" fill="url(#grid)" />""")

# 连线(肘形:父右缘→中继竖线→子左缘)
for n in nodes:
    if not n["children"]:
        continue
    trunk_x = n["x"] + NODE_W + H_GAP / 2
    parent_cy = n["y"] + NODE_H / 2
    kids = n["children"]
    first_cy = kids[0]["y"] + NODE_H / 2
    last_cy = kids[-1]["y"] + NODE_H / 2
    svg.append(f'<line x1="{n["x"] + NODE_W:.1f}" y1="{parent_cy:.1f}" x2="{trunk_x:.1f}" y2="{parent_cy:.1f}" class="edge"/>')
    svg.append(f'<line x1="{trunk_x:.1f}" y1="{first_cy:.1f}" x2="{trunk_x:.1f}" y2="{last_cy:.1f}" class="edge"/>')
    for k in kids:
        k_cy = k["y"] + NODE_H / 2
        svg.append(f'<line x1="{trunk_x:.1f}" y1="{k_cy:.1f}" x2="{k["x"]:.1f}" y2="{k_cy:.1f}" class="edge"/>')

# 节点（点击 → 浮层显示该 skill 的 refs 列表）
for n in nodes:
    stroke, fill = COLORS[n["color"]]
    x, y = n["x"], n["y"]
    svg.append(f'<g class="node" data-skill="{html.escape(n["label"])}">')
    svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{NODE_W}" height="{NODE_H}" rx="6" fill="#0f172a"/>')
    svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{NODE_W}" height="{NODE_H}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    svg.append(f'<text x="{x + 10:.1f}" y="{y + 19:.1f}" class="lbl">{html.escape(n["label"])}</text>')
    if n["sub"]:
        svg.append(f'<text x="{x + 10:.1f}" y="{y + 33:.1f}" class="sublbl">{html.escape(n["sub"])}</text>')
    svg.append("</g>")
svg.append("</svg>")

# ============ refs 点击数据（磁盘实扫，与图同步） ============
ref_map = {}
for n in nodes:
    r = refs_of(n["label"])
    if r is not None:
        key = _norm_label(n["label"])
        d = _skill_dirs.get(key) or _skill_dirs.get(n["label"])
        ref_map[n["label"]] = {"path": d or "", "refs": r}
REF_JSON = json.dumps(ref_map, ensure_ascii=False)

# ============ 信息卡 ============
cards = f"""
    <div class="cards">
      <div class="card"><div class="card-header"><div class="card-dot emerald"></div><h3>大索引(导航)</h3></div>
        <ul>
          <li>• galaxy-platform ⭐ 21.9KB · 104 refs · 18 scripts(路由 8 个深度专项 + 8 data-query)</li>
          <li>• hermes-config-troubleshooting 20KB·30refs / hermes-agent 21KB·16refs</li>
          <li>• cron 9KB·19refs · gateway 11KB·9refs · dashboard 7KB·6refs · system-maint 10KB·14refs · kibana 8KB·11refs(全部已瘦身)</li>
          <li>• feishu-platform ✅ 标准形态 29行·3refs(含 feishu-galaxy-release-timeline 特例)</li>
        </ul>
      </div>
      <div class="card"><div class="card-header"><div class="card-dot violet"></div><h3>深度专项(细节下沉)</h3></div>
        <ul>
          <li>• galaxy/ 7 个专项 + data-query/ 8 个专项,全部由 galaxy-platform 路由</li>
          <li>• galaxy-stitch = 拼接+修复+排障三合一(13 refs);10 个纯API流程已并回 galaxy-platform refs</li>
          <li>• odin-platform 吸收 galaxy-odin-image-sync(独有 Galaxy侧触发/SPU sync 入 references/galaxy-sync-trigger.md)</li>
          <li>• 模式: 总索引只做导航,细节下沉到专项/reference</li>
          <li>• 🛡️ 治理: skill-architecture-governance 每周一 11:00 健康周检</li>
          <li>• 🔄 索引自循环: system-maintenance references/index-self-maintenance.md 每5任务检查</li>
        </ul>
      </div>
      <div class="card"><div class="card-header"><div class="card-dot emerald"></div><h3>体系健康状态</h3></div>
        <ul>
          <li>• 顶层未分类 0 · 断裂引用 0 · 空目录 0</li>
          <li>• 高重叠 26 对:已内容级裁决(广vs专/误报,非问题,仅标注)</li>
          <li>• 16 个分类目录全部为「分类+自身SKILL.md」合法结构 · {SKILL_COUNT} skills</li>
          <li>• 2026-08-24 晚: 收敛删 12 个skill(并回2+删10)+清7空目录 · {SKILL_COUNT} skills</li>
        </ul>
      </div>
    </div>
"""

js_code = """
<script>
const REF_DATA = %s;
function closeRefPanel(){ document.getElementById('refpanel').classList.add('hidden'); }
document.querySelectorAll('.node[data-skill]').forEach(function(g){
  g.addEventListener('click', function(){
    var label = g.getAttribute('data-skill');
    var d = REF_DATA[label];
    document.getElementById('refpanel-title').textContent = label;
    var body = document.getElementById('refpanel-body');
    var pth = document.getElementById('refpanel-path');
    if (!d) {
      pth.textContent = '';
      body.innerHTML = '<div class="ref-empty">该节点无对应 skill 目录</div>';
    } else if (d.refs.length === 0) {
      pth.textContent = d.path;
      body.innerHTML = '<div class="ref-empty">该 skill 无 references 文件</div>';
    } else {
      pth.textContent = d.path;
      body.innerHTML = '<div class="ref-count">' + d.refs.length + ' 个 references · 点击文件名打开</div>' +
        d.refs.map(function(r){
          return '<a class="ref-item" href="file://' + encodeURI(r.path) + '" target="_blank" title="' + r.path + '">' +
            '<span class="ref-name">' + r.name + '</span>' +
            '<span class="ref-meta">' + r.lines + '行 · ' + (r.size/1024).toFixed(1) + 'KB</span></a>';
        }).join('');
    }
    document.getElementById('refpanel').classList.remove('hidden');
  });
});
document.addEventListener('keydown', function(e){ if (e.key === 'Escape') closeRefPanel(); });
</script>
""" % REF_JSON

html_out = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hermes Skill 体系树状架构图</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'JetBrains Mono', monospace; background: #020617; min-height: 100vh; padding: 2rem; color: white; }}
    .container {{ max-width: 1500px; margin: 0 auto; }}
    .header {{ margin-bottom: 1.5rem; }}
    .header-row {{ display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem; }}
    .pulse-dot {{ width: 12px; height: 12px; background: #22d3ee; border-radius: 50%; animation: pulse 2s infinite; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
    h1 {{ font-size: 1.5rem; font-weight: 700; letter-spacing: -0.025em; }}
    .subtitle {{ color: #94a3b8; font-size: 0.875rem; margin-left: 1.75rem; }}
    .diagram-container {{ background: rgba(15, 23, 42, 0.5); border-radius: 1rem; border: 1px solid #1e293b; padding: 1rem; overflow: auto; }}
    svg {{ width: 100%; min-width: 1000px; display: block; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top: 1.5rem; }}
    .card {{ background: rgba(15, 23, 42, 0.5); border-radius: 0.75rem; border: 1px solid #1e293b; padding: 1.25rem; }}
    .card-header {{ display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }}
    .card-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
    .card-dot.cyan {{ background: #22d3ee; }} .card-dot.emerald {{ background: #34d399; }}
    .card-dot.violet {{ background: #a78bfa; }} .card-dot.amber {{ background: #fbbf24; }}
    .card-dot.rose {{ background: #fb7185; }} .card-dot.slate {{ background: #94a3b8; }}
    .card h3 {{ font-size: 0.875rem; font-weight: 600; }}
    .card ul {{ list-style: none; color: #94a3b8; font-size: 0.75rem; }}
    .card li {{ margin-bottom: 0.375rem; }}
    .footer {{ text-align: center; margin-top: 1.25rem; color: #475569; font-size: 0.75rem; }}
    .node {{ cursor: pointer; }}
    .node:hover rect {{ filter: brightness(1.3); }}
    .refpanel {{ position: fixed; top: 0; right: 0; width: 380px; height: 100%; background: rgba(2,6,23,0.97); border-left: 1px solid #1e293b; padding: 1.25rem; overflow-y: auto; z-index: 100; box-shadow: -8px 0 24px rgba(0,0,0,0.5); }}
    .refpanel.hidden {{ display: none; }}
    .refpanel-head {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; padding-bottom: 0.75rem; border-bottom: 1px solid #1e293b; }}
    .refpanel-title {{ font-size: 0.875rem; font-weight: 700; color: #22d3ee; word-break: break-all; }}
    .refpanel-close {{ background: #1e293b; border: none; color: #94a3b8; border-radius: 6px; width: 28px; height: 28px; cursor: pointer; font-size: 0.875rem; flex-shrink: 0; }}
    .refpanel-close:hover {{ color: white; }}
    .ref-path {{ color: #475569; font-size: 0.6875rem; margin-bottom: 0.75rem; word-break: break-all; }}
    .ref-count {{ color: #94a3b8; font-size: 0.75rem; margin-bottom: 0.5rem; }}
    .ref-item {{ display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; padding: 0.5rem 0.625rem; border-radius: 6px; color: #e2e8f0; text-decoration: none; font-size: 0.75rem; margin-bottom: 0.25rem; }}
    .ref-item:hover {{ background: #1e293b; }}
    .ref-name {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .ref-meta {{ color: #64748b; font-size: 0.6875rem; white-space: nowrap; flex-shrink: 0; }}
    .ref-empty {{ color: #64748b; font-size: 0.75rem; padding: 1rem 0; }}
  </style>
</head>
<body>
  <div class="container">
    <a href="index.html" style="display:inline-block; margin-bottom:8px; background:rgba(34,211,238,0.12); border:1px solid #22d3ee; border-radius:6px; padding:4px 12px; color:#22d3ee; font-size:11px; text-decoration:none;">← 返回目录</a>
    <div class="header">
      <div class="header-row"><div class="pulse-dot"></div><h1>Hermes Skill 体系 · 树状架构</h1></div>
      <p class="subtitle">分类 → 大索引 → references/深度专项 · {SKILL_COUNT} skills · {CAT_COUNT} 语义域分组 · 更新于 {UPDATED}</p>
    </div>
    <div style="display:flex; gap:14px; margin:6px 0 10px; align-items:center; font-size:11px; color:#94a3b8; flex-wrap:wrap;">
      <span style="display:flex; align-items:center; gap:5px;"><span style="width:10px;height:10px;border-radius:50%;background:#34d399;display:inline-block;"></span>大索引/中枢</span>
      <span style="display:flex; align-items:center; gap:5px;"><span style="width:10px;height:10px;border-radius:50%;background:#a78bfa;display:inline-block;"></span>深度专项</span>
      <span style="display:flex; align-items:center; gap:5px;"><span style="width:10px;height:10px;border-radius:50%;background:#22d3ee;display:inline-block;"></span>标准形态</span>
      <span style="display:flex; align-items:center; gap:5px;"><span style="width:10px;height:10px;border-radius:50%;background:#94a3b8;display:inline-block;"></span>普通</span>
      <span style="display:flex; align-items:center; gap:5px;"><span style="width:10px;height:10px;border-radius:50%;background:#fb7185;display:inline-block;"></span>⚠️ 待处理</span>
    </div>
    <div class="diagram-container">{"".join(svg)}</div>
    {cards}
    <div id="refpanel" class="refpanel hidden">
      <div class="refpanel-head">
        <span id="refpanel-title" class="refpanel-title"></span>
        <button class="refpanel-close" onclick="closeRefPanel()">✕</button>
      </div>
      <div id="refpanel-path" class="ref-path"></div>
      <div id="refpanel-body"></div>
    </div>
    {js_code}
    <p class="footer">Hermes Skills 树状架构 · {SKILL_COUNT} skills · 更新于 {UPDATED} · 治理: skill-architecture-governance</p>
  </div>
</body>
</html>
"""

out_path = "/Users/huangqixuan/hermes_output/skill-viz/skill-tree.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_out)

# ============ 同步入口页统计(2026-08-28,不再手写 58) ============
index_path = "/Users/huangqixuan/hermes_output/skill-viz/index.html"
if os.path.exists(index_path):
    _it = open(index_path, encoding="utf-8").read()
    _it = re.sub(r"Hermes Agent skill 架构 · \d+ 用户 skills",
                 f"Hermes Agent skill 架构 · {SKILL_COUNT} 用户 skills", _it)
    open(index_path, "w", encoding="utf-8").write(_it)
    print(f"index.html updated: {SKILL_COUNT} 用户 skills")

# ============ 自检 ============
stale = [t for t in ["待瘦身", "88 refs", "9:30", "89 skills", "空目录 14", "29 对", "galaxy-display-image-fix(未合并)"] if t in html_out]
print(f"nodes: {len(nodes)} (skills: {sum(1 for n in nodes if n['color'] in ('violet','cyan','emerald','slate') and '域' not in n['label'] and '⚠️' not in n['label'])})")
print(f"viewBox: {W:.0f} x {H:.0f}")
print(f"overlap: {len(overlap)}")
print(f"stale-text: {stale}")
print(f"written: {out_path}")
