# 🔗 Express Bot - Граф связей и зависимостей

## 📊 Центральный граф системы

```mermaid
graph TB
    subgraph "🌐 Express Platform"
        A[Express Messenger] 
        B[WebView Container]
        C[BotX API Server]
        D[Express Users]
    end
    
    subgraph "📱 SmartApp Frontend"
        E[SPA Application]
        F[Form Interface]
        G[Calendar Widget]
        H[Location Selector]
        I[Data Validator]
    end
    
    subgraph "🤖 SmartApp Backend"
        J[Express Bot API]
        K[Application Processor]
        L[User Manager]
        M[Statistics Engine]
        N[BotX Integration]
    end
    
    subgraph "🔧 Core System"
        O[Flask API Server]
        P[Database Layer]
        Q[File Storage]
        R[Notification System]
        S[Session Manager]
    end
    
    subgraph "🌍 External Services"
        T[Cloudflare Tunnel]
        U[Webhook Handler]
        V[Telegram Bot]
        W[Message Queue]
    end
    
    subgraph "📊 Data Flow"
        X[User Data]
        Y[Application Data]
        Z[Statistics Data]
        AA[Log Data]
    end
    
    %% Express Platform Connections
    A --> B
    A --> C
    A --> D
    B --> E
    C --> N
    
    %% Frontend Connections
    E --> F
    E --> G
    E --> H
    E --> I
    F --> J
    G --> J
    H --> J
    I --> J
    
    %% Backend Connections
    J --> K
    J --> L
    J --> M
    J --> N
    K --> O
    L --> O
    M --> O
    N --> C
    
    %% Core System Connections
    O --> P
    O --> Q
    O --> R
    O --> S
    P --> X
    P --> Y
    Q --> Y
    R --> W
    S --> X
    
    %% External Services Connections
    T --> U
    U --> J
    V --> O
    W --> R
    
    %% Data Flow Connections
    X --> L
    Y --> K
    Z --> M
    AA --> O
    
    %% Styling
    style A fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    style E fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style J fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    style O fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style T fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    style V fill:#f1f8e9,stroke:#33691e,stroke-width:2px
```

---

## 🔄 Потоки данных

### 1. Поток создания заявки

```mermaid
sequenceDiagram
    participant U as User
    participant W as WebView
    participant F as Frontend SPA
    participant B as Bot API
    participant E as BotX API
    participant C as Core System
    participant D as Database
    
    U->>W: Открывает SmartApp
    W->>F: Загружает SPA
    F->>U: Показывает форму
    U->>F: Заполняет данные
    F->>B: POST /api/smartapp/submit
    B->>E: Отправляет в BotX API
    E->>C: Обрабатывает заявку
    C->>D: Сохраняет данные
    D-->>C: Подтверждение
    C-->>E: Результат
    E-->>B: Ответ
    B-->>F: Статус заявки
    F-->>U: Уведомление
```

### 2. Поток получения статистики

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend SPA
    participant B as Bot API
    participant C as Core System
    participant D as Database
    
    U->>F: Запрашивает статистику
    F->>B: GET /api/smartapp/statistics
    B->>C: Запрос данных
    C->>D: SELECT статистика
    D-->>C: Данные
    C-->>B: Результат
    B-->>F: JSON статистика
    F-->>U: Отображает графики
```

---

## 🏗️ Архитектурные слои

### Слой представления (Presentation Layer)
- **Frontend SPA** - Пользовательский интерфейс
- **WebView Container** - Контейнер Express
- **Form Components** - Компоненты форм
- **UI Widgets** - Виджеты интерфейса

### Слой бизнес-логики (Business Logic Layer)
- **Bot API** - API для обработки запросов
- **Application Processor** - Обработчик заявок
- **User Manager** - Управление пользователями
- **Statistics Engine** - Аналитика

### Слой интеграции (Integration Layer)
- **BotX Integration** - Интеграция с Express
- **Webhook Handler** - Обработка webhook'ов
- **Message Queue** - Очередь сообщений
- **External APIs** - Внешние API

### Слой данных (Data Layer)
- **Database Layer** - Слой базы данных
- **File Storage** - Файловое хранилище
- **Cache Layer** - Кэширование
- **Session Storage** - Хранение сессий

---

## 🔗 Зависимости между компонентами

### Прямые зависимости

| Компонент | Зависит от | Тип зависимости |
|-----------|------------|-----------------|
| **Frontend SPA** | Bot API | HTTP API calls |
| **Bot API** | BotX API | HTTP integration |
| **Bot API** | Flask API | Fallback API |
| **Flask API** | Database | Data persistence |
| **Webhook Handler** | Bot API | Event processing |
| **Telegram Bot** | Flask API | Data synchronization |

### Обратные зависимости

| Компонент | Используется в | Назначение |
|-----------|----------------|------------|
| **Database** | Flask API | Хранение данных |
| **BotX API** | Bot API | Интеграция с Express |
| **Cloudflare Tunnel** | Webhook Handler | Публичный доступ |
| **Session Manager** | Bot API | Управление сессиями |

---

## 📊 Метрики и мониторинг

### Ключевые метрики

```mermaid
graph LR
    A[System Metrics] --> B[Performance]
    A --> C[Availability]
    A --> D[Errors]
    A --> E[Usage]
    
    B --> B1[Response Time]
    B --> B2[Throughput]
    B --> B3[Resource Usage]
    
    C --> C1[Uptime]
    C --> C2[Health Checks]
    C --> C3[Service Status]
    
    D --> D1[Error Rate]
    D --> D2[Exception Count]
    D --> D3[Failed Requests]
    
    E --> E1[Active Users]
    E --> E2[API Calls]
    E --> E3[Data Volume]
    
    style A fill:#e3f2fd
    style B fill:#e8f5e8
    style C fill:#fff3e0
    style D fill:#ffebee
    style E fill:#f3e5f5
