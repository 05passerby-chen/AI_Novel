# AI Novel Editor

AI 驱动的长篇小说创作工具。提供从大纲规划、角色设计、章节写作到世界设定的一站式创作体验，由 DeepSeek 大模型提供智能辅助。
目前写的比较简陋，还望包涵
---

## 功能特性

- **📋 大纲规划** — AI 自动生成故事梗概、情节线、情感弧光和章节摘要
- **👤 角色管理** — 完整的角色档案，含性格、外貌、背景、目标、秘密等维度
- **✍️ 章节写作** — AI 辅助逐章生成正文，保持角色一致性和情节连贯性
- **🌍 世界圣经** — 管理世界观设定：物品、地点、势力、力量体系、时间线
- **🎬 场景卡片** — 按章节组织场景，支持拖拽排序
- **🔮 伏笔管理** — 追踪已埋设和已揭示的伏笔
- **🔍 向量检索** — ChromaDB 驱动的角色语义搜索，确保角色行为一致

---

## 系统架构

```
┌────────────────────┐     ┌────────────────────┐
│  launcher.exe      │     │  install_deps.exe  │
│  桌面启动器 (GUI)   │     │  依赖安装器 (GUI)   │
└──────┬─────────────┘     └────────────────────┘
       │ 启动子进程
       ▼
┌────────────────────────────────────────────┐
│              后端 (FastAPI)                 │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │  api/    │ │ services/│ │  prompts/  │  │
│  │ REST API │ │ 业务逻辑  │ │ AI 提示词   │  │
│  └──────────┘ └──────────┘ └────────────┘  │
│       │              │                      │
│       ▼              ▼                      │
│  ┌──────────┐ ┌──────────────────────┐     │
│  │ ~/Novels │ │ ~/.ai_novel_editor_  │     │
│  │ JSON+MD  │ │ vectors/ (ChromaDB)  │     │
│  └──────────┘ └──────────────────────┘     │
└────────────────────────────────────────────┘
       │ 静态文件服务
       ▼
┌────────────────────────────────────────────┐
│            前端 (React SPA)                 │
│        dist/index.html + assets/           │
└────────────────────────────────────────────┘
```

---

## 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Windows 10+ | — | 当前仅支持 Windows |
| Python | ≥ 3.9 | 用于运行后端服务 |
| DeepSeek API Key | — | 在应用内 Settings 页面配置 |
| 网络连接 | — | 下载依赖 + 调用 AI API |

---

## 快速开始

### 1. 安装依赖

双击项目根目录下的 **`install_deps.exe`**，程序会自动：

- 检测系统中的 Python 安装
- 通过 pip 安装所需依赖包
- 生成 `backend/.env` 配置文件

> 如果 exe 无法正常运行，也可以手动执行：
> ```cmd
> pip install -r backend/requirements.txt
> ```
> 然后复制 `backend/.env.template` 为 `backend/.env` 并填入实际路径。

### 2. 启动应用

双击 **`launcher.exe`**，界面会显示环境信息。点击 **▶ Start Server** 启动后端，浏览器会自动打开前端页面。

默认地址：`http://127.0.0.1:8765`

---

## 项目结构

```
AI_NovelEditor/
├── install_deps.exe          # 依赖安装器（一次性使用）
├── launcher.exe              # 桌面启动器
├── README.md
├── dist/                     # 前端（React SPA，预构建）
│   ├── index.html
│   └── assets/
├── backend/
│   ├── main.py               # FastAPI 入口
│   ├── install_deps.py       # install_deps.exe 源码
│   ├── launcher.py           # launcher.exe 源码
│   ├── requirements.txt      # Python 依赖清单
│   ├── .env.template         # .env 模板
│   ├── api/                  # REST API 路由
│   │   ├── novels.py         # 小说 CRUD
│   │   ├── characters.py     # 角色 CRUD
│   │   ├── chapters.py       # 章节 CRUD
│   │   ├── outline.py        # 大纲 CRUD + 影响分析
│   │   ├── scenes.py         # 场景卡片 CRUD
│   │   ├── world_bible.py    # 世界观设定 CRUD
│   │   ├── foreshadowing.py  # 伏笔 CRUD
│   │   ├── generate.py       # AI 生成（大纲/角色/向量）
│   │   ├── chapter_generate.py  # AI 生成章节正文
│   │   ├── settings.py       # LLM 设置（API Key 等）
│   │   └── prompts_editor.py # 提示词编辑器
│   ├── models/               # Pydantic 数据模型
│   ├── services/             # 业务逻辑层
│   │   ├── file_service.py   # 文件读写（JSON/Markdown）
│   │   ├── llm_service.py    # DeepSeek API 调用
│   │   ├── vector_service.py # ChromaDB 向量索引
│   │   ├── outline_service.py    # 大纲 AI 生成逻辑
│   │   └── chapter_service.py    # 章节 AI 生成逻辑
│   └── prompts/              # AI 提示词模板（可在线编辑）
│       ├── outline.py
│       ├── chapter.py
│       ├── character.py
│       └── analysis.py
└── Novels/                   # 用户小说数据（运行时创建）
```

---

## API 参考

所有接口前缀：`/api`

### 小说

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/novels` | 列出所有小说 |
| POST | `/api/novels` | 创建小说 |
| GET | `/api/novels/{id}` | 获取小说详情 |
| PUT | `/api/novels/{id}` | 更新小说 |
| DELETE | `/api/novels/{id}` | 删除小说 |

### 角色

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/novels/{id}/characters` | 列出角色 |
| POST | `/api/novels/{id}/characters` | 创建角色 |
| GET | `/api/novels/{id}/characters/{cid}` | 获取角色 |
| PUT | `/api/novels/{id}/characters/{cid}` | 更新角色 |
| DELETE | `/api/novels/{id}/characters/{cid}` | 删除角色 |
| POST | `/api/novels/{id}/characters/{cid}/generate-dynamics` | AI 生成角色动态 |

