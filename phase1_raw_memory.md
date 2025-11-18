https://deepwiki.com/search/mirx-agent-ocr-url-app-name-me_b144fe9e-3eeb-4db2-b31a-7f3524549053

我理解你想要设计一个系统，在发送给各个记忆 agent 之前，先将原始截图数据和元数据存储到一个专门的 `raw_memory` 或 `base_memory` 表中，然后其他记忆类型通过引用这个表来获取基础信息。<cite/>这是一个很好的架构改进，可以避免数据冗余并增强可追溯性。<cite/>

## 设计方案：创建 RawMemory 表作为基础记忆层

### 1. 创建新的 ORM 模型

在 `mirix/orm/` 目录下创建新文件 `raw_memory.py`：

```python
from typing import Optional
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from mirix.orm.sqlalchemy_base import SqlalchemyBase
from mirix.orm.mixins import OrganizationMixin, UserMixin
from mirix.constants import MAX_EMBEDDING_DIM

class RawMemoryItem(SqlalchemyBase, OrganizationMixin, UserMixin):
    """
    原始记忆存储 - 存储截图的原始数据和OCR提取的元数据
    作为所有其他记忆类型的基础引用源
    """
    
    __tablename__ = "raw_memory"
    
    # 基础标识
    id: Mapped[str] = mapped_column(String, primary_key=True)
    
    # 截图元数据
    screenshot_path: Mapped[str] = mapped_column(String, doc="截图在本地文件系统的路径")
    source_app: Mapped[str] = mapped_column(String, doc="截图来源的应用名称")
    captured_at: Mapped[datetime] = mapped_column(DateTime, doc="截图捕获时间")
    
    # OCR 提取的数据
    ocr_text: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="OCR提取的完整文本")
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="OCR提取的URL")
    
    # 云存储引用（用于 Gemini 模型）
    google_cloud_url: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="Google Cloud Storage URI")
    
    # 向量嵌入（用于搜索）
    ocr_text_embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(MAX_EMBEDDING_DIM), 
        nullable=True,
        doc="OCR文本的向量嵌入"
    )
    
    # 额外元数据
    metadata_: Mapped[dict] = mapped_column(JSON, default={}, doc="其他元数据信息")
    
    # 处理状态
    processed: Mapped[bool] = mapped_column(default=False, doc="是否已被记忆agents处理")
    processing_count: Mapped[int] = mapped_column(Integer, default=0, doc="被处理的次数")
```

### 2. 扩展现有记忆模型添加引用字段

修改现有的记忆 ORM 模型（以 `mirix/orm/episodic_memory.py` 为例）：

```python
# 在 EpisodicEvent 类中添加
raw_memory_references: Mapped[list] = mapped_column(
    JSON, 
    default=list, 
    doc="引用的 raw_memory 表中的 ID 列表"
)
```

对其他记忆类型做类似修改：
- `mirix/orm/semantic_memory.py` 中的 `SemanticMemoryItem`
- `mirix/orm/procedural_memory.py` 中的 `ProceduralMemoryItem`
- `mirix/orm/resource_memory.py` 中的 `ResourceMemoryItem`
- `mirix/orm/knowledge_vault.py` 中的 `KnowledgeVaultItem`

### 3. 创建 RawMemoryManager

在 `mirix/services/` 目录下创建 `raw_memory_manager.py`：

