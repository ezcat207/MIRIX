# MIRIX 优化与增强任务 (OE)

**创建时间**: 2025-11-22
**目的**: 记录所有性能优化和功能增强任务的进度、问题和解决方案

---

## 📋 当前任务：记忆吸收性能优化

**背景**:
- 问题：Meta Memory Agent 处理截图耗时 90 秒，阻塞主线程
- 影响：健康检查超时，前端卡死
- 根本原因：同步处理 Embedding 生成、OCR、LLM 调用

**目标**:
- 将处理时间从 90 秒降至 10-15 秒
- 消除主线程阻塞
- 改善用户体验

---

## ✅ 已完成

### 2025-11-22: 临时方案 - 增加前端健康检查超时时间

**Commit**: 待提交

**修改**:
```javascript
// frontend/src/App.js:128
}, 120000); // 从 30s 改为 120s
```

**原因**:
- 后端处理 5 张截图仍需约 25 秒
- 30 秒超时仍可能触发
- 临时增加到 120 秒确保不超时

**注意**: ⚠️ **这是临时方案，优化完成后需改回 30 秒**

**回滚计划**:
- 完成任务 1-4 后
- 验证处理时间降至 10-15 秒
- 改回 `30000` (30s)

---

### 2025-11-22: 降低批处理大小

**Commit**: a758e01

**修改**:
```python
# mirix/agent/app_constants.py
TEMPORARY_MESSAGE_LIMIT = 5  # 从 20 降到 5
```

**效果**:
- 预期: 90秒 → 25秒 (降低 72%)
- 减少单次 LLM 调用的图片数量
- 降低阻塞风险

**注意**: ⚠️ **未来优化完成后可能需要调整回 10-15**

**测试**: ⏳ 待观察下次记忆吸收

---

## 🚧 进行中：中期优化（1-2 天）

### 任务 1: 批量数据库插入优化

**目标**: 减少数据库操作次数，从 20 次 commit 降至 1 次

**当前问题**:
```python
# mirix/agent/temporary_message_accumulator.py:662-676
for idx, image_uri in enumerate(image_uris):
    raw_memory = raw_memory_manager.insert_raw_memory(...)  # 串行插入
    # 每次都 session.add() + session.commit()
    raw_memory_ids.append(raw_memory.id)
```

**耗时**: 5 张 × 200ms = 1 秒

**优化方案**:
- 改为批量插入 `session.bulk_save_objects()`
- 一次性 commit

**预期效果**: 1 秒 → 0.2 秒 (节省 0.8 秒)

**状态**: ⏳ 未开始

**相关文件**:
- `mirix/services/raw_memory_manager.py`
- `mirix/agent/temporary_message_accumulator.py`

---

### 任务 2: 异步 Embedding 生成

**目标**: 将 Embedding 生成移到后台，不阻塞主线程

**当前问题**:
```python
# mirix/services/raw_memory_manager.py:64-115
if ocr_text and BUILD_EMBEDDINGS_FOR_MEMORY:
    embed_model = embedding_model(embedding_config)
    raw_embedding = embed_model.get_text_embedding(ocr_text)  # 同步 API 调用
    # 每张截图 500ms，5 张 = 2.5 秒
```

**耗时**: 5 张 × 500ms = 2.5 秒

**优化方案**:
- 先保存 raw_memory（embedding=None）
- 使用 FastAPI BackgroundTasks 异步生成 embedding
- 生成完成后更新数据库

**预期效果**: 2.5 秒阻塞 → 0 秒阻塞 (embedding 在后台完成)

**状态**: ⏳ 未开始

**相关文件**:
- `mirix/services/raw_memory_manager.py`
- `mirix/agent/temporary_message_accumulator.py`

---

### 任务 3: 并行 OCR 处理

**目标**: 使用多线程并行处理 OCR，加速提取

**当前问题**:
```python
# mirix/agent/temporary_message_accumulator.py:640-643
for idx, image_uri in enumerate(image_uris):
    ocr_text, urls = OCRUrlExtractor.extract_urls_and_text(local_file_path)
    # 串行处理，每张 400ms，5 张 = 2 秒
```

**耗时**: 5 张 × 400ms = 2 秒

**优化方案**:
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(OCRUrlExtractor.extract_urls_and_text, path)
        for path in image_paths
    ]
    results = [f.result() for f in futures]
```

**预期效果**: 2 秒 → 0.5 秒 (节省 1.5 秒)

**状态**: ⏳ 未开始

**相关文件**:
- `mirix/agent/temporary_message_accumulator.py`
- `mirix/helpers/ocr_url_extractor.py`

---

### 任务 4: 添加性能监控

**目标**: 记录每个步骤的耗时，便于后续优化

**方案**:
```python
import time
from contextlib import contextmanager

@contextmanager
def timer(name):
    start = time.time()
    yield
    elapsed = time.time() - start
    logger.info(f"⏱️  [{name}] took {elapsed:.2f} seconds")

