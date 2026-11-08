# MyTutor v1.0 — Agent-Ready Architecture & Product Specification

**日期：** 2026-11-08（Asia/Tokyo）  
**受众：** 未来的你（防烂尾 / 防需求膨胀）+ 编程 Agent（防幻觉 / 防乱改架构）  
**字数目标：** ~2–3 页 · Agent 可执行契约  
**学习域：** 基本情報技術者（FE）+ 情報処理安全確保支援士（SG）  
**前置：** 学习闭环见 `docs/project-plan.md`；教学协议见仓库 `AGENT.md`（PR #1）

> **选型拍板：** 内容 = 概念费曼为主 + LaTeX P0 + 本地 Python/Node lab P1；Sidecar = **Python FastAPI**。

---

## 1. 项目定位与四大铁律

MyTutor 是 **本地优先（Local-First）智能体自学工作台**，三栏桌面范式（类 Claude Desktop / DSH）。强制闭环：**苏格拉底追问 → 费曼笔记（含 LaTeX）→ `02_labs/` 沙盒实证 → 归档 / 复习卡**。

| # | 铁律 | 写死含义 |
|---|------|----------|
| 1 | **数据主权本地化** | 知识资产 = 纯文本 `.md`（YAML frontmatter）+ `.py`/`.js`，落在本地 Git 仓。SQLite **仅**本地状态/全文索引，可随时销毁重建。禁止私有云库锁死笔记。 |
| 2 | **三栏契约** | **禁止 Modal/Alert 打断心流**。功能只进左栏 / 中栏 / 右栏。 |
| 3 | **教学反剧透** | Prompt Engine 按 Mode 在系统层拦截直出答案；默认线索、反问、带 `TODO`/`assert` 的脚手架。 |
| 4 | **Loopback 隔离** | FastAPI 仅绑 `127.0.0.1:8420`；只读写 Workspace Root 白名单；lab 子进程 + 超时。 |

**刻意留白：** UI 微交互/配色（用 shadcn tokens）；边缘异常（MVP 打控制台即可）；非核心自动化（论文抓取等作远期插件）。

---

## 2. 技术栈与目录契约

### 2.1 黄金技术栈

| 层 | 选型 |
|----|------|
| **前端 `/ui`** | Vite + React 19 + TypeScript + Tailwind v4 + shadcn/ui + `react-resizable-panels` + `remark-math`/`rehype-katex` + Monaco 或 CodeMirror 6 |
| **桌面壳（可选）** | Tauri v2（复用前端；系统快捷键）— Phase 1 可先纯本地 Web |
| **Sidecar `/sidecar`** | Python 3.11+ · FastAPI · Uvicorn · Watchdog · Subprocess · LiteLLM/原生 SDK |

### 2.2 仓库布局（Agent 不得另起平行知识树）

```text
self-development/
├── SPEC.md                 # 仓库内契约副本（与本文同源；合入后放根目录）
├── AGENT.md                # 教学协议（PR #1）
├── 00_roadmap/ … 03_reviews/ · templates/
├── sidecar/
│   ├── main.py             # 路由、CORS、SSE
│   ├── fs_manager.py       # MD 读写、frontmatter、Watchdog
│   ├── tutor_engine.py     # 注入 AGENT.md 的多 Mode Prompt
│   └── lab_runner.py       # [P1] Python/Node 安全执行
└── ui/src/
    ├── components/layout/  # Titlebar, LeftSidebar, CenterStream, RightDrawer
    └── stores/             # Zustand：当前文件、Mode、抽屉 Tab、会话
```

**核心数据流：**  
`Workspace .md/.py` ←读写→ `fs_manager` ←索引→ `SQLite(cache)`  
`CenterStream` ←SSE→ `tutor_engine`（读 `AGENT.md` + 钉选上下文 + Mode）  
`RightDrawer Lab` → `lab_runner` → stdout/stderr（不落云）

---

## 3. 三栏 Layout Slots（写死）

| 栏 | 只允许放 | 禁止 |
|----|----------|------|
| **左 · Navigation & Roadmap** | 工作区文件树（`00_`–`03_` + templates）、Session 列表、掌握度徽章（P1） | 聊天、编辑器、设置大页 |
| **中 · Pedagogical Stream** | Mode Pill、消息流、Context Pin 区、盲区提取按钮（P1） | 文件树、大段笔记编辑 |
| **右 · Inspector & Lab** | Tab「费曼 MD+LaTeX」· Tab「Code/Lab + 运行输出」· 选段→中栏挑刺 | 导航树、全局设置 |

---

## 4. 核心状态机（一次学习闭环）

```text
Idle
  → SelectTopic (左栏点开 roadmap/concept)
  → PinContext (可选：钉 PDF 段/代码)
  → TutorTurn [Mode ∈ {inspire, stress, unlock}]
  → FeynmanEdit (右栏写卡) ⇄ SocraticOnSelection (选段回中栏)
  → LabVerify (右栏跑 02_labs)      # P1；P0 可先手写结果
  → Archive (frontmatter 状态 + 可选写入 03_reviews)
  → Milestone (P1+: 语义 git commit) → Idle
```

