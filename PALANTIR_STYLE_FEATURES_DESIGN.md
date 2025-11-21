# MIRIX Palantir 风格功能设计

**文档日期**: 2025-11-21
**目标**: 将 MIRIX 打造成个人版 Palantir - 数据整合 + 关系图谱 + 模式发现

---

## 🎯 Palantir 核心能力分析

### Palantir Gotham/Foundry 的核心功能

1. **数据整合 (Data Integration)**
   - 整合多源异构数据（数据库、文件、API、实时流）
   - 统一数据模型
   - 数据清洗和标准化

2. **实体关系图谱 (Entity-Relationship Graph)**
   - 实体识别（人、组织、事件、地点、文档）
   - 关系发现（工作关系、社交关系、因果关系）
   - 图谱可视化和探索

3. **时空分析 (Temporal-Spatial Analysis)**
   - 时间线可视化
   - 地理位置映射
   - 时空关联分析

4. **模式识别 (Pattern Discovery)**
   - 异常检测
   - 趋势预测
   - 因果推断

5. **交互式探索 (Interactive Exploration)**
   - 钻取和筛选
   - 多维度分析
   - 实时查询

6. **协作和共享 (Collaboration)**
   - 团队协作
   - 知识共享
   - 工作流自动化

---

## 🔄 MIRIX 当前状态 vs Palantir

| 功能 | Palantir | MIRIX 当前 | 差距 |
|------|----------|-----------|------|
| 数据整合 | ⭐⭐⭐⭐⭐ 多源 | ⭐⭐ 仅截图 | 需增加数据源 |
| 实体图谱 | ⭐⭐⭐⭐⭐ 完整 | ⭐ 仅记忆分类 | 需构建图谱 |
| 时空分析 | ⭐⭐⭐⭐⭐ 强大 | ⭐ 仅时间戳 | 需时间线可视化 |
| 模式识别 | ⭐⭐⭐⭐⭐ 智能 | ⭐⭐ 浅层模式 | 需深度分析 |
| 交互探索 | ⭐⭐⭐⭐⭐ 流畅 | ⭐⭐ 基础搜索 | 需交互组件 |
| 协作共享 | ⭐⭐⭐⭐⭐ 团队 | N/A 个人版 | 不需要 |

---

## 🚀 MIRIX Palantir 风格功能设计

### 阶段 1：实体关系图谱（最核心）

#### 1.1 实体类型定义

**为 MIRIX 定义的实体类型**：

```python
# 新建文件：mirix/orm/entity.py

from enum import Enum
from sqlalchemy import Column, String, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

class EntityType(str, Enum):
    """实体类型枚举"""
    PERSON = "person"              # 人物（同事、朋友、导师）
    ORGANIZATION = "organization"  # 组织（公司、学校、社区）
    PROJECT = "project"            # 项目（MIRIX、其他项目）
    SKILL = "skill"                # 技能（Python、AI、设计）
    CONCEPT = "concept"            # 概念（设计模式、架构理念）
    TOOL = "tool"                  # 工具（VSCode、Notion、Chrome）
    DOCUMENT = "document"          # 文档（文章、论文、教程）
    EVENT = "event"                # 事件（会议、发布、里程碑）
    LOCATION = "location"          # 地点（办公室、咖啡厅、家）
    GOAL = "goal"                  # 目标（短期、长期目标）

class Entity(Base):
    """实体表 - Palantir 风格的核心"""
    __tablename__ = "entities"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    organization_id = Column(String, ForeignKey("organizations.id"))

    # 基本信息
    entity_type = Column(String, nullable=False)  # EntityType
    name = Column(String, nullable=False)         # 实体名称
    display_name = Column(String)                 # 显示名称
    description = Column(Text)                    # 描述

    # 属性（JSON 存储灵活属性）
    properties = Column(JSON, default=dict)
    # 例如：
    # Person: {"role": "同事", "company": "OpenAI", "expertise": ["AI", "NLP"]}
    # Project: {"status": "active", "start_date": "2025-11-01", "tech_stack": ["Python", "React"]}
    # Skill: {"proficiency": 4, "years_experience": 2}

    # 标签
    tags = Column(JSON, default=list)

    # 时间信息
    first_mentioned_at = Column(DateTime)  # 首次提及时间
    last_mentioned_at = Column(DateTime)   # 最后提及时间

    # 关联的原始记忆
    raw_memory_references = Column(JSON, default=list)

    # 元数据
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(dt.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(dt.timezone.utc))

    # 关系（双向）
    outgoing_relationships = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.from_entity_id",
        back_populates="from_entity"
    )
    incoming_relationships = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.to_entity_id",
        back_populates="to_entity"
    )
```

