import json
import os
import time
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional
import threading
import time

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Типы уведомлений"""
    APPLICATION_OPEN = "application_open"  # Начало приема заявок
    APPLICATION_CLOSING_SOON = "application_closing_soon"  # Скоро окончание
    APPLICATION_CLOSED = "application_closed"  # Прием заявок завершен
    APPLICATION_REMINDER = "application_reminder"  # Напоминание о заявке
    SYSTEM_ANNOUNCEMENT = "system_announcement"  # Системное объявление

class NotificationStatus(Enum):
    """Статусы уведомлений"""
    PENDING = "pending"  # Ожидает отправки
    SENT = "sent"  # Отправлено
    DELIVERED = "delivered"  # Доставлено
    FAILED = "failed"  # Ошибка отправки
    READ = "read"  # Прочитано

class ScheduleType(Enum):
    """Типы расписания"""
    ONCE = "once"  # Одноразово
    DAILY = "daily"  # Ежедневно
    WEEKLY = "weekly"  # Еженедельно
    MONTHLY = "monthly"  # Ежемесячно

@dataclass
class Notification:
    """Модель уведомления"""
    id: str
    type: NotificationType
    title: str
    message: str
    user_id: Optional[str] = None  # Если None - для всех пользователей
    data: Dict = None
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = None
    sent_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.data is None:
            self.data = {}

@dataclass
class ApplicationPeriod:
    """Период приема заявок"""
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    reminder_hours: List[int] = None  # Часы до окончания для напоминаний
    
    def __post_init__(self):
        if self.reminder_hours is None:
            self.reminder_hours = [24, 12, 6, 1]  # Напоминания за 24, 12, 6 и 1 час

@dataclass
class NotificationSchedule:
    """Расписание уведомлений"""
    id: str
    name: str
    type: NotificationType
    title: str
    message: str
    schedule_type: ScheduleType
    schedule_config: Dict
    is_active: bool = True
    created_at: datetime = None
    last_sent: Optional[datetime] = None
    next_send: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.schedule_config is None:
            self.schedule_config = {}

class NotificationManager:
    """Менеджер уведомлений"""
    
    def __init__(self, data_file: str = "notifications.json"):
        self.data_file = data_file
        self.notifications: Dict[str, Notification] = {}
        self.application_periods: Dict[str, ApplicationPeriod] = {}
        self.notification_schedules: Dict[str, NotificationSchedule] = {}
        self.subscribers: Dict[str, List[str]] = {}  # user_id -> [subscription_ids]
        self.is_running = False
        self.worker_thread = None
        
        self.load_data()
        self._initialize_default_period()
        logger.info(f"🔔 NotificationManager инициализирован. Уведомлений: {len(self.notifications)}, Расписаний: {len(self.notification_schedules)}")
    
    def load_data(self):
        """Загружает данные из файла"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Загружаем уведомления
                for notif_data in data.get('notifications', []):
                    notif = Notification(
                        id=notif_data['id'],
                        type=NotificationType(notif_data['type']),
                        title=notif_data['title'],
                        message=notif_data['message'],
                        user_id=notif_data.get('user_id'),
                        data=notif_data.get('data', {}),
                        status=NotificationStatus(notif_data['status']),
                        created_at=datetime.fromisoformat(notif_data['created_at']),
                        sent_at=datetime.fromisoformat(notif_data['sent_at']) if notif_data.get('sent_at') else None,
                        expires_at=datetime.fromisoformat(notif_data['expires_at']) if notif_data.get('expires_at') else None
                    )
                    self.notifications[notif.id] = notif
                
                # Загружаем периоды приема заявок
                for period_data in data.get('application_periods', []):
                    period = ApplicationPeriod(
                        id=period_data['id'],
                        name=period_data['name'],
                        start_date=datetime.fromisoformat(period_data['start_date']),
                        end_date=datetime.fromisoformat(period_data['end_date']),
                        is_active=period_data['is_active'],
                        reminder_hours=period_data.get('reminder_hours', [24, 12, 6, 1])
                    )
                    self.application_periods[period.id] = period
                
                # Загружаем подписчиков
                self.subscribers = data.get('subscribers', {})
                
                logger.info(f"📖 Загружено {len(self.notifications)} уведомлений, {len(self.application_periods)} периодов")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки данных уведомлений: {e}")
    
    def save_data(self):
        """Сохраняет данные в файл"""
        try:
            data = {
                'notifications': [],
                'application_periods': [],
                'subscribers': self.subscribers
            }
            
            # Сохраняем уведомления
            for notif in self.notifications.values():
                notif_data = {
                    'id': notif.id,
                    'type': notif.type.value,
                    'title': notif.title,
                    'message': notif.message,
                    'user_id': notif.user_id,
                    'data': notif.data,
                    'status': notif.status.value,
                    'created_at': notif.created_at.isoformat(),
                    'sent_at': notif.sent_at.isoformat() if notif.sent_at else None,
                    'expires_at': notif.expires_at.isoformat() if notif.expires_at else None
                }
                data['notifications'].append(notif_data)
            
            # Сохраняем периоды
            for period in self.application_periods.values():
                period_data = {
                    'id': period.id,
                    'name': period.name,
                    'start_date': period.start_date.isoformat(),
                    'end_date': period.end_date.isoformat(),
                    'is_active': period.is_active,
                    'reminder_hours': period.reminder_hours
                }
                data['application_periods'].append(period_data)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"💾 Сохранено {len(self.notifications)} уведомлений")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения данных уведомлений: {e}")
    
    def _initialize_default_period(self):
        """Инициализирует период приема заявок по умолчанию"""
        if not self.application_periods:
            # Создаем период на следующий месяц
            now = datetime.now()
            start_date = now.replace(day=1, hour=9, minute=0, second=0, microsecond=0)
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1, day=31)
            else:
                end_date = start_date.replace(month=start_date.month + 1, day=31)
            
            period = ApplicationPeriod(
                id="default_period",
                name="Прием заявок на командировки",
                start_date=start_date,
                end_date=end_date
            )
            self.application_periods[period.id] = period
            self.save_data()
    
    def create_notification(self, 
                          type: NotificationType, 
                          title: str, 
                          message: str, 
                          user_id: Optional[str] = None,
                          data: Dict = None,
                          expires_in_hours: int = 24) -> str:
        """Создает новое уведомление"""
        notif_id = f"notif_{int(time.time() * 1000)}"
        
        notification = Notification(
            id=notif_id,
            type=type,
            title=title,
            message=message,
            user_id=user_id,
            data=data or {},
            expires_at=datetime.now() + timedelta(hours=expires_in_hours)
        )
        
        self.notifications[notif_id] = notification
        self.save_data()
        
        logger.info(f"📝 Создано уведомление: {title}")
        return notif_id
    
    def get_user_notifications(self, user_id: str, unread_only: bool = True) -> List[Notification]:
        """Получает уведомления пользователя"""
        user_notifications = []
        
        for notif in self.notifications.values():
            if notif.user_id is None or notif.user_id == user_id:
                if not unread_only or notif.status == NotificationStatus.PENDING:
                    user_notifications.append(notif)
        
        # Сортируем по дате создания (новые сверху)
        user_notifications.sort(key=lambda x: x.created_at, reverse=True)
        return user_notifications
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Отмечает уведомление как прочитанное"""
        if notification_id in self.notifications:
            notif = self.notifications[notification_id]
            if notif.user_id is None or notif.user_id == user_id:
                notif.status = NotificationStatus.READ
                self.save_data()
                return True
        return False
    
    def subscribe_user(self, user_id: str, subscription_id: str) -> bool:
        """Подписывает пользователя на уведомления"""
        if user_id not in self.subscribers:
            self.subscribers[user_id] = []
        
        if subscription_id not in self.subscribers[user_id]:
            self.subscribers[user_id].append(subscription_id)
            self.save_data()
            logger.info(f"👤 Пользователь {user_id} подписан на уведомления")
            return True
        return False
    
    def unsubscribe_user(self, user_id: str, subscription_id: str) -> bool:
        """Отписывает пользователя от уведомлений"""
        if user_id in self.subscribers and subscription_id in self.subscribers[user_id]:
            self.subscribers[user_id].remove(subscription_id)
            self.save_data()
            logger.info(f"👤 Пользователь {user_id} отписан от уведомлений")
            return True
        return False
    
    def get_active_application_periods(self) -> List[ApplicationPeriod]:
        """Получает активные периоды приема заявок"""
        now = datetime.now()
        active_periods = []
        
        for period in self.application_periods.values():
            if period.is_active and period.start_date <= now <= period.end_date:
                active_periods.append(period)
        
        return active_periods
    
    def check_application_periods(self):
        """Проверяет периоды приема заявок и создает уведомления"""
        now = datetime.now()
        
        for period in self.application_periods.values():
            if not period.is_active:
                continue
            
            # Проверяем начало периода
            if period.start_date <= now <= period.start_date + timedelta(minutes=5):
                self.create_notification(
                    type=NotificationType.APPLICATION_OPEN,
                    title="🚀 Начался прием заявок!",
                    message=f"Период '{period.name}' начался. Заявки принимаются до {period.end_date.strftime('%d.%m.%Y %H:%M')}",
                    data={'period_id': period.id}
                )
            
            # Проверяем напоминания о скором окончании
            for hours in period.reminder_hours:
                reminder_time = period.end_date - timedelta(hours=hours)
                if reminder_time <= now <= reminder_time + timedelta(minutes=5):
                    self.create_notification(
                        type=NotificationType.APPLICATION_CLOSING_SOON,
                        title=f"⏰ Напоминание: до окончания приема заявок {hours}ч",
                        message=f"Период '{period.name}' завершится через {hours} часов. Не забудьте подать заявку!",
                        data={'period_id': period.id, 'hours_left': hours}
                    )
            
            # Проверяем окончание периода
            if period.end_date <= now <= period.end_date + timedelta(minutes=5):
                self.create_notification(
                    type=NotificationType.APPLICATION_CLOSED,
                    title="🔒 Прием заявок завершен",
                    message=f"Период '{period.name}' завершен. Заявки больше не принимаются.",
                    data={'period_id': period.id}
                )
                period.is_active = False
                self.save_data()
    
    def start_worker(self):
        """Запускает фоновый процесс проверки уведомлений"""
        if self.is_running:
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("🔄 Фоновый процесс уведомлений запущен")
    
    def stop_worker(self):
        """Останавливает фоновый процесс"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join()
        logger.info("⏹️ Фоновый процесс уведомлений остановлен")
    
    def _worker_loop(self):
        """Основной цикл фонового процесса"""
        while self.is_running:
            try:
                # Проверяем периоды приема заявок
                self.check_application_periods()
                
                # Проверяем запланированные уведомления
                self.check_scheduled_notifications()
                
                # Проверяем просроченные уведомления
                now = datetime.now()
                for notif in self.notifications.values():
                    if (notif.expires_at and 
                        notif.expires_at <= now and 
                        notif.status == NotificationStatus.PENDING):
                        notif.status = NotificationStatus.FAILED
                        logger.info(f"⏰ Уведомление {notif.id} просрочено")
                
                self.save_data()
                
                # Ждем 1 минуту перед следующей проверкой
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в фоновом процессе уведомлений: {e}")
                time.sleep(60)
    
    def get_notification_stats(self) -> Dict:
        """Получает статистику уведомлений"""
        stats = {
            'total': len(self.notifications),
            'pending': 0,
            'sent': 0,
            'delivered': 0,
            'failed': 0,
            'read': 0
        }
        
        for notif in self.notifications.values():
            stats[notif.status.value] += 1
        
        return stats

    # ==================== МЕТОДЫ РАСПИСАНИЯ УВЕДОМЛЕНИЙ ====================

    def create_notification_schedule(self, 
                                   name: str,
                                   notification_type: NotificationType,
                                   title: str,
                                   message: str,
                                   schedule_type: str,
                                   schedule_config: Dict,
                                   is_active: bool = True) -> str:
        """Создает расписание уведомлений"""
        schedule_id = f"schedule_{int(time.time() * 1000)}"
        
        schedule = NotificationSchedule(
            id=schedule_id,
            name=name,
            type=notification_type,
            title=title,
            message=message,
            schedule_type=ScheduleType(schedule_type),
            schedule_config=schedule_config,
            is_active=is_active
        )
        
        # Вычисляем время следующей отправки
        schedule.next_send = self._calculate_next_send(schedule)
        
        self.notification_schedules[schedule_id] = schedule
        self.save_data()
        
        logger.info(f"📅 Создано расписание уведомлений: {name}")
        return schedule_id

    def get_notification_schedules(self) -> List[NotificationSchedule]:
        """Получает все расписания уведомлений"""
        return list(self.notification_schedules.values())

    def update_notification_schedule(self, schedule_id: str, **kwargs) -> bool:
        """Обновляет расписание уведомлений"""
        if schedule_id not in self.notification_schedules:
            return False
        
        schedule = self.notification_schedules[schedule_id]
        
        for key, value in kwargs.items():
            if hasattr(schedule, key):
                if key == 'type':
                    setattr(schedule, key, NotificationType(value))
                elif key == 'schedule_type':
                    setattr(schedule, key, ScheduleType(value))
                else:
                    setattr(schedule, key, value)
        
        # Пересчитываем время следующей отправки
        schedule.next_send = self._calculate_next_send(schedule)
        
        self.save_data()
        return True

    def delete_notification_schedule(self, schedule_id: str) -> bool:
        """Удаляет расписание уведомлений"""
        if schedule_id in self.notification_schedules:
            del self.notification_schedules[schedule_id]
            self.save_data()
            return True
        return False

    def test_notification_schedule(self, schedule_id: str) -> bool:
        """Тестирует расписание уведомлений (отправляет уведомление сейчас)"""
        if schedule_id not in self.notification_schedules:
            return False
        
        schedule = self.notification_schedules[schedule_id]
        
        # Создаем тестовое уведомление
        notif_id = self.create_notification(
            type=schedule.type,
            title=f"[ТЕСТ] {schedule.title}",
            message=f"[ТЕСТ] {schedule.message}",
            expires_in_hours=1
        )
        
        logger.info(f"🧪 Тестовое уведомление отправлено: {schedule.name}")
        return True

    # Методы для управления периодами подачи заявок
    def get_application_periods(self) -> List['ApplicationPeriod']:
        """Получает все периоды подачи заявок"""
        return list(self.application_periods.values())

    def create_application_period(self, name: str, start_date: str, end_date: str, 
                                description: str = '', is_active: bool = True) -> Optional['ApplicationPeriod']:
        """Создает новый период подачи заявок"""
        try:
            period_id = f"period_{int(time.time())}"
            period = ApplicationPeriod(
                period_id=period_id,
                name=name,
                start_date=datetime.fromisoformat(start_date),
                end_date=datetime.fromisoformat(end_date),
                description=description,
                is_active=is_active
            )
            
            self.application_periods[period_id] = period
            self.save_application_periods()
            
            logger.info(f"✅ Период заявок создан: {name}")
            return period
            
        except Exception as e:
            logger.error(f"Ошибка создания периода заявок: {e}")
            return None

    def update_application_period(self, period_id: str, name: str = None, 
                                start_date: str = None, end_date: str = None,
                                description: str = None, is_active: bool = None) -> bool:
        """Обновляет период подачи заявок"""
        try:
            if period_id not in self.application_periods:
                return False
            
            period = self.application_periods[period_id]
            
            if name is not None:
                period.name = name
            if start_date is not None:
                period.start_date = datetime.fromisoformat(start_date)
            if end_date is not None:
                period.end_date = datetime.fromisoformat(end_date)
            if description is not None:
                period.description = description
            if is_active is not None:
                period.is_active = is_active
            
            self.save_application_periods()
            logger.info(f"✅ Период заявок обновлен: {period_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления периода заявок: {e}")
            return False

    def delete_application_period(self, period_id: str) -> bool:
        """Удаляет период подачи заявок"""
        try:
            if period_id not in self.application_periods:
                return False
            
            del self.application_periods[period_id]
            self.save_application_periods()
            
            logger.info(f"✅ Период заявок удален: {period_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления периода заявок: {e}")
            return False

    def _calculate_next_send(self, schedule: NotificationSchedule) -> Optional[datetime]:
        """Вычисляет время следующей отправки"""
        now = datetime.now()
        
        if schedule.schedule_type == ScheduleType.ONCE:
            # Одноразово - отправляем в указанное время
            send_time = schedule.schedule_config.get('send_time')
            if send_time:
                try:
                    return datetime.fromisoformat(send_time)
                except:
                    return now + timedelta(minutes=1)
            return now + timedelta(minutes=1)
        
        elif schedule.schedule_type == ScheduleType.DAILY:
            # Ежедневно в указанное время
            hour = schedule.schedule_config.get('hour', 9)
            minute = schedule.schedule_config.get('minute', 0)
            
            next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_send <= now:
                next_send += timedelta(days=1)
            
            return next_send
        
        elif schedule.schedule_type == ScheduleType.WEEKLY:
            # Еженедельно в указанный день недели
            weekday = schedule.schedule_config.get('weekday', 0)  # 0 = понедельник
            hour = schedule.schedule_config.get('hour', 9)
            minute = schedule.schedule_config.get('minute', 0)
            
            days_ahead = weekday - now.weekday()
            if days_ahead <= 0:  # Если день уже прошел на этой неделе
                days_ahead += 7
            
            next_send = now + timedelta(days=days_ahead)
            next_send = next_send.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            return next_send
        
        elif schedule.schedule_type == ScheduleType.MONTHLY:
            # Ежемесячно в указанный день месяца
            day = schedule.schedule_config.get('day', 1)
            hour = schedule.schedule_config.get('hour', 9)
            minute = schedule.schedule_config.get('minute', 0)
            
            # Следующий месяц
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=day, hour=hour, minute=minute, second=0, microsecond=0)
            else:
                next_month = now.replace(month=now.month + 1, day=day, hour=hour, minute=minute, second=0, microsecond=0)
            
            # Если день не существует в месяце, берем последний день
            try:
                return next_month
            except ValueError:
                if now.month == 12:
                    next_month = now.replace(year=now.year + 1, month=1, day=1, hour=hour, minute=minute, second=0, microsecond=0)
                else:
                    next_month = now.replace(month=now.month + 1, day=1, hour=hour, minute=minute, second=0, microsecond=0)
                
                # Находим последний день месяца
                while True:
                    try:
                        next_month = next_month.replace(day=next_month.day + 1)
                    except ValueError:
                        next_month = next_month.replace(day=next_month.day - 1)
                        break
                
                return next_month
        
        return None

    def check_scheduled_notifications(self):
        """Проверяет и отправляет запланированные уведомления"""
        now = datetime.now()
        
        for schedule in self.notification_schedules.values():
            if not schedule.is_active:
                continue
            
            if schedule.next_send and schedule.next_send <= now:
                # Время отправки наступило
                self.create_notification(
                    type=schedule.type,
                    title=schedule.title,
                    message=schedule.message,
                    expires_in_hours=24
                )
                
                # Обновляем время последней отправки
                schedule.last_sent = now
                
                # Вычисляем следующее время отправки
                if schedule.schedule_type != ScheduleType.ONCE:
                    schedule.next_send = self._calculate_next_send(schedule)
                else:
                    schedule.is_active = False  # Одноразовое уведомление
                
                logger.info(f"📤 Отправлено запланированное уведомление: {schedule.name}")
        
        self.save_data()

# Глобальный экземпляр менеджера уведомлений
notification_manager = NotificationManager()

# Запускаем фоновый процесс
notification_manager.start_worker()
