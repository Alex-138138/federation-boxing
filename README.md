# Federation Boxing — Full Build 1.0

Полная тестовая сборка приложения Федерации бокса Иркутского округа.

## Быстрый запуск

```bash
git clone https://github.com/Alex-138138/federation-boxing.git
cd federation-boxing
bash install.sh
docker compose up --build
```

`install.sh` автоматически восстанавливает обычную структуру проекта из встроенного payload:
- `backend/`
- `frontend/`
- `nginx/`
- миграции Alembic
- тесты
- конфигурация Docker Compose

После запуска:
- приложение: http://localhost
- API/Swagger: http://localhost/api/docs

## Демо

OTP: `1234`

- Администратор: `+79000000001`
- Тренер: `+79000000002`
- Родитель: `+79000000003`
- Спортсмен: `+79000000004`
- Код присоединения: `DEMO-GROUP`

После первого запуска можно создать тестовые данные через кнопку в интерфейсе или `POST /api/dev/seed`.

## Важно

Это development/test build, не production-релиз. Перед реальным запуском необходимо заменить demo OTP и секреты, настроить HTTPS, реальный SMS/push, production storage и резервное копирование базы данных.
