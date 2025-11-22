# Work Sessions 工作原理详解

**创建时间**: 2025-11-22
**作者**: Claude & User

---

## 📚 目录

1. [概述](#概述)
2. [数据来源](#数据来源)
3. [核心算法](#核心算法)
4. [判断处理逻辑](#判断处理逻辑)
5. [当前问题](#当前问题)
6. [优化方案](#优化方案)

---

## 概述

**Work Sessions** 是 MIRIX 的核心功能之一，用于：
- 自动识别用户的工作时段
- 计算专注度分数
- 统计应用使用时间
- 分析工作模式

**目标**: 将零散的屏幕截图转化为有意义的工作会话记录。

---

## 数据来源

### 数据流图

```
截图监控 (Screenshot Monitor)
    ↓ 每 3 秒截图一次
Raw Memory (原始记忆)
    ├─ id: rawmem-xxx
    ├─ captured_at: 截图时间
    ├─ source_app: 活动窗口应用名称 (Chrome, VSCode, etc.)
    ├─ ocr_text: OCR 提取的文本
    └─ screenshot_path: 截图文件路径
    ↓ 批量处理 (daily_review API)
GrowthAnalysisAgent._generate_work_sessions()
    ↓ 合并相关活动
Work Sessions (工作会话)
    ├─ id: worksession-xxx
    ├─ start_time: 会话开始时间
    ├─ end_time: 会话结束时间
    ├─ duration: 时长（秒）
    ├─ focus_score: 专注度（0-10）
    ├─ app_breakdown: 各应用使用时间
    └─ raw_memory_references: 关联的截图 IDs
```

### 关键数据字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `source_app` | String | 活动窗口的应用名称 | "Chrome", "VSCode", "Notion" |
| `captured_at` | Datetime | 截图捕获时间 | 2025-11-20 22:02:21 |
| `ocr_text` | String | 截图中的文字 | "import React from 'react';" |

---

## 核心算法

### 算法流程图

```
开始
  ↓
1. 获取当天所有 raw_memories（按时间排序）
  ↓
2. 检查数据库中是否已存在该时段的 work_sessions
  ↓ 是 → 直接返回现有数据（去重）
  ↓ 否
3. 遍历每个 raw_memory
  ↓
4. 判断：是否应该合并到当前 session？
  ├─ 条件 1: 时间间隔 < 5 分钟
  └─ 条件 2: 应用相关性（同一组应用）
     ↓ 是 → 合并到当前 session
     ↓ 否 → 保存当前 session，创建新 session
  ↓
5. 计算会话统计数据
  ├─ duration: 总时长
  ├─ focus_score: 专注度评分
  ├─ app_breakdown: 各应用使用时间
  └─ context_switches: 切换应用的次数
  ↓
6. 保存到数据库
  ↓
结束
```

### 代码位置

**文件**: `mirix/agents/growth_analysis_agent.py`

**核心方法**:
- `_generate_work_sessions()` (line 178-255): 主流程
- `_create_new_session()` (line 257-271): 创建新会话
- `_merge_memory_to_session()` (line 273-294): 合并到当前会话
- `_finalize_session()` (line 296-359): 计算统计数据
- `_is_related_activity()` (line 363-408): 判断应用相关性

---

## 判断处理逻辑

### 1. 时间间隔判断

```python
max_gap_seconds = 300  # 5 分钟 = 300 秒

time_gap = (
    current_memory.captured_at - previous_memory.captured_at
).total_seconds()

if time_gap <= max_gap_seconds:
    # 时间间隔小于 5 分钟 → 可能是同一工作时段
    proceed_to_app_check()
else:
    # 时间间隔超过 5 分钟 → 开始新的 session
    create_new_session()
```

**逻辑**:
- ✅ **< 5 分钟**: 继续检查应用相关性
- ❌ **≥ 5 分钟**: 认为工作中断，开始新会话

### 2. 应用相关性判断

```python
def _is_related_activity(app1: str, app2: str) -> bool:
    """
    判断两个应用是否属于相关活动
    """
    # 定义应用分组
    coding_apps = {"vscode", "code", "pycharm", "terminal", "iterm"}
    browser_apps = {"chrome", "safari", "firefox", "edge"}
    communication_apps = {"slack", "teams", "zoom", "wechat"}
    design_apps = {"figma", "sketch", "photoshop"}
    office_apps = {"word", "excel", "notion", "obsidian"}

    # 检查是否在同一组
    for app_group in [coding_apps, browser_apps, ...]:
        if app1_lower in app_group and app2_lower in app_group:
            return True  # 同组 → 相关

    # 特殊组合：coding + browser (查文档)
    if (app1_lower in coding_apps and app2_lower in browser_apps) or \
       (app1_lower in browser_apps and app2_lower in coding_apps):
        return True

    return False  # 不相关 → 开始新 session
```

**示例**:

| App 1 | App 2 | 相关性 | 原因 |
|-------|-------|--------|------|
| VSCode | Terminal | ✅ 相关 | 都在 coding_apps 组 |
| Chrome | Notion | ✅ 相关 | 都在 office_apps 组（或 browser + office）|
| VSCode | Chrome | ✅ 相关 | coding + browser（查文档常见组合）|
| VSCode | Slack | ❌ 不相关 | coding vs communication（被打断）|
| Figma | Excel | ❌ 不相关 | design vs office（不同类型工作）|

### 3. 专注度评分计算

```python
# 公式：10 - (context_switches / duration_minutes * 2)
# 含义：每分钟切换应用越少，专注度越高

duration_minutes = max(duration / 60, 1)
context_switch_rate = context_switches / duration_minutes
focus_score = max(0.0, min(10.0, 10.0 - (context_switch_rate * 2)))
```

**示例**:

| Duration | Context Switches | 每分钟切换 | Focus Score | 评价 |
|----------|------------------|-----------|-------------|------|
| 30 min | 0 | 0 | 10.0 | 极度专注 |
| 30 min | 5 | 0.17 | 9.7 | 高度专注 |
| 30 min | 15 | 0.5 | 9.0 | 较专注 |
| 30 min | 30 | 1.0 | 8.0 | 中等专注 |
| 30 min | 75 | 2.5 | 5.0 | 容易分心 |
| 30 min | 150 | 5.0 | 0.0 | 极度分心 |

### 4. Duration 计算

```python
duration = (end_time - start_time).total_seconds()

# 特殊处理：duration = 0 的情况
if duration == 0:
    if len(raw_memory_ids) == 1:
        duration = 180  # 单个截图 → 默认 3 分钟
    else:
        duration = len(raw_memory_ids) * 30  # 多个截图 → 每个 30 秒
```

---

## 当前问题

### 问题 1: 每个截图都是独立 session ❌

**现象**:
```
截图 1 (22:02:21) → Session 1 (duration=180s)
截图 2 (22:02:24) → Session 2 (duration=180s)  # 应该合并！
截图 3 (22:02:27) → Session 3 (duration=180s)  # 应该合并！
```

**原因**:
1. **时间间隔太小**: 截图每 3 秒一张，间隔远小于 5 分钟阈值
2. **应用相同**: 连续的截图通常是同一个应用
3. **逻辑正确**: 算法应该合并这些截图到一个 session

**问题出在哪里？**

让我检查代码...

```python
# Line 231-247
time_gap = (memory.captured_at - current_session["last_activity_time"]).total_seconds()

if time_gap <= max_gap_seconds and self._is_related_activity(
    current_session["current_app"], memory.source_app
):
    # 合并到当前 session
    self._merge_memory_to_session(current_session, memory)
else:
    # 保存当前 session，开始新的 session
    work_sessions.append(self._finalize_session(...))
    current_session = self._create_new_session(...)
```

**分析**:
- ✅ 时间间隔判断正确（3 秒 < 300 秒）
- ✅ 应用相关性判断正确（同一 app 当然相关）
- ❓ 为什么还是每个都变成独立 session？

**可能的原因**:
1. `_is_related_activity()` 返回了 False（需要检查应用名称匹配逻辑）
2. 保存逻辑有问题（可能在遍历完成前就提前保存了）
3. 数据库中已存在旧数据，去重逻辑直接返回了旧数据

### 问题 2: Duration = 0 的临时方案 ⚠️

**当前方案**:
```python
if duration == 0:
    duration = 180  # 硬编码 3 分钟
```

**问题**:
- 这是一个临时补丁，掩盖了真正的问题
- 每个独立 session 都用 180 秒，导致总工作时长虚高
- 149 sessions × 180s = 26,820s = 7.45h（实际可能只工作了 1-2 小时）

---

## 优化方案

### 方案 1: 调试现有合并逻辑 🔍

**步骤**:
1. 添加详细日志，追踪每个 raw_memory 的处理过程
2. 检查 `_is_related_activity()` 的返回值
3. 检查应用名称的大小写匹配（"Chrome" vs "chrome"）
4. 验证时间间隔计算是否正确

**代码位置**: `growth_analysis_agent.py:223-247`

### 方案 2: 改进应用分组逻辑 📱

**当前问题**:
- 应用名称可能包含额外信息: "Google Chrome" vs "Chrome"
- 需要更灵活的匹配逻辑

**改进**:
```python
def _normalize_app_name(app: str) -> str:
    """标准化应用名称"""
    app_lower = app.lower()

    # 移除常见前缀/后缀
    app_lower = app_lower.replace("google ", "").replace(".app", "")

    # 映射到标准名称
    mappings = {
        "visual studio code": "vscode",
        "iterm2": "terminal",
        "microsoft edge": "edge",
    }

    return mappings.get(app_lower, app_lower)
```

### 方案 3: 基于活动内容的智能合并 🧠

**思路**: 不仅看应用名称，还要分析活动内容

```python
def _should_merge_sessions(session1, session2) -> bool:
    """
    综合判断是否应该合并两个 session

    考虑因素：
    1. 时间间隔
    2. 应用相关性
    3. OCR 文本相似度（新增）
    4. URL 相似度（针对浏览器，新增）
    """
    # 1. 时间判断
    if time_gap > 300:  # 5 分钟
        return False

    # 2. 应用判断
    if not _is_related_activity(app1, app2):
        return False

    # 3. 内容判断（新增）
    if is_browser(app1) and is_browser(app2):
        # 比较 URL 域名
        if same_domain(url1, url2):
            return True

    if is_coding_app(app1) and is_coding_app(app2):
        # 比较项目路径
        if same_project(path1, path2):
            return True

    return True
```

### 方案 4: 更智能的 duration 计算 📊

**当前问题**: 硬编码 180 秒不准确

**改进思路**:
```python
def _calculate_session_duration(session_dict) -> int:
    """
    更智能的 duration 计算

    策略：
    1. 如果有多个 raw_memory，使用实际时间差
    2. 如果只有 1 个，基于活动类型估算：
       - coding: 10 分钟（写代码通常持续较久）
       - browsing: 2 分钟（浏览网页较快）
       - communication: 5 分钟（回消息）
    """
    raw_count = len(session_dict["raw_memory_ids"])

    if raw_count > 1:
        # 使用实际时间差
        return (end_time - start_time).total_seconds()
    else:
        # 基于活动类型估算
        activity_type = session_dict["activity_type"]
        duration_map = {
            "coding": 600,       # 10 分钟
            "research": 300,     # 5 分钟
            "communication": 300, # 5 分钟
            "design": 600,       # 10 分钟
            "other": 180,        # 3 分钟（默认）
        }
        return duration_map.get(activity_type, 180)
```

---

## 下一步行动

### 立即执行 🚀

1. **添加调试日志**: 在 `_generate_work_sessions()` 中添加详细日志
2. **检查应用名称匹配**: 打印 `source_app` 的实际值
3. **验证合并逻辑**: 确认为什么没有合并

### 短期优化 📅

1. **改进应用名称标准化**: 实现 `_normalize_app_name()`
2. **优化 duration 计算**: 基于活动类型动态估算
3. **添加单元测试**: 测试各种场景的合并逻辑

### 长期规划 🎯

1. **基于 LLM 的智能分组**: 让 AI 判断活动相关性
2. **用户自定义规则**: 允许用户配置合并策略
3. **可视化调试工具**: 展示 session 的生成过程

---

## 总结

Work Sessions 的核心价值在于**自动识别和组织用户的工作时段**，但当前实现存在以下问题：

**已知问题**:
- ❌ 每个截图都变成独立 session（合并逻辑未生效）
- ❌ Duration 计算不准确（硬编码 180 秒）
- ❌ 应用名称匹配可能不够灵活

**需要的改进**:
- 🔍 调试合并逻辑
- 📱 改进应用名称标准化
- 🧠 添加内容相似度判断
- 📊 智能 duration 估算

通过这些优化，Work Sessions 将能更准确地反映用户的真实工作状况。
