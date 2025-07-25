# Быстрое исправление проблемы с ngrok

## Проблема: ERR_NGROK_3200 - endpoint is offline

## Причина
Ngrok не может подключиться к Flask приложению, хотя оно работает на localhost:5000

## Решения (попробуйте по порядку)

### 1. Специальная команда ngrok для Replit
```bash
ngrok http 127.0.0.1:5000 --host-header=localhost
```

### 2. Альтернативная команда
```bash
ngrok http localhost:5000 --host-header=rewrite
```

### 3. Убедитесь что приложение работает
```bash
curl http://localhost:5000
# Должно показать HTML страницу
```

### 4. Попробуйте другой порт (если есть конфликты)
```bash
# Измените порт в workflow на 3000
ngrok http 3000
```

### 5. Проверьте ngrok статус
```bash
ngrok status
```

## Правильный вывод ngrok
После успешного запуска вы должны увидеть:
```
Session Status                online
Session Expires               7 hours, 59 minutes
Version                       2.3.35
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    http://abc123.ngrok.io -> http://localhost:5000
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000
```

## Тестирование
1. Скопируйте https URL из ngrok
2. Откройте в браузере
3. Должно загрузиться приложение Interview Prep

## Если все равно не работает
1. Используйте Replit URL: `https://640dcace-fc1d-4f73-95b6-e196d98eec59-00-6y6u6ng03tqr.worf.replit.dev`
2. Этот URL уже работает и не требует ngrok
3. Используйте его для настройки Telegram бота