// Service Worker для push-уведомлений
const CACHE_NAME = 'smartapp-v1';
const SMARTAPP_URL = 'http://localhost:5002';

// Установка Service Worker
self.addEventListener('install', function(event) {
    console.log('Service Worker: Установка');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Service Worker: Кеширование файлов');
                return cache.addAll([
                    '/',
                    '/notifications.html',
                    '/admin_panel.html',
                    '/search_interface.html'
                ]);
            })
    );
});

// Активация Service Worker
self.addEventListener('activate', function(event) {
    console.log('Service Worker: Активация');
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Service Worker: Удаление старого кеша', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Обработка fetch запросов
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Возвращаем кешированную версию или делаем запрос
                return response || fetch(event.request);
            }
        )
    );
});

// Обработка push-уведомлений
self.addEventListener('push', function(event) {
    console.log('Service Worker: Получено push-уведомление');
    
    let notificationData = {
        title: 'SmartApp',
        body: 'Новое уведомление',
        icon: '/icon-192x192.png',
        badge: '/badge-72x72.png',
        tag: 'smartapp-notification',
        data: {
            url: '/notifications.html'
        }
    };

    if (event.data) {
        try {
            const data = event.data.json();
            notificationData = {
                title: data.title || 'SmartApp',
                body: data.message || 'Новое уведомление',
                icon: data.icon || '/icon-192x192.png',
                badge: data.badge || '/badge-72x72.png',
                tag: data.tag || 'smartapp-notification',
                data: {
                    url: data.url || '/notifications.html',
                    notificationId: data.notificationId
                }
            };
        } catch (e) {
            console.error('Ошибка парсинга push-данных:', e);
        }
    }

    event.waitUntil(
        self.registration.showNotification(notificationData.title, notificationData)
    );
});

// Обработка клика по уведомлению
self.addEventListener('notificationclick', function(event) {
    console.log('Service Worker: Клик по уведомлению');
    
    event.notification.close();
    
    const urlToOpen = event.notification.data.url || '/notifications.html';
    
    event.waitUntil(
        clients.matchAll({
            type: 'window',
            includeUncontrolled: true
        }).then(function(clientList) {
            // Ищем открытую вкладку с нашим приложением
            for (let i = 0; i < clientList.length; i++) {
                const client = clientList[i];
                if (client.url.includes('localhost:8080') && 'focus' in client) {
                    client.focus();
                    client.navigate(urlToOpen);
                    return;
                }
            }
            
            // Если нет открытых вкладок, открываем новую
            if (clients.openWindow) {
                return clients.openWindow(urlToOpen);
            }
        })
    );
});

// Обработка закрытия уведомления
self.addEventListener('notificationclose', function(event) {
    console.log('Service Worker: Уведомление закрыто');
    
    // Можно отправить аналитику о том, что уведомление было закрыто
    if (event.notification.data && event.notification.data.notificationId) {
        // Отправляем информацию о закрытии уведомления на сервер
        fetch(`${SMARTAPP_URL}/api/notifications/${event.notification.data.notificationId}/close`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).catch(err => console.error('Ошибка отправки статистики:', err));
    }
});

// Обработка сообщений от основного потока
self.addEventListener('message', function(event) {
    console.log('Service Worker: Получено сообщение', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({
            version: CACHE_NAME
        });
    }
});

// Фоновая синхронизация
self.addEventListener('sync', function(event) {
    console.log('Service Worker: Фоновая синхронизация', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

// Выполнение фоновой синхронизации
function doBackgroundSync() {
    return fetch(`${SMARTAPP_URL}/api/notifications`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Ошибка синхронизации');
    }).then(data => {
        console.log('Service Worker: Синхронизация завершена', data);
        
        // Уведомляем все открытые вкладки о новых данных
        return clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'NOTIFICATION_UPDATE',
                    data: data
                });
            });
        });
    }).catch(error => {
        console.error('Service Worker: Ошибка синхронизации', error);
    });
}

// Обработка ошибок
self.addEventListener('error', function(event) {
    console.error('Service Worker: Ошибка', event.error);
});

self.addEventListener('unhandledrejection', function(event) {
    console.error('Service Worker: Необработанное отклонение промиса', event.reason);
});


