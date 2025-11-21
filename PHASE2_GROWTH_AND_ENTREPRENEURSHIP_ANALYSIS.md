# MIRIX Phase 2: 个人成长与创业复盘功能分析

**文档日期**: 2025-11-21
**核心目标**:
1. **个人成长（内功）** - AI 帮助用户复盘和成长
2. **创业成功（外功）** - AI 帮助用户实现创业目标

---

## 📊 当前系统能力分析（基于 Phase 1 实现）

### 已有的强项 ✅

**完整数据捕获流程**：
```
截图监控 → OCR (tesseract) → Raw Memory (PostgreSQL + pgvector)
                ↓
        LLM 多模态分析 (Gemini 2.0 Flash)
                ↓
    6 种记忆 + raw_memory_references 双向关联
```

**Agent 生态系统（9个Agent）**：
1. **MetaMemoryAgent** - 智能分类调度器
2. **SemanticMemoryAgent** - 知识/概念存储
3. **EpisodicMemoryAgent** - 事件/时间线存储
4. **ProceduralMemoryAgent** - 流程/技能存储
5. **ResourceMemoryAgent** - 资源/链接存储
6. **KnowledgeVaultAgent** - 结构化知识库
7. **CoreMemoryAgent** - 用户核心信息
8. **ReflexionAgent** - 记忆清理 + 浅层模式识别
9. **BackgroundAgent** - 预测下一步行为

**数据可追溯性**：
- ✅ raw_memory_references 双向关联
- ✅ 用户可以验证每个记忆的来源
- ✅ 前端紫色徽章显示（app 图标、URL、时间、OCR 预览）
- ✅ 点击跳转到原始截图

### 关键技术特点

**多模态 LLM 理解**：
- LLM 可以"看"截图（Google Cloud File URI / base64）
- LLM 可以"读" OCR 文本
- LLM 根据视觉 + 文本智能分类存储

**向量搜索能力**：
- pgvector 支持语义搜索
- text-embedding-3-small (1536 维)
- 支持"找关于 AI 的记忆"这种模糊查询

---

## ❌ 关键缺口分析（针对核心目标）

### 缺口 1：ReflexionAgent 功能不足

**当前状态** (`mirix/prompts/system/base/reflexion_agent.txt`):
```
Task 7: User Lifestyle Pattern Analysis
- Analyze episodic memories to identify patterns about user lifestyle
- Look for patterns such as:
  • Daily routines (e.g., "User sends emails every morning")
  • Work patterns (e.g., "User is working 10/24 hours today")
  • Activity changes (e.g., "User is watching videos more than before today, they might be relaxing")
  • Behavioral trends or shifts
```

**问题**：
- ✅ 做清理（去重、修复 corruption）
- ✅ 识别**浅层模式**（"今天看视频比平时多"）
- ❌ **没有深度复盘**（为什么看视频多？是休息还是拖延？效果如何？）
- ❌ **没有成长分析**（这周学了什么？技能有提升吗？）
- ❌ **没有对比功能**（本周 vs 上周的变化）
- ❌ **没有可行动建议**（明天应该做什么？）

**核心问题**：只是"观察"，不是"成长教练"。

---

### 缺口 2：没有"时间维度分析"功能

**当前数据结构**：
```python
# episodic_memory 有 occurred_at
# semantic_memory 有 created_at
# raw_memory 有 captured_at
```

**但是缺少**：
- ❌ 时间范围聚合（"这周我做了什么？"）
- ❌ 时间对比（"本周 vs 上周"）
- ❌ 趋势分析（"学习时间是增加还是减少？"）
- ❌ 时间分布统计（"工作时间分布"）
- ❌ 时间线可视化（一天/一周的活动流）

**影响**：
- 无法做日复盘、周复盘、月复盘
- 无法追踪成长轨迹
- 无法识别效率模式（什么时候最高效？）

---

### 缺口 3：没有"目标系统"

**当前系统只记录"发生了什么"，不记录"想要什么"**：
- ❌ 没有 Goals 表/数据结构
- ❌ 没有 OKR/KPI 追踪
- ❌ 没有目标进度计算
- ❌ 无法对齐"行为"和"目标"
- ❌ 无法回答"今天的工作对目标有帮助吗？"