```

### Мониторинг компонентов

| Компонент | Метрики | Алерты |
|-----------|---------|--------|
| **Frontend SPA** | Load time, Error rate | > 3s load, > 5% errors |
| **Bot API** | Response time, Success rate | > 1s response, < 95% success |
| **Flask API** | CPU usage, Memory usage | > 80% CPU, > 1GB RAM |
| **Database** | Query time, Connections | > 500ms query, > 80% connections |
| **BotX API** | Integration status | Connection failures |

---

## 🔧 Конфигурационные связи

### Переменные окружения

```bash
# Express Bot Configuration
EXPRESS_BOT_ID=00c46d64-1127-5a96-812d-3d8b27c58b99
EXPRESS_SECRET_KEY=a75b4cd97d9e88e543f077178b2d5a4f
EXPRESS_BOT_TOKEN=mock_bot_token

# API URLs
FLASK_API_URL=http://localhost:5002
EXPRESS_BOTX_URL=http://localhost:8080/api/botx
WEBHOOK_URL=https://comparing-doom-solving-royalty.trycloudflare.com/webhook

# Server Configuration
BOT_PORT=5006
LOG_LEVEL=INFO
SESSION_TIMEOUT=3600
```

### Конфигурационные файлы

| Файл | Назначение | Зависимости |
|------|------------|-------------|
| `express_bot_config.py` | Основная конфигурация | Environment variables |
| `express_smartapp_bot.py` | Bot API конфигурация | Bot config, Flask API |
| `express_smartapp_frontend.html` | Frontend конфигурация | Bot API endpoints |
| `manage_all.sh` | Скрипты управления | Все сервисы |

---

## 🚀 Развертывание и масштабирование

### Горизонтальное масштабирование

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[NGINX Load Balancer]
    end
    
    subgraph "Bot API Instances"
        B1[Bot API Instance 1]
        B2[Bot API Instance 2]
        B3[Bot API Instance 3]
    end
    
    subgraph "Flask API Instances"
        F1[Flask API Instance 1]
        F2[Flask API Instance 2]
    end
    
    subgraph "Database Cluster"
        DB1[Primary Database]
        DB2[Replica Database]
    end
    
    LB --> B1
    LB --> B2
    LB --> B3
    
    B1 --> F1
    B2 --> F1
    B3 --> F2
    
    F1 --> DB1
    F2 --> DB2
    
    DB1 --> DB2
    
    style LB fill:#e3f2fd
    style B1 fill:#e8f5e8
    style B2 fill:#e8f5e8
    style B3 fill:#e8f5e8
    style F1 fill:#fff3e0
    style F2 fill:#fff3e0
    style DB1 fill:#fce4ec
    style DB2 fill:#fce4ec
```

### Вертикальное масштабирование

| Ресурс | Текущее | Рекомендуемое | Максимальное |
|--------|---------|---------------|--------------|
| **CPU** | 2 cores | 4 cores | 8 cores |
| **RAM** | 4GB | 8GB | 16GB |
| **Storage** | 20GB | 50GB | 100GB |
| **Network** | 100Mbps | 1Gbps | 10Gbps |

---

## 🔐 Безопасность и изоляция

### Сетевая изоляция

```mermaid
graph TB
    subgraph "DMZ"
        A[Cloudflare Tunnel]
        B[Webhook Handler]
    end
    
    subgraph "Application Layer"
        C[Bot API]
        D[Frontend SPA]
    end
    
    subgraph "Internal Network"
        E[Flask API]
        F[Database]
        G[File Storage]
    end
    
    subgraph "External Services"
        H[Express Platform]
        I[Telegram API]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    E --> F
    E --> G
    C --> H
    E --> I
    
    style A fill:#ffebee
    style C fill:#e8f5e8
    style E fill:#fff3e0
    style H fill:#e3f2fd
```

### Уровни безопасности

1. **Сетевой уровень** - Firewall, VPN, SSL/TLS
2. **Прикладной уровень** - JWT токены, CORS, валидация
3. **Уровень данных** - Шифрование, резервное копирование
4. **Уровень доступа** - Аутентификация, авторизация

---

## 📈 Производительность и оптимизация

### Кэширование

```mermaid
graph LR
    A[User Request] --> B[CDN Cache]
    B --> C[Application Cache]
    C --> D[Database Cache]
    D --> E[Database]
    
    B --> F[Static Assets]
    C --> G[API Responses]
    D --> H[Query Results]
    
    style A fill:#e3f2fd
    style B fill:#e8f5e8
    style C fill:#fff3e0
    style D fill:#f3e5f5
    style E fill:#fce4ec
```

### Оптимизация запросов

| Операция | Текущее время | Оптимизированное | Улучшение |
|----------|---------------|------------------|-----------|
| **Загрузка SPA** | 2.5s | 0.8s | 68% |
| **API Response** | 500ms | 150ms | 70% |
| **Database Query** | 200ms | 50ms | 75% |
| **File Upload** | 1.2s | 0.4s | 67% |

---

## 🏷️ Теги и категории

#graph #connections #architecture #dependencies #dataflow #monitoring #scaling #security #performance #optimization #express #bot #smartapp #api #frontend #backend

---

*Создано: 2025-01-27*  
*Версия: 1.0*  
*Статус: ✅ Активный*



