# skill-viz scripts

两类生成器，产出本 repo 的 HTML：
- `gen_skill_tree.py` → `skill-tree.html`(树状架构图，自动扫 skills)
- `gen_skill_synapse.py` → `skill-synapse-network.html`(神经突触图，自动扫 skills)

用法(本地 `~/.hermes/scripts/` 同款)：`python3 gen_xxx.py`
无敏感信息(不读凭证/密钥)；生成后 `git push` 即发布 Pages。
2026-08-28 建立：原 build_synapse_v2.py 被 cleanup 误删，重写并备份上库，防止再次丢失。