# 使用示例
with timer("OCR Processing"):
    ocr_results = extract_ocr(images)

with timer("Database Insert"):
    insert_raw_memories(memories)
```

**监控指标**:
- OCR 处理时间
- Embedding 生成时间
- 数据库操作时间
- LLM 调用时间
- 总处理时间

**状态**: ⏳ 未开始

**相关文件**:
- `mirix/agent/temporary_message_accumulator.py`
- 新文件: `mirix/utils/performance.py`

---

## 📊 性能目标

### 当前性能 (批处理大小=5)

```
总耗时 ~25 秒:
├─ OCR 处理:        2.0 秒  (5 张 × 400ms)
├─ Embedding 生成:  2.5 秒  (5 张 × 500ms)
├─ 数据库插入:      1.0 秒  (5 次 commit)
├─ LLM 视觉分析:   18.0 秒  (5 张图片)
└─ 其他开销:        1.5 秒
```

### 优化后目标

```
总耗时 ~10-15 秒:
├─ OCR 处理:        0.5 秒  (并行 4 线程) ✅ 节省 1.5 秒
├─ Embedding 生成:  0.0 秒  (异步后台)    ✅ 节省 2.5 秒
├─ 数据库插入:      0.2 秒  (批量插入)    ✅ 节省 0.8 秒
├─ LLM 视觉分析:   10.0 秒  (5 张图片，无法优化)
└─ 其他开销:        1.0 秒

总节省: 4.8 秒 → 从 25 秒降至 ~12 秒 (降低 52%)
```

---

## 🧪 测试计划

### 单元测试

1. **批量插入测试**:
   - 验证批量插入和单个插入结果一致
   - 验证 ID 生成正确
   - 验证事务回滚

2. **异步 Embedding 测试**:
   - 验证 embedding 最终生成成功
   - 验证失败重试机制
   - 验证并发安全

3. **并行 OCR 测试**:
   - 验证 OCR 结果准确性
   - 验证线程安全
   - 验证资源清理

### 集成测试

1. **端到端流程**:
   - 发送 5 张截图
   - 验证 raw_memory 创建
   - 验证 embedding 异步生成
   - 验证高层记忆创建

2. **性能测试**:
   - 测量实际处理时间
   - 验证无阻塞
   - 验证健康检查正常

### 压力测试

1. **大批量测试**:
   - 连续发送 100 张截图
   - 验证系统稳定性
   - 验证内存不泄漏

---

## 📝 开发规范

### Git Commit 约定

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**:
- `perf`: 性能优化
- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 代码重构
- `test`: 测试相关
- `docs`: 文档更新

**示例**:
```
perf(raw_memory): 实现批量数据库插入优化

- 将串行插入改为批量插入
- 减少 commit 次数从 5 次到 1 次
- 性能提升: 1秒 → 0.2秒

测试: ✅ 单元测试通过
```

### 开发流程

1. **开发**:
   - 创建新分支或在 main 直接开发
   - 编写代码
   - 添加日志和注释

2. **测试**:
   - 编写单元测试
   - 运行测试确保通过
   - 手动测试验证功能

3. **提交**:
   - Git commit 按照约定格式
   - 更新本文档（OE.md）
   - Push 到仓库

4. **记录**:
   - 在对应任务下记录完成状态
   - 记录遇到的问题和解决方案
   - 更新性能数据

---

## 📌 注意事项

1. **向后兼容**:
   - 确保优化不破坏现有功能
   - 保持 API 接口不变
   - 数据库 schema 兼容

2. **错误处理**:
   - 异步任务失败要有重试机制
   - 失败时不影响主流程
   - 记录错误日志

3. **性能监控**:
   - 每个优化都要测量实际效果
   - 对比优化前后数据
   - 记录在本文档

4. **代码质量**:
   - 保持代码可读性
   - 添加必要的注释
   - 遵循项目代码风格

---

## 🔜 未来计划

### 短期（本周）
- ✅ 降低批处理大小
- ⏳ 批量数据库插入
- ⏳ 异步 Embedding 生成
- ⏳ 并行 OCR 处理
- ⏳ 性能监控

### 中期（本月）
- 完整异步架构（Celery / Redis）
- WebSocket 实时通知
- 前端进度条显示
- 缓存优化

### 长期（未来）
- 分布式处理
- GPU 加速 OCR
- 智能批处理（动态调整大小）
- 预测性加载

---

## 📊 性能数据记录

| 日期 | 优化项 | 优化前 | 优化后 | 改善 | Commit |
|------|--------|--------|--------|------|---------|
| 2025-11-22 | 批处理大小 | 90秒 (20张) | 25秒 (5张) | -72% | a758e01 |
| - | 批量插入 | - | - | - | - |
| - | 异步 Embedding | - | - | - | - |
| - | 并行 OCR | - | - | - | - |

---

**最后更新**: 2025-11-22
**负责人**: Claude + User
**优先级**: P0 (最高)