---

#### 1.2 关系类型定义

```python
class RelationType(str, Enum):
    """关系类型枚举"""
    # 人际关系
    KNOWS = "knows"                    # 认识
    WORKS_WITH = "works_with"          # 共事
    MENTORS = "mentors"                # 指导
    COLLABORATES_WITH = "collaborates_with"  # 合作

    # 项目关系
    WORKS_ON = "works_on"              # 参与项目
    OWNS = "owns"                      # 拥有
    CONTRIBUTES_TO = "contributes_to"  # 贡献给

    # 技能关系
    HAS_SKILL = "has_skill"            # 拥有技能
    LEARNING = "learning"              # 正在学习
    TEACHES = "teaches"                # 教授

    # 知识关系
    KNOWS_ABOUT = "knows_about"        # 了解概念
    RELATED_TO = "related_to"          # 相关
    DEPENDS_ON = "depends_on"          # 依赖

    # 工具关系
    USES = "uses"                      # 使用工具
    PREFERS = "prefers"                # 偏好

    # 目标关系
    PURSUES = "pursues"                # 追求目标
    ACHIEVED = "achieved"              # 达成
    SUPPORTS = "supports"              # 支持

    # 文档关系
    READS = "reads"                    # 阅读
    WRITES = "writes"                  # 撰写
    REFERENCES = "references"          # 引用

class EntityRelationship(Base):
    """实体关系表"""
    __tablename__ = "entity_relationships"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    organization_id = Column(String, ForeignKey("organizations.id"))

    # 关系
    from_entity_id = Column(String, ForeignKey("entities.id"))
    to_entity_id = Column(String, ForeignKey("entities.id"))
    relationship_type = Column(String, nullable=False)  # RelationType

    # 关系属性
    properties = Column(JSON, default=dict)
    # 例如：
    # WORKS_WITH: {"since": "2025-01", "frequency": "daily"}
    # HAS_SKILL: {"proficiency": 4, "acquired_at": "2023-06"}
    # USES: {"frequency": "daily", "purpose": "coding"}

    # 置信度（AI 推断的关系可能有不确定性）
    confidence = Column(Float, default=1.0)  # 0.0 ~ 1.0

    # 证据（关联的原始记忆）
    raw_memory_references = Column(JSON, default=list)

    # 时间信息
    valid_from = Column(DateTime)  # 关系起始时间
    valid_to = Column(DateTime)    # 关系结束时间（null = 仍然有效）

    # 元数据
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(dt.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(dt.timezone.utc))

    # ORM 关系
    from_entity = relationship(
        "Entity",
        foreign_keys=[from_entity_id],
        back_populates="outgoing_relationships"
    )
    to_entity = relationship(
        "Entity",
        foreign_keys=[to_entity_id],
        back_populates="incoming_relationships"
    )
```

---

#### 1.3 实体抽取 Agent

```python
# 新建文件：mirix/agent/entity_extraction_agent.py

class EntityExtractionAgent(Agent):
    """
    实体抽取 Agent

    从现有记忆中自动抽取实体和关系
    类似 Palantir 的 Entity Resolution
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_manager = EntityManager(self.session_maker)

    async def extract_entities_from_memories(self):
        """
        从各类记忆中抽取实体和关系
        """

        # 1. 从 Semantic Memory 抽取
        # "Cursor (AI Code Editor)" → Entity(type=TOOL, name="Cursor")

        # 2. 从 Episodic Memory 抽取
        # "与张三讨论项目" → Entity(type=PERSON, name="张三")
        #                    + Relationship(User, WORKS_WITH, 张三)

        # 3. 从 Procedural Memory 抽取
        # "使用 VSCode 调试" → Entity(type=TOOL, name="VSCode")
        #                     + Relationship(User, USES, VSCode)

        # 4. 从 Resource Memory 抽取
        # "LangChain 文档" → Entity(type=DOCUMENT, name="LangChain Docs")
        #                   + Relationship(User, READS, LangChain Docs)

        # 5. 使用 LLM 推断关系
        # "学习 LangChain" + "开发 MIRIX"
        # → Relationship(MIRIX, DEPENDS_ON, LangChain)

        pass
```