**Frontmatter 掌握度（概念卡）：**  
`untouched | learning | lab_passed | internalized`

**Mode 语义：**  
`inspire` = 只线索；`stress` = 杠精反问；`unlock` = 允许直出解析（需显式切换，对齐 `unlock solution`）。

---

## 5. MoSCoW → 三栏映射

### 左栏
- **P0** 文件树实时映射 · Session 切换  
- **P1** 掌握度四态徽章  
- **P2** 双链知识图谱  

### 中栏
- **P0** Mode Pill · SSE 对话 · Context Pinning  
- **P1** 一键提取盲区 → `03_reviews/blindspots.md`  
- **P2** 语音模拟面试（TTS/STT）  

### 右栏
- **P0** 双 Tab：MD+LaTeX 编辑保存 · Lab 预览；选段→中栏挑刺  
- **P1** 一键跑本地 Python/Node（底部 stdout）  
- **P2** FSRS 抽认卡面板  

---

## 6. Sidecar API（Phase 1 最小面）

Base: `http://127.0.0.1:8420` · CORS 仅 localhost UI origin。

| Method | Path | 职责 |
|--------|------|------|
| `GET` | `/health` | 存活 |
| `GET` | `/fs/tree?root=` | 白名单内目录树 |
| `GET` | `/fs/file?path=` | 读文件 + 解析 frontmatter |
| `PUT` | `/fs/file` | 写回 `.md`/源码（path 校验） |
| `GET` | `/fs/events` | SSE：Watchdog 变更 |
| `POST` | `/tutor/chat` | body: `{mode, messages, pins[]}` → SSE token 流；服务端注入 `AGENT.md` |
| `POST` | `/labs/run` | **P1** `{path, runtime: py\|node}` → `{stdout, stderr, exit_code}`；超时杀进程 |
| `GET` | `/sessions` · `PUT /sessions/{id}` | 会话元数据（可先 SQLite） |

错误：MVP 返回 JSON `{error}` + sidecar 控制台日志即可。

---

## 7. 实行 Phase 与验收

| Phase | 目标 | 验收（Done 长什么样） |
|-------|------|------------------------|
| **0 · 协议验证（1–2 天）** | 零前端；IDE + `AGENT.md` 真实学完 1 个知识点 | 模板与提问节奏可用；依赖 PR #1 merge |
| **1 · 三栏 MVP（3–5 天）** | `/ui` 骨架 + `/sidecar` 桥；**只做 P0** | 左开 MD、右编辑保存、中栏带 `AGENT.md` SSE 对话 |
| **2 · 沙盒与批注（第 2 周）** | Mode 切换 · 选段挑刺 · `/labs/run` | 不切 IDE 完成：线索 → 半成品代码 → 跑通 → 费曼卡 |
| **3 · 复盘与 Git（第 3 周+）** | 盲区提取 · FSRS · 一键语义 commit | P1 齐；P2 可按需 |

### Phase 1 任务清单（Agent 开工顺序）

1. 脚手架 `sidecar/`：`health` + `fs/tree|file` + path 白名单  
2. `tutor_engine`：读 `AGENT.md` + 三 Mode 系统提示 + `/tutor/chat` SSE  
3. 脚手架 `ui/`：三栏 resizable 壳 + Zustand（path / mode / drawerTab）  
4. 左栏接 `/fs/tree`；中栏接 SSE；右栏 MD 编辑器接 `GET/PUT /fs/file` + KaTeX 预览  
5. 手工冒烟：打开 `templates/concept-card.md` → inspire 对话 → 另存到 `01_concepts/`  

**非目标（v1）：** 云端 SaaS、原生手机 App、完整 DeepTutor 安装、Modal 设置中心、全网论文抓取。

---

## 8. Agent 执行约束（防幻觉）

- 不得把笔记迁入仅云端 DB；不得新增第四栏或全局 Modal 工作流。  
- 不得在 `inspire`/`stress` 默认直出完整答案。  
- 不得监听非 loopback；不得读写 Workspace 外路径。  
- Phase 1 禁止先做图谱 / FSRS / TTS / Tauri 打磨。  
- 学习内容域保持 FE/SG；lab 以验证理解为最小单位，不作攻击工具链。

---

## 9. 与现有资产关系

| 资产 | 关系 |
|------|------|
| [PR #1](https://github.com/michaelho1117-cloud/self-development/pull/1) | 目录 + `AGENT.md` + 模板；**Phase 0/1 依赖 merge** |
| `docs/project-plan.md` | 学习侧路线图（人读）；本文是产品/架构契约（Agent 搭架子） |
| 仓库根 `SPEC.md` | 本文合入主仓后的权威副本；开发以 SPEC + `AGENT.md` 为准 |

**下一步：** 用户 merge PR #1 → Phase 0 实学 1 点 → 另开工程 PR 搭 `sidecar/` + `ui/`（按 §7 清单，勿扩 scope）。
