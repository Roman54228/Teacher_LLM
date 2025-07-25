#!/usr/bin/env python3
"""
Автоматическое исправление SSH туннеля для localhost.run
"""
import subprocess
import time
import os
import signal

def kill_existing_tunnels():
    """Останавливает существующие SSH туннели"""
    try:
        # Найти и убить процессы SSH туннелей
        result = subprocess.run(['pgrep', '-f', 'ssh.*localhost.run'], 
                              capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"✓ Остановлен туннель PID: {pid}")
    except Exception as e:
        print(f"Предупреждение: {e}")

def test_app_connection():
    """Проверяет доступность приложения"""
    import requests
    try:
        response = requests.get('http://127.0.0.1:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Приложение работает на 127.0.0.1:5000")
            return True
    except Exception as e:
        print(f"❌ Приложение недоступно: {e}")
        return False

def start_tunnel():
    """Запускает SSH туннель с правильными параметрами"""
    print("🚀 Запуск SSH туннеля...")
    
    # Команда с правильным адресом
    cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', 
           '-R', '80:127.0.0.1:5000', 'localhost.run']
    
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("📡 Ждем URL от localhost.run...")
        
        for line in iter(process.stdout.readline, ''):
            print(f"[SSH] {line.strip()}")
            
            # Ищем URL
            if 'https://' in line and 'localhost.run' in line:
                import re
                url_match = re.search(r'https://[a-zA-Z0-9-]+\.localhost\.run', line)
                if url_match:
                    url = url_match.group(0)
                    print(f"\n🎉 Туннель готов: {url}")
                    print(f"\n📝 Теперь обновите config.yaml:")
                    print(f"telegram:")
                    print(f"  web_app_url: \"{url}\"")
                    print(f"\n🔄 После обновления перезапустите бота:")
                    print(f"python telegram_bot_simple.py")
                    break
                    
    except KeyboardInterrupt:
        print("\n⛔ Туннель остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка туннеля: {e}")

def main():
    print("🔧 Исправление SSH туннеля для Telegram Mini App")
    print("=" * 50)
    
    # Останавливаем старые туннели
    kill_existing_tunnels()
    
    # Проверяем приложение
    if not test_app_connection():
        print("❌ Сначала запустите основное приложение:")
        print("python telegram_app.py")
        return
    
    # Запускаем туннель
    start_tunnel()

if __name__ == '__main__':
    main()