**LLM Prompt 示例**：
```
你是实体抽取专家。从以下记忆中抽取实体和关系。

记忆：
1. "今天学习了 LangChain 的 Multi-Agent 架构"
2. "在 MIRIX 项目中实现了 GrowthAnalysisAgent"
3. "使用 VSCode 编写代码"

请抽取：
- 实体（类型、名称、属性）
- 关系（from, type, to, 属性）

输出格式（JSON）：
{
  "entities": [
    {
      "type": "concept",
      "name": "LangChain Multi-Agent",
      "properties": {"category": "AI/Agent"}
    },
    {
      "type": "project",
      "name": "MIRIX",
      "properties": {"status": "active"}
    },
    {
      "type": "tool",
      "name": "VSCode",
      "properties": {"category": "IDE"}
    }
  ],
  "relationships": [
    {
      "from": "User",
      "type": "learning",
      "to": "LangChain Multi-Agent"
    },
    {
      "from": "User",
      "type": "works_on",
      "to": "MIRIX"
    },
    {
      "from": "User",
      "type": "uses",
      "to": "VSCode"
    },
    {
      "from": "MIRIX",
      "type": "depends_on",
      "to": "LangChain Multi-Agent"
    }
  ]
}
```

---

#### 1.4 图谱查询和分析

```python
# 新建文件：mirix/services/graph_analytics_service.py

class GraphAnalyticsService:
    """
    图谱分析服务
    提供 Palantir 风格的图谱查询和分析
    """

    def __init__(self, session_maker):
        self.session_maker = session_maker

    def get_entity_neighborhood(
        self,
        entity_id: str,
        depth: int = 2,
        relationship_types: List[str] = None
    ) -> Dict:
        """
        获取实体的邻域图

        类似 Palantir 的 "Expand" 功能

        例如：点击 "MIRIX" 项目
        → 展开相关的人物、技能、工具、文档
        """
        # 使用 NetworkX 或 SQL 递归查询
        pass

    def find_shortest_path(
        self,
        from_entity_id: str,
        to_entity_id: str
    ) -> List[Dict]:
        """
        查找两个实体之间的最短路径

        例如："我" 到 "AGI" 的路径
        → User -[learning]-> LangChain -[related_to]-> Multi-Agent -[leads_to]-> AGI
        """
        pass

    def find_common_connections(
        self,
        entity_ids: List[str]
    ) -> List[Dict]:
        """
        查找多个实体的共同连接

        例如："Python" 和 "React" 的共同点
        → 都被用于 MIRIX 项目
        → 都在学习中
        """
        pass

    def get_entity_timeline(
        self,
        entity_id: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Dict]:
        """
        获取实体的时间线

        例如："MIRIX" 项目的时间线
        → 2025-11-01: 项目启动
        → 2025-11-15: Phase 1 开始
        → 2025-11-19: Phase 1 完成
        → ...
        """
        pass

    def calculate_entity_importance(
        self,
        entity_id: str
    ) -> float:
        """
        计算实体的重要性（PageRank 或度中心性）

        重要性高的实体：
        - 连接多（度中心性高）
        - 被重要实体连接（PageRank 高）
        - 频繁提及（出现在很多 raw_memory 中）
        """
        pass

    def detect_communities(self) -> List[List[str]]:
        """
        检测社区（聚类）

        例如：
        - 社区 1: MIRIX 相关（Python, FastAPI, React, PostgreSQL）
        - 社区 2: AI 学习相关（LangChain, LLM, Agent）
        - 社区 3: 日常工具（VSCode, Chrome, Notion）
        """
        pass

    def find_knowledge_gaps(
        self,
        user_id: str,
        target_skill: str
    ) -> List[str]:
        """
        查找知识缺口

        例如：目标是 "掌握 Multi-Agent 系统"
        → 发现需要学习：LangGraph, Crew AI, AutoGen
        → 但目前只学了 LangChain
        """
        pass
```

---

### 阶段 2：交互式时间线

#### 2.1 时间线数据结构