```python
from typing import List, Optional
from datetime import datetime
from mirix.orm.raw_memory import RawMemoryItem
from mirix.schemas.user import User as PydanticUser

class RawMemoryManager:
    """管理原始记忆的 CRUD 操作"""
    
    def __init__(self):
        from mirix.server.server import db_context
        self.session_maker = db_context
    
    def insert_raw_memory(
        self,
        actor: PydanticUser,
        screenshot_path: str,
        source_app: str,
        captured_at: datetime,
        ocr_text: Optional[str] = None,
        source_url: Optional[str] = None,
        google_cloud_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        organization_id: Optional[str] = None,
    ) -> RawMemoryItem:
        """插入新的原始记忆记录"""
        with self.session_maker() as session:
            raw_memory = RawMemoryItem(
                screenshot_path=screenshot_path,
                source_app=source_app,
                captured_at=captured_at,
                ocr_text=ocr_text,
                source_url=source_url,
                google_cloud_url=google_cloud_url,
                metadata_=metadata or {},
                user_id=actor.id,
                organization_id=organization_id or actor.organization_id,
            )
            session.add(raw_memory)
            session.commit()
            session.refresh(raw_memory)
            return raw_memory
    
    def get_raw_memory_by_id(self, raw_memory_id: str) -> Optional[RawMemoryItem]:
        """根据ID获取原始记忆"""
        with self.session_maker() as session:
            return session.query(RawMemoryItem).filter(
                RawMemoryItem.id == raw_memory_id
            ).first()
    
    def mark_as_processed(self, raw_memory_id: str):
        """标记原始记忆已被处理"""
        with self.session_maker() as session:
            raw_memory = session.query(RawMemoryItem).filter(
                RawMemoryItem.id == raw_memory_id
            ).first()
            if raw_memory:
                raw_memory.processed = True
                raw_memory.processing_count += 1
                session.commit()
```

### 4. 修改消息累积流程

修改 `mirix/agent/temporary_message_accumulator.py` 中的 `_build_memory_message()` 方法：

```python
def _build_memory_message(self, temporary_messages):
    """构建记忆消息，先存储到 raw_memory 表"""
    
    # 1. 首先将所有截图存储到 raw_memory 表
    raw_memory_ids = []
    raw_memory_manager = RawMemoryManager()
    
    for timestamp, item in temporary_messages:
        if "image_uris" in item and item["image_uris"]:
            sources = item.get("sources", [])
            
            for idx, image_uri in enumerate(item["image_uris"]):
                source_app = sources[idx] if idx < len(sources) else "Unknown"
                
                # 执行 OCR（如果已实现）
                ocr_result = self._perform_ocr_if_available(image_uri)
                
                # 存储到 raw_memory 表
                raw_memory = raw_memory_manager.insert_raw_memory(
                    actor=self.user,
                    screenshot_path=image_uri,
                    source_app=source_app,
                    captured_at=timestamp,
                    ocr_text=ocr_result.get("text") if ocr_result else None,
                    source_url=ocr_result.get("url") if ocr_result else None,
                    google_cloud_url=item.get("google_cloud_url"),
                    metadata={
                        "original_index": idx,
                        "batch_id": self._generate_batch_id(),
                    },
                    organization_id=self.user.organization_id,
                )
                raw_memory_ids.append(raw_memory.id)
    
    # 2. 构建发送给记忆 agents 的消息，包含 raw_memory_ids
    message_parts = []
    
    # 按 source 分组
    images_by_source = {}
    for timestamp, item in temporary_messages:
        # ... 现有的分组逻辑 ...
    
    # 为每个 source 构建消息
    for source_name, images in images_by_source.items():
        message_parts.append({
            "type": "text",
            "text": f"These are the screenshots from {source_name}:",
        })
        
        # 添加 raw_memory 引用信息
        relevant_raw_memory_ids = [
            raw_id for raw_id in raw_memory_ids 
            if self._matches_source(raw_id, source_name)
        ]
        
        message_parts.append({
            "type": "text",
            "text": f"Raw Memory References: {', '.join(relevant_raw_memory_ids)}",
        })
        
        # 添加图片
        for timestamp, file_ref in images:
            message_parts.append({
                "type": "image_url",
                "image_url": {"url": file_ref},
            })
    
    # 3. 在消息中包含 raw_memory_ids，供记忆 agents 引用
    return {
        "message_parts": message_parts,
        "raw_memory_ids": raw_memory_ids,
    }
```

### 5. 修改记忆工具函数

修改 `mirix/functions/function_sets/memory_tools.py` 中的记忆插入函数，添加 `raw_memory_references` 参数：

```python
def episodic_memory_insert(
    self: "Agent", 
    items: List[EpisodicEventForLLM],
    raw_memory_references: Optional[List[str]] = None
):
    """插入情节记忆，包含对原始记忆的引用"""
    for item in items:
        self.episodic_memory_manager.insert_event(
            actor=self.user,
            agent_state=self.agent_state,
            timestamp=item["occurred_at"],
            event_type=item["event_type"],
            event_actor=item["actor"],
            summary=item["summary"],
            details=item["details"],
            organization_id=self.user.organization_id,
            tree_path=item.get("tree_path"),
            raw_memory_references=raw_memory_references or [],  # 新增
        )
    return "Events inserted with raw memory references!"
```

