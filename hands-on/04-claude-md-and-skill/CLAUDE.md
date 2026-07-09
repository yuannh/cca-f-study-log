# 动手项目4：CLAUDE.md 层级 + 自定义 Skill + Slash Command

**对应计划**：第2周 周四（2026-07-16）| **官方 Domain**：3 Claude Code配置与工作流（Task Statement 3.1、3.2、3.3）

## 任务目标

挑一个真实的小项目（可以就用这个 `claude certified architect` 项目本身，或另找一个练手仓库），搭建一套完整的 CLAUDE.md 配置层级。

## 验收标准

- [ ] 项目根目录有一份 CLAUDE.md（你已经在用这个项目根目录的了——去读一读，思考它符合"项目级配置"的哪些特征）
- [ ] 用 `.claude/rules/` 写至少一个路径级规则文件，YAML frontmatter 里用 `paths:` glob 限定它只在特定文件类型/目录生效（本项目的 `.claude/rules/hands-on.md` 就是一个现成例子，去读一下）
- [ ] 写一个自定义 skill（`.claude/skills/<name>/SKILL.md`），配置 `context: fork`（隔离输出）和 `allowed-tools`（限制工具访问），本项目的 `quiz-me` 就是例子
- [ ] 写一个自定义 slash command，理解它和 skill 的区别（skill 可以被 Claude 主动调用，command 通常需要你手动 `/触发`）
- [ ] 用 `/memory`（如果你的 Claude Code 版本支持）确认当前会话实际加载了哪些内存文件

## 完成后

在本文件夹创建 `learnings.md`，写下：CLAUDE.md 的用户级/项目级/目录级配置分别解决了什么问题？如果新同事加入团队却没收到某条指令，最可能是放错了哪一级？