```python
# 新建文件：mirix/services/timeline_service.py

class TimelineService:
    """
    Palantir 风格的时间线服务
    """

    def get_timeline_data(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime,
        filters: Dict = None
    ) -> Dict:
        """
        获取时间线数据

        返回格式：
        {
          "events": [
            {
              "timestamp": "2025-11-21T09:00:00",
              "type": "work",
              "category": "coding",
              "title": "开发 GrowthAnalysisAgent",
              "project": "MIRIX",
              "entities": ["MIRIX", "Python", "VSCode"],
              "raw_memory_refs": ["rawmem-xxx"],
              "duration": 3600  # 秒
            },
            {
              "timestamp": "2025-11-21T14:00:00",
              "type": "meeting",
              "category": "discussion",
              "title": "与张三讨论项目",
              "entities": ["张三", "MIRIX"],
              "raw_memory_refs": ["rawmem-yyy"],
              "duration": 1800
            }
          ],
          "lanes": [
            {"id": "work", "label": "工作", "color": "#3b82f6"},
            {"id": "learning", "label": "学习", "color": "#10b981"},
            {"id": "social", "label": "社交", "color": "#f59e0b"}
          ]
        }
        """
        pass

    def get_time_distribution(
        self,
        user_id: str,
        time_range: Tuple[datetime, datetime],
        granularity: str = "hour"  # "hour", "day", "week"
    ) -> Dict:
        """
        获取时间分布统计

        返回格式：
        {
          "work": {"total": 32, "by_hour": {...}},
          "learning": {"total": 8, "by_hour": {...}},
          "entertainment": {"total": 6, "by_hour": {...}}
        }
        """
        pass

    def find_temporal_patterns(
        self,
        user_id: str,
        pattern_type: str = "recurring"  # "recurring", "anomaly", "trend"
    ) -> List[Dict]:
        """
        发现时间模式

        例如：
        - 每周三下午 14:00-16:00 效率低（recurring）
        - 今天学习时间 4 小时（异常高）（anomaly）
        - 工作时间逐周递增（trend）
        """
        pass
```

---

#### 2.2 前端时间线组件

```jsx
// 新建文件：frontend/src/components/PalantirTimeline.js

import React, { useState, useEffect } from 'react';
import { Gantt } from 'gantt-task-react';  // 或使用 react-calendar-timeline

const PalantirTimeline = () => {
  const [timelineData, setTimelineData] = useState(null);
  const [zoomLevel, setZoomLevel] = useState('day');  // 'hour', 'day', 'week', 'month'
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [filters, setFilters] = useState({
    types: [],  // ['work', 'learning', 'social']
    entities: [],  // ['MIRIX', 'Python']
    projects: []
  });

  // 加载时间线数据
  useEffect(() => {
    fetch(`/api/timeline?zoom=${zoomLevel}&filters=${JSON.stringify(filters)}`)
      .then(res => res.json())
      .then(data => setTimelineData(data));
  }, [zoomLevel, filters]);

  // 事件点击处理 - 展开详情和关系图
  const handleEventClick = (event) => {
    setSelectedEvent(event);
    // 加载事件关联的实体图谱
    fetch(`/api/graph/event/${event.id}/neighborhood`)
      .then(res => res.json())
      .then(graph => setEventGraph(graph));
  };

  return (
    <div className="palantir-timeline">
      {/* 时间轴控制 */}
      <div className="timeline-controls">
        <button onClick={() => setZoomLevel('hour')}>小时</button>
        <button onClick={() => setZoomLevel('day')}>天</button>
        <button onClick={() => setZoomLevel('week')}>周</button>
        <button onClick={() => setZoomLevel('month')}>月</button>

        {/* 过滤器 */}
        <MultiSelect
          options={['work', 'learning', 'social']}
          value={filters.types}
          onChange={(types) => setFilters({...filters, types})}
        />
      </div>

      {/* 主时间线 */}
      <div className="timeline-main">
        {/* 泳道 */}
        {timelineData?.lanes.map(lane => (
          <div key={lane.id} className="timeline-lane">
            <div className="lane-header">{lane.label}</div>
            <div className="lane-events">
              {timelineData.events
                .filter(e => e.category === lane.id)
                .map(event => (
                  <div
                    key={event.id}
                    className="timeline-event"
                    onClick={() => handleEventClick(event)}
                    style={{
                      left: calculatePosition(event.timestamp),
                      width: calculateWidth(event.duration)
                    }}
                  >
                    {event.title}
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>

      {/* 侧边栏 - 事件详情和关系图 */}
      {selectedEvent && (
        <div className="timeline-sidebar">
          <h3>{selectedEvent.title}</h3>
          <p>{selectedEvent.description}</p>

          {/* 关联实体 */}
          <div className="related-entities">
            {selectedEvent.entities.map(entity => (
              <span key={entity} className="entity-badge">
                {entity}
              </span>
            ))}
          </div>

          {/* 小型关系图 */}
          <div className="event-graph">
            <MiniGraphView graph={eventGraph} />
          </div>

          {/* 原始截图 */}
          <div className="raw-memories">
            {selectedEvent.raw_memory_refs.map(ref => (
              <img key={ref} src={`/api/raw_memory/${ref}/screenshot`} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

---

### 阶段 3：模式发现引擎

#### 3.1 模式发现 Agent

```python
# 新建文件：mirix/agent/pattern_discovery_agent.py

