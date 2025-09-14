"""
Комплексная система тестирования Express SmartApp
Включает unit тесты, integration тесты и автоматическое тестирование
"""

import unittest
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Настройка логирования для тестов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestConfig:
    """Конфигурация для тестов"""
    BASE_URL = "http://localhost:5002"
    STATIC_URL = "http://localhost:8080"
    TEST_USER_ID = "test_user_123"
    TEST_CHAT_ID = "test_chat_456"

class APITestCase(unittest.TestCase):
    """Базовый класс для API тестов"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.base_url = TestConfig.BASE_URL
        self.static_url = TestConfig.STATIC_URL
        self.session = requests.Session()
        self.auth_token = None
        self._login()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.session.close()
    
    def _login(self):
        """Авторизация для тестов"""
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.auth_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
        except Exception as e:
            logger.warning(f"Failed to login for tests: {e}")
            # Для некоторых тестов авторизация может быть не нужна
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> Dict:
        """Выполнение HTTP запроса"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            self.assertEqual(response.status_code, expected_status, 
                           f"Expected status {expected_status}, got {response.status_code}")
            
            return response.json() if response.content else {}
            
        except requests.exceptions.ConnectionError:
            self.fail(f"Could not connect to {url}. Is the server running?")
        except json.JSONDecodeError:
            self.fail(f"Invalid JSON response from {url}")

class HealthCheckTests(APITestCase):
    """Тесты проверки здоровья системы"""
    
    def test_health_endpoint(self):
        """Тест endpoint /health"""
        response = self.make_request("GET", "/health")
        self.assertIn("status", response)
        self.assertEqual(response["status"], "ok")
    
    def test_static_server_health(self):
        """Тест статического сервера"""
        try:
            response = self.session.get(f"{self.static_url}/")
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.fail("Static server is not running")

class ExcelIntegrationTests(APITestCase):
    """Тесты Excel интеграции"""
    
    def test_statistics_endpoint(self):
        """Тест получения статистики"""
        response = self.make_request("GET", "/api/statistics")
        self.assertIn("statistics", response)
        self.assertIsInstance(response["statistics"], dict)
    
    def test_application_creation(self):
        """Тест создания заявки"""
        application_data = {
            "user_id": TestConfig.TEST_USER_ID,
            "location": "Москва",
            "oke": "ОКЭ 1",
            "date": "2025-09-20",
            "position": "БП",
            "fio": "Тест Тест Тестович",
            "tab_num": "123456",
            "direction": "Санкт-Петербург",
            "wishes": "Тестовая заявка"
        }
        
        response = self.make_request("POST", "/api/application", application_data)
        self.assertTrue(response.get("success", False))
        self.assertIn("application_id", response)

class UserManagementTests(APITestCase):
    """Тесты управления пользователями"""
    
    def test_user_authentication(self):
        """Тест аутентификации пользователя"""
        # Здесь можно добавить тесты аутентификации
        pass
    
    def test_user_permissions(self):
        """Тест прав доступа пользователей"""
        # Здесь можно добавить тесты прав доступа
        pass

class NotificationTests(APITestCase):
    """Тесты системы уведомлений"""
    
    def test_notification_creation(self):
        """Тест создания уведомления"""
        notification_data = {
            "title": "Тестовое уведомление",
            "message": "Это тестовое уведомление",
            "type": "system_announcement",
            "target_audience": "all"
        }
        
        response = self.make_request("POST", "/api/notifications/create", notification_data)
        self.assertTrue(response.get("success", False))
    
    def test_notification_schedules(self):
        """Тест расписаний уведомлений"""
        response = self.make_request("GET", "/api/notifications/schedules")
        self.assertIn("schedules", response)
        self.assertIsInstance(response["schedules"], list)

class ExpressIntegrationTests(APITestCase):
    """Тесты интеграции с Express мессенджером"""
    
    def test_express_webhook_endpoint(self):
        """Тест webhook endpoint"""
        # Тест доступности endpoint
        response = self.make_request("POST", "/webhook/express", {}, 401)  # Ожидаем 401 из-за неверной подписи
        self.assertIn("error", response)
    
    def test_express_subscription(self):
        """Тест подписки на уведомления Express"""
        subscription_data = {
            "user_id": TestConfig.TEST_USER_ID,
            "chat_id": TestConfig.TEST_CHAT_ID,
            "preferences": {}
        }
        
        response = self.make_request("POST", "/api/express/subscribe", subscription_data)
        self.assertTrue(response.get("success", False))

class PerformanceTests(APITestCase):
    """Тесты производительности"""
    
    def test_response_time(self):
        """Тест времени ответа API"""
        start_time = time.time()
        self.make_request("GET", "/health")
        response_time = time.time() - start_time
        
        self.assertLess(response_time, 1.0, f"Response time too slow: {response_time:.2f}s")
    
    def test_concurrent_requests(self):
        """Тест одновременных запросов"""
        import threading
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = self.make_request("GET", "/health")
                results.append(response)
            except Exception as e:
                errors.append(str(e))
        
        # Создаем 10 одновременных запросов
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()
        
        self.assertEqual(len(errors), 0, f"Errors in concurrent requests: {errors}")
        self.assertEqual(len(results), 10, "Not all requests completed")