### 6. 修改系统提示词

修改 `mirix/agent/agent.py` 中的 `build_system_prompt()` 方法，在展示记忆时包含来源信息：

```python
def build_system_prompt(self, retrieved_memories: dict) -> str:
    # ... 现有代码 ...
    
    # 在构建 episodic_memory 字符串时
    for idx, event in enumerate(current_episodic_memory):
        # 获取 raw_memory 引用
        raw_refs = event.raw_memory_references if hasattr(event, 'raw_memory_references') else []
        
        # 如果有引用，获取详细信息
        source_info = ""
        if raw_refs:
            raw_memory_manager = RawMemoryManager()
            for ref_id in raw_refs[:2]:  # 只显示前2个引用
                raw_mem = raw_memory_manager.get_raw_memory_by_id(ref_id)
                if raw_mem:
                    source_info += f" [Source: {raw_mem.source_app}"
                    if raw_mem.source_url:
                        source_info += f", URL: {raw_mem.source_url}"
                    source_info += "]"
        
        episodic_memory += (
            f"[{idx}] Timestamp: {event.occurred_at.strftime('%Y-%m-%d %H:%M:%S')} "
            f"- {event.summary}{source_info}{tree_path_str} "
            f"(Details: {len(event.details)} Characters)\n"
        )
```

### 7. 前端展示改进

在 `mirix/server/fastapi_server.py` 中添加新的 API 端点：

```python
@app.get("/memory/raw/{raw_memory_id}")
async def get_raw_memory_detail(raw_memory_id: str):
    """获取原始记忆的详细信息"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    raw_memory_manager = agent.client.server.raw_memory_manager
    raw_memory = raw_memory_manager.get_raw_memory_by_id(raw_memory_id)
    
    if not raw_memory:
        raise HTTPException(status_code=404, detail="Raw memory not found")
    
    return {
        "id": raw_memory.id,
        "screenshot_path": raw_memory.screenshot_path,
        "source_app": raw_memory.source_app,
        "captured_at": raw_memory.captured_at.isoformat(),
        "ocr_text": raw_memory.ocr_text,
        "source_url": raw_memory.source_url,
        "metadata": raw_memory.metadata_,
    }
```

### 8. 数据库迁移

需要创建数据库迁移脚本来添加新表和字段：

```sql
-- 创建 raw_memory 表
CREATE TABLE raw_memory (
    id VARCHAR PRIMARY KEY,
    screenshot_path VARCHAR NOT NULL,
    source_app VARCHAR NOT NULL,
    captured_at TIMESTAMP NOT NULL,
    ocr_text TEXT,
    source_url VARCHAR,
    google_cloud_url VARCHAR,
    ocr_text_embedding vector(1536),
    metadata_ JSONB DEFAULT '{}',
    processed BOOLEAN DEFAULT FALSE,
    processing_count INTEGER DEFAULT 0,
    user_id VARCHAR NOT NULL,
    organization_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 为现有记忆表添加 raw_memory_references 字段
ALTER TABLE episodic_memory ADD COLUMN raw_memory_references JSONB DEFAULT '[]';
ALTER TABLE semantic_memory ADD COLUMN raw_memory_references JSONB DEFAULT '[]';
ALTER TABLE procedural_memory ADD COLUMN raw_memory_references JSONB DEFAULT '[]';
ALTER TABLE resource_memory ADD COLUMN raw_memory_references JSONB DEFAULT '[]';
ALTER TABLE knowledge_vault ADD COLUMN raw_memory_references JSONB DEFAULT '[]';
```

## 实施步骤总结

1. **Phase 1 - 数

Wiki pages you might want to explore:
- [System Architecture (Mirix-AI/MIRIX)](/wiki/Mirix-AI/MIRIX#2)
- [Core Agent System (Mirix-AI/MIRIX)](/wiki/Mirix-AI/MIRIX#3)