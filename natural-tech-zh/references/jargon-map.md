# AI Agent Tech Jargon & Translationese Reference

> **Usage Note**: Consult this reference only during dedicated document-polishing passes or when maintaining `scripts/tic_lint.py`. Do **not** load it during routine coding turns, and never treat examples as fixed templates.

## Part 1: Universal English-to-Chinese Translationese Patterns

Even without buzzwords, models that draft latent English clauses and translate 1-to-1 produce stiff, choppy Chinese. Restore idiomatic Chinese clause flow without dropping any technical fact:

| English-Syntax Habit | Typical Translationese Symptom | Idiomatic Chinese Principle |
| :--- | :--- | :--- |
| **1 English clause = 1 Chinese period** (`逗句比 ≈ 1.0`) | Chopping every SVO block, `When X, do Y` branch, or `原先…现在…` contrast into isolated short sentences | Link the same causal, temporal, or before/after arc with commas, omitting repeated subjects until the thought lands |
| **Dummy inanimate pronouns (`它` / `它们的` / `这会让`)** | Starting sentences with `它负责…` / `这会让…`, or dangling `, as well as their...` as `，以及它们的…` | Lead with the concrete module, action, or symptom; drop redundant inanimate pronouns and pair each noun with a matching verb |
| **Sentence-initial `也 + verb` (`Also check...`)** | Starting an independent sentence with `也检查…` / `也确认…` | Connect naturally with `顺带确认…` / `同时看下…` |
| **`来自` causatives & `be / by` passives** | `耗时来自…` / `一旦超时就会被丢弃` / `报错由某逻辑吞掉` | State active cause and effect in chronological order (`之所以慢，是因为…` / `一超时就直接丢弃` / `某处直接把报错吞了`) |
| **`of` Nominalization & 5+ item `、` stacks** | `负责任务的调度和执行` / `增加异常排查的负担` / packing 5–6 `、` nouns after one verb | Turn nominalized wrappers back into verbs; split long parallel noun lists into two layered clauses |
| **Mid-clause translated adverbs (`因此` / `随后`)** | `消费端因此堆积了大量消息` / `解析器随后读取下一段` | Place connectors at clause openings or let sequence carry the flow (`消息越攒越多` / `接着解析器再读下一段`) |
| **English bullet periods, stub periods & `\u3000` dodges** | `- **标题**。` / `1. **核对配置。**` / `1. 核对配置。再去查…` / `- **标题**　正文` | Write full flowing step sentences, or use normal Chinese colons (`- 模块或问题名：…`) when naming distinct items |

## Part 2: Tier 1 Pure Agent Calques, Melodrama & Plastic Tics (Drop or Replace)

| Agent Slop / Calque | Origin / Why It Sounds Unnatural | Natural Engineering Chinese |
| :--- | :--- | :--- |
| **Non-spatial `XX侧`** (`调用侧 / 生产侧 / 代码侧 / 入口侧 / 业务侧 / 发起请求的一侧`) | Mechanical `-side` calque | `调用方 / 线上环境 / 代码里 / 入口处 / 业务方 / 发起请求的一端` *(keep only spatial `左/右/两侧` and mobile `端侧`)* |
| `数据形态 / 接口形态 / 返回形态 / 目标形态` | Calque of *data/API shape* | `数据结构 / 接口格式 / 返回值结构` |
| `基线 / 建基线 / 记录基线 / 保留基线` | Mechanical calque of *baseline* | `改前数据 / 初始数值 / 原来的结果 / 对照组` |
| `保留零条 / 零个…` | Calque of *keep zero items* | `不保留 / 设为空` |
| `最小闭环 / 完整闭环 / 已闭环` | Overused workflow cliché | `从头跑通 / 拿样本测通 / 测完了` |
| `收口 / 逻辑收口 / 权限收口` | Post-ban substitute for 闭环 | `归并到一处 / 统一走某处 / 定案` |
| `落盘 / 已落盘` *(for ordinary files/configs)* | Storage-engine WAL term used for `write_file` | `写入配置 / 存进文件` *(keep only for DB/storage engine disk flush)* |
| `静默吞掉 / 静默失败 / 静默降级` | Calque of *silently swallow / fail* | `直接把报错吞了 / 不报错直接失败 / 悄悄退回旧逻辑` |
| `技术底座 / 底座 / 基座 / 单一事实源 / 一等公民` | Grandiose inflation | `底层库 / 基础框架 / 唯一准绳 / 原生直接支持` |
| `外科手术式 / 最小侵入 / 零侵入` | *Surgical / non-invasive* self-praise | `只改了某处，没动公共逻辑` |
| `承重逻辑 / 爆炸半径 / 自伤陷阱` | *Load-bearing / blast radius / footgun* | `核心依赖 / 影响范围 / 容易踩的坑` |
| `全程只读 / 不污染工作区 / 不把猜测当根因` | Methodological virtue-signaling | *Omit routine hygiene; report actual checks and changes* |
| `破案了 / 罪魁祸首 / 你说得对 / 如果你愿意…` | Melodrama / flattery / chatbait | *Delete* |
| `不能保证全量无误 / 不能据此宣称` | Generic CYA tail | *Delete generic CYA; state concrete untested gaps plainly* |
| Inline `smoke / fallback / guard / sanity check` in Chinese prose | Untranslated CoT spillover | `冒烟测试 / 失败回退 / 前置检查 / 基础自检` |

## Part 3: Tier 2 High-Drift Words (Control Density) & Tier 3 Protected CS Terms (Keep Intact)

- **Avoid stacking post-ban filler words**: Keep `收敛`, `口径`, `对齐`, `兜底`, `主链路/全链路`, `收紧/放宽`, `心智`, `抓手`, `赋能`, `颗粒度` from crowding out plain verbs (`归并`, `统计标准`, `核对一致`, `失败回退`, `核心流程`, `粒度`).
- **Always preserve genuine CS terminology**: Keep `幂等`, `隐式/显式类型转换`, `接口契约`, `向后兼容`, `线性一致`, `可观测性`, `死锁`, `竞态条件`, `背压`, `边界条件`, `锁粒度 / 采样粒度` intact.
