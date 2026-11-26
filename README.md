# Ezer Audit 审阅降级版

给老师审阅的开源降级后端。阶段结构已拆开，商业效果没有随结构开放。

这不是生产系统。私有历史没有带入本仓库。详见 [REVIEW_NOTICE.md](REVIEW_NOTICE.md)。

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

本仓库没有上游远程。未发布。回退方式是删除本目录。
