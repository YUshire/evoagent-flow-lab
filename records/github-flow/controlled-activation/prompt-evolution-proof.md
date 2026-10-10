# EvoAgent 提示词版本进化回放证明

## 结论

- 进化决策：`activated`
- 数值门禁：`PASS`
- 生产来源门禁：`FAIL`
- 生产激活：`BLOCKED`

> 本报告证明受控离线环境中的行为版本进化，不证明外部 LLM 权重提升，也不代表真实 GitHub PR 的生产效果。

## 数据与反馈

- 样本：12（Validation 6 / Holdout 6）
- 仓库：2
- 来源：`new-authored-controlled`
- Validation 漏报反馈：2
- 自动学习规则：`SEC-ASSERT-AUTH`, `SEC-YAML-LOAD`

## Validation 回放

| 指标 | Prompt v1 | Prompt v2 | 变化 |
|---|---:|---:|---:|
| Precision | 100.00% | 100.00% | +0.00 pp |
| Recall | 33.33% | 100.00% | +66.67 pp |
| F1 | 50.00% | 100.00% | +50.00 pp |
| 高风险召回率 | 50.00% | 100.00% | +50.00 pp |
| 干净样本准确率 | 100.00% | 100.00% | +0.00 pp |
| 综合得分 | 67.50% | 100.00% | +32.50 pp |

## Holdout 回放

| 指标 | Prompt v1 | Prompt v2 | 变化 |
|---|---:|---:|---:|
| Precision | 100.00% | 100.00% | +0.00 pp |
| Recall | 33.33% | 100.00% | +66.67 pp |
| F1 | 50.00% | 100.00% | +50.00 pp |
| 高风险召回率 | 50.00% | 100.00% | +50.00 pp |
| 干净样本准确率 | 100.00% | 100.00% | +0.00 pp |
| 综合得分 | 67.50% | 100.00% | +32.50 pp |

## 审计证据

- Evolution run：`e1f84b3a-35e3-4ce9-a68b-f526320d0bb3`
- 原因：candidate improved on validation and passed the non-regression holdout gate
- Prompt v1：active=`false`，parent=`None`，SHA-256=`7744079c9edf276b4855958d232aff16e93c6623d8d3812a49b8ddcfb209eceb`
- Prompt v2：active=`true`，parent=`1`，SHA-256=`a105ec40e0427f7086e4b145100351aa71af8c329229f45ddcd6145c6c42f55b`
- 完整数据集指纹：`139a45f9ea92a969f54b59a232ae9a5b33f8b0bff8dc7c5201958355b60109c2`
- Validation 数据指纹：`214be5e2db47b0b2d906b75582c61aec7f74d374456167e89cc582c4bae1cbe8`
- Holdout 数据指纹：`dea2d2db3a54441022ff6eb92cdfe4c5e997c778eb8e3e8a833f899ceb108c66`
