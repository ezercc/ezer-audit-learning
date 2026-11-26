# 模块结构

审阅版按阶段拆开，方便查看链路。拆开不等于带入商业效果。

```mermaid
flowchart TD
    A[resolver<br/>字段检查] --> B[fetcher<br/>本地样例]
    B --> C[planner<br/>一条不执行的查询]
    C --> D[normalizer<br/>两个指标]
    D --> E[router<br/>单槽位]
    E --> F[analyzer<br/>三张短卡片]
    F --> G[gate<br/>不补数]
    G --> H[industry<br/>空主题]
    H --> I[outlook<br/>不可用]
    I --> J[auditor<br/>限制说明]
    J --> K[summarizer<br/>短摘要]
    A --> X[字段不足]
    B --> Y[样例不匹配]
```

对应目录：

- `stages/`：每个阶段一个模块
- `contracts/`：状态机、事件和结果组装
- `api/`：本机任务接口和降级清单
- `prompts/`：短提示词
- `fixtures/`：唯一数据样例

状态顺序是 `INIT -> RESOLVED -> FETCHED -> PLANNED -> ANALYZED -> GATED -> INDUSTRY -> OUTLOOK -> REVIEWED -> SUMMARIZED -> DELIVERED`。非法跳转会直接失败。
