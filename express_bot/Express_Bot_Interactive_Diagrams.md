# 🎨 Express Bot - Интерактивные диаграммы

## 🚀 Системная архитектура

### Общая схема системы

```mermaid
graph TB
    subgraph "🌐 Express Ecosystem"
        A[Express Messenger<br/>📱 Пользовательский интерфейс]
        B[WebView Container<br/>🖥️ Контейнер приложения]
        C[BotX API Server<br/>🔗 API сервер Express]
        D[Express Users<br/>👥 Пользователи системы]
    end
    
    subgraph "📱 SmartApp Frontend"
        E[SPA Application<br/>⚡ Одностраничное приложение]
        F[Form Interface<br/>📝 Интерфейс форм]
        G[Calendar Widget<br/>📅 Календарь]
        H[Location Selector<br/>📍 Выбор локаций]
        I[Data Validator<br/>✅ Валидация данных]
    end
    
    subgraph "🤖 SmartApp Backend"
        J[Express Bot API<br/>🔌 API бота]
        K[Application Processor<br/>⚙️ Обработчик заявок]
        L[User Manager<br/>👤 Управление пользователями]
        M[Statistics Engine<br/>📊 Аналитика]
        N[BotX Integration<br/>🔗 Интеграция с Express]
    end
    
    subgraph "🔧 Core System"
        O[Flask API Server<br/>🌐 Основной API]
        P[Database Layer<br/>🗄️ Слой базы данных]
        Q[File Storage<br/>📁 Файловое хранилище]
        R[Notification System<br/>🔔 Система уведомлений]
        S[Session Manager<br/>🔐 Управление сессиями]
    end
    
    subgraph "🌍 External Services"
        T[Cloudflare Tunnel<br/>🌐 Публичный доступ]
        U[Webhook Handler<br/>🪝 Обработчик webhook]
        V[Telegram Bot<br/>📱 Telegram бот]
        W[Message Queue<br/>📬 Очередь сообщений]
    end
    
    %% Express Platform Connections
    A -.->|"Открывает SmartApp"| B
    A -.->|"Управляет пользователями"| C
    A -.->|"Взаимодействует"| D
    B -.->|"Загружает SPA"| E
    C -.->|"API интеграция"| N
    
    %% Frontend Connections
    E -.->|"Содержит"| F
    E -.->|"Содержит"| G
    E -.->|"Содержит"| H
    E -.->|"Содержит"| I
    F -.->|"Отправляет данные"| J
    G -.->|"Отправляет данные"| J
    H -.->|"Отправляет данные"| J
    I -.->|"Валидирует данные"| J
    
    %% Backend Connections
    J -.->|"Обрабатывает"| K
    J -.->|"Управляет"| L
    J -.->|"Генерирует"| M
    J -.->|"Интегрирует"| N
    K -.->|"Сохраняет данные"| O
    L -.->|"Управляет пользователями"| O
    M -.->|"Получает данные"| O
    N -.->|"Синхронизирует"| C
    
    %% Core System Connections
    O -.->|"Сохраняет"| P
    O -.->|"Хранит файлы"| Q
    O -.->|"Отправляет уведомления"| R
    O -.->|"Управляет сессиями"| S
    P -.->|"Хранит"| D
    Q -.->|"Хранит файлы"| D
    R -.->|"Обрабатывает"| W
    S -.->|"Управляет"| D
    
    %% External Services Connections
    T -.->|"Проксирует"| U
    U -.->|"Обрабатывает события"| J
    V -.->|"Синхронизирует"| O
    W -.->|"Обрабатывает"| R
    
    %% Styling
    style A fill:#e1f5fe,stroke:#01579b,stroke-width:3px,color:#000
    style E fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style J fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px,color:#000
    style O fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style T fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style V fill:#f1f8e9,stroke:#33691e,stroke-width:2px,color:#000
```

---

## 🔄 Жизненный цикл заявки

### Полный процесс от создания до обработки

```mermaid
flowchart TD
    A[👤 Пользователь открывает SmartApp] --> B[🌐 WebView загружает SPA]
    B --> C[📱 Отображение главного меню]
    C --> D[📝 Выбор "Подать заявку"]
    D --> E[🏢 Выбор локации]
    E --> F[🏭 Выбор ОКЭ]
    F --> G[📅 Выбор даты через календарь]
    G --> H[👔 Выбор должности]
    H --> I[✍️ Ввод ФИО и табельного номера]
    I --> J[✈️ Выбор направления]
    J --> K[💭 Ввод пожеланий]
    K --> L[✅ Подтверждение данных]
    L --> M[📤 Отправка заявки]
    M --> N[🤖 Обработка через Bot API]
    N --> O[🔗 Интеграция с BotX API]
    O --> P[💾 Сохранение в базе данных]
    P --> Q[📧 Отправка уведомления]
    Q --> R[✅ Подтверждение пользователю]
    
    %% Обработка ошибок
    M --> S{❌ Ошибка отправки?}
    S -->|Да| T[🔄 Повторная попытка]
    S -->|Нет| N
    T --> U{🔄 Максимум попыток?}
    U -->|Нет| M
    U -->|Да| V[❌ Уведомление об ошибке]
    
    %% Стилизация
    style A fill:#e3f2fd,stroke:#01579b,stroke-width:2px
    style M fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    style P fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style R fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style S fill:#ffebee,stroke:#c62828,stroke-width:2px
    style V fill:#ffebee,stroke:#c62828,stroke-width:2px
```

