#!/usr/bin/env python3
"""
Отладка SSH туннеля для localhost.run
"""
import subprocess
import socket
import time

def test_ports():
    """Проверяет доступность портов"""
    ports_to_test = [
        ('127.0.0.1', 5000),
        ('localhost', 5000),
        ('0.0.0.0', 5000),
    ]
    
    print("🔍 Проверка доступности портов:")
    for host, port in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {host}:{port} - доступен")
            else:
                print(f"❌ {host}:{port} - недоступен")
        except Exception as e:
            print(f"❌ {host}:{port} - ошибка: {e}")

def test_tunnel_variants():
    """Тестирует разные варианты туннеля"""
    variants = [
        "ssh -R 80:127.0.0.1:5000 localhost.run",
        "ssh -R 80:localhost:5000 localhost.run", 
        "ssh -R 80:0.0.0.0:5000 localhost.run",
        "ssh -R 5000:127.0.0.1:5000 localhost.run"
    ]
    
    print("\n📋 Попробуйте эти варианты туннеля:")
    for i, cmd in enumerate(variants, 1):
        print(f"{i}. {cmd}")

def check_replit_network():
    """Проверяет особенности сети Replit"""
    try:
        # Получаем внутренний IP
        hostname = socket.gethostname()
        internal_ip = socket.gethostbyname(hostname)
        print(f"\n🌐 Внутренний IP: {internal_ip}")
        
        # Проверяем доступность через внутренний IP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((internal_ip, 5000))
        sock.close()
        
        if result == 0:
            print(f"✅ {internal_ip}:5000 - доступен")
            print(f"💡 Попробуйте: ssh -R 80:{internal_ip}:5000 localhost.run")
        else:
            print(f"❌ {internal_ip}:5000 - недоступен")
            
    except Exception as e:
        print(f"❌ Ошибка проверки сети: {e}")

def main():
    print("🔧 Отладка SSH туннеля")
    print("=" * 40)
    
    test_ports()
    check_replit_network()
    test_tunnel_variants()
    
    print("\n💡 Рекомендации:")
    print("1. Убедитесь что приложение запущено: python telegram_app.py")
    print("2. Попробуйте каждый вариант туннеля по очереди")
    print("3. Если ничего не работает - используйте ngrok")

if __name__ == '__main__':
    main()