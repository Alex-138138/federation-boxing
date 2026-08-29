# Federation Boxing — Full Build 1.0

Полная тестовая сборка приложения Федерации бокса Иркутского округа.

## Быстрый запуск

```bash
git clone https://github.com/Alex-138138/federation-boxing.git
cd federation-boxing
bash install.sh
cd federation_boxing_full_build_1_0
docker compose up --build
```

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

Это development/test build, не production-релиз. Перед реальным запуском необходимо заменить demo OTP, секреты, настроить HTTPS, реальный SMS/push и production storage/database settings.
