# Ezer Audit 审阅降级版

给老师审阅的开源降级后端。它保留阶段链路，但去掉了关键信息，并故意降低提示词和效果路径。

这不是生产系统。私有历史没有带入本仓库。详见 [REVIEW_NOTICE.md](REVIEW_NOTICE.md)。

## 链路

解析请求 → 读取本地样例 → 记录一条不执行的查询 → 标准化 → 三张短卡片 → 硬门 → 跳过产业整理和经营展望 → 清单复核 → 交付。

图示见 [docs/chain.md](docs/chain.md)。去掉的类别见 [docs/removed.md](docs/removed.md)。

## 降级

- 提示词只有几行，要求列数字，不要求质量判断。
- 默认使用本地模板，不调用模型服务。
- 历史最多四个期间，样例只有营收和净利润。
- 只出三张短卡片，每段不超过 60 字。
- 不补数，不回退到另一个模型，不能给出 `TRUSTED`。
- 产业整理和经营展望固定跳过。
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
