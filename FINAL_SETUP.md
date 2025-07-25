# Финальная настройка Telegram Mini App

## ✅ Ваш рабочий URL:
```
https://640dcace-fc1d-4f73-95b6-e196d98eec59-00-6y6u6ng03tqr.worf.replit.dev
```

## 🎯 Настройка Telegram Mini App:

### 1. Создайте бота
1. Напишите **@BotFather** в Telegram
2. Отправьте: `/newbot`
3. Введите имя: `Interview Prep Bot`
4. Введите username: `interview_prep_test_bot`
5. **Скопируйте токен** (вида: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Добавьте токен в config.yaml
1. Откройте файл `config.yaml`
2. Найдите строку: `bot_token: "ВСТАВЬТЕ_ТОКЕН_ВАШЕГО_БОТА_ЗДЕСЬ"`
3. Замените на: `bot_token: "ВАШ_ТОКЕН_ЗДЕСЬ"`

### 3. Настройте Menu Button
1. Снова напишите **@BotFather**
2. Отправьте: `/mybots`
3. Выберите созданного бота
4. Нажмите: `Bot Settings`
5. Нажмите: `Menu Button`
6. Выберите: `Configure menu button`
7. **URL**: `https://640dcace-fc1d-4f73-95b6-e196d98eec59-00-6y6u6ng03tqr.worf.replit.dev`
8. **Text**: `🎯 Начать тест`

### 4. Тестируйте
1. Найдите своего бота в Telegram (по username)
2. Отправьте команду: `/start`
3. Нажмите кнопку меню (внизу экрана)
4. Приложение откроется в Telegram!

## 🎉 Готово!

После настройки ваш Telegram Mini App будет полностью функциональным:
- Тесты по Python, Machine Learning, NLP, Computer Vision
- Система прогресса и уровней (Junior/Middle/Senior)
- Красивый интерфейс с бежево-оранжевым градиентом
- Сохранение результатов
- Личный профиль пользователя

## 📝 Примечания:
- Приложение уже запущено и работает
- URL стабильный и не требует дополнительных туннелей
- Все данные сохраняются в SQLite базе
- Админ панель доступна на отдельном порту для управления вопросами