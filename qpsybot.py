import config
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import random
import string


bot = telebot.TeleBot(config.token) #должно быть в начале. Вызывает токен
cred = credentials.Certificate("home\qpsyback\key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://qpsyback-default-rtdb.firebaseio.com/' })


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id

    bot.send_message(user_id,"Привет, друг! Введи код школы:")
    db.reference("/student/"+str(user_id)).update({"current": "second"})

@bot.message_handler(content_types = ['text'])
def start_dialog(message):
    user_id = message.from_user.id
    current = db.reference("/student/"+str(user_id)+"/current").get()
    if current == "second":
        global code
        code = message.text
        psy = db.reference("/psy/" + str(code)).get()
        if not psy:
            bot.send_message(message.from_user.id,"Неверный код. Попробуй еще раз")
            return
            
        db.reference("/student/" + str(user_id)).update({"tg_id": user_id})
        db.reference("/messages/" + str(code) +"/" + str(user_id)).update({"tg_id": user_id})
        bot.send_message(user_id,"Как я могу тебя называть?")
        db.reference("/student/" + str(user_id)).update({"code": code})
        db.reference("/student/"+str(user_id)).update({"current": "name"})
        

    elif current == "name":
        user_markup = telebot.types.ReplyKeyboardMarkup(True)
        user_markup.row("По телефону")
        user_markup.row("По переписке")
        bot.send_message(user_id, message.text + ", тебе легче по телефону поговорить о своей проблеме или по переписке?",reply_markup = user_markup)
        db.reference("/student/" + str(user_id)).update({"name": message.text})
        db.reference("/messages/" + str(code) +"/" + str(user_id)).update({"name": message.text})
        db.reference("/student/"+str(user_id)).update({"current": "numorsms"})

    elif current == "numorsms":
        if message.text == "По телефону":
            user_markup = telebot.types.ReplyKeyboardMarkup(True)
            user_markup.row("Назад")
            bot.send_message(user_id, "Позвони по этому номер: 8787878787 \nОни дружелюбные)",reply_markup = user_markup)
            db.reference("/student/"+str(user_id)).update({"current": "back"})
        elif message.text == "По переписке":
            bot.send_message(user_id, 'Напиши сюда сообщение психологу. Он ответит в течение 2-5 минут.')
            db.reference("/student/"+str(user_id)).update({"current": "msgs"})
            
        else:
            bot.send_message(message.from_user.id,"Нет. Нужно Ввыбрать из перечисленных. Попробуй еще раз.")

    elif current == "back":
        if message.text == "Назад":
            user_markup = telebot.types.ReplyKeyboardMarkup(True)
            user_markup.row("По телефону")
            user_markup.row("По переписке")
            bot.send_message(user_id, "Тебе легче по телефону поговорить о своей проблеме или по переписке?",reply_markup = user_markup)
            db.reference("/student/"+str(user_id)).update({"current": "numorsms"})
        else:
            bot.send_message(message.from_user.id,"Ошибка! Выберите из перечисленных.")

    elif current == "msgs":
        user_id = message.from_user.id
        msgs = db.reference("/messages/"+ str(code) +"/" + str(user_id) +"/content").get()
        if not msgs:
            msgs = ""
        db.reference("/messages/" + str(code) +"/" + str(user_id)).update({"content": msgs + " / " + message.text})
        
        
    else:
        bot.send_message(message.from_user.id,"Ошибка! Выберите из перечисленных.")


bot.polling(none_stop=True) #в конце. Бесконечно.
