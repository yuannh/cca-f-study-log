# 动手项目3：写一个 MCP Server

**对应计划**：第2周 周二（2026-07-14）| **官方 Domain**：2 工具设计与MCP集成（Task Statement 2.2、2.4）

## 任务目标

用 Python 或 TypeScript 官方 SDK 写一个简单 MCP server（例如：查天气、算数、读取本地笔记），并分别在项目级 `.mcp.json` 和用户级 `~/.claude.json` 各配置一次，体会两者的区别。

## 验收标准

- [ ] 至少2个工具，工具描述互相之间边界清晰（试着故意写两个功能相近的工具，看 Claude 是否会选错，然后修改描述解决）
- [ ] 每个工具在失败时返回结构化错误：包含 `errorCategory`（transient/validation/business/permission之一）、`isRetryable` 布尔值、人类可读的错误说明，而不是笼统的 "operation failed"
- [ ] 用 `.mcp.json`（项目级，写入本仓库根目录）配置一次，用环境变量占位符（如 `${API_KEY}`）管理凭据，不要把密钥写死
- [ ] 也在 `~/.claude.json`（用户级）配置一个实验性/个人的 server，理解它不会随仓库分享给队友
- [ ] 运行 `claude mcp list` 或会话内 `/mcp` 确认连接状态

## 完成后

在本文件夹创建 `learnings.md`，写下你的两个工具描述最初为什么会让 Claude 选错，后来怎么改的。
