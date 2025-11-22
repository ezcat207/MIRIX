"""
性能监控工具

提供性能计时和监控功能，用于优化性能瓶颈。
"""

import time
import logging
from contextlib import contextmanager
from typing import Optional


@contextmanager
def timer(name: str, logger: Optional[logging.Logger] = None):
    """
    性能计时器上下文管理器。

    使用示例:
    ```python
    from mirix.utils.performance import timer

    with timer("OCR Processing", logger):
        ocr_results = extract_ocr(images)
    ```

    Args:
        name: 计时器名称，用于日志输出
        logger: 可选的 logger 实例。如果未提供，使用默认 logger

    Yields:
        None
    """
    if logger is None:
        logger = logging.getLogger("Mirix.Performance")

    start = time.time()
    logger.info(f"⏱️  [{name}] Starting...")

    try:
        yield
    finally:
        elapsed = time.time() - start
        logger.info(f"⏱️  [{name}] Completed in {elapsed:.2f} seconds")


class PerformanceMonitor:
    """
    性能监控器类，用于收集和报告性能指标。

    使用示例:
    ```python
    monitor = PerformanceMonitor()

    with monitor.measure("OCR Processing"):
        ocr_results = extract_ocr(images)

    with monitor.measure("Database Insert"):
        insert_raw_memories(memories)

    # 输出性能报告
    monitor.report()
    ```
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化性能监控器。

        Args:
            logger: 可选的 logger 实例
        """
        self.logger = logger or logging.getLogger("Mirix.Performance")
        self.metrics = {}  # {name: [duration1, duration2, ...]}
        self.total_start = None

    def start_total(self):
        """开始总计时"""
        self.total_start = time.time()

    def end_total(self) -> float:
        """结束总计时，返回总耗时（秒）"""
        if self.total_start is None:
            return 0.0
        return time.time() - self.total_start

    @contextmanager
    def measure(self, name: str):
        """
        测量某个操作的耗时。

        Args:
            name: 操作名称

        Yields:
            None
        """
        start = time.time()
        self.logger.debug(f"⏱️  [{name}] Starting...")

        try:
            yield
        finally:
            elapsed = time.time() - start
            self.logger.debug(f"⏱️  [{name}] Completed in {elapsed:.2f} seconds")

            # 记录到 metrics
            if name not in self.metrics:
                self.metrics[name] = []
            self.metrics[name].append(elapsed)

    def report(self):
        """
        输出性能报告。

        报告格式:
        ```
        Performance Report:
        ├─ OCR Processing:     0.50s (avg), 2 calls
        ├─ Database Insert:    0.20s (avg), 1 call
        └─ Total:              12.50s
        ```
        """
        total_elapsed = self.end_total()

        self.logger.info("=" * 60)
        self.logger.info("📊 Performance Report:")
        self.logger.info("=" * 60)

        for name, durations in self.metrics.items():
            avg_duration = sum(durations) / len(durations)
            total_duration = sum(durations)
            call_count = len(durations)

            if call_count == 1:
                self.logger.info(f"├─ {name:30s} {total_duration:6.2f}s (1 call)")
            else:
                self.logger.info(
                    f"├─ {name:30s} {avg_duration:6.2f}s avg, {total_duration:6.2f}s total ({call_count} calls)"
                )

        self.logger.info(f"└─ {'Total Time':30s} {total_elapsed:6.2f}s")
        self.logger.info("=" * 60)

    def get_metric(self, name: str) -> float:
        """
        获取某个指标的平均值。

        Args:
            name: 指标名称

        Returns:
            平均耗时（秒），如果指标不存在则返回 0
        """
        if name not in self.metrics or not self.metrics[name]:
            return 0.0
        return sum(self.metrics[name]) / len(self.metrics[name])