class PatternDiscoveryAgent(Agent):
    """
    Palantir 风格的模式发现 Agent

    自动发现行为模式、异常和洞察
    """

    def discover_patterns(self, user_id: str, time_range: Tuple[datetime, datetime]):
        """
        发现多种类型的模式
        """
        patterns = []

        # 1. 时间模式（Temporal Patterns）
        patterns.extend(self._find_temporal_patterns(user_id, time_range))

        # 2. 因果模式（Causal Patterns）
        patterns.extend(self._find_causal_patterns(user_id, time_range))

        # 3. 关联模式（Association Patterns）
        patterns.extend(self._find_association_patterns(user_id, time_range))

        # 4. 异常模式（Anomaly Patterns）
        patterns.extend(self._find_anomaly_patterns(user_id, time_range))

        # 5. 趋势模式（Trend Patterns）
        patterns.extend(self._find_trend_patterns(user_id, time_range))

        return patterns

    def _find_temporal_patterns(self, user_id, time_range):
        """
        时间模式

        例如：
        - "每周三下午 14:00-16:00 效率低 90%"
        - "每天 09:00-12:00 是深度工作时段"
        - "周末学习时间是工作日的 2 倍"
        """
        patterns = []

        # 使用时间序列分析
        # 识别周期性模式（FFT、自相关）

        return patterns

    def _find_causal_patterns(self, user_id, time_range):
        """
        因果模式

        例如：
        - "睡眠 < 7h → 第二天分心次数 +50%"
        - "学习后 1 小时内实践 → 知识留存率 +60%"
        - "连续 3 天加班 → 第 4 天效率 -50%"
        """
        patterns = []

        # 使用因果推断方法
        # Granger 因果检验、倾向得分匹配

        return patterns

    def _find_association_patterns(self, user_id, time_range):
        """
        关联模式

        例如：
        - "看技术文章 → 1 小时后开始编码（75%）"
        - "使用 Notion → 通常是在规划阶段"
        - "与张三讨论 → 通常涉及 MIRIX 项目"
        """
        patterns = []

        # 使用关联规则挖掘（Apriori）
        # 序列模式挖掘

        return patterns

    def _find_anomaly_patterns(self, user_id, time_range):
        """
        异常模式

        例如：
        - "今天学习时间 4h（平均 1.5h，+167%）"
        - "本周娱乐时间 2h（平均 6h，-67%）"
        - "昨天工作到凌晨 2 点（异常晚）"
        """
        patterns = []

        # 使用异常检测算法
        # Z-score、IQR、Isolation Forest

        return patterns

    def _find_trend_patterns(self, user_id, time_range):
        """
        趋势模式

        例如：
        - "工作效率逐周提升 5%"
        - "学习时间逐月递增"
        - "分心次数逐周减少"
        """
        patterns = []

        # 使用趋势分析
        # 线性回归、移动平均、ARIMA

        return patterns
```

---

#### 3.2 模式展示

```markdown
# 🔍 发现的模式 (2025-11-21)

## ⏰ 时间模式

### 高效时段（Recurring Pattern）
✅ **早上 09:00-12:00 深度工作黄金时段**
- 发生频率：90%（过去 4 周）
- 平均专注时长：2.8 小时
- 产出：比其他时段高 40%
- 证据：32 次观察
- 建议：保护此时段，关闭所有通知

### 低效时段（Recurring Pattern）
⚠️ **周三下午 14:00-16:00 效率低谷**
- 发生频率：85%（过去 4 周）
- 平均分心次数：5 次/小时
- 原因推测：周会后疲劳 + 午餐后困倦
- 证据：17 次观察
- 建议：调整会议时间或安排轻松任务

---

## 🔗 因果模式

### 睡眠影响专注力（Causal Pattern）
⚠️ **睡眠 < 7h → 第二天分心次数 +45%**
- 置信度：92%
- 样本量：15 次观察
- 效应大小：中等
- 证据：
  - 11-15: 睡眠 6.5h → 11-16: 分心 8 次（vs 平均 5.5 次）
  - 11-18: 睡眠 6h → 11-19: 分心 9 次
- 建议：确保每天睡眠 ≥ 7 小时

### 学习后立即实践（Causal Pattern）
✅ **学习后 1 小时内实践 → 知识留存率 +60%**
- 置信度：88%
- 样本量：12 次观察
- 效应大小：大
- 证据：
  - 11-17: 学习 LangChain → 1h 后在 MIRIX 中应用 → 1 周后仍记得
  - 11-19: 学习 pgvector → 立即测试 → 2 周后仍熟练
- 建议：学习新技术后立即找机会实践

---

## 🔄 关联模式