---

## 📊 Структура данных

### Модель данных заявки

```mermaid
erDiagram
    APPLICATION {
        string id PK "Уникальный ID заявки"
        string user_id FK "ID пользователя"
        string location "Локация"
        string oke "ОКЭ"
        date flight_date "Дата вылета"
        string position "Должность"
        string fio "ФИО"
        string tab_num "Табельный номер"
        string direction "Направление"
        text wishes "Пожелания"
        string status "Статус заявки"
        datetime created_at "Дата создания"
        datetime updated_at "Дата обновления"
    }
    
    USER {
        string id PK "Уникальный ID пользователя"
        string express_id "ID в Express"
        string name "Имя пользователя"
        string email "Email"
        string phone "Телефон"
        string department "Отдел"
        datetime last_active "Последняя активность"
        datetime created_at "Дата регистрации"
    }
    
    LOCATION {
        string id PK "Уникальный ID локации"
        string name "Название локации"
        string code "Код локации"
        boolean active "Активна ли локация"
    }
    
    OKE {
        string id PK "Уникальный ID ОКЭ"
        string name "Название ОКЭ"
        string location_id FK "ID локации"
        boolean active "Активна ли ОКЭ"
    }
    
    APPLICATION_PERIOD {
        string id PK "Уникальный ID периода"
        string name "Название периода"
        date start_date "Дата начала"
        date end_date "Дата окончания"
        boolean active "Активен ли период"
    }
    
    NOTIFICATION {
        string id PK "Уникальный ID уведомления"
        string user_id FK "ID пользователя"
        string application_id FK "ID заявки"
        string type "Тип уведомления"
        string message "Текст уведомления"
        boolean sent "Отправлено ли"
        datetime created_at "Дата создания"
    }
    
    %% Связи
    APPLICATION ||--|| USER : "принадлежит"
    APPLICATION ||--|| LOCATION : "содержит"
    APPLICATION ||--|| OKE : "содержит"
    OKE ||--|| LOCATION : "принадлежит"
    APPLICATION ||--o{ NOTIFICATION : "генерирует"
    USER ||--o{ NOTIFICATION : "получает"
```

---

## 🔧 Техническая архитектура

### Слоистая архитектура

```mermaid
graph TB
    subgraph "🎨 Presentation Layer"
        A[WebView Container]
        B[SPA Frontend]
        C[UI Components]
        D[Form Validators]
    end
    
    subgraph "🧠 Business Logic Layer"
        E[Bot API Controller]
        F[Application Service]
        G[User Service]
        H[Statistics Service]
        I[Notification Service]
    end
    
    subgraph "🔗 Integration Layer"
        J[BotX API Client]
        K[Webhook Handler]
        L[Message Queue]
        M[External API Client]
    end
    
    subgraph "💾 Data Access Layer"
        N[Database Repository]
        O[File Storage]
        P[Cache Manager]
        Q[Session Store]
    end
    
    subgraph "🗄️ Data Layer"
        R[PostgreSQL Database]
        S[File System]
        T[Redis Cache]
        U[Session Storage]
    end
    
    %% Connections
    A --> B
    B --> C
    C --> D
    D --> E
    
    E --> F
    E --> G
    E --> H
    E --> I
    
    F --> J
    G --> K
    H --> L
    I --> M
    
    J --> N
    K --> O
    L --> P
    M --> Q
    
    N --> R
    O --> S
    P --> T
    Q --> U
    
    %% Styling
    style A fill:#e3f2fd,stroke:#01579b,stroke-width:2px
    style E fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    style J fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style N fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style R fill:#fce4ec,stroke:#880e4f,stroke-width:2px
```

---

## 📈 Производительность и мониторинг

### Метрики системы

```mermaid
graph LR
    subgraph "📊 System Metrics"
        A[Performance Metrics]
        B[Availability Metrics]
        C[Error Metrics]
        D[Usage Metrics]
    end
    
    subgraph "⚡ Performance"
        A1[Response Time<br/>⏱️ < 200ms]
        A2[Throughput<br/>📈 1000 req/min]
        A3[Resource Usage<br/>💻 CPU < 70%]
        A4[Memory Usage<br/>🧠 RAM < 80%]
    end
    
    subgraph "✅ Availability"
        B1[Uptime<br/>⏰ 99.9%]
        B2[Health Checks<br/>💚 All Green]
        B3[Service Status<br/>🟢 Online]
        B4[Recovery Time<br/>🔄 < 5min]
    end
    
    subgraph "❌ Error Metrics"
        C1[Error Rate<br/>📉 < 1%]
        C2[Exception Count<br/>⚠️ < 10/hour]
        C3[Failed Requests<br/>🚫 < 5%]
        C4[Timeout Rate<br/>⏰ < 0.1%]
    end
    
    subgraph "👥 Usage Metrics"
        D1[Active Users<br/>👤 500+]
        D2[API Calls<br/>📞 10k/day]
        D3[Data Volume<br/>📊 1GB/day]
        D4[Session Duration<br/>⏱️ 15min avg]
    end
    
    A --> A1
    A --> A2
    A --> A3
    A --> A4
    
    B --> B1
    B --> B2
    B --> B3
    B --> B4
    
    C --> C1
    C --> C2
    C --> C3
    C --> C4
    
    D --> D1
    D --> D2
    D --> D3
    D --> D4
    
    %% Styling
    style A fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    style B fill:#e3f2fd,stroke:#01579b,stroke-width:2px
    style C fill:#ffebee,stroke:#c62828,stroke-width:2px
    style D fill:#fff3e0,stroke:#e65100,stroke-width:2px
```

