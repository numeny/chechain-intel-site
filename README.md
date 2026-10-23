# 汽车出海情报变现项目

把 `parser` 项目中已发布的澳洲、巴西、日本公开信息，整理成可销售的经销商渠道地图与信号简报。

## 目标与约束

原目标：30 天内完成上架、内容发布、首单成交，并冲刺 1 万元营收。用户后续提出“1 天 1 万、1 个月 10 万、第 2 个月 20 万”；按当前约束（零渠道、无实名账号、无广告预算、每周 <5 小时），这些目标不保证达成，测算与实现条件见 `docs/business/2026-10-23-revenue-model.md`。

详细设计见 `docs/superpowers/specs/2026-10-23-auto-export-intel-design.md`，实施计划见 `docs/superpowers/plans/2026-10-23-auto-export-intel.md`。

## 数据概况（2026-10-23）

| 国家 | 企业 | 品牌代理 | 集团/门店关系 | 信号 |
|---|---:|---:|---:|---:|
| 澳洲 | 353 | 254（比亚迪 132、名爵 122） | 98 | 10 |
| 巴西 | 378 | 335（比亚迪 235、奇瑞 100） | 94 | 60 |
| 日本 | — | — | — | 70 |

标准包不含联系方式，只整理企业级公开信息。定制调研可核验企业官网公开的 `info@`/`sales@` 或总机。

## 快速开始

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install openpyxl reportlab pillow pytest

# 生成正式交付物
.venv\Scripts\python tools\export.py --country au --kind full
.venv\Scripts\python tools\export.py --country br --kind full
.venv\Scripts\python tools\export.py --country jp --kind full

# 生成 99 元试用样本
.venv\Scripts\python tools\export.py --country au --kind sample
.venv\Scripts\python tools\export.py --country br --kind sample

# 生成商品封面图
.venv\Scripts\python tools\make_covers.py

# 测试
.venv\Scripts\python -m pytest
```

默认读取 `..\parser\data\gan.db`（只读）。可用 `--db` 指定其他数据库，`--out` 指定输出目录。

## 产品站点

```powershell
cd site
py -m http.server 8080
```

浏览器打开 `http://127.0.0.1:8080`。部署与替换说明见 `site/README.md`。

站点已做本地检查：无 JS 报错、无失败请求、无缺失锚点、无破图；桌面 1440px 与移动 390px 均验证。

## 目录

```
src/export_intel/   数据读取、Excel/PDF 生成、样本脱敏、CLI
tools/              导出入口、统计/校验/截图脚本
tests/              单元测试
deliverables/       生成物（gitignore）
site/               静态产品页、样本、封面
sales/              上架文案、文章、FAQ、交付话术、运营手册、CRM
docs/               设计文档、实施计划、商业分析
```

商业与运营文档：

- `docs/business/2026-10-23-revenue-model.md`：1 天/1 月/2 月目标测算与实现条件。
- `docs/business/2026-10-23-competitor-analysis.md`：竞品对比与差异化策略。
- `docs/business/2026-10-23-funnel-architecture.md`：销售漏斗与系统架构。

## 销售资产

- `sales/listings/xianyu.md`：3 条闲鱼文案（澳洲、巴西、定制）。
- `sales/listings/zhubajie.md`：猪八戒/一品威客服务文案。
- `sales/listings/xiaohongshu.md`：3 篇小红书笔记。
- `sales/covers/`：4 张商品封面图（澳洲、巴西、日本、定制）。
- `sales/templates/faq.md`：客户常见问题。
- `sales/templates/delivery.md`：收款、交付、售后话术。
- `sales/templates/delivery-runbook.md`：每日/每周运营流程与 KPI。
- `sales/ops/crm.csv`：线索与成交记录模板。
- `sales/ops/scripts.md`：首次回复、跟进、异议处理、定制问卷。
- `sales/articles/`：10 篇知乎/公众号长尾文章。

## 合规边界

- 只读公开数据库，不修改 `parser`。
- 只导出 `status='published'` 的记录。
- 只售企业级公开信息，不售个人信息。
- 遵守来源网站 robots.txt 与平台规则；不整站复制、不转售原始快照。
- 不做冷邮件、不批量加微信、不投付费广告。
- 收入依法申报；保留订单与交付记录。

## 当前状态

- 导出工具、样本脱敏、Excel/PDF 已实现，11 个测试通过。
- 澳洲 353 家、巴西 378 家、日本 70 条信号已生成。
- 产品站点、竞品分析、营收测算、漏斗架构、运营脚本已完成。
- **收入仍为 0**：下一步必须由用户实名注册/上架/收款；代码和素材不能代替账号与流量。
- 执行顺序：部署 `site/` → 上架闲鱼/猪八戒 → 发知乎/小红书 → 按 `sales/ops/scripts.md` 回复 → 用 `sales/ops/crm.csv` 记录。
