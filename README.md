# Ezer Audit 学习交流版

> 仅供学习交流。这是降级示例，不是弈泽（Ezer）商业版本，不能用于生产或商用。

公开仓库：<https://github.com/ezercc/ezer-audit-learning>

阶段结构已拆开，商业效果没有随结构开放。私有历史没有带入本仓库。详见 [REVIEW_NOTICE.md](REVIEW_NOTICE.md) 和 [LICENSE](LICENSE)。

## 结构

`resolver -> fetcher -> planner -> normalizer -> router -> analyzer -> gate -> industry -> outlook -> auditor -> summarizer`

图示见 [docs/architecture.md](docs/architecture.md)。降级对照见 [docs/downgrade_matrix.md](docs/downgrade_matrix.md)。去掉的类别见 [docs/removed.md](docs/removed.md)。

## 降级

- 提示词只有几行，要求列数字或返回不可用。
- 默认使用本地模板，不调用模型服务。
- 历史最多四个期间，样例只有营收和净利润。
- 只出三张短卡片，每段不超过 60 字。
- 不补数，不回退到另一个模型，不能给出高置信结论。
- 产业阶段返回空主题，展望阶段返回不可用。
- 打开已删除能力的环境变量会使本次运行失败关闭。
- 接口只监听 `127.0.0.1`。

## 运行

```bash
python3 -m ezer_audit_review --code 000000.SZ --year 2024 --period FY
python3 -m unittest discover -s tests -t .
```

样例代码是 `000000.SZ`，期间是 `2024 FY`。其他代码或期间会返回 `NO_VALID_CONCLUSION`，因为这里没有外部取数。

可选远程模型不是质量路径。需要自行提供兼容接口，输出仍会被截断：

```bash
export REVIEW_MODEL_MODE=remote
export REVIEW_MODEL_BASE_URL=
export REVIEW_MODEL_API_KEY=
python3 -m ezer_audit_review serve --port 8765
```

未设置 `REVIEW_DEMO_TOKEN` 时，本机接口不鉴权。设置后，请求需要 `Authorization: Bearer <token>`。

## 边界

本仓库仅供学习交流。公开地址是 <https://github.com/ezercc/ezer-audit-learning>。它不是商业版本，也不授予商用许可。