**创业场景的问题**：
```
用户目标：3 个月内发布 MIRIX Beta 版，获取 100 个用户
当前系统：只知道用户每天在写代码，但不知道进度如何
```

---

### 缺口 4：BackgroundAgent 是"预测"，不是"复盘"

**BackgroundAgent 的作用** (`mirix/prompts/system/screen_monitor/background_agent.txt`):
```
Immediate Visual Predictions (Next 30 seconds - 5 minutes)
   • Interface Actions: Predict next clicks, navigation, or interface interactions
   • Content Creation: Anticipate text entry, file creation, or content manipulation

Short-term Workflow Predictions (Next 5 minutes - 1 hour)
   • Application Switching: Predict transitions between different applications
   • File Operations: Anticipate file opening, saving, or manipulation needs
```

**定位**：
- ✅ 向前看（预测下一步）
- ❌ 向后看（复盘过去）

**BackgroundAgent 是"贾维斯"（预测助手），不是"成长教练"（复盘导师）。**

---

### 缺口 5：没有"成长指标系统"

**如何定义"成长"？**
- ❌ 没有量化指标（学习时间、新知识数量、技能进步）
- ❌ 没有可视化（成长曲线、技能树）
- ❌ 没有对比基准（本周 vs 上周、本月 vs 上月）
- ❌ 没有目标对齐（行为 vs 目标的匹配度）

**用户视角的问题**：
```
用户问：我这周进步了吗？
系统答：（只能罗列记忆，无法给出结论）
```

---

## 🎯 目标 1：个人成长（内功）

### 核心需求：从"被动记录"到"主动成长"

#### 1.1 时间线复盘

**日复盘**：
```markdown
# 今日复盘 (2025-11-21)

## 时间分配
- 工作：6.5 小时 (↓0.5h vs 昨天)
- 学习：2 小时 (↑1h vs 昨天)
- 娱乐：1 小时
- 社交：0.5 小时

## 今日成果
- 完成 MIRIX Phase 1 任务 21 ✅
- 学习了 ReflexionAgent 和 BackgroundAgent 的设计
- 阅读了 3 篇关于 AI Agent 架构的文章

## 今日亮点
- 专注工作时段：09:00-12:00 (3 小时连续深度工作)
- 新增知识点：5 个（pgvector、multi-agent 架构、raw_memory_references、...）

## 需要改进
- 下午 14:00-15:00 分心频繁（切换到 YouTube 3 次）
- 晚饭后效率低下（19:00-20:00 几乎没产出）

## 明日建议
- 保持上午的深度工作状态
- 下午设定专注时段（番茄工作法）
- 考虑 19:00 后安排轻松任务或学习
```

**周复盘**：
```markdown
# 本周复盘 (2025-11-17 ~ 2025-11-23)

## 时间分配对比
|        | 本周  | 上周  | 变化   |
|--------|-------|-------|--------|
| 工作   | 32h   | 28h   | +4h ↑  |
| 学习   | 8h    | 5h    | +3h ↑  |
| 娱乐   | 6h    | 10h   | -4h ↓  |

## 本周成果
- ✅ 完成 MIRIX Phase 1 所有任务
- ✅ 实现 raw_memory 双向关联
- ✅ 前端记忆引用展示功能
- ⚠️ OCR 准确率测试尚未完成

## 成长亮点
- 工作时间增加 4 小时（效率提升）
- 学习时间增加 3 小时（持续成长）
- 深度工作时段更长（平均 2.5h/天 → 3h/天）

## 需要改进
- 周三和周五下午效率低（多次分心）
- 学习内容缺乏系统性（随机阅读，缺少主题规划）

## 下周计划
- [ ] 完成 Phase 1 测试验证
- [ ] 规划 Phase 2 功能
- [ ] 系统学习 PostgreSQL 向量搜索（2 小时）
```

