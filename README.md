# 汽车出海情报变现项目

把 `parser` 项目中已发布的澳洲、巴西、日本公开信息，整理成可销售的经销商渠道地图与信号简报。

## 目标

30 天内完成上架、内容发布、首单成交，并冲刺 1 万元营收；未达成则转入第 2 个月订阅续费。详细设计见 `docs/superpowers/specs/2026-10-23-auto-export-intel-design.md`，实施计划见 `docs/superpowers/plans/2026-10-23-auto-export-intel.md`。

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
.venv\Scripts\python -m pip install openpyxl reportlab pytest

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

## 目录

```
src/export_intel/   数据读取、Excel/PDF 生成、样本脱敏、CLI
tools/              导出入口、统计与校验脚本
tests/              单元测试
deliverables/       生成物（gitignore）
sales/              上架文案、文章、FAQ、交付话术、运营手册
docs/               设计文档与实施计划
```

## 销售资产

- `sales/listings/xianyu.md`：3 条闲鱼文案（澳洲、巴西、定制）。
- `sales/listings/zhubajie.md`：猪八戒/一品威客服务文案。
- `sales/listings/xiaohongshu.md`：3 篇小红书笔记。
- `sales/covers/`：3 张商品封面图（澳洲、巴西、定制）。
- `sales/templates/faq.md`：客户常见问题。
- `sales/templates/delivery.md`：收款、交付、售后话术。
- `sales/templates/delivery-runbook.md`：每日/每周运营流程与 KPI。
- `sales/articles/`：10 篇知乎/公众号长尾文章。

## 合规边界

- 只读公开数据库，不修改 `parser`。
- 只导出 `status='published'` 的记录。
- 只售企业级公开信息，不售个人信息。
- 遵守来源网站 robots.txt 与平台规则；不整站复制、不转售原始快照。
- 不做冷邮件、不批量加微信、不投付费广告。
- 收入依法申报；保留订单与交付记录。

## 当前状态

- 导出工具、样本脱敏、Excel/PDF 已实现，10 个测试通过。
- 澳洲 353 家、巴西 378 家、日本 70 条信号已生成。
- 下一步：用户注册/实名闲鱼、知乎、猪八戒，按 `sales/listings/` 上架，按 `sales/templates/delivery-runbook.md` 执行 30 天冲刺。
