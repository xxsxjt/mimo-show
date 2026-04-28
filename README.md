# MiMo Show

个人 AI 项目展示。

## 项目

### 1. [ai-novel-agent](./ai-novel-agent/)

用 CodeBuddy Agent + GLM 模型辅助写网文的工具链。维护几份结构化 Markdown 文档（伏笔追踪、大纲时间线、角色卡片）配合 Agent 的读写闭环，减少长篇写作中伏笔遗忘和情节矛盾的问题。另外写了个 Playwright 脚本自动往番茄小说发布和修改章节。

实际用了一个月以上，写了约 197 章 / 43 万字。不算成熟产品，更像给自己用的 workflow + 脚本。

### 2. [ai_sandbox](https://github.com/xxsxjt/ai_sandbox)

AI 交互实验项目，纯前端为主，接 OpenAI 兼容 API。做了六个模块：多角色对话模拟、狼人杀、战斗模拟、占卜、AI 回复分析、文字冒险游戏。后端是可选的 Java 小服务，主要做联网搜索和跨域代理。可打包 Electron 桌面端。

功能都能跑但比较粗糙，精力和 token 都有限，很多功能没完善。

### 3. [world-guardian](./world-guardian/)

多人在线塔防生存游戏《万界守卫》，用 Claude Code 生成。Node.js + WebSocket 服务器，Vue 3 + Canvas 客户端，10+ 个游戏系统（战斗、经济、塔防、程序化地图、毒圈等）。支持4人在线，三种职业，六边形地图。

基本功能能跑，但游戏平衡性没调，有些系统交互有 bug，属于 demo 级别。

---

## 我的 AI 使用情况

- **Agent 工具**：CodeBuddy (WorkBuddy)、Claude Code
- **底层模型**：GLM 系列、Claude 系列
- **使用场景**：长文创作、自动化脚本、前端项目、游戏开发