**月复盘**：
```markdown
# 本月复盘 (2025-11)

## 月度目标达成
- [ ] 完成 MIRIX Phase 1 和 Phase 2（达成度 70%）
- [x] 学习 AI Agent 架构（完成 ✅）
- [ ] 发布技术博客 3 篇（完成 1 篇，达成度 33%）

## 成长趋势
- 工作效率：📈 提升 15%（对比 10 月）
- 学习时间：📈 增加 20 小时（对比 10 月）
- 新增技能：Multi-Agent 系统、pgvector、OCR

## 知识图谱
- AI/Agent 架构（深入）
- PostgreSQL 向量搜索（入门）
- FastAPI 开发（熟练）
- React Hooks（熟练）

## 下月重点
- 完成 Phase 2 复盘功能
- 系统学习 LangChain 和 LangGraph
- 发布 2 篇技术博客
```

---

#### 1.2 成长对比分析

**对比维度**：

**A. 时间分配对比**：
```python
本周 vs 上周：
  - 工作时间变化
  - 学习时间变化
  - 娱乐时间变化
  - 深度工作时长变化
```

**B. 知识积累对比**：
```python
本周 vs 上周：
  - 新增 semantic_memory 数量
  - 学习主题分布
  - 知识深度评估
```

**C. 效率对比**：
```python
本周 vs 上周：
  - 专注时长（连续工作不被打断）
  - 任务完成数量
  - 分心频率
  - 高效时段识别
```

---

#### 1.3 习惯追踪与优化

**工作习惯分析**：
```markdown
## 工作模式分析

### 高效时段
- 🌅 早上 09:00-12:00（深度工作，专注度 90%）
- 🌃 晚上 21:00-23:00（编码效率高，但持续性差）

### 低效时段
- 🌞 下午 14:00-16:00（饭后疲劳，分心频繁）
- 🌆 晚饭后 19:00-20:00（过渡时间，效率低）

### 分心模式
- YouTube 浏览：平均 3 次/天，集中在下午
- 社交媒体：平均 2 次/天，集中在休息时段
- 邮件检查：平均 5 次/天，打断工作流

### 优化建议
- 保护早上 09:00-12:00 黄金时段（关闭通知）
- 下午采用番茄工作法（25 分钟专注 + 5 分钟休息）
- 设定固定邮件检查时间（10:00, 14:00, 17:00）
- 晚饭后安排轻松任务或学习（避免高强度编码）
```

**学习习惯分析**：
```markdown
## 学习模式分析

### 学习时间分布
- 工作日：平均 1.5 小时/天
- 周末：平均 3 小时/天

### 学习主题
- AI/Agent 架构（40%）
- 数据库技术（30%）
- 前端开发（20%）
- 其他（10%）

### 学习深度
- 深度学习（系统性阅读文档/书籍）：30%
- 中度学习（阅读博客/教程）：50%
- 浅度学习（快速查阅/Stack Overflow）：20%

### 优化建议
- 增加深度学习比例（目标 50%）
- 每周设定学习主题（避免随机阅读）
- 建立学习笔记系统（知识留存）
```

---

#### 1.4 知识图谱构建

**技能树可视化**：
```
AI/Machine Learning
├── LLM 应用开发 ⭐⭐⭐⭐⭐ (精通)
│   ├── Prompt Engineering
│   ├── Function Calling
│   └── Multi-Agent Systems
├── Embeddings & Vector Search ⭐⭐⭐⭐ (熟练)
│   ├── text-embedding-3-small
│   ├── pgvector
│   └── Semantic Search
└── Fine-tuning ⭐ (入门)

Backend Development
├── FastAPI ⭐⭐⭐⭐⭐ (精通)
├── PostgreSQL ⭐⭐⭐⭐ (熟练)
│   ├── SQL Queries
│   ├── pgvector Extension
│   └── Performance Optimization
├── SQLAlchemy ORM ⭐⭐⭐⭐ (熟练)
└── Redis (待学习)

Frontend Development
├── React ⭐⭐⭐⭐ (熟练)
│   ├── Hooks
│   ├── State Management
│   └── Performance Optimization
├── JavaScript/ES6+ ⭐⭐⭐⭐ (熟练)
└── TypeScript ⭐⭐⭐ (中级)
```

**知识缺口识别**：
```markdown
## 需要加强的领域

### 高优先级
- [ ] LangChain/LangGraph（多 Agent 协作）
- [ ] PostgreSQL 性能优化（大规模数据）
- [ ] 前端性能优化（React 性能瓶颈）

### 中优先级
- [ ] Redis 缓存（减少数据库压力）
- [ ] Docker/Kubernetes（部署优化）
- [ ] 监控和日志（observability）

### 低优先级
- [ ] GraphQL（API 优化）
- [ ] WebSocket（实时通信）
```