class FrontendTests(unittest.TestCase):
    """Тесты фронтенда"""
    
    def setUp(self):
        self.static_url = TestConfig.STATIC_URL
        self.session = requests.Session()
    
    def test_main_pages_load(self):
        """Тест загрузки основных страниц"""
        pages = [
            "/index.html",
            "/flight_booking_ui.html",
            "/mobile_booking_ui.html",
            "/admin_panel.html",
            "/application_periods.html",
            "/search_interface.html",
            "/notifications.html"
        ]
        
        for page in pages:
            with self.subTest(page=page):
                try:
                    response = self.session.get(f"{self.static_url}{page}")
                    self.assertEqual(response.status_code, 200, f"Page {page} failed to load")
                except requests.exceptions.ConnectionError:
                    self.fail(f"Could not connect to static server for page {page}")
    
    def test_simple_test_page(self):
        """Тест тестовой страницы"""
        try:
            response = self.session.get(f"{self.static_url}/simple_test_page.html")
            self.assertEqual(response.status_code, 200)
            # Устанавливаем правильную кодировку
            response.encoding = 'utf-8'
            self.assertIn("Простое тестирование", response.text)
        except requests.exceptions.ConnectionError:
            self.fail("Could not connect to static server for test page")

class IntegrationTests(unittest.TestCase):
    """Интеграционные тесты"""
    
    def test_full_application_flow(self):
        """Тест полного потока подачи заявки"""
        # 1. Проверяем доступность системы
        health_response = requests.get(f"{TestConfig.BASE_URL}/health")
        self.assertEqual(health_response.status_code, 200)
        
        # 2. Создаем заявку
        application_data = {
            "user_id": TestConfig.TEST_USER_ID,
            "location": "Москва",
            "oke": "ОКЭ 1",
            "date": "2025-09-20",
            "position": "БП",
            "fio": "Интеграционный Тест",
            "tab_num": "999999",
            "direction": "Санкт-Петербург",
            "wishes": "Интеграционный тест заявки"
        }
        
        app_response = requests.post(f"{TestConfig.BASE_URL}/api/application", json=application_data)
        self.assertEqual(app_response.status_code, 200)
        
        # 3. Проверяем, что заявка появилась в статистике
        stats_response = requests.get(f"{TestConfig.BASE_URL}/api/statistics")
        self.assertEqual(stats_response.status_code, 200)
        
        # 4. Проверяем доступность админ панели
        admin_response = requests.get(f"{TestConfig.STATIC_URL}/admin_panel.html")
        self.assertEqual(admin_response.status_code, 200)

class TestRunner:
    """Запускатель тестов"""
    
    def __init__(self):
        self.test_suites = [
            HealthCheckTests,
            ExcelIntegrationTests,
            UserManagementTests,
            NotificationTests,
            ExpressIntegrationTests,
            PerformanceTests,
            FrontendTests,
            IntegrationTests
        ]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "test_results": [],
            "start_time": datetime.now(),
            "end_time": None
        }
        
        logger.info("🚀 Запуск тестов Express SmartApp...")
        
        for test_suite in self.test_suites:
            suite_name = test_suite.__name__
            logger.info(f"📋 Запуск тестов: {suite_name}")
            
            suite = unittest.TestLoader().loadTestsFromTestCase(test_suite)
            runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
            result = runner.run(suite)
            
            suite_result = {
                "suite": suite_name,
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
                "success": result.wasSuccessful()
            }
            
            results["test_results"].append(suite_result)
            results["total_tests"] += result.testsRun
            results["passed"] += result.testsRun - len(result.failures) - len(result.errors)
            results["failed"] += len(result.failures)
            results["errors"] += len(result.errors)
            
            status = "✅ PASSED" if result.wasSuccessful() else "❌ FAILED"
            logger.info(f"   {status}: {result.testsRun} тестов, {len(result.failures)} ошибок, {len(result.errors)} исключений")
        
        results["end_time"] = datetime.now()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()
        
        # Вывод итогов
        logger.info("🎯 Результаты тестирования:")
        logger.info(f"   Всего тестов: {results['total_tests']}")
        logger.info(f"   ✅ Пройдено: {results['passed']}")
        logger.info(f"   ❌ Провалено: {results['failed']}")
        logger.info(f"   ⚠️  Ошибок: {results['errors']}")
        logger.info(f"   ⏱️  Время выполнения: {results['duration']:.2f}s")
        
        return results
    
    def run_specific_tests(self, test_names: List[str]) -> Dict[str, Any]:
        """Запуск конкретных тестов"""
        # Реализация запуска конкретных тестов
        pass
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Генерация отчета о тестировании"""
        report = f"""
# 📊 Отчет о тестировании Express SmartApp

**Время выполнения:** {results['start_time'].strftime('%Y-%m-%d %H:%M:%S')} - {results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}
**Длительность:** {results['duration']:.2f} секунд

## 📈 Общая статистика
- **Всего тестов:** {results['total_tests']}
- **✅ Пройдено:** {results['passed']}
- **❌ Провалено:** {results['failed']}
- **⚠️  Ошибок:** {results['errors']}
- **Процент успеха:** {(results['passed'] / max(results['total_tests'], 1) * 100):.1f}%

## 📋 Результаты по модулям
"""
        
        for test_result in results['test_results']:
            status = "✅" if test_result['success'] else "❌"
            report += f"- **{test_result['suite']}:** {status} {test_result['tests_run']} тестов"
            if test_result['failures'] > 0 or test_result['errors'] > 0:
                report += f" ({test_result['failures']} ошибок, {test_result['errors']} исключений)"
            report += "\n"
        
        return report

def run_tests():
    """Функция для запуска тестов"""
    runner = TestRunner()
    results = runner.run_all_tests()
    
    # Генерируем отчет
    report = runner.generate_report(results)
    print(report)
    
    return results

if __name__ == "__main__":
    run_tests()

