---
name: openclaw-timebox-cpr
description: 使用时间盒（Timebox）+ CPR 工作法管理 OpenClaw 任务的完整执行周期。流程：Context 锚定 → Align 对齐优先级 → Plan+Run 执行 → Review 复盘。自动写入本地日志，可选接入 macOS 日历。触发词："时间盒"、"timebox"、"CPR 复盘"、"开始一个任务"、"帮我规划任务"、"用 timebox"、"start timebox"、"task planning"。
version: 2.3.0
metadata:
  author: vincent
  based_on: OpenClaw Timebox-CPR 工作法
---

# OpenClaw Timebox-CPR

一套**全天维度**的任务管理工作法，分四个阶段：

```
早晨规划（PLAN）→ 执行时间盒（RUN）→ 单盒收集（CHECK）→ 全天复盘（REVIEW）
```

每个时间盒是一个**不可拆分的执行单元**，AI 不干预盒内执行细节，只负责规划、衔接和复盘。

---

## 使用方式

```bash
/openclaw-timebox-cpr                  # 开始今天的规划
/openclaw-timebox-cpr --run            # 跳过规划，直接开始一个时间盒
/openclaw-timebox-cpr --check          # 完成一个时间盒后做快速收集
/openclaw-timebox-cpr --review         # 全天结束后做整体复盘
/openclaw-timebox-cpr --log            # 查看今日日志摘要
```

---

## 偏好配置（EXTEND.md）

按优先级搜索以下路径，找到即用：
1. 项目级：`{project}/.baoyu-skills/openclaw-timebox-cpr/EXTEND.md`
2. 用户级：`~/.baoyu-skills/openclaw-timebox-cpr/EXTEND.md`

**如果 EXTEND.md 不存在，MUST 执行首次配置（见下方章节），完成后继续。**

```yaml
default_timebox: 25          # 默认单个时间盒时长（分钟）
calendar: macos              # 日历工具（见支持列表）
calendar_name: 工作          # 日历名称/账户
calendar_alert_before: 2     # 提醒提前几分钟
log_backend: local           # 日志工具（见支持列表）
log_dir: ~/.openclaw/logs    # 仅 local 模式使用
log_token:                   # 第三方日志工具的 Token/Key（如需要）
log_workspace:               # 第三方日志工具的空间/数据库 ID（如需要）
lang: zh                     # zh | en
```

---

## 首次配置

EXTEND.md 不存在时，**一次性**提问以下四项，创建文件后继续。

### 问题 1：默认时间盒时长

> 你常用的专注时长是多少分钟？
> 推荐：**25 分钟**（番茄钟）/ **45 分钟**（深度工作）/ **90 分钟**（长任务）/ 自定义

### 问题 2：日历工具

> 你用哪个日历记录时间安排？时间盒会自动在日历里创建占位事件。

| 选项 | 说明 |
|------|------|
| `macos` | 苹果日历（Apple Calendar），本地，无需配置 |
| `wecom` | 企业微信日历，需要企业微信登录态 |
| `feishu` | 飞书日历，需要飞书 API Token |
| `google` | Google 日历，需要 Google OAuth |
| `none` | 不使用日历 |

选择后追问：
- 若 `macos`：使用哪个日历名称？（默认"工作"，不存在则用默认日历）
- 若 `feishu` / `google` / `wecom`：需要提供对应 Token 或引导完成授权

### 问题 3：日志工具

> 你用什么记录工作日志？每个时间盒的执行记录和复盘会自动写入。

| 选项 | 说明 |
|------|------|
| `local` | 本地 Markdown 文件（默认，无需配置）|
| `feishu_doc` | 飞书文档，需要飞书 API Token + 文档 ID |
| `wecom_doc` | 企业微信文档，需要企业微信登录态 |
| `notion` | Notion，需要 Integration Token + Database ID |
| `google_doc` | Google Docs，需要 Google OAuth |
| `flomo` | Flomo，需要 Flomo API（`https://flomoapp.com/mine?source=incoming_webhook`）|

选择后追问对应的 Token / ID / 路径配置项（若需要）。

### 问题 4：交互语言

