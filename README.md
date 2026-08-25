# skill-viz

Hermes Agent skill 体系可视化（静态页面，GitHub Pages 托管）。

## 页面

| 页面 | 说明 |
|---|---|
| [index.html](index.html) | 入口目录 |
| [skill-tree.html](skill-tree.html) | 树状架构图：分类 → 大索引 → references 层级视图 |
| [skill-synapse-network.html](skill-synapse-network.html) | 神经突触网络：力导向互联图，中枢/专项/末梢，可拖拽缩放悬停 |

## 访问

https://archiloss.github.io/skill-viz/

## 更新

重新生成 HTML 后 push 到 `main` 分支，GitHub Pages 自动部署：

```bash
cp ~/hermes_output/skill-tree.html ~/hermes_output/skill-synapse-network.html .
git add . && git commit -m "update" && git push origin main
```

## 数据来源

- `skill-tree.html` 由 `~/.hermes/scripts/gen_skill_tree.py` 生成
- `skill-synapse-network.html` 由磁盘实扫（.hermes/skills 下 SKILL.md + references 统计 + 正文引用关系）生成

> ⚠️ 仅含 skill 元数据（名称/分类/refs 数/大小），不含任何凭证或业务数据。
