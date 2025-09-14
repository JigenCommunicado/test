"""
Модуль оптимизации производительности
Включает кэширование данных, оптимизацию запросов и ленивую загрузку
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from threading import Lock
import hashlib

logger = logging.getLogger(__name__)

class CacheManager:
    """Менеджер кэширования данных"""
    
    def __init__(self, default_ttl: int = 300):  # 5 минут по умолчанию
        self.cache = {}
        self.default_ttl = default_ttl
        self.lock = Lock()
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Генерация ключа кэша"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Получение данных из кэша"""
        with self.lock:
            if key in self.cache:
                data, expiry = self.cache[key]
                if datetime.now() < expiry:
                    logger.debug(f"Cache hit: {key}")
                    return data
                else:
                    # Удаляем устаревшие данные
                    del self.cache[key]
                    logger.debug(f"Cache expired: {key}")
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Сохранение данных в кэш"""
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        
        with self.lock:
            self.cache[key] = (data, expiry)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str) -> None:
        """Удаление данных из кэша"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Cache deleted: {key}")
    
    def clear(self) -> None:
        """Очистка всего кэша"""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """Очистка устаревших данных"""
        now = datetime.now()
        expired_keys = []
        
        with self.lock:
            for key, (data, expiry) in self.cache.items():
                if now >= expiry:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        with self.lock:
            total_entries = len(self.cache)
            now = datetime.now()
            active_entries = sum(1 for _, (_, expiry) in self.cache.items() if now < expiry)
            
            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "expired_entries": total_entries - active_entries,
                "memory_usage": sum(len(str(data)) for data, _ in self.cache.values())
            }

# Глобальный экземпляр кэша
cache_manager = CacheManager()

def cached(ttl: int = 300, key_prefix: str = ""):
    """Декоратор для кэширования результатов функций"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            cache_key = cache_manager._generate_key(
                f"{key_prefix}:{func.__name__}", 
                *args, 
                **kwargs
            )
            
            # Пытаемся получить из кэша
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Выполняем функцию и кэшируем результат
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

class QueryOptimizer:
    """Оптимизатор запросов к базе данных"""
    
    def __init__(self):
        self.query_stats = {}
        self.slow_query_threshold = 1.0  # 1 секунда
    
    def track_query(self, query_name: str, execution_time: float, query_type: str = "unknown"):
        """Отслеживание статистики запросов"""
        if query_name not in self.query_stats:
            self.query_stats[query_name] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0,
                "slow_queries": 0,
                "query_type": query_type
            }
        
        stats = self.query_stats[query_name]
        stats["count"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
        stats["max_time"] = max(stats["max_time"], execution_time)
        
        if execution_time > self.slow_query_threshold:
            stats["slow_queries"] += 1
            logger.warning(f"Slow query detected: {query_name} took {execution_time:.2f}s")
    
    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """Получение списка медленных запросов"""
        return [
            {**stats, "query_name": name}
            for name, stats in self.query_stats.items()
            if stats["avg_time"] > self.slow_query_threshold
        ]
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Получение статистики запросов"""
        total_queries = sum(stats["count"] for stats in self.query_stats.values())
        total_time = sum(stats["total_time"] for stats in self.query_stats.values())
        
        return {
            "total_queries": total_queries,
            "total_time": total_time,
            "avg_time": total_time / total_queries if total_queries > 0 else 0,
            "slow_queries": sum(stats["slow_queries"] for stats in self.query_stats.values()),
            "queries": self.query_stats
        }

# Глобальный экземпляр оптимизатора
query_optimizer = QueryOptimizer()

