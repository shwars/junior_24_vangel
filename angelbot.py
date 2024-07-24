import telebot 
import threading 
import time 
import os 
import random 
from datetime import datetime 
from config import telegram_token 
 
bot = telebot.TeleBot(telegram_token,parse_mode='Markdown') 
 
# Путь к папке с изображениями 
images_directory = 'pix' 
 
# Файл для хранения ID пользователей 
users_file = 'users.txt' 
 
# Файл для хранения отправленных изображений 
sent_images_file = 'sent_images.txt' 
 
# Переменная для хранения текущего отправляемого изображения 
current_image = None 
 
# Функция для проверки, добавлен ли пользователь уже в файл 
def is_user_added(user_id):
    with open(users_file, 'r') as file: 
        for line in file: 
            if str(user_id) in line: 
                return True 
    return False 
 
# Функция для загрузки списка отправленных изображений из файла 
def load_sent_images(): 
    if not os.path.exists(sent_images_file): 
        return set()  # Если файл не существует, возвращаем пустое множество 
     
    with open(sent_images_file, 'r') as file: 
        return set(file.read().splitlines()) 
 
# Функция для сохранения нового отправленного изображения в файл 
def save_sent_image(image_name): 
    with open(sent_images_file, 'a') as file: 
        file.write(f"{image_name}\n") 
 
def send_photo(user_id,fname,caption=None):
    with open(os.path.join(images_directory, fname), 'rb') as photo:
        bot.send_photo(user_id, photo, caption) 

# Функция для выбора случайного изображения и его отправки всем пользователям 
def send_random_image_to_all_users(): 
    global current_image 
     
    # Получаем список файлов из папки с изображениями, исключая уже отправленные 
    sent = load_sent_images()
    available_images = [image for image in os.listdir(images_directory) if image not in sent] 

    if not available_images: 
        print("Нет новых изображений для отправки.") 
        return 
     
    # Выбираем случайное изображение из доступных 
    current_image = random.choice(available_images) 
     
    # Отправляем изображение всем пользователям 
    for user_id in get_all_user_ids(): 
        try: 
            cap = f"*{current_image.replace('_',' ')[:-4]}*, by NeuroAngel"
            send_photo(user_id, current_image, caption = cap) 
            time.sleep(1)  # Задержка между отправками сообщений 
        except Exception as e: 
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {str(e)}") 

    # Сохраняем отправленное изображение в файл 
    save_sent_image(current_image) 
 
# Функция для получения всех ID пользователей из файла 
def get_all_user_ids(): 
    with open(users_file, 'r') as file: 
        return [line.strip() for line in file] 
 
@bot.message_handler(commands=['start']) 
def start_message(message): 
    # Проверяем, добавлен ли пользователь 
    if not is_user_added(message.chat.id): 
        # Если не добавлен, добавляем в файл 
        with open(users_file, 'a') as file: 
            file.write(f"{message.chat.id}\n") 
    # Отправляем приветственное сообщение и изображение при старте 
    welcome = "Привет! Это бот виртуальной художницы NeuroAngel, которая рисует кофейные зарисовки в стиле Анны Горвиц. Каждый час я буду посылать новое произведение, нарисованное нейросетью. Если хочешь, чтобы я нарисовала что-то конкретное - придумай идею для картины и пришли её мне в сообщении, и я учту это в последующих генерациях." 
    send_photo(message.chat.id,'Detailed_Coffee_Cup.png',caption=welcome)

@bot.message_handler(content_types=['text']) 
def message_reply(message): 
    # Отвечаем пользователю и записываем его идею в файл 
    bot.send_message(message.chat.id, f"Спасибо за идею! Мы постараемся ее реализовать.") 
     
    with open('angel.txt', 'a', encoding='utf8') as file: 
        file.write(f"{message.text}\n")  # Записываем текст с новой строки 
 
# Функция для рассылки сообщения каждые 3 часа 
def send_images_periodically(): 
    while True: 
        # Получаем текущее время 
        current_time = datetime.now().time() 
        # Проверяем, что текущее время находится в диапазоне с 9:00 утра до 6:00 вечера 
        if current_time >= datetime.strptime('09:00:00', '%H:%M:%S').time() and \
           current_time <= datetime.strptime('18:00:00', '%H:%M:%S').time():
            # Отправляем случайное изображение всем пользователям 
            send_random_image_to_all_users() 
         
        # Пауза перед следующей проверкой времени 
        time.sleep(60*60) 
# Запускаем функцию рассылки изображений в отдельном потоке 
thread = threading.Thread(target=send_images_periodically) 
thread.start() 

# Запускаем бота 
bot.infinity_polling()