> 中文 / English

---

## 日历集成

### 通用行为

- PLAN 阶段时间分配确认后，为每个时间盒批量创建日历事件
- 事件标题格式：`[Timebox #{N}] {任务名}`
- 事件描述：任务名 + 优先级 + 紧急程度
- CHECK 收集完成后，更新对应事件备注（追加实际完成情况）
- **任何日历操作失败，仅提示，不阻断主流程**

### 各平台实现

**macOS Apple Calendar（AppleScript）**
```applescript
tell application "Calendar"
  set targetCal to first calendar whose name is "{calendar_name}"
  -- 若不存在则用 first calendar whose writable is true
  tell targetCal
    make new event with properties {
      summary: "[Timebox #{N}] {任务名}",
      start date: {开始时间},
      end date: {开始时间} + {时长} * minutes,
      description: "优先级：{priority} · 紧急程度：{urgency}"
    }
  end tell
end tell
```

**飞书日历（Feishu Calendar API）**
```
POST https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events
Authorization: Bearer {log_token}
{
  "summary": "[Timebox #{N}] {任务名}",
  "start_time": { "timestamp": "{unix_ts}" },
  "end_time": { "timestamp": "{unix_ts}" },
  "description": "优先级：{priority} · 紧急程度：{urgency}"
}
```

**企业微信日历（WeCom）**
> 企业微信日历暂无开放 API，使用 AppleScript 控制企业微信桌面端或提示用户手动创建。

**Google Calendar API**
```
POST https://www.googleapis.com/calendar/v3/calendars/{calendarId}/events
Authorization: Bearer {oauth_token}
{
  "summary": "[Timebox #{N}] {任务名}",
  "start": { "dateTime": "{ISO8601}" },
  "end": { "dateTime": "{ISO8601}" }
}
```

---

## 日志集成

### 通用行为

- 每天在 PLAN 阶段确认时间分配后，创建当日日志并写入今日规划
- RUN 阶段每个时间盒启动时，追加启动记录到本地日志
- CHECK 阶段收集每个时间盒结果后，追加结果记录到本地日志
- REVIEW 阶段将 CPR 复盘报告写入本地日志
- **外部工具同步（flomo、Notion 等）**：仅在 REVIEW 完成后推送每日总结 + CPR 复盘，不推送逐条执行记录
- **任何日志写入失败，仅提示，不阻断主流程**

### 各平台实现

**本地 Markdown（local）**

存储结构：
```
{log_dir}/
├── {YYYY-MM}/
│   └── {YYYY-MM-DD}.md
└── index.md
```

**飞书文档（feishu_doc）**
```
POST https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks
-- 在指定文档末尾追加当天日志块
```

**企业微信文档（wecom_doc）**
> 通过企业微信文档 API 写入，需要企业自建应用 Token。

**Notion**
```
POST https://api.notion.com/v1/pages
Authorization: Bearer {log_token}
-- 在指定 Database 创建新 Page，每天一条
-- 追加内容通过 PATCH blocks endpoint 实现
```

**Google Docs**
```
-- 通过 Google Docs API batchUpdate 在文档末尾追加内容
POST https://docs.googleapis.com/v1/documents/{documentId}:batchUpdate
```

**Flomo**
```
POST {flomo_webhook_url}
{ "content": "[Timebox #{N}] {任务名}\n{执行记录}\n{复盘内容}" }
-- Flomo 每条为独立笔记，建议每个时间盒一条，复盘单独一条
```

---

## 完整工作流

---

### Phase 1 · PLAN · 早晨规划

**触发时机**：每天开始工作时，或用户说"开始今天的规划"。

#### Step 1 — 任务收集（用户主导，AI 倾听）

AI 开启一段**开放式收集对话**，让用户把今天所有想做的事都说出来：

> "今天有哪些事要做？把脑子里所有的都说出来，可以同时告诉我优先级、紧急程度、预计时间和时长，没有的话我们之后再确认。说完告诉我'说完了'。"

用户可以一次说完，也可以分多条输入，格式自由，例如：
- "开会，10点，1小时，很紧急"
- "写周报，不急，大概半小时"
- "回复客户邮件"（无时间信息，后续补充）

