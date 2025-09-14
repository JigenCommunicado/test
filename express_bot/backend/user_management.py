#!/usr/bin/env python3
"""
Модуль управления пользователями
Система ролей, авторизации и прав доступа
"""

import os
import json
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
from threading import Lock

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """Роли пользователей"""
    ADMIN = "admin"           # Администратор - полный доступ
    MANAGER = "manager"       # Менеджер - управление заявками
    USER = "user"            # Пользователь - создание заявок
    VIEWER = "viewer"        # Наблюдатель - только просмотр

class UserStatus(Enum):
    """Статусы пользователей"""
    ACTIVE = "active"         # Активный
    INACTIVE = "inactive"     # Неактивный
    BLOCKED = "blocked"       # Заблокирован
    PENDING = "pending"       # Ожидает активации

@dataclass
class User:
    """Модель пользователя"""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}

@dataclass
class UserSession:
    """Сессия пользователя"""
    token: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str

class UserManager:
    """Менеджер пользователей"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        self.lock = Lock()
        
        # Создаем директорию если не существует
        os.makedirs(data_dir, exist_ok=True)
        
        # Загружаем данные
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, UserSession] = {}
        self.load_users()
        self.load_sessions()
        
        # Создаем администратора по умолчанию
        self.create_default_admin()
        
        logger.info(f"👥 UserManager инициализирован. Пользователей: {len(self.users)}")
    
    def load_users(self):
        """Загружает пользователей из файла"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_data in data.get('users', []):
                        user = User(
                            id=user_data['id'],
                            username=user_data['username'],
                            email=user_data['email'],
                            full_name=user_data['full_name'],
                            role=UserRole(user_data['role']),
                            status=UserStatus(user_data['status']),
                            password_hash=user_data['password_hash'],
                            created_at=datetime.fromisoformat(user_data['created_at']),
                            last_login=datetime.fromisoformat(user_data['last_login']) if user_data.get('last_login') else None,
                            login_attempts=user_data.get('login_attempts', 0),
                            locked_until=datetime.fromisoformat(user_data['locked_until']) if user_data.get('locked_until') else None,
                            preferences=user_data.get('preferences', {})
                        )
                        self.users[user.id] = user
                logger.info(f"📖 Загружено {len(self.users)} пользователей")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки пользователей: {e}")
    
    def save_users(self):
        """Сохраняет пользователей в файл"""
        try:
            with self.lock:
                data = {
                    'users': []
                }
                for user in self.users.values():
                    user_data = asdict(user)
                    # Конвертируем datetime в строки
                    user_data['created_at'] = user.created_at.isoformat()
                    user_data['last_login'] = user.last_login.isoformat() if user.last_login else None
                    user_data['locked_until'] = user.locked_until.isoformat() if user.locked_until else None
                    user_data['role'] = user.role.value
                    user_data['status'] = user.status.value
                    data['users'].append(user_data)
                
                with open(self.users_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"💾 Сохранено {len(self.users)} пользователей")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения пользователей: {e}")
    
    def load_sessions(self):
        """Загружает сессии из файла"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_data in data.get('sessions', []):
                        session = UserSession(
                            token=session_data['token'],
                            user_id=session_data['user_id'],
                            created_at=datetime.fromisoformat(session_data['created_at']),
                            expires_at=datetime.fromisoformat(session_data['expires_at']),
                            ip_address=session_data['ip_address'],
                            user_agent=session_data['user_agent']
                        )
                        self.sessions[session.token] = session
                logger.info(f"📖 Загружено {len(self.sessions)} сессий")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки сессий: {e}")
    
    def save_sessions(self):
        """Сохраняет сессии в файл"""
        try:
            with self.lock:
                data = {
                    'sessions': []
                }
                for session in self.sessions.values():
                    session_data = asdict(session)
                    session_data['created_at'] = session.created_at.isoformat()
                    session_data['expires_at'] = session.expires_at.isoformat()
                    data['sessions'].append(session_data)
                
                with open(self.sessions_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения сессий: {e}")
    
    def create_default_admin(self):
        """Создает администратора по умолчанию"""
        admin_id = "admin"
        if admin_id not in self.users:
            admin_user = User(
                id=admin_id,
                username="admin",
                email="admin@smartapp.local",
                full_name="Администратор системы",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                password_hash=self.hash_password("admin123"),
                created_at=datetime.now()
            )
            self.users[admin_id] = admin_user
            self.save_users()
            logger.info("👑 Создан администратор по умолчанию (admin/admin123)")
    
    def hash_password(self, password: str) -> str:
        """Хеширует пароль"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Проверяет пароль"""
        try:
            salt, hash_part = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return password_hash_check.hex() == hash_part
        except:
            return False
    
    def create_user(self, username: str, email: str, full_name: str, password: str, role: UserRole = UserRole.USER) -> Optional[User]:
        """Создает нового пользователя"""
        try:
            # Проверяем уникальность
            for user in self.users.values():
                if user.username == username or user.email == email:
                    return None
            
            user_id = secrets.token_hex(8)
            user = User(
                id=user_id,
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                status=UserStatus.PENDING,
                password_hash=self.hash_password(password),
                created_at=datetime.now()
            )
            
            self.users[user_id] = user
            self.save_users()
            logger.info(f"👤 Создан пользователь: {username} ({role.value})")
            return user
        except Exception as e:
            logger.error(f"❌ Ошибка создания пользователя: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str, ip_address: str = "", user_agent: str = "") -> Optional[UserSession]:
        """Аутентификация пользователя"""
        try:
            # Находим пользователя
            user = None
            for u in self.users.values():
                if u.username == username or u.email == username:
                    user = u
                    break
            
            if not user:
                return None
            
            # Проверяем статус
            if user.status != UserStatus.ACTIVE:
                return None
            
            # Проверяем блокировку
            if user.locked_until and user.locked_until > datetime.now():
                return None
            
            # Проверяем пароль
            if not self.verify_password(password, user.password_hash):
                # Увеличиваем счетчик попыток
                user.login_attempts += 1
                if user.login_attempts >= 5:
                    user.locked_until = datetime.now() + timedelta(minutes=30)
                    logger.warning(f"🔒 Пользователь {username} заблокирован на 30 минут")
                self.save_users()
                return None
            
            # Сбрасываем счетчик попыток
            user.login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now()
            self.save_users()
            
            # Создаем сессию
            token = secrets.token_urlsafe(32)
            session = UserSession(
                token=token,
                user_id=user.id,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.sessions[token] = session
            self.save_sessions()
            
            logger.info(f"✅ Пользователь {username} успешно авторизован")
            return session
            
        except Exception as e:
            logger.error(f"❌ Ошибка аутентификации: {e}")
            return None
    
    def get_user_by_token(self, token: str) -> Optional[User]:
        """Получает пользователя по токену"""
        try:
            session = self.sessions.get(token)
            if not session:
                return None
            
            # Проверяем срок действия
            if session.expires_at < datetime.now():
                del self.sessions[token]
                self.save_sessions()
                return None
            
            return self.users.get(session.user_id)
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя по токену: {e}")
            return None
    
    def logout_user(self, token: str) -> bool:
        """Выход пользователя"""
        try:
            if token in self.sessions:
                del self.sessions[token]
                self.save_sessions()
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка выхода: {e}")
            return False
    
    def get_user_permissions(self, user: User) -> List[str]:
        """Получает права пользователя"""
        permissions = []
        
        if user.role == UserRole.ADMIN:
            permissions = [
                "users.create", "users.read", "users.update", "users.delete",
                "applications.create", "applications.read", "applications.update", "applications.delete",
                "reports.read", "settings.read", "settings.update"
            ]
        elif user.role == UserRole.MANAGER:
            permissions = [
                "applications.create", "applications.read", "applications.update",
                "reports.read"
            ]
        elif user.role == UserRole.USER:
            permissions = [
                "applications.create", "applications.read"
            ]
        elif user.role == UserRole.VIEWER:
            permissions = [
                "applications.read", "reports.read"
            ]
        
        return permissions
    
    def has_permission(self, user: User, permission: str) -> bool:
        """Проверяет права пользователя"""
        return permission in self.get_user_permissions(user)
    
    def get_all_users(self) -> List[User]:
        """Получает всех пользователей"""
        return list(self.users.values())
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Обновляет пользователя"""
        try:
            if user_id not in self.users:
                return False
            
            user = self.users[user_id]
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.save_users()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка обновления пользователя: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Удаляет пользователя"""
        try:
            if user_id not in self.users:
                return False
            
            # Нельзя удалить администратора
            if self.users[user_id].role == UserRole.ADMIN:
                return False
            
            del self.users[user_id]
            self.save_users()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка удаления пользователя: {e}")
            return False

# Глобальный экземпляр менеджера пользователей
user_manager = UserManager()

def test_user_management():
    """Тестирование системы пользователей"""
    print("🧪 Тестирование системы пользователей...")
    
    # Создаем тестового пользователя
    user = user_manager.create_user(
        username="testuser",
        email="test@example.com",
        full_name="Тестовый Пользователь",
        password="test123",
        role=UserRole.USER
    )
    
    if user:
        print(f"✅ Пользователь создан: {user.username}")
        
        # Тестируем аутентификацию
        session = user_manager.authenticate_user("testuser", "test123")
        if session:
            print(f"✅ Аутентификация успешна: {session.token[:10]}...")
            
            # Получаем пользователя по токену
            user_by_token = user_manager.get_user_by_token(session.token)
            if user_by_token:
                print(f"✅ Пользователь получен по токену: {user_by_token.full_name}")
                
                # Проверяем права
                permissions = user_manager.get_user_permissions(user_by_token)
                print(f"✅ Права пользователя: {permissions}")
            
            # Выход
            if user_manager.logout_user(session.token):
                print("✅ Выход выполнен")
        else:
            print("❌ Ошибка аутентификации")
    else:
        print("❌ Ошибка создания пользователя")
    
    print("🎉 Тест завершен!")

if __name__ == "__main__":
    test_user_management()