### 阅读 → 编码序列（Association Pattern）
📚 **阅读技术文章 → 1 小时后开始编码（75%）**
- 支持度：18 次 / 24 次阅读
- 置信度：75%
- Lift: 2.1（比随机高 2.1 倍）
- 典型序列：
  - 阅读文档 → 打开 VSCode → 创建测试项目 → 实践
- 建议：阅读后预留 1-2 小时实践时间

### 工具使用模式（Association Pattern）
💻 **使用 Notion → 通常是在规划阶段（90%）**
- 支持度：27 次 / 30 次 Notion 使用
- 置信度：90%
- 典型场景：
  - 项目启动前：用 Notion 规划任务
  - 周复盘：用 Notion 记录总结
  - 学习规划：用 Notion 制定学习路径
- 洞察：Notion 是你的"战略工具"，VSCode 是"战术工具"

---

## ⚡ 异常模式

### 学习时间异常高（Anomaly）
🎓 **今天学习时间 4h（平均 1.5h，+167%）**
- Z-score: 2.8（异常）
- 百分位：95%（只有 5% 的天数学习时间更长）
- 分析：
  - 原因：周末 + 新技术（Palantir 风格功能）
  - 效果：很可能产生大量新知识
- 建议：继续保持，周末是学习的好时机

### 娱乐时间异常低（Anomaly）
⏸️ **本周娱乐时间 2h（平均 6h，-67%）**
- Z-score: -2.1（异常）
- 分析：
  - 原因：专注于 MIRIX 开发
  - 风险：可能导致疲劳
- 建议：适当增加休息时间，避免 burnout

---

## 📈 趋势模式

### 工作效率上升（Trend）
📊 **工作效率逐周提升 +5%**
- 趋势：线性上升
- R²: 0.87（强相关）
- 预测：按此趋势，1 个月后效率提升 20%
- 原因推测：
  - 技术栈熟悉度提升
  - 工作流程优化
  - 专注力训练
- 建议：继续保持当前工作模式

### 学习时间递增（Trend）
📚 **学习时间逐月递增 +15%**
- 趋势：指数增长
- 10 月：20h → 11 月：30h（预计）
- 原因：对 AI/Agent 领域兴趣增加
- 建议：保持学习热情，但注意平衡

---

## 💡 综合洞察

### 🎯 最佳工作模式
1. 早上 09:00-12:00 做最重要的深度工作
2. 下午安排轻松任务或学习
3. 学习后立即实践
4. 确保充足睡眠（≥ 7h）

### ⚠️ 需要改进
1. 周三下午效率低 → 调整会议或任务安排
2. 连续加班风险 → 注意休息
3. 娱乐时间太少 → 适当放松

### 🚀 成长亮点
1. 工作效率持续提升
2. 学习时间增加
3. 学以致用能力强
```

---

### 阶段 4：数据源扩展

#### 4.1 多数据源整合架构

```python
# 新建文件：mirix/integrations/base_integration.py

from abc import ABC, abstractmethod

class BaseIntegration(ABC):
    """
    数据源集成基类

    类似 Palantir 的 Data Integration
    """

    @abstractmethod
    async def fetch_data(self, start_time: datetime, end_time: datetime):
        """获取数据"""
        pass

    @abstractmethod
    def transform_to_raw_memory(self, data: Any) -> List[RawMemoryItem]:
        """转换为 raw_memory 格式"""
        pass

    @abstractmethod
    def extract_entities(self, data: Any) -> List[Entity]:
        """抽取实体"""
        pass
```

#### 4.2 具体集成实现

**Gmail 集成**：
```python
# mirix/integrations/gmail_integration.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailIntegration(BaseIntegration):
    """Gmail 邮件集成"""

    async def fetch_data(self, start_time, end_time):
        """获取指定时间范围的邮件"""
        service = build('gmail', 'v1', credentials=self.credentials)

        query = f'after:{start_time.timestamp()} before:{end_time.timestamp()}'
        results = service.users().messages().list(userId='me', q=query).execute()

        messages = []
        for msg in results.get('messages', []):
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            messages.append(message)

        return messages

    def transform_to_raw_memory(self, messages):
        """转换邮件为 raw_memory"""
        raw_memories = []

        for msg in messages:
            # 提取邮件内容
            subject = self._get_header(msg, 'Subject')
            from_addr = self._get_header(msg, 'From')
            body = self._get_body(msg)

            raw_memory = RawMemoryItem(
                id=f"rawmem-gmail-{msg['id']}",
                source_app="Gmail",
                source_url=f"https://mail.google.com/mail/u/0/#inbox/{msg['id']}",
                ocr_text=f"Subject: {subject}\nFrom: {from_addr}\n\n{body}",
                captured_at=datetime.fromtimestamp(int(msg['internalDate']) / 1000),
                metadata_={
                    "integration": "gmail",
                    "message_id": msg['id'],
                    "labels": msg.get('labelIds', [])
                }
            )

            raw_memories.append(raw_memory)

        return raw_memories

    def extract_entities(self, messages):
        """从邮件中抽取实体"""
        entities = []

        for msg in messages:
            from_addr = self._get_header(msg, 'From')

            # 抽取人物实体
            person_name = self._parse_email_name(from_addr)
            person_entity = Entity(
                entity_type=EntityType.PERSON,
                name=person_name,
                properties={
                    "email": from_addr,
                    "source": "gmail"
                }
            )
            entities.append(person_entity)

        return entities