---

## 🔐 Безопасность

### Модель безопасности

```mermaid
graph TB
    subgraph "🛡️ Security Layers"
        A[Network Security]
        B[Application Security]
        C[Data Security]
        D[Access Control]
    end
    
    subgraph "🌐 Network Layer"
        A1[Firewall<br/>🔥 Block malicious traffic]
        A2[SSL/TLS<br/>🔒 Encrypt connections]
        A3[VPN<br/>🔐 Secure tunnels]
        A4[DDoS Protection<br/>🛡️ Mitigate attacks]
    end
    
    subgraph "🔧 Application Layer"
        B1[JWT Tokens<br/>🎫 Authentication]
        B2[CORS Policy<br/>🌐 Cross-origin control]
        B3[Input Validation<br/>✅ Data sanitization]
        B4[Rate Limiting<br/>⏱️ Request throttling]
    end
    
    subgraph "💾 Data Layer"
        C1[Encryption at Rest<br/>🔐 Encrypt stored data]
        C2[Encryption in Transit<br/>🚀 Encrypt network data]
        C3[Backup Security<br/>💾 Secure backups]
        C4[Data Anonymization<br/>👤 Privacy protection]
    end
    
    subgraph "🔑 Access Control"
        D1[Role-Based Access<br/>👥 RBAC system]
        D2[Multi-Factor Auth<br/>🔐 MFA required]
        D3[Session Management<br/>⏰ Secure sessions]
        D4[Audit Logging<br/>📝 Track all actions]
    end
    
    A --> A1
    A --> A2
    A --> A3
    A --> A4
    
    B --> B1
    B --> B2
    B --> B3
    B --> B4
    
    C --> C1
    C --> C2
    C --> C3
    C --> C4
    
    D --> D1
    D --> D2
    D --> D3
    D --> D4
    
    %% Styling
    style A fill:#e3f2fd,stroke:#01579b,stroke-width:2px
    style B fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    style C fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style D fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
```

---

## 🚀 Развертывание

### Схема развертывания

```mermaid
graph TB
    subgraph "🌐 Production Environment"
        A[Load Balancer<br/>⚖️ NGINX]
        B[CDN<br/>🌍 Cloudflare]
        C[Container Orchestrator<br/>🐳 Docker Swarm]
    end
    
    subgraph "📱 Frontend Services"
        D[Frontend Container 1<br/>📱 SPA Instance 1]
        E[Frontend Container 2<br/>📱 SPA Instance 2]
        F[Frontend Container 3<br/>📱 SPA Instance 3]
    end
    
    subgraph "🤖 Backend Services"
        G[Bot API Container 1<br/>🤖 Bot Instance 1]
        H[Bot API Container 2<br/>🤖 Bot Instance 2]
        I[Flask API Container 1<br/>🔧 API Instance 1]
        J[Flask API Container 2<br/>🔧 API Instance 2]
    end
    
    subgraph "💾 Data Services"
        K[Database Primary<br/>🗄️ PostgreSQL Master]
        L[Database Replica<br/>🗄️ PostgreSQL Slave]
        M[Cache Cluster<br/>⚡ Redis Cluster]
        N[File Storage<br/>📁 MinIO Cluster]
    end
    
    subgraph "🔍 Monitoring"
        O[Prometheus<br/>📊 Metrics Collection]
        P[Grafana<br/>📈 Dashboards]
        Q[ELK Stack<br/>📝 Logging]
        R[AlertManager<br/>🚨 Alerts]
    end
    
    %% Connections
    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    C --> G
    C --> H
    C --> I
    C --> J
    
    D --> G
    E --> G
    F --> H
    G --> I
    H --> J
    
    I --> K
    J --> L
    I --> M
    J --> N
    
    O --> P
    O --> Q
    O --> R
    
    %% Styling
    style A fill:#e3f2fd,stroke:#01579b,stroke-width:3px
    style C fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    style K fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style O fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
```

---

## 🏷️ Теги и категории

#diagrams #interactive #architecture #visualization #mermaid #system-design #express #bot #smartapp #frontend #backend #api #database #security #monitoring #deployment

---

*Создано: 2025-01-27*  
*Версия: 1.0*  
*Статус: ✅ Активный*