---

#### 1.5 可行动建议生成

**AI 教练的建议**：
```markdown
## 🎯 本周行动建议

### 习惯优化
1. ⏰ 保护早上黄金时段
   - 09:00-12:00 关闭所有通知
   - 只做最重要的深度工作
   - 预期效果：提升 30% 产出

2. 📱 减少分心时间
   - 使用番茄工作法（下午时段）
   - 设定固定社交媒体时间（12:00, 18:00）
   - 预期效果：减少 50% 分心次数

### 学习优化
3. 📚 系统学习 LangChain
   - 周一-周三：阅读官方文档（2h）
   - 周四-周五：实战项目（3h）
   - 周末：总结笔记（1h）

4. 📝 建立学习笔记系统
   - 使用 Obsidian 记录学习笔记
   - 每天花 15 分钟整理
   - 建立知识图谱链接

### 创业优化
5. 🚀 推进 MIRIX Phase 2
   - 完成 GrowthAnalysisAgent 设计（周一）
   - 实现时间范围查询（周二-周三）
   - 前端 Dashboard 原型（周四-周五）

6. 👥 用户访谈
   - 联系 2 位潜在用户
   - 收集反馈和需求
   - 调整产品方向
```

---

## 🎯 目标 2：创业成功（外功）

### 核心需求：目标对齐 + 进度追踪 + 决策复盘

#### 2.1 目标系统设计

**Goals 表结构**：
```sql
CREATE TABLE goals (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    organization_id TEXT,

    -- 基本信息
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,  -- 'career', 'learning', 'health', 'entrepreneurship', 'personal'
    priority TEXT,  -- 'high', 'medium', 'low'

    -- 时间维度
    target_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,

    -- 进度追踪
    status TEXT,  -- 'active', 'completed', 'abandoned', 'paused'
    progress_percentage REAL DEFAULT 0.0,

    -- 关联数据
    parent_goal_id TEXT,  -- 支持目标层级
    raw_memory_references JSON DEFAULT '[]',  -- 关联的原始记忆
    related_memories JSON DEFAULT '{}',  -- 关联的各类记忆

    -- 元数据
    metadata JSON DEFAULT '{}',
    tags JSON DEFAULT '[]',

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (parent_goal_id) REFERENCES goals(id)
);
```

**目标示例**：
```json
{
  "id": "goal-startup-2025",
  "title": "MIRIX 产品化并实现盈利",
  "category": "entrepreneurship",
  "priority": "high",
  "target_date": "2025-12-31",
  "status": "active",
  "progress_percentage": 25.0,

  "sub_goals": [
    {
      "id": "goal-phase2-completion",
      "title": "完成 Phase 2 功能开发",
      "target_date": "2025-12-31",
      "status": "in_progress",
      "progress_percentage": 40.0
    },
    {
      "id": "goal-user-acquisition",
      "title": "获取 100 个 Beta 用户",
      "target_date": "2026-02-28",
      "status": "not_started",
      "progress_percentage": 0.0
    },
    {
      "id": "goal-revenue",
      "title": "月收入达到 $1000",
      "target_date": "2026-06-30",
      "status": "not_started",
      "progress_percentage": 0.0
    }
  ]
}
```

---

#### 2.2 目标对齐分析

**每日目标对齐**：
```markdown
# 今日目标对齐报告 (2025-11-21)

## 主要目标
🎯 完成 MIRIX Phase 2 功能开发（进度 40% → 45%）

## 今日行为分析
- ✅ MIRIX 开发：6.5 小时（高度对齐 ⭐⭐⭐⭐⭐）
  - 实现了 GrowthAnalysisAgent 设计
  - 完成了时间范围查询功能
- ✅ 学习 LangChain：2 小时（中度对齐 ⭐⭐⭐）
  - 为后续多 Agent 协作做准备
- ⚠️ 看 YouTube 视频：1 小时（无对齐）
  - 建议：减少娱乐时间，或选择教育类视频

## 目标对齐度
- 今日对齐度：85%（6.5h / 7.5h 有效时间）
- 本周平均对齐度：78%
- 建议：继续保持，争取达到 90%

## 进度更新
- Phase 2 进度：40% → 45%（+5%）
- 预计完成日期：2025-12-15（提前 2 周）
```

