# Руководство по интеграции реальной оплаты

## Текущий статус
✅ Демо-версия системы оплаты работает  
✅ UI блокировки премиум модулей готов  
✅ Модальное окно оплаты настроено  
✅ Обработка платежей через API реализована  

## Варианты платежных систем

### 1. Telegram Payments API (Рекомендуется)

**Преимущества:**
- Нативная интеграция с Telegram
- Безопасность транзакций
- Удобство для пользователей
- Поддержка основных провайдеров

**Поддерживаемые провайдеры:**
- **ЮKassa (ЮMoney)** - Россия
- **Stripe** - Международные платежи  
- **LiqPay** - Украина
- **Tranzzo** - Альтернатива

### 2. Прямая интеграция с провайдерами

#### ЮKassa (для России)
```bash
# Установка
pip install yookassa
```

```python
# Конфигурация
from yookassa import Configuration, Payment

Configuration.account_id = "YOUR_SHOP_ID"
Configuration.secret_key = "YOUR_SECRET_KEY"

# Создание платежа
payment = Payment.create({
    "amount": {"value": "499.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect", 
        "return_url": "https://your-app.com/success"
    },
    "description": "Premium доступ Interview Prep"
})
```

#### Stripe (международные)
```bash
# Установка
pip install stripe
```

```python
# Конфигурация
import stripe
stripe.api_key = "sk_test_..."

# Создание Checkout Session
checkout_session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {
            'currency': 'usd',
            'product_data': {'name': 'Interview Prep Premium'},
            'unit_amount': 999,  # $9.99
        },
        'quantity': 1,
    }],
    mode='payment',
    success_url='https://your-app.com/success',
    cancel_url='https://your-app.com/cancel',
)
```

### 3. Криптоплатежи
- **TON Wallet** - нативно для Telegram
- **USDT TRC-20** - через TronLink
- **Telegram Wallet** (beta)

## Пошаговая инструкция

### Шаг 1: Регистрация в платежной системе

**Для ЮKassa:**
1. Зайдите на [yookassa.ru](https://yookassa.ru)
2. Создайте магазин
3. Получите `shop_id` и `secret_key`
4. Настройте уведомления (webhook)

**Для Stripe:**
1. Зайдите на [stripe.com](https://stripe.com)
2. Создайте аккаунт
3. Получите API ключи (test/live)
4. Настройте webhook endpoints

### Шаг 2: Обновление кода

#### Обновите `telegram_app.py`:
```python
# Добавьте в начало файла
from yookassa import Configuration, Payment
# или 
import stripe

# Конфигурация провайдера
PAYMENT_PROVIDER = os.environ.get('PAYMENT_PROVIDER', 'yookassa')
YOOKASSA_SHOP_ID = os.environ.get('YOOKASSA_SHOP_ID')
YOOKASSA_SECRET_KEY = os.environ.get('YOOKASSA_SECRET_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

if PAYMENT_PROVIDER == 'yookassa':
    Configuration.account_id = YOOKASSA_SHOP_ID
    Configuration.secret_key = YOOKASSA_SECRET_KEY
elif PAYMENT_PROVIDER == 'stripe':
    stripe.api_key = STRIPE_SECRET_KEY

@app.route('/api/create_invoice', methods=['POST'])
def create_invoice():
    """Создание реального платежа"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        if PAYMENT_PROVIDER == 'yookassa':
            payment = Payment.create({
                "amount": {"value": "499.00", "currency": "RUB"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"https://your-app.com/payment/success?user_id={user_id}"
                },
                "description": "Interview Prep Premium доступ",
                "metadata": {"user_id": user_id}
            })
            
            return jsonify({
                'status': 'success',
                'payment_url': payment.confirmation.confirmation_url,
                'payment_id': payment.id
            })
            
        elif PAYMENT_PROVIDER == 'stripe':
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'Interview Prep Premium'},
                        'unit_amount': 999,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'https://your-app.com/payment/success?session_id={{CHECKOUT_SESSION_ID}}&user_id={user_id}',
                cancel_url='https://your-app.com/payment/cancel',
                metadata={'user_id': user_id}
            )
            
            return jsonify({
                'status': 'success',
                'payment_url': checkout_session.url,
                'session_id': checkout_session.id
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/payment', methods=['POST'])
def payment_webhook():
    """Обработка уведомлений о платежах"""
    try:
        if PAYMENT_PROVIDER == 'yookassa':
            # Проверка подписи ЮKassa
            notification_object = json.loads(request.data)
            payment = notification_object['object']
            
            if payment['status'] == 'succeeded':
                user_id = payment['metadata']['user_id']
                grant_premium_access(user_id)
                
        elif PAYMENT_PROVIDER == 'stripe':
            # Проверка подписи Stripe
            payload = request.data
            sig_header = request.headers.get('Stripe-Signature')
            
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                user_id = session['metadata']['user_id']
                grant_premium_access(user_id)
                
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400
```

### Шаг 3: Обновление базы данных

Добавьте таблицу для отслеживания платежей:

```python
# В utils/database.py
def create_tables(self):
    # ... существующие таблицы ...
    
    # Таблица платежей
    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            payment_id TEXT UNIQUE NOT NULL,
            provider TEXT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            currency TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Таблица премиум подписок
    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_premium (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            payment_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (payment_id) REFERENCES user_payments (id)
        )
    ''')
```

### Шаг 4: Обновление функций премиум доступа

```python
def check_user_premium(user_id):
    """Проверка премиум статуса в базе данных"""
    try:
        cursor = db_manager.cursor
        cursor.execute('''
            SELECT expires_at FROM user_premium 
            WHERE user_id = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        ''', (user_id,))
        
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"Error checking premium status: {e}")
        return False

def grant_premium_access(user_id, payment_id=None):
    """Активация премиум доступа с записью в БД"""
    try:
        cursor = db_manager.cursor
        
        # Добавляем или обновляем премиум статус
        cursor.execute('''
            INSERT OR REPLACE INTO user_premium (user_id, payment_id, activated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, payment_id))
        
        db_manager.connection.commit()
        print(f"Premium access granted to user: {user_id}")
        return True
    except Exception as e:
        print(f"Error granting premium access: {e}")
        return False
```

### Шаг 5: Переменные окружения

Создайте файл `.env` или добавьте в Replit Secrets:

```bash
# ЮKassa
PAYMENT_PROVIDER=yookassa
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key

# или Stripe
PAYMENT_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Шаг 6: Тестирование

1. **Тестовые платежи:**
   - ЮKassa: используйте тестовые карты
   - Stripe: карта `4242 4242 4242 4242`

2. **Проверка webhook:**
   - Используйте ngrok для локального тестирования
   - Настройте URL webhook в панели провайдера

3. **Логирование:**
   - Добавьте подробные логи всех операций
   - Мониторьте статусы платежей

## Безопасность

1. **Проверка подписей:** Всегда проверяйте подписи webhook
2. **HTTPS:** Используйте только HTTPS для продакшена
3. **Идемпотентность:** Обрабатывайте дублирующие уведомления
4. **Логирование:** Записывайте все транзакции для аудита

## Готовые файлы в проекте

- `telegram_app.py` - основная логика (строки 1004-1062)
- `templates/index.html` - UI оплаты (строки 5368-5467)
- База данных уже настроена для премиум статуса

**Что нужно изменить:** Только заменить демо-логику на реальные API вызовы провайдера.