AI 在这个阶段只做一件事：**逐条记录，不插话**。

#### Step 2 — AI 整理清单

用户说完后，AI 将所有任务整理成结构化清单，尽可能从用户输入中提取已有信息：

```
今天的任务清单（共 N 项）：

序号  任务名              优先级   紧急程度   计划时间   预计时长
────────────────────────────────────────────────────────
1.   {任务名}            {高/中/低}  {高/中/低}  {HH:MM 或 —}  {N 分钟 或 —}
2.   {任务名}            ...
...

有没有需要修改、补充或删除的？
```

- 用户已提供的字段直接填入
- 用户未提供的字段标为 `—`，**不在此处追问**，进入 Step 3 统一补充

#### Step 3 — 补全缺失信息

清单确认后，AI 只针对**有缺失字段的任务**一次性追问，按任务分组：

> "以下任务还缺一些信息，帮我确认一下：
>
> **回复客户邮件**：优先级和紧急程度怎么看？大概需要多久？有没有要在特定时间做？
>
> **写周报**：计划几点开始？"

用户补充后，AI 更新清单。**若用户仍未提供某字段，AI 根据上下文合理推断并标注"（推断）"**，不再追问。

#### Step 4 — 优先级讨论（AI 主导对话）

清单完整后，AI 与用户讨论执行顺序。**用自然对话**，不用表格，针对清单提出 2–3 个引导性问题：

- "今天如果只能完成一件事，你会选哪个？"
- "有没有哪个任务今天必须完成，否则会影响别人？"
- "有没有固定时间的事项需要作为锚点？"

根据用户回答，AI 输出**排序后的执行顺序建议**并说明理由。

#### Step 5 — 时间分配确认

基于优先级排序、固定时间锚点和用户可用时间，AI 给出完整的今日安排：

```
今日时间盒安排（建议）：
┌──────────────────────────────────────────────────┐
│ #1  {任务名}   优先级:高  紧急:高   09:00  25分钟  │
│ #2  {任务名}   优先级:高  紧急:中   09:30  45分钟  │
│ 📌  {外部事项}（非时间盒）          10:00  1小时   │
│ #3  {任务名}   优先级:中  紧急:低   11:30  25分钟  │
│                              合计约 {X} 小时       │
└──────────────────────────────────────────────────┘
```

**固定时间事项（会议、外出等）标注为 📌，不放入时间盒编号。**

用户确认或调整后：
- 写入今日日志
- 根据 `calendar` 配置批量创建日历事件

---

### Phase 2 · RUN · 执行时间盒

**触发时机**：用户说"开始"、"开始第 N 个"或"开始做{任务名}"。

AI 做两件事，然后**不再干预**：

1. 输出启动卡片：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱  时间盒  #{N}  ·  {duration} 分钟
🎯 {任务名}
开始 → 专注执行，完成后告诉我
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

2. 在本地日志写入启动记录：`[HH:MM] ⏱ 时间盒 #{N} 开始 · {任务名}`

然后**等待用户主动回来**，期间不发送任何消息，**不向外部工具同步**。

> **原则**：时间盒内是用户的专注时间，AI 不拆解任务、不询问进度、不主动打扰。

---

### Phase 3 · CHECK · 单盒快速收集

**触发时机**：用户完成（或中断）一个时间盒后，说"完成了"、"结束了"、"超时了"等。

AI 用**一次性提问**收集结果：

> "快速记录一下：
> 1. 完成了吗？（完成 / 部分完成 / 未完成）
> 2. 一句话说说结果或卡点？
> 3. 有没有新冒出来的任务？"

收到回复后，AI：
- 将结果追加写入日志（含实际用时与计划用时对比）
- 若有新任务，加入今日清单并提示是否调整后续顺序
- 输出下一个时间盒启动提示：

```
✅ #{N} 已归档
下一个：#{N+1} {任务名}（{duration} 分钟）
准备好了说"开始"。
```

若今日所有时间盒执行完毕，提示进入 REVIEW：
```
✅ 今天的时间盒全部完成，说"复盘"开始全天总结。
```

