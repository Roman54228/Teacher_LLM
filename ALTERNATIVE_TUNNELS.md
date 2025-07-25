# Альтернативы для создания туннеля без ngrok

## Вариант 1: localhost.run (рекомендуется)

**Если SSH доступен:**
```bash
ssh -R 80:localhost:5000 localhost.run
```

**Если SSH недоступен:**
- Windows: Установите Git Bash 
- Linux: `sudo apt install openssh-client`

## Вариант 2: serveo.net

```bash
ssh -R 80:localhost:5000 serveo.net
```

## Вариант 3: bore.pub

```bash
# Установка
curl -L https://github.com/ekzhang/bore/releases/download/v0.4.0/bore-v0.4.0-x86_64-unknown-linux-musl.tar.gz | tar xz

# Запуск
./bore local 5000 --to bore.pub
```

## Вариант 4: cloudflared (Cloudflare Tunnel)

```bash
# Установка (пример для Linux)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64

# Запуск
./cloudflared-linux-amd64 tunnel --url http://localhost:5000
```

## Вариант 5: Простое тестирование без туннеля

Если туннели не работают, можно сначала протестировать:

1. **Создать бота** у @BotFather
2. **Настроить токен** в config.yaml
3. **Запустить** `python telegram_bot_simple.py`
4. **Тестировать кнопки** "О боте" и "Статистика"

Кнопка "Начать подготовку" не будет работать без туннеля, но основной функционал бота можно проверить.

## Для локального тестирования

**Основное приложение доступно по адресу:**
- http://localhost:5000 - интерфейс Mini App
- http://localhost:5001/admin - админ-панель

Можно тестировать функционал напрямую в браузере.

## Рекомендация

1. Попробуйте localhost.run с SSH
2. Если не работает - используйте bore.pub
3. В крайнем случае - тестируйте локально без туннеля