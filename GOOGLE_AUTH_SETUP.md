# Настройка Google авторизации

## Текущее состояние

✅ **Google авторизация уже работает в демо-режиме**  
✅ Кнопка "Continue with Google" готова  
✅ Обработка Google данных реализована  
✅ Красивый дизайн кнопки с Google логотипом  

## Как работает сейчас

1. При нажатии "Continue with Google" показывается демо:
   ```
   Демо Google авторизации.
   Имя: Demo Google User
   Email: demo@gmail.com
   
   Продолжить?
   ```

2. Создается пользователь с Google данными
3. В профиле отображается "🌐 Привет, Demo Google User!"

## Настройка реальной Google авторизации

### Шаг 1: Создание Google OAuth приложения

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com)
2. Создайте новый проект или выберите существующий
3. Включите Google+ API и Google Sign-In API
4. Настройки OAuth 2.0:
   - Authorized JavaScript origins: `https://640dcace-fc1d-4f73-95b6-e196d98eec59-00-6y6u6ng03tqr.worf.replit.dev`
   - Authorized redirect URIs: не требуется для JavaScript

### Шаг 2: Получение Client ID

1. В разделе "Credentials" создайте OAuth 2.0 Client ID
2. Тип: Web application
3. Скопируйте Client ID (формат: `123456789-abc.apps.googleusercontent.com`)

### Шаг 3: Обновление кода

Замените демо-реализацию на реальную в `templates/index.html`:

```javascript
async function authenticateWithGoogle() {
    try {
        const clientId = 'ВАШ_GOOGLE_CLIENT_ID_ЗДЕСЬ';
        
        // Загрузка Google Sign-In SDK
        await loadGoogleSignIn();
        
        // Инициализация Google Identity Services
        google.accounts.id.initialize({
            client_id: clientId,
            callback: handleGoogleSignIn
        });
        
        // Показать окно авторизации
        google.accounts.id.prompt();
        
    } catch (error) {
        console.error('Google authentication failed:', error);
        alert('Ошибка авторизации Google. Продолжить как гость?') && await continueAsGuest();
    }
}
```

### Шаг 4: Добавление в config.yaml

```yaml
google:
  client_id: "ВАШ_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
  enabled: true
```

## Преимущества Google авторизации

✅ **Быстрый вход** - один клик без паролей  
✅ **Безопасность** - OAuth 2.0 стандарт  
✅ **Персонализация** - имя и email пользователя  
✅ **Кроссплатформенность** - работает везде  

## Текущая функциональность

1. **Дизайн**: Красивая кнопка с Google логотипом
2. **Обработка**: Полная интеграция с системой пользователей
3. **Профиль**: Отображение данных Google в интерфейсе
4. **Прогресс**: Сохранение результатов для Google пользователей

## Тестирование

Сейчас можно протестировать:
1. Откройте приложение
2. Нажмите "Continue with Google"
3. Подтвердите демо-авторизацию
4. Проверьте профиль - должно быть "🌐 Привет, Demo Google User!"

Для активации реальной авторизации нужен только Google Client ID.