---

#### 2.3 项目进度追踪

**项目看板**：
```markdown
# MIRIX 项目进度看板

## Phase 1: 核心记忆系统 ✅
- 状态：已完成
- 完成日期：2025-11-19
- 耗时：3 周
- 关键成果：
  - ✅ Raw Memory 双向关联
  - ✅ 6 种记忆类型完整实现
  - ✅ 前端记忆引用展示

## Phase 2: 复盘和成长功能 ⏳
- 状态：进行中（45%）
- 开始日期：2025-11-20
- 预计完成：2025-12-15
- 当前任务：
  - ✅ GrowthAnalysisAgent 设计（已完成）
  - ✅ 时间范围查询（已完成）
  - ⏳ 成长指标计算（进行中）
  - ⏳ 前端 Dashboard（计划中）
- 遇到的问题：
  - ⚠️ 时间分配算法复杂度较高
  - ⚠️ 前端图表库选型待定

## Phase 3: 多模态和智能推荐 📅
- 状态：计划中
- 预计开始：2026-01-01
- 关键功能：
  - 语音输入支持
  - 视频内容理解
  - 智能推荐引擎
```

---

#### 2.4 资源管理

**时间资源分析**：
```markdown
# 本周时间资源分析

## 总时间分配
- 总可用时间：112 小时（7 天 × 16 小时）
- 实际工作时间：40 小时（36%）
- 睡眠休息：56 小时（50%）
- 生活琐事：16 小时（14%）

## 创业时间细分
- MIRIX 开发：32 小时（80%）
  - 后端开发：20 小时
  - 前端开发：8 小时
  - 测试调试：4 小时
- 学习提升：5 小时（12.5%）
  - 阅读文档：3 小时
  - 技术文章：2 小时
- 营销推广：3 小时（7.5%）
  - 社交媒体：2 小时
  - 用户访谈：1 小时

## 优化建议
⚠️ 营销时间不足：只有 7.5%，建议增加到 20%
💡 开发效率高：保持当前节奏
📚 学习时间合理：可以适当增加到 15%
```

**资金资源追踪**：
```markdown
# 本月成本追踪

## LLM 成本
- Gemini 2.0 Flash API：$45.00
  - 截图分析：$30.00（~15,000 次调用）
  - 对话生成：$10.00
  - 记忆处理：$5.00
- 预计月成本：~$180.00
- 优化机会：
  - 减少重复分析（缓存机制）
  - 批量处理截图（降低调用次数）

## 基础设施成本
- PostgreSQL 数据库：$25.00/月
- 对象存储（截图）：$10.00/月
- 域名和 SSL：$5.00/月

## 总计
- 本月成本：$220.00
- 预计年成本：$2,640.00
```

**知识资源管理**：
```markdown
# 知识资源盘点

## 已掌握的核心技能
- ✅ Multi-Agent 系统架构
- ✅ LLM Function Calling
- ✅ PostgreSQL + pgvector
- ✅ FastAPI + React 全栈开发

## 需要补充的技能
- [ ] 用户增长策略（营销）
- [ ] 数据分析和可视化（Dashboard）
- [ ] 性能优化（大规模数据）

## 知识来源
- 官方文档：40%
- 技术博客：30%
- Stack Overflow：20%
- 实战经验：10%

## 知识留存策略
- 建立 Obsidian 笔记系统
- 每周总结学习笔记
- 定期复习关键知识点
```

---

#### 2.5 决策记录与复盘

**决策日志**：
```markdown
# 重要决策记录

## 决策 #001: 选择 Gemini 2.0 Flash 而非 GPT-4
- 日期：2025-11-15
- 背景：需要多模态 LLM 分析截图
- 理由：
  - 成本：Gemini 比 GPT-4 便宜 70%
  - 性能：Gemini 2.0 Flash 速度更快
  - 功能：原生支持 Google Cloud Storage
- 决策者：我自己
- raw_memory_references: ["rawmem-xxx", "rawmem-yyy"]

## 决策 #002: 优先实现 raw_memory 双向关联
- 日期：2025-11-18
- 背景：Phase 1 功能优先级排序
- 理由：
  - 用户信任：可追溯性增强用户信任
  - 差异化：竞品没有这个功能
  - 技术价值：为后续分析打基础
- 决策者：我自己
- raw_memory_references: ["rawmem-zzz"]

## 决策 #003: Phase 2 先做成长功能，后做创业功能
- 日期：2025-11-21
- 背景：Phase 2 功能规划
- 理由：
  - 个人成长是内功，更基础
  - 复盘功能用户价值更直接
  - 创业功能依赖成长功能的数据
- 决策者：我自己 + Claude 建议
```

