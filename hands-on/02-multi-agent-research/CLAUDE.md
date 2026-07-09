# 动手项目2：多智能体研究系统 Demo

**对应计划**：第1周 周六（2026-07-11）| **官方 Domain**：1 智能体架构与编排（Task Statement 1.2、1.3）

## 任务目标

实现一个 coordinator + 至少2个 subagent 的最小研究系统：coordinator 负责任务分解，委派给（例如）一个"网页搜索" subagent 和一个"文档分析/总结" subagent，最后由 coordinator 汇总结果。

## 验收标准

- [ ] 用 Task 工具（或等价机制）真正生成/调用了独立的 subagent，而不是在同一个 prompt 里模拟
- [ ] subagent 的 prompt 里显式包含了它需要的全部上下文——验证一下：如果不显式传，subagent 是不是真的看不到 coordinator 的历史对话
- [ ] 所有 subagent 之间的通信都经过 coordinator 转发，没有 subagent 之间的直接通信
- [ ] 至少测试一次"故意让某个 subagent 失败"，观察 coordinator 如何处理（是否有合理的错误传播，而不是直接崩溃整个流程）
- [ ] 如果可以并行，验证多个 Task 调用是否在同一轮里并发发出

## 完成后

在本文件夹创建 `learnings.md`，记录：coordinator 是如何决定该调用哪些 subagent 的？如果换成更宽泛的研究主题，你的任务分解逻辑会不会遗漏某些子领域（对应"分解粒度过窄"的官方考点）？