### 大纲

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/novels/{id}/outline` | 获取大纲 |
| PUT | `/api/novels/{id}/outline` | 保存大纲 |
| POST | `/api/novels/{id}/outline/generate` | AI 生成大纲 |
| POST | `/api/novels/{id}/outline/extract-characters` | AI 从大纲提取角色 |
| POST | `/api/novels/{id}/outline/analyze-impact` | 分析角色变动对大纲的影响 |

### 章节

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/novels/{id}/chapters` | 列出章节 |
| POST | `/api/novels/{id}/chapters` | 创建章节 |
| GET | `/api/novels/{id}/chapters/{n}` | 获取章节 |
| PUT | `/api/novels/{id}/chapters/{n}` | 更新章节 |
| DELETE | `/api/novels/{id}/chapters/{n}` | 删除章节 |
| POST | `/api/novels/{id}/chapters/{n}/generate` | AI 生成章节正文 |

### 场景卡片

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/novels/{id}/scenes` | 列出场景 |
| POST | `/api/novels/{id}/scenes` | 创建场景 |
| PUT | `/api/novels/{id}/scenes/{sid}` | 更新场景 |
| PUT | `/api/novels/{id}/scenes/reorder` | 场景排序 |
| DELETE | `/api/novels/{id}/scenes/{sid}` | 删除场景 |

### 世界圣经

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/novels/{id}/world-bible/{category}` | 列出分类条目 |
| POST | `/api/novels/{id}/world-bible/{category}` | 创建条目 |
| PUT | `/api/novels/{id}/world-bible/{category}/{eid}` | 更新条目 |
| DELETE | `/api/novels/{id}/world-bible/{category}/{eid}` | 删除条目 |

> `category`: `items` / `locations` / `factions` / `power` / `timeline`

### 伏笔

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/novels/{id}/foreshadowing` | 列出伏笔 |
| POST | `/api/novels/{id}/foreshadowing` | 创建伏笔 |
| PUT | `/api/novels/{id}/foreshadowing/{eid}` | 更新伏笔 |
| DELETE | `/api/novels/{id}/foreshadowing/{eid}` | 删除伏笔 |

### 设置 & 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/settings` | 获取 LLM 设置 |
| PUT | `/api/settings` | 保存 LLM 设置 |
| GET | `/api/prompts/{name}` | 获取提示词 |
| PUT | `/api/prompts/{name}` | 更新提示词 |

---

## 数据存储

| 路径 | 内容 |
|------|------|
| `~/Novels/{novel_id}/` | 小说正文、大纲、角色、章节（JSON + Markdown） |
| `~/.ai_novel_editor_vectors/` | ChromaDB 向量索引 |
| `~/.ai_novel_editor_settings.json` | LLM 设置（API Key、模型等） |
| `backend/.env` | 运行时环境变量（由 install_deps 生成） |
| `backend/launcher_settings.json` | 启动器 UI 状态（端口、小说目录） |

### 小说目录结构示例

```
~/Novels/
└── a1b2c3d4e5f6/
    ├── metadata.json          # 标题、作者、题材、类型
    ├── outline.json           # 梗概、情节线、情感弧光
    ├── characters.json        # 角色档案
    ├── scene_cards.json       # 场景卡片
    ├── foreshadowing.json     # 伏笔
    ├── items.json             # 世界圣经·物品
    ├── locations.json         # 世界圣经·地点
    ├── factions.json          # 世界圣经·势力
    ├── power.json             # 世界圣经·力量体系
    ├── timeline.json          # 世界圣经·时间线
    └── chapters/
        ├── _index.json        # 章节索引
        ├── 0001.md            # 第 1 章正文
        ├── 0002.md            # 第 2 章正文
        └── ...
```

---

## 从源码构建

如果需要重新编译 exe：

```cmd
pip install pyinstaller

# 构建依赖安装器
pyinstaller --onefile --windowed --name install_deps backend/install_deps.py

# 构建启动器
pyinstaller --onefile --windowed --name launcher backend/launcher.py
```

生成的 exe 在 `dist/` 目录下，复制到项目根目录即可。

---

## 常见问题

### install_deps.exe 闪退

确保已安装 **Python 3.9+** 并添加到系统 PATH。也可以手动执行：

```cmd
pip install -r backend/requirements.txt
```

然后复制 `backend/.env.template` 为 `backend/.env` 并填入正确路径。

### 启动后看不到之前的小说

检查 `backend/.env` 中的 `NOVELS_DIR` 是否正确。默认路径为 `C:\Users\<用户名>\Novels`。

### 端口被占用

编辑 `backend/.env` 中的 `PORT` 值，或在启动器界面修改端口号。

### 卸载清理

```cmd
# 卸载依赖
pip uninstall fastapi uvicorn openai chromadb pydantic python-dotenv

# 删除小说数据
rmdir /s %USERPROFILE%\Novels
rmdir /s %USERPROFILE%\.ai_novel_editor_vectors

# 删除配置文件
del %USERPROFILE%\.ai_novel_editor_settings.json
del backend\.env
del backend\launcher_settings.json
```

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + React Router v6 + lucide-react |
| 后端 | Python FastAPI + Uvicorn |
| AI | DeepSeek API（OpenAI 兼容） |
| 向量库 | ChromaDB（PersistentClient，SQLite 存储） |
| 桌面 GUI | Python tkinter（启动器 + 安装器） |
| 打包 | PyInstaller（--onefile --windowed） |