```

**GitHub 集成**：
```python
# mirix/integrations/github_integration.py

class GitHubIntegration(BaseIntegration):
    """GitHub 代码提交集成"""

    async def fetch_data(self, start_time, end_time):
        """获取指定时间范围的 commits"""
        # 使用 PyGithub 或 GitHub API
        pass

    def transform_to_raw_memory(self, commits):
        """转换 commit 为 raw_memory"""
        raw_memories = []

        for commit in commits:
            raw_memory = RawMemoryItem(
                id=f"rawmem-github-{commit.sha}",
                source_app="GitHub",
                source_url=commit.html_url,
                ocr_text=f"Commit: {commit.message}\n\nFiles: {len(commit.files)}",
                captured_at=commit.commit.author.date,
                metadata_={
                    "integration": "github",
                    "repo": commit.repository.full_name,
                    "sha": commit.sha,
                    "stats": commit.stats
                }
            )

            raw_memories.append(raw_memory)

        return raw_memories

    def extract_entities(self, commits):
        """从 commit 中抽取实体"""
        entities = []

        for commit in commits:
            # 抽取项目实体
            project_entity = Entity(
                entity_type=EntityType.PROJECT,
                name=commit.repository.name,
                properties={
                    "github_url": commit.repository.html_url,
                    "language": commit.repository.language
                }
            )
            entities.append(project_entity)

        return entities
```

**Notion 集成**：
```python
# mirix/integrations/notion_integration.py

class NotionIntegration(BaseIntegration):
    """Notion 笔记集成"""

    async def fetch_data(self, start_time, end_time):
        """获取指定时间范围的页面"""
        # 使用 notion-client
        pass
```

**其他潜在集成**：
- Slack/微信聊天记录
- Google Calendar 日历事件
- Apple Health 健康数据
- Screen Time 手机使用数据
- Kindle/微信读书阅读记录
- 支付宝/微信支付消费记录

---

### 阶段 5：Palantir 风格仪表板

#### 5.1 主仪表板设计

```jsx
// frontend/src/components/PalantirDashboard.js

