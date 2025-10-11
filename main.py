import telebot
from config import TOKEN, YOUR_KEY, YOUR_SECRET
from logic import photo, FusionBrainAPI
import os
import time

bot = telebot.TeleBot(TOKEN)
api = FusionBrainAPI('https://api-key.fusionbrain.ai/', YOUR_KEY, YOUR_SECRET)
GLOBAL_PIPELINE_ID = None

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, 'Привет, этот бот, который генерирует фотографии по твоим запросам, просто напиши какое фото тебе сделать')

@bot.message_handler(func=lambda message: message.content_type == 'text' and message.text.strip() != '')
def handle_text_message(message):
    prompt = message.text.strip() #получаем запрос
    if not GLOBAL_PIPELINE_ID:
        bot.reply_to(message, "Извините, сервис генерации изображений временно недоступен. Попробуйте позже.")
        return
    msg_waiting = bot.reply_to(message, "Принято! Пожалуйста, подождите, ваше изображение генерируется...")#запрос принят
    #генерируем инид для файла
    unique_id = f"{message.chat.id}_{message.message_id}_{int(time.time())}"
    output_filename_base = f"generated_image_{unique_id}" 
    
    #запрашиваем генерацию у класса 
    uuid_gen = api.generate(prompt)#передаем запрос
    if uuid_gen:
        files_data = api.check_generation(uuid_gen, GLOBAL_PIPELINE_ID)
        if files_data and files_data [0] : # Если получили данные
            base64_image_string = files_data[0]
            #сохран изоо
            if photo(base64_image_string, output_filename_base):
                #отправ изоо
                final_file_path = os.path.splitext(output_filename_base)[0] + (".jpg" if "data:image/jpeg" in base64_image_string else ".png")       
                with open(final_file_path, 'rb') as img_file:
                    bot.send_photo(message.chat.id, img_file, caption=f"Ваше изображение по запросу: '{prompt}'")
                    #удаляем соо
                    bot.delete_message(message.chat.id, msg_waiting.message_id)
                #удаляем файл
                os.remove(final_file_path)
            else:
                bot.reply_to(message, "Извините, произошла ошибка при сохранении изображения.")
        else:
            bot.reply_to(message, "Извините, не удалось получить данные изображения от FusionBrain.")
    else:
        bot.reply_to(message, "Извините, не удалось начать генерацию изображения. Возможно, запрос слишком сложный или произошла ошибка на сервере.")


if __name__ == "__main__":
    bot.infinity_polling()