**决策效果评估**：
```markdown
# 决策复盘

## 决策 #001 效果评估（2025-11-21）
✅ **成功**
- 成本节省：预计每月节省 $150
- 性能满意：Gemini 2.0 速度快，准确率高
- 无重大问题：API 稳定，支持良好

## 决策 #002 效果评估（2025-11-21）
✅ **成功**
- 用户反馈：紫色徽章设计受好评
- 技术价值：为 Phase 2 分析功能打下基础
- 开发成本：比预期多花了 2 天（值得）

## 需要调整的决策
- 暂无
```

---

## 🚀 Phase 2 实施计划

### Phase 2A：复盘和成长功能（内功）

**优先级：🔥 最高**

#### 任务 1：创建 GrowthAnalysisAgent
```
文件：
- mirix/agent/growth_analysis_agent.py
- mirix/prompts/system/base/growth_analysis_agent.txt
- mirix/prompts/system/screen_monitor/growth_analysis_agent.txt

功能：
- 时间线回顾（日/周/月）
- 成长指标计算
- 习惯分析
- 可行动建议生成

预计工作量：2-3 天
```

#### 任务 2：实现时间范围查询
```
文件：
- mirix/services/raw_memory_manager.py
- mirix/services/semantic_memory_manager.py
- mirix/services/episodic_memory_manager.py
- (其他 memory managers)

新增方法：
- get_memories_by_timerange(start, end, organization_id)
- get_memories_grouped_by_day(start, end)
- get_memories_grouped_by_week(start, end)

预计工作量：1 天
```

#### 任务 3：实现成长指标计算
```
文件：
- mirix/services/growth_metrics_service.py

功能：
- calculate_daily_metrics(user_id, date)
  - 学习时间、工作时间、娱乐时间
  - 新增知识数量
  - 专注时长、分心次数
- calculate_weekly_comparison(user_id, week)
  - 本周 vs 上周对比
- calculate_habit_patterns(user_id, timerange)
  - 高效时段识别
  - 低效时段识别
  - 分心模式分析

预计工作量：3-4 天
```

#### 任务 4：添加定时触发机制
```
文件：
- mirix/settings.py
- mirix/scheduler.py (新建)

功能：
- 每天 21:00 自动触发日复盘
- 每周日 20:00 自动触发周复盘
- 每月最后一天触发月复盘

技术方案：
- 使用 APScheduler 或 Celery Beat
- 触发 GrowthAnalysisAgent

预计工作量：1 天
```

#### 任务 5：前端 Growth Dashboard
```
文件：
- frontend/src/components/GrowthDashboard.js
- frontend/src/components/GrowthDashboard.css

功能：
- 今日/本周/本月复盘视图
- 时间分配饼图
- 成长曲线图（学习时间、工作效率）
- 习惯分析图表
- 可行动建议列表

技术方案：
- 使用 Chart.js 或 Recharts 图表库
- 响应式设计

预计工作量：3-4 天
```

#### 任务 6：API 端点
```
文件：
- mirix/server/fastapi_server.py

新增端点：
- GET /growth/daily_review?date=2025-11-21
- GET /growth/weekly_review?week=2025-W47
- GET /growth/monthly_review?month=2025-11
- GET /growth/metrics?start=...&end=...
- POST /growth/trigger_review (手动触发)

预计工作量：1 天
```

**Phase 2A 总工作量：11-14 天**

---

### Phase 2B：目标和创业功能（外功）

**优先级：⚡ 中等**

#### 任务 7：创建 Goals 数据表
```
文件：
- mirix/orm/goal.py
- database/migrate_add_goals.sql

字段：
- id, user_id, organization_id
- title, description, category, priority
- target_date, created_at, completed_at
- status, progress_percentage
- parent_goal_id (层级支持)
- raw_memory_references, related_memories

预计工作量：1 天
```