const PalantirDashboard = () => {
  return (
    <div className="palantir-dashboard">
      {/* 顶部：全局搜索和过滤 */}
      <div className="dashboard-header">
        <GlobalSearch />
        <DateRangePicker />
        <FilterPanel />
      </div>

      {/* 主区域：3 列布局 */}
      <div className="dashboard-main">
        {/* 左侧：实体关系图 */}
        <div className="panel-left">
          <h2>知识图谱</h2>
          <InteractiveGraph
            data={graphData}
            onNodeClick={handleNodeClick}
            onEdgeClick={handleEdgeClick}
          />
        </div>

        {/* 中间：时间线 */}
        <div className="panel-center">
          <h2>时间线</h2>
          <PalantirTimeline
            data={timelineData}
            onEventClick={handleEventClick}
          />

          {/* 模式发现面板 */}
          <div className="patterns-panel">
            <h3>🔍 发现的模式</h3>
            {patterns.map(pattern => (
              <PatternCard key={pattern.id} pattern={pattern} />
            ))}
          </div>
        </div>

        {/* 右侧：详情和分析 */}
        <div className="panel-right">
          {/* 实体详情 */}
          {selectedEntity && (
            <EntityDetailPanel entity={selectedEntity} />
          )}

          {/* 事件详情 */}
          {selectedEvent && (
            <EventDetailPanel event={selectedEvent} />
          )}

          {/* 统计分析 */}
          <AnalyticsPanel metrics={metrics} />
        </div>
      </div>
    </div>
  );
};
```

---

## 📅 实施路线图

### Phase 2A：实体图谱基础（2-3 周）

**Week 1: 数据建模**
- Day 1-2: 设计 Entity 和 EntityRelationship 表
- Day 3-4: 实现 EntityManager 服务
- Day 5: 数据库迁移脚本

**Week 2: 实体抽取**
- Day 1-3: 实现 EntityExtractionAgent
- Day 4-5: 从现有记忆批量抽取实体和关系

**Week 3: 图谱查询和前端**
- Day 1-2: 实现 GraphAnalyticsService
- Day 3-5: 前端图谱可视化（使用 React Flow 或 D3.js）

---

### Phase 2B：交互式时间线（1-2 周）

**Week 4: 时间线后端**
- Day 1-2: 实现 TimelineService
- Day 3: API 端点

**Week 5: 时间线前端**
- Day 1-3: 实现 PalantirTimeline 组件
- Day 4-5: 交互功能（缩放、过滤、点击）

---

### Phase 2C：模式发现（2-3 周）

**Week 6-7: 模式算法**
- 实现 5 类模式发现算法
- 时间模式、因果模式、关联模式、异常模式、趋势模式

**Week 8: 前端展示**
- 模式卡片设计
- 模式可视化

---

### Phase 2D：数据源扩展（2-4 周）

**Week 9-10: 核心集成**
- Gmail、GitHub、Notion

**Week 11-12: 其他集成（可选）**
- Slack、Calendar、Health 数据

---

### Phase 2E：Palantir 仪表板（1-2 周）

**Week 13-14: 整合**
- 设计统一仪表板
- 整合图谱、时间线、模式面板

---

## 🎯 优先级建议

基于你的核心目标（**个人成长 + 创业**），建议优先级：

### 🔥 最高优先级（立即开始）
1. **实体关系图谱** - Palantir 的核心，也是最有价值的功能
2. **交互式时间线** - 探索式分析的基础
3. **模式发现引擎** - 自动洞察

### ⚡ 中等优先级（1-2 月内）
4. **数据源扩展** - 增加数据丰富度
5. **Palantir 仪表板** - 统一体验

---

## 💡 关键技术决策

### 1. 图数据库 vs 关系数据库

**选项 A：继续使用 PostgreSQL**
- ✅ 现有技术栈
- ✅ 支持图查询（递归 CTE）
- ❌ 图查询性能较差

**选项 B：使用图数据库（Neo4j / ArangoDB）**
- ✅ 图查询性能极高
- ✅ 原生图算法支持
- ❌ 增加技术复杂度
- ❌ 需要维护两个数据库

**建议：先用 PostgreSQL，数据量大后再考虑 Neo4j**

---

### 2. 图可视化库选择

**选项 A：React Flow**
- ✅ React 原生，组件化好
- ✅ 性能优秀
- ❌ 自定义能力有限

**选项 B：D3.js**
- ✅ 自定义能力极强
- ✅ 社区庞大
- ❌ 学习曲线陡

**选项 C：Cytoscape.js**
- ✅ 专门为图设计
- ✅ 性能和功能平衡好
- ❌ React 集成稍麻烦

**建议：使用 **Cytoscape.js**（最适合知识图谱）**

---

### 3. 实体抽取方式

**方案 A：基于规则**
- ✅ 快速、低成本
- ❌ 准确率低、不灵活

**方案 B：使用 LLM**
- ✅ 准确率高、灵活
- ❌ 成本较高

**方案 C：混合方式**
- 高置信度实体用规则（工具名、项目名）
- 复杂实体用 LLM（人物、概念）

**建议：使用混合方式**

---

## 🎉 总结

### Palantir 风格功能的核心价值

对于 MIRIX 来说，Palantir 风格的功能将带来：

1. **更深度的洞察**
   - 不只是"记录了什么"
   - 而是"之间有什么关系"、"背后有什么模式"

2. **更强的探索能力**
   - 从"搜索"到"探索"
   - 点击实体 → 展开关系 → 发现新连接

3. **更智能的建议**
   - 基于图谱找知识缺口
   - 基于模式给优化建议
   - 基于趋势做预测

4. **更全面的数据整合**
   - 不只是截图，整合所有数字足迹
   - 构建完整的"数字分身"

---

### 实施建议

**渐进式实现，快速迭代**：
```
v1.0: 基础图谱（实体 + 关系）
v1.5: 交互式时间线
v2.0: 模式发现
v2.5: 数据源扩展
v3.0: 完整 Palantir 仪表板
```

**先验证核心价值，再扩展**：
- 先做图谱和时间线（最核心）
- 验证用户价值
- 再投入模式发现和数据整合

---

需要我开始实施吗？建议从**实体关系图谱**开始，这是 Palantir 风格的核心！
