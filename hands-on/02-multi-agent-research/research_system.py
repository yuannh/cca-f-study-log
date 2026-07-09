"""
多智能体研究系统 Demo —— coordinator + 并行搜索 subagent + 串行分析 subagent

对应官方 Domain 1（Task Statement 1.2、1.3）。

架构（由学习者自己设计推演得出）：

                    coordinator（组长）
                          │  拆任务
        ┌─────────────────┴─────────────────┐   ← 并行：两个搜索互不依赖
        ▼                                   ▼
   搜索员(笔记本1)                     搜索员(笔记本2)
        └─────────────────┬─────────────────┘
                          ▼  收集两份结果（唯一枢纽）
                    coordinator
                          ▼  串行：分析依赖搜索结果，显式塞进 prompt
                    分析员(对比+推荐)
                          ▼
                     最终报告

运行前：export ANTHROPIC_API_KEY=...   （绝不把密钥写死在代码里）
"""

import asyncio
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

# 从项目根目录的 .env 文件把 ANTHROPIC_API_KEY 加载进环境变量。
# load_dotenv() 会从本文件所在目录向上逐层找 .env，所以放在项目根目录也能找到。
# 好处：密钥留在 .env（已被 .gitignore 忽略），绝不写进代码、也不用在命令里贴。
load_dotenv()

# AsyncAnthropic() 自动从环境变量 ANTHROPIC_API_KEY 读取密钥 —— 不硬编码。
client = AsyncAnthropic()

MODEL = "claude-opus-4-8"
# 备注：真实系统里 subagent 常用更便宜的模型（如 haiku）以省成本，
# coordinator 用强模型。这里为最小化只用一个模型。


# ─────────────────────────── subagent：搜索员 ───────────────────────────
async def search_subagent(laptop_name: str, fail: bool = False) -> str:
    """搜索单台笔记本的资料。每次调用都是一个【独立的 subagent】。"""

    # 为什么有 fail 参数：满足验收标准 4 —— 故意让一个 subagent 失败，
    # 用来观察 coordinator 如何处理（模拟"搜索超时"这类瞬时故障）。
    if fail:
        raise RuntimeError(f"搜索 {laptop_name} 超时（模拟瞬时故障）")

    # 关键（验收标准 1、2）：每个 subagent 是一次全新的、独立的 API 调用，
    # 有自己从零开始的 messages。coordinator 的历史、另一个搜索员查到的东西，
    # 它统统【看不到】—— 除非被显式写进下面这个 prompt。这就是"上下文不自动继承"。
    resp = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="你是一名硬件搜索员。只输出这一台笔记本的规格、价格、评测要点，简明扼要。",
        messages=[{"role": "user", "content": f"查一下这台笔记本的资料：{laptop_name}"}],
    )
    return next(b.text for b in resp.content if b.type == "text")


# ─────────────────────────── subagent：分析员 ───────────────────────────
async def analysis_subagent(findings: dict[str, str]) -> str:
    """基于搜集到的资料对比笔记本、给出推荐。"""

    # 关键（验收标准 2、3）：分析员是另一个独立 subagent，它【看不到】搜索员的对话。
    # 所以 coordinator 必须把搜索结果"显式塞进"这个 prompt —— 即"提炼关键事实注入"，
    # 而不是指望分析员自动继承。
    facts = "\n\n".join(f"【{name}】\n{info}" for name, info in findings.items())
    resp = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "你是一名分析员。基于给你的资料对比这些笔记本，给出购买推荐。"
            "若某台资料缺失，必须明确指出无法对该台做完整对比。"
        ),
        messages=[{"role": "user", "content": f"这是搜集到的资料：\n\n{facts}\n\n请对比并给出推荐。"}],
    )
    return next(b.text for b in resp.content if b.type == "text")


# ─────────────────────────── coordinator（唯一枢纽） ───────────────────────────
async def coordinator(laptops: list[str], fail_on: str | None = None) -> str:
    """总调度：并行派搜索员 → 汇总 → 串行派分析员。所有通信都经这里中转。"""

    # 阶段 1：并行 spawn（验收标准 5）。
    # asyncio.gather 让两个搜索调用【同时】发出 —— 因为搜 A 和搜 B 互不依赖。
    # 这就是"同一轮并发派生多个 subagent"的等价机制。
    tasks = {
        name: asyncio.create_task(search_subagent(name, fail=(name == fail_on)))
        for name in laptops
    }

    findings: dict[str, str] = {}
    for name, task in tasks.items():
        try:
            findings[name] = await task
        except Exception as e:
            # 验收标准 4 + 错误处理三原则：
            #   不崩全局（不是 A）、不静默编造（不是 D），而是【如实记录部分结果】。
            print(f"[coordinator] 搜索员失败：{name} —— {e}")
            findings[name] = f"（资料缺失：{e}）"

    # 阶段 2：串行交接。搜索全部收齐后，才派分析员（分析依赖搜索结果）。
    # subagent 之间【不直连】—— 结果经 coordinator 转发给分析员，符合"唯一枢纽"。
    return await analysis_subagent(findings)


if __name__ == "__main__":
    laptops = ["MacBook Air M3", "Dell XPS 13"]

    print("========== 正常运行 ==========")
    print(asyncio.run(coordinator(laptops)))

    print("\n========== 故意失败演示（笔记本2搜索失败） ==========")
    print(asyncio.run(coordinator(laptops, fail_on="Dell XPS 13")))