#### 任务 8：实现 GoalManager 服务
```
文件：
- mirix/services/goal_manager.py

功能：
- insert_goal(...)
- update_goal_progress(goal_id, progress)
- get_goals_by_status(user_id, status)
- get_goal_hierarchy(goal_id)  # 获取目标树
- calculate_goal_alignment(user_id, date)  # 行为与目标对齐度

预计工作量：2 天
```

#### 任务 9：创建 EntrepreneurshipCoachAgent
```
文件：
- mirix/agent/entrepreneurship_coach_agent.py
- mirix/prompts/system/entrepreneurship_coach_agent.txt

功能：
- 目标对齐检查（每日行为 vs 创业目标）
- 项目进度追踪
- 时间分配分析（开发、营销、学习）
- 决策记录和复盘
- 资源优化建议
- 风险预警

预计工作量：2-3 天
```

#### 任务 10：实现目标对齐功能
```
文件：
- mirix/services/goal_alignment_service.py

功能：
- calculate_daily_alignment(user_id, date)
  - 今天的行为与目标的匹配度
  - 有效时间 vs 目标相关时间
- generate_weekly_report(user_id, week)
  - 创业周报
- identify_goal_gaps(user_id)
  - 识别目标缺口

预计工作量：2 天
```

#### 任务 11：前端 Goals & Projects 界面
```
文件：
- frontend/src/components/GoalsProjects.js
- frontend/src/components/GoalsProjects.css

功能：
- 目标列表（短期、中期、长期）
- 目标进度条
- 项目看板（Kanban 风格）
- 时间分配可视化
- 决策记录时间线
- 创业周报/月报展示

预计工作量：3-4 天
```

#### 任务 12：API 端点
```
文件：
- mirix/server/fastapi_server.py

新增端点：
- GET /goals (列出所有目标)
- POST /goals (创建目标)
- PUT /goals/{goal_id} (更新目标)
- DELETE /goals/{goal_id} (删除目标)
- GET /goals/{goal_id}/alignment (目标对齐度)
- GET /entrepreneurship/weekly_report
- GET /entrepreneurship/monthly_report

预计工作量：1 天
```

**Phase 2B 总工作量：11-13 天**

---

### Phase 2C：知识图谱可视化（可选）

**优先级：📌 低**

#### 任务 13：构建知识图谱
```
文件：
- mirix/services/knowledge_graph_service.py

功能：
- build_knowledge_graph(user_id)
  - 从 semantic_memory 构建知识节点
  - 识别知识之间的关联
- identify_knowledge_gaps(user_id)
  - 孤立知识节点
  - 需要加强的领域
- calculate_knowledge_depth(user_id, topic)
  - 评估某个主题的学习深度

技术方案：
- 使用 NetworkX 构建图
- 使用 LLM 识别知识关联

预计工作量：3-4 天
```

#### 任务 14：前端知识图谱可视化
```
文件：
- frontend/src/components/KnowledgeGraph.js

功能：
- 交互式知识图谱（节点和边）
- 点击节点查看详情
- 高亮相关知识
- 识别知识缺口

技术方案：
- 使用 D3.js 或 React Flow
- 力导向图布局

预计工作量：4-5 天
```

**Phase 2C 总工作量：7-9 天**

---

## 📊 优先级总结

基于核心目标（**个人成长优先，创业成功次之**），建议优先级：

### 🔥 高优先级（立即开始）
1. **GrowthAnalysisAgent** - 复盘功能的核心
2. **时间范围查询** - 支撑所有分析的基础
3. **成长指标计算** - 量化成长的关键
4. **定时触发机制** - 自动化复盘
5. **前端 Growth Dashboard** - 用户可见的价值

**预计：2-3 周完成**

---

### ⚡ 中优先级（1 个月内）
6. **Goals 系统** - 目标管理的基础
7. **GoalManager 服务** - 目标 CRUD
8. **EntrepreneurshipCoachAgent** - 创业教练
9. **目标对齐功能** - 行为与目标的匹配度
10. **前端 Goals & Projects** - 创业看板