> **原则**：CHECK 最多 1 轮对话，不展开分析，分析留给全天 REVIEW。

---

### Phase 4 · REVIEW · 全天复盘（CPR）

**触发时机**：用户说"今天结束了"、"复盘"、"review"，或所有时间盒执行完毕后用户确认。

AI 基于全天日志生成 CPR 复盘报告：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 全天复盘  ·  {YYYY-MM-DD}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Completed（今天完成了什么）
   完成 {X}/{N} 个时间盒
   · #{1} {任务名} — ✅ 完成  实际 {N} 分钟（计划 {M} 分钟）
   · #{2} {任务名} — ⏳ 未完成
   · #{3} {任务名} — ✅ 完成，超时 {K} 分钟

🔍 Problem（遇到了什么问题）
   · {从 CHECK 收集的卡点汇总}
   · 超时任务分析
   · 未完成原因

🗺  Roadmap（明天怎么走）
   · 移入明日：{未完成任务列表}
   · 时间估算规律：{AI 观察，如"沟通类任务建议 ×1.5"}
   · 明日建议优先处理：{任务名}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

复盘完成后：
- 将报告写入今日日志
- 更新 `index.md`（local 模式）或对应平台索引
- 询问：**"是否把未完成任务带入明天的规划？"**

---

## 日志格式（local 模式）

### 每日日志（`{YYYY-MM-DD}.md`）

```markdown
---
date: {YYYY-MM-DD}
timebox_count: {N}
completed: {X}/{N}
---

## 今日规划
| # | 任务名 | 优先级 | 紧急程度 | 计划时间 | 预计时长 |
|---|--------|--------|---------|---------|---------|
| 1 | ...    | 高     | 高      | 09:00   | 25min   |

## 执行记录
- [HH:MM] ⏱ 时间盒 #1 开始 · {任务名}
- [HH:MM] ✅ 时间盒 #1 结束 · {结果一句话} · 实际 {N} 分钟
- [HH:MM] 📌 外部事项：{事项名}
...

## 每日总结（外部工具同步此段）
- ✅ #{1} {任务名} — 完成，实际 {N} 分钟（计划 {M} 分钟）
- ⏳ #{2} {任务名} — 未完成，{原因一句话}
- ✅ #{3} {任务名} — 完成，超时 {K} 分钟，{原因一句话}

## CPR 复盘（外部工具同步此段）
### Completed
...
### Problem
...
### Roadmap
...
```

### index.md

```markdown
| 日期 | 时间盒数 | 完成率 | 关键词 |
|------|---------|--------|--------|
| 2026-03-22 | 4 | 3/4 | 领跑配置、首页设计 |
```

---

## 与其他 Skill 的联动

| 场景 | 联动 Skill |
|------|-----------|
| 将全天复盘生成可视化卡片 | `baoyu-infographic` |
| 将复盘整理成汇报 PPT | `baoyu-slide-deck` |
| 分享复盘到社交平台 | `baoyu-post-to-wechat` / `baoyu-post-to-weibo` |

---

## AI 行为原则

1. **任务收集阶段不打断**：用户说完之前，AI 只记录，不评价、不归类
2. **缺失信息分两步处理**：Step 2 先整理清单展示已有信息，Step 3 再一次性补全缺失字段，避免边收集边追问
3. **推断优于追问**：用户二次补充后仍缺失的字段，AI 合理推断并标注"（推断）"，不反复询问
4. **时间盒内不干预**：RUN 阶段 AI 保持沉默，等用户主动回来
5. **CHECK 保持轻量**：单盒收集最多 1 轮对话，不展开分析
6. **复盘才是深度分析的时机**：规律总结、原因分析统一放到全天 REVIEW
7. **本地日志完整记录**：规划 + 每条执行记录 + 每日总结 + CPR 复盘，全部写入本地
8. **外部工具只同步摘要**：flomo、Notion 等外部工具仅在 REVIEW 完成后推送"每日总结 + CPR 复盘"两段，不推送逐条执行记录
9. **不阻断流程**：日历/日志写入失败等外部错误，提示后继续执行
