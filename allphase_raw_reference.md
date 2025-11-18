我理解你想要通过展示记忆的来源信息（references）来增强用户对 AI 记忆的信任度。<cite />让我分析当前系统如何展示记忆信息，以及如何改进以支持 URL 和其他元数据的展示。<cite />

## 当前记忆展示机制

### 1. 系统提示词中的记忆展示

当前系统在构建系统提示词时会展示记忆的详细信息，包括时间戳、路径等元数据：<cite />

**Episodic Memory 展示格式**： [1](#1-0) 

**Semantic Memory 展示格式**： [2](#1-1) 

这些格式已经包含了基本的元数据（时间戳、路径、ID），但缺少来源 URL 和应用名称等信息。<cite />

### 2. 前端记忆可视化

前端通过 `ExistingMemory` 组件展示记忆，支持搜索和过滤。<cite />根据 wiki 页面，该组件提供了多种视图模式（列表视图、树状视图）和搜索功能。<cite />

## 建议的改进方案

### 方案一：在记忆存储时添加元数据字段

**1. 扩展记忆 Schema**

在各个记忆类型（Episodic、Semantic 等）的数据库表中添加元数据字段：<cite />

```python
# 在相应的 ORM 模型中添加
source_url: Optional[str]  # OCR 提取的 URL
source_app: Optional[str]  # 应用名称
screenshot_path: Optional[str]  # 截图路径
ocr_text: Optional[str]  # OCR 提取的完整文本
```

**2. 在消息累积阶段保存元数据**

修改 `TemporaryMessageAccumulator._build_memory_message()` 方法，将 OCR 提取的 URL 和应用名称作为结构化元数据传递： [3](#1-2) 

在这个方法中，可以添加：<cite />

```python
# 在构建 message_parts 时添加元数据
if item.get("ocr_metadata"):
    ocr_info = item["ocr_metadata"][idx]
    message_parts.append({
        "type": "text",
        "text": f"Source: {ocr_info['app_name']}\nExtracted URLs: {', '.join(ocr_info['urls'])}\n"
    })
```

**3. 在记忆 Agent 处理时保存元数据**

当各个记忆 Agent（Episodic、Semantic 等）处理消息时，需要从消息中提取并保存这些元数据到数据库。<cite />

### 方案二：在系统提示词中展示来源信息

修改 `build_system_prompt()` 方法，在展示记忆时包含来源信息： [4](#1-3) 

改进后的格式示例：<cite />

```python
# 在 episodic_memory 部分
episodic_memory += f"[{idx}] Timestamp: {event.occurred_at.strftime('%Y-%m-%d %H:%M:%S')} - {event.summary}"
if event.source_app:
    episodic_memory += f" (Source: {event.source_app})"
if event.source_url:
    episodic_memory += f" [URL: {event.source_url}]"
episodic_memory += f"{tree_path_str} (Details: {len(event.details)} Characters)\n"
```

### 方案三：在前端展示记忆来源

**1. 在 ChatBubble 中展示引用信息**

当 AI 回复引用了某个记忆时，可以在消息中添加来源标注。<cite />参考当前的图片展示逻辑： [5](#1-4) 

可以添加类似的记忆来源展示：<cite />

```javascript
{memoryReferences && memoryReferences.length > 0 && (
  <div className="memory-references">
    <div className="reference-header">📚 Referenced Memories:</div>
    {memoryReferences.map((ref, index) => (
      <div key={index} className="reference-item">
        <span className="reference-type">{ref.type}</span>
        <span className="reference-timestamp">{ref.timestamp}</span>
        {ref.sourceApp && <span className="reference-app">📱 {ref.sourceApp}</span>}
        {ref.sourceUrl && <a href={ref.sourceUrl} className="reference-url">🔗 {ref.sourceUrl}</a>}
      </div>
    ))}
  </div>
)}
```

**2. 在 ExistingMemory 组件中展示元数据**

在记忆浏览界面中，为每条记忆添加来源信息的展示，让用户可以看到记忆的完整上下文。<cite />

### 方案四：结构化的引用系统

**1. 在 AI 回复中添加引用标记**

修改 Chat Agent 的系统提示词，要求它在回复时明确标注引用的记忆： [6](#1-5) 

可以在系统提示词中添加：<cite />

```
When referencing information from memory, use citation format: [Memory ID: xxx]
Include source information when available: [Source: App Name, URL: xxx]
```

**2. 解析和渲染引用**

在前端解析 AI 回复中的引用标记，并将其渲染为可点击的链接，点击后可以查看完整的记忆详情。<cite />

## 具体实现建议

### 优先级 1：OCR 集成和元数据存储

1. 在前端 Electron 层面集成 OCR（使用 tesseract.js）
2. 提取 URL、应用名称、关键文本
3. 将元数据随截图一起发送到后端
4. 在数据库中存储这些元数据

### 优先级 2：系统提示词改进

1. 修改 `build_system_prompt()` 方法，在展示记忆时包含来源信息
2. 让 AI 能够看到并引用这些来源信息

### 优先级 3：前端展示优化

1. 在 ChatBubble 中添加记忆引用的展示
2. 在 ExistingMemory 组件中展示完整的元数据
3. 添加可点击的 URL 链接和应用标识

## Notes

1. **信任度提升的关键**：展示记忆的来源（时间、应用、URL）可以让用户验证 AI 回复的准确性，这对于建立信任至关重要。<cite />

2. **URL 提取的挑战**：OCR 提取的 URL 可能不完整或有错误，需要添加验证和清理逻辑。<cite />

3. **隐私考虑**：展示截图来源和 URL 时需要考虑隐私问题，可能需要添加用户控制选项。<cite />

4. **性能影响**：OCR 处理会增加截图处理时间，建议异步处理并添加进度提示。<cite />

5. **现有基础**：系统已经有 `sources` 数组来传递应用名称，可以在此基础上扩展添加 URL 和其他元数据。<cite />

Wiki pages you might want to explore:
- [Core Agent System (Mirix-AI/MIRIX)](/wiki/Mirix-AI/MIRIX#3)
- [User Interface and Settings (Mirix-AI/MIRIX)](/wiki/Mirix-AI/MIRIX#5.2)

### Citations

**File:** mirix/agent/agent.py (L1758-1760)
```python
                        episodic_memory += f"[Event ID: {event.id}] Timestamp: {event.occurred_at.strftime('%Y-%m-%d %H:%M:%S')} - {event.summary}{tree_path_str} (Details: {len(event.details)} Characters)\n"
                    else:
                        episodic_memory += f"[{idx}] Timestamp: {event.occurred_at.strftime('%Y-%m-%d %H:%M:%S')} - {event.summary}{tree_path_str} (Details: {len(event.details)} Characters)\n"
```

**File:** mirix/agent/agent.py (L1907-1909)
```python
                        semantic_memory += f"[Semantic Memory ID: {semantic_memory_item.id}] Name: {semantic_memory_item.name}; Summary: {semantic_memory_item.summary}{tree_path_str}\n"
                    else:
                        semantic_memory += f"[{idx}] Name: {semantic_memory_item.name}; Summary: {semantic_memory_item.summary}{tree_path_str}\n"
```

**File:** mirix/agent/agent.py (L1930-2036)
```python
    def build_system_prompt(self, retrieved_memories: dict) -> str:
        """Build the system prompt for the LLM API"""
        template = """Current Time: {current_time}

User Focus:
<keywords>
{keywords}
</keywords>
These keywords have been used to retrieve relevant memories from the database. 

<core_memory>
{core_memory}
</core_memory>

<episodic_memory> Most Recent Events (Orderred by Timestamp):
{episodic_memory}
</episodic_memory>
"""
        user_timezone_str = self.user_manager.get_user_by_id(self.user.id).timezone
        user_tz = pytz.timezone(user_timezone_str.split(" (")[0])
        current_time = datetime.now(user_tz).strftime("%Y-%m-%d %H:%M:%S")

        keywords = retrieved_memories["key_words"]
        core_memory = retrieved_memories["core"]
        episodic_memory = retrieved_memories["episodic"]
        resource_memory = retrieved_memories["resource"]
        semantic_memory = retrieved_memories["semantic"]
        procedural_memory = retrieved_memories["procedural"]
        knowledge_vault = retrieved_memories["knowledge_vault"]

        system_prompt = template.format(
            current_time=current_time,
            keywords=keywords,
            core_memory=core_memory if core_memory else "Empty",
            episodic_memory=episodic_memory["recent_episodic_memory"]
            if episodic_memory
            else "Empty",
        )

        if keywords is not None:
            episodic_total = (
                episodic_memory["total_number_of_items"] if episodic_memory else 0
            )
            relevant_episodic_text = (
                episodic_memory["relevant_episodic_memory"] if episodic_memory else ""
            )
            relevant_count = episodic_memory["relevant_count"] if episodic_memory else 0

            system_prompt += (
                f"\n<episodic_memory> Most Relevant Events ({relevant_count} out of {episodic_total} Events Orderred by Relevance to Keywords):\n"
                + (relevant_episodic_text if relevant_episodic_text else "Empty")
                + "\n</episodic_memory>\n"
            )

        # Add knowledge vault with counts
        knowledge_vault_total = (
            knowledge_vault["total_number_of_items"] if knowledge_vault else 0
        )
        knowledge_vault_text = knowledge_vault["text"] if knowledge_vault else ""
        knowledge_vault_count = (
            knowledge_vault["current_count"] if knowledge_vault else 0
        )
        system_prompt += (
            f"\n<knowledge_vault> ({knowledge_vault_count} out of {knowledge_vault_total} Items):\n"
            + (knowledge_vault_text if knowledge_vault_text else "Empty")
            + "\n</knowledge_vault>\n"
        )

        # Add semantic memory with counts
        semantic_total = (
            semantic_memory["total_number_of_items"] if semantic_memory else 0
        )
        semantic_text = semantic_memory["text"] if semantic_memory else ""
        semantic_count = semantic_memory["current_count"] if semantic_memory else 0
        system_prompt += (
            f"\n<semantic_memory> ({semantic_count} out of {semantic_total} Items):\n"
            + (semantic_text if semantic_text else "Empty")
            + "\n</semantic_memory>\n"
        )

        # Add resource memory with counts
        resource_total = (
            resource_memory["total_number_of_items"] if resource_memory else 0
        )
        resource_text = resource_memory["text"] if resource_memory else ""
        resource_count = resource_memory["current_count"] if resource_memory else 0
        system_prompt += (
            f"\n<resource_memory> ({resource_count} out of {resource_total} Items):\n"
            + (resource_text if resource_text else "Empty")
            + "\n</resource_memory>\n"
        )

        # Add procedural memory with counts
        procedural_total = (
            procedural_memory["total_number_of_items"] if procedural_memory else 0
        )
        procedural_text = procedural_memory["text"] if procedural_memory else ""
        procedural_count = (
            procedural_memory["current_count"] if procedural_memory else 0
        )
        system_prompt += (
            f"\n<procedural_memory> ({procedural_count} out of {procedural_total} Items):\n"
            + (procedural_text if procedural_text else "Empty")
            + "\n</procedural_memory>"
        )

        return system_prompt
```

**File:** frontend/src/components/ChatBubble.js (L116-163)
```javascript
      {images && images.length > 0 && (
        <div className="message-images">
          {images.map((image, index) => {
            // Determine the correct image source
            let imageSrc;
            if (image.displayUrl) {
              // Use displayUrl if available (base64 data URL for secure display)
              imageSrc = image.displayUrl;
            } else if (image.url) {
              // Use existing URL (blob URLs, etc.)
              imageSrc = image.url;
            } else if (image.path) {
              // Check if path is a base64 data URL
              if (image.path.startsWith('data:')) {
                imageSrc = image.path; // Use base64 data URL directly
              } else {
                // For file paths, use file:// protocol (though this may be blocked)
                imageSrc = `file://${image.path}`;
              }
            } else {
              // Fallback to name
              imageSrc = image.name;
            }

            return (
              <div key={index} className="image-preview">
                <img 
                  src={imageSrc}
                  alt={t('chat.attachmentAlt', { index: index + 1 })}
                  onError={(e) => {
                    // If file:// URL doesn't work, try without protocol for electron
                    if (image.path && e.target.src.startsWith('file://') && !image.path.startsWith('data:')) {
                      e.target.src = image.path;
                    }
                  }}
                  onLoad={(e) => {
                    // Revoke object URL after loading to prevent memory leaks
                    if (image.url && image.url.startsWith('blob:')) {
                      URL.revokeObjectURL(image.url);
                    }
                  }}
                />
                <span className="image-name">{image.name}</span>
              </div>
            );
          })}
        </div>
      )}
```

**File:** mirix/prompts/system/screen_monitor/chat_agent.txt (L1-42)
```text
You are the Chat Agent, responsible for user communication and proactive memory management. The system includes specialized memory managers: Episodic, Procedural, Resource, Semantic, Core Memory, and Knowledge Vault Managers.

**Core Responsibilities:**
1. Manage user communication
2. Proactively update memories using `trigger_memory_update_with_instruction`
3. Monitor conversation topics for context continuity

**Memory Systems:**
- **Core Memory**: User identity, preferences (Human Block) and your personality (Persona Block)
- **Episodic Memory**: Chronological interaction history
- **Procedural Memory**: Step-by-step processes and procedures
- **Resource Memory**: Documents and files for active tasks
- **Knowledge Vault**: Structured factual data and credentials
- **Semantic Memory**: Conceptual knowledge about entities and concepts

**Memory Management:**
- Regularly analyze conversations and update relevant memory systems
- Identify when new information should be stored or existing memories need updates
- Ensure consistency across different memory categories
- Use `search_in_memory` and `list_memory_within_timerange` for information retrieval

**User Interaction Protocol:**
1. **Reasoning Phase** (optional): Analyze queries internally using memory search tools
2. **Response Transmission** (mandatory): Use `send_message` to respond to users
3. **`send_message` only for final responses**: Terminates chaining. Use `send_intermediate_message` for status updates. NEVER use `send_message` to return something like "I will...", "I am doing...". These should be sent using `send_intermediate_message`.

**CRITICAL: Conversation Flow Rules:**
- `send_intermediate_message` is ONLY for brief status updates during long operations
- EVERY user query MUST end with a `send_message` call containing your final response
- Do NOT use multiple consecutive `send_intermediate_message` calls without substantial work between them
- If you have completed your task or answered the question, use `send_message` immediately
- `send_intermediate_message` does NOT end the conversation - you must continue processing

**Key Guidelines:**
- Maintain concise internal monologue (max 50 words)
- Monitor user sentiment; update Persona Block if self-improvement needed
- Messages without function calls are internal reasoning (invisible to users)
- Use `send_intermediate_message` sparingly - only for genuine progress updates
- Always complete reasoning with `send_message` to prevent loops
- If unsure whether to use intermediate or final message, default to `send_message`

```