def track_query_time(query_name: str, query_type: str = "unknown"):
    """Декоратор для отслеживания времени выполнения запросов"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                query_optimizer.track_query(query_name, execution_time, query_type)
        
        return wrapper
    return decorator

class LazyLoader:
    """Менеджер ленивой загрузки данных"""
    
    def __init__(self):
        self.loaders = {}
        self.cache = {}
        self.lock = Lock()
    
    def register_loader(self, data_type: str, loader_func: Callable):
        """Регистрация загрузчика данных"""
        self.loaders[data_type] = loader_func
        logger.info(f"Registered lazy loader for: {data_type}")
    
    def load(self, data_type: str, *args, **kwargs) -> Any:
        """Ленивая загрузка данных"""
        cache_key = f"{data_type}:{str(args)}:{str(sorted(kwargs.items()))}"
        
        with self.lock:
            if cache_key in self.cache:
                logger.debug(f"Lazy load cache hit: {data_type}")
                return self.cache[cache_key]
        
        if data_type not in self.loaders:
            raise ValueError(f"No loader registered for data type: {data_type}")
        
        # Загружаем данные
        data = self.loaders[data_type](*args, **kwargs)
        
        with self.lock:
            self.cache[cache_key] = data
        
        logger.debug(f"Lazy loaded: {data_type}")
        return data
    
    def clear_cache(self, data_type: str = None):
        """Очистка кэша ленивой загрузки"""
        with self.lock:
            if data_type:
                keys_to_remove = [k for k in self.cache.keys() if k.startswith(f"{data_type}:")]
                for key in keys_to_remove:
                    del self.cache[key]
                logger.info(f"Cleared lazy load cache for: {data_type}")
            else:
                self.cache.clear()
                logger.info("Cleared all lazy load cache")

# Глобальный экземпляр ленивой загрузки
lazy_loader = LazyLoader()

class PerformanceMonitor:
    """Монитор производительности системы"""
    
    def __init__(self):
        self.metrics = {
            "requests": 0,
            "response_times": [],
            "errors": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "start_time": datetime.now()
        }
        self.lock = Lock()
    
    def record_request(self, response_time: float, success: bool = True):
        """Запись метрики запроса"""
        with self.lock:
            self.metrics["requests"] += 1
            self.metrics["response_times"].append(response_time)
            
            if not success:
                self.metrics["errors"] += 1
            
            # Ограничиваем размер списка времен ответа
            if len(self.metrics["response_times"]) > 1000:
                self.metrics["response_times"] = self.metrics["response_times"][-500:]
    
    def record_cache_hit(self):
        """Запись попадания в кэш"""
        with self.lock:
            self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """Запись промаха кэша"""
        with self.lock:
            self.metrics["cache_misses"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        with self.lock:
            response_times = self.metrics["response_times"]
            uptime = (datetime.now() - self.metrics["start_time"]).total_seconds()
            
            return {
                "uptime_seconds": uptime,
                "total_requests": self.metrics["requests"],
                "error_rate": self.metrics["errors"] / max(self.metrics["requests"], 1),
                "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "cache_hit_rate": self.metrics["cache_hits"] / max(
                    self.metrics["cache_hits"] + self.metrics["cache_misses"], 1
                ),
                "cache_stats": cache_manager.get_stats(),
                "query_stats": query_optimizer.get_query_stats()
            }
    
    def reset_metrics(self):
        """Сброс метрик"""
        with self.lock:
            self.metrics = {
                "requests": 0,
                "response_times": [],
                "errors": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "start_time": datetime.now()
            }

# Глобальный экземпляр монитора
performance_monitor = PerformanceMonitor()

def monitor_performance(func: Callable) -> Callable:
    """Декоратор для мониторинга производительности"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            raise e
        finally:
            response_time = time.time() - start_time
            performance_monitor.record_request(response_time, success)
    
    return wrapper

class DataPaginator:
    """Пагинатор данных для оптимизации загрузки"""
    
    def __init__(self, page_size: int = 20):
        self.page_size = page_size
    
    def paginate(self, data: List[Any], page: int = 1) -> Dict[str, Any]:
        """Пагинация данных"""
        total_items = len(data)
        total_pages = (total_items + self.page_size - 1) // self.page_size
        
        start_index = (page - 1) * self.page_size
        end_index = start_index + self.page_size
        
        paginated_data = data[start_index:end_index]
        
        return {
            "data": paginated_data,
            "pagination": {
                "page": page,
                "page_size": self.page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

# Глобальный экземпляр пагинатора
data_paginator = DataPaginator()

def cleanup_performance_data():
    """Очистка данных производительности"""
    cache_manager.cleanup_expired()
    logger.info("Performance data cleanup completed")

# Автоматическая очистка каждые 5 минут
import threading

def start_cleanup_scheduler():
    """Запуск планировщика очистки"""
    def cleanup_worker():
        while True:
            time.sleep(300)  # 5 минут
            cleanup_performance_data()
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    logger.info("Performance cleanup scheduler started")