**预计：2-3 周完成**

---

### 📌 低优先级（可延后或作为 Phase 3）
11. **知识图谱构建** - 技术复杂度高
12. **知识图谱可视化** - 用户价值相对较低

**预计：1-2 周完成**

---

## 🎯 建议执行路径

### 第一阶段（Week 1-3）：个人成长功能
```
Week 1:
- Day 1-2: GrowthAnalysisAgent 设计和实现
- Day 3: 时间范围查询
- Day 4-5: 成长指标计算（基础版）

Week 2:
- Day 1: 定时触发机制
- Day 2-5: 前端 Growth Dashboard

Week 3:
- Day 1-2: API 端点和集成
- Day 3-5: 测试和优化
```

### 第二阶段（Week 4-6）：创业功能
```
Week 4:
- Day 1: Goals 数据表
- Day 2-3: GoalManager 服务
- Day 4-5: EntrepreneurshipCoachAgent

Week 5:
- Day 1-2: 目标对齐功能
- Day 3-5: 前端 Goals & Projects

Week 6:
- Day 1-2: API 端点
- Day 3-5: 测试和优化
```

### 第三阶段（可选）：知识图谱
```
Week 7-8:
- 知识图谱构建和可视化
```

---

## 📝 关键技术决策

### 1. 时间分配计算算法

**问题**：如何从 raw_memory 推断时间分配？

**方案 A（简单）**：
```python
# 基于应用类型分类
app_categories = {
    "Chrome": "工作" if url in work_domains else "娱乐",
    "VSCode": "工作",
    "Notion": "工作",
    "YouTube": "娱乐",
    ...
}

# 按 captured_at 时间戳聚合
```

**方案 B（智能）**：
```python
# 使用 LLM 分析截图内容
# GrowthAnalysisAgent 从 episodic_memory 中推断
# 更准确但成本更高
```

**建议**：先用方案 A，后期优化到方案 B。

---

### 2. 图表库选择

**候选**：
- Chart.js：简单易用，文档完善
- Recharts：React 原生，组件化好
- D3.js：功能强大，学习曲线陡

**建议**：使用 **Recharts**（React 生态，适合 Dashboard）。

---

### 3. 定时任务框架

**候选**：
- APScheduler：Python 原生，轻量级
- Celery Beat：功能强大，但需要 Redis/RabbitMQ
- 系统 Cron：最简单，但不够灵活

**建议**：使用 **APScheduler**（轻量级，适合 MIRIX 规模）。

---

### 4. 知识图谱技术栈

**后端**：
- NetworkX：图算法
- LLM：识别知识关联（可选）

**前端**：
- React Flow：组件化好，适合 React
- D3.js：自定义能力强

**建议**：使用 **NetworkX + React Flow**。

---

## 🎉 总结

### 当前状态
✅ **MIRIX 是一个完美的"记录员"**
- 数据捕获完整（截图 + OCR + 多模态 LLM）
- 记忆系统完善（6 种记忆 + 双向关联）
- 可追溯性强（raw_memory_references）

### 缺少的能力
❌ **还不是"成长教练"和"创业导师"**
- 没有深度复盘（只有浅层模式识别）
- 没有时间维度分析（无法对比和趋势分析）
- 没有目标系统（无法对齐行为和目标）
- 没有成长指标（无法量化进步）

### Phase 2 的核心任务
🎯 **从"存储"到"分析"，从"记录"到"复盘"，从"被动"到"主动"**

#### 个人成长（内功）
1. GrowthAnalysisAgent - 复盘大脑
2. 时间维度分析 - 对比和趋势
3. 成长指标系统 - 量化进步
4. 习惯分析 - 优化模式
5. 可行动建议 - AI 教练

#### 创业成功（外功）
1. Goals 系统 - 目标管理
2. 目标对齐 - 行为与目标匹配
3. EntrepreneurshipCoachAgent - 创业导师
4. 项目看板 - 进度追踪
5. 决策复盘 - 效果评估

### 执行建议
- 🔥 优先：个人成长功能（2-3 周）
- ⚡ 其次：创业功能（2-3 周）
- 📌 可选：知识图谱（1-2 周）

---

**下一步**：开始实施 Phase 2A 任务 1（创建 GrowthAnalysisAgent）？
