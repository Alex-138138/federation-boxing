# Federation Boxing — Full Build 2.0

Развиваемая полная сборка приложения Федерации бокса Иркутского округа.

## Что уже есть

- публичная главная страница Федерации
- кабинеты администратора, тренера, родителя и спортсмена
- авторизация по телефону + demo OTP
- роли и переключение ролей
- заявки на вступление по коду/QR
- сообщения группы
- уведомления
- профиль спортсмена
- рейтинг, достижения и расписание
- CMS-версии и публикация
- PostgreSQL + FastAPI + Docker
- production HTTPS через Caddy

## Локальный запуск

```bash
git clone https://github.com/Alex-138138/federation-boxing.git
cd federation-boxing
bash install.sh
docker compose up --build
```

## Production

Используется `docker-compose.prod.yml` и `deploy/first-run.sh`.

Демо OTP: `1234`.

Это development/test build. Перед реальным эксплуатационным запуском необходимо заменить demo OTP, секреты, настроить реальный SMS/push, production storage и завершить security hardening.
