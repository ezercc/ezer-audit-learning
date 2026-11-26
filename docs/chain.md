# 审阅版链路

模块图和状态顺序见 [architecture.md](architecture.md)。每个阶段的降级边界见 [downgrade_matrix.md](downgrade_matrix.md)。

产业和展望模块都在链路里，但分别只返回空主题和不可用。查询不会执行。远程模型即使启用，也只接收短提示词，输出会被截断。
