#Import
import os;
import time;
import sqlite3;
from time import sleep;
from telebot import *;
from telebot import types;
from dotenv import *;
#PreLoad
load_dotenv()
conn = sqlite3.connect('database.db')
cur = conn.cursor()
# Создание БД

# 
cur.execute("""
        CREATE TABLE IF NOT EXISTS InnerCityDistrict(
            idDistrict INT PRIMARY KEY,
            nameDistrict TEXT
        );
""")
conn.commit()

cur.execute("""
        CREATE TABLE IF NOT EXISTS Street(
            idStreet INT PRIMARY KEY,
            idDistrict INT,
            nameStreet TEXT
        );
""")
conn.commit()

cur.execute("""
        CREATE TABLE IF NOT EXISTS ShutdownLocation(
            idRecord INT PRIMARY KEY,
            idStreet INT,
            idDisconnection INT
        );
""")
conn.commit()

cur.execute("""
        CREATE TABLE IF NOT EXISTS Disconnection(
            idDisconnection INT PRIMARY KEY,
            idCommunalResource INT,
            dataStart  TEXT,
            dataEnd TEXT,
            comment TEXT
        ); 
""")
conn.commit()

cur.execute("""
        CREATE TABLE IF NOT EXISTS CommunalResource(
            idCommunalResource INT PRIMARY KEY,
            type TEXT,
            contact TEXT
        );  
""")
conn.commit()



# Данные для заполнения БД
# InnerCityDistrict
more_InnerCityDistrict = [
    (0, "Центральный"), 
    (1, "Хостинский"),
    (2, "Лазаревский"),
    (3, "Адлерский")
    ]
cur.executemany("INSERT or IGNORE INTO InnerCityDistrict VALUES(?, ?);", more_InnerCityDistrict)
conn.commit()

# Street
more_Street = [
    (0, 0, "ул. Роз"),
    (1, 1, "ул. 50 лет СССР"),
    (2, 2, "ул. Победы"),
    (3, 0, "ул. Гагарина"),
    (4, 3,"ул. Ленина"),
    (5, 1, "ул. Механизаторов")
]
cur.executemany("INSERT OR IGNORE INTO Street VALUES(?, ?, ?);", more_Street)
conn.commit()

# CommunalResource
more_CommunalResource = [
    (0, "Вода", "Водоканал, +7 (862) 444 05 05"),
    (1, "Электричество", "Сочинские электросети, +7 (862) 269 02 42"),
    (2, "Газ", "Сочигоргаз, +7 (862) 296 08 04")
]
cur.executemany("INSERT OR IGNORE INTO CommunalResource VALUES(?, ?, ?);", more_CommunalResource)
conn.commit()

# Disconnection
more_Disconnection = [
    (0, 1, "2023-09-15 10:00:00", "2023-09-15 12:00:00", "Причина: Ремонт линии"),
    (1, 0, "2023-09-20 14:30:00", "2023-09-21 08:00:00", "Причина: Авария"),
    (2, 2, "2023-09-25 18:45:00", "2023-09-26 09:30:00", "Причина: Плановые работы"),
    (3, 1, "2023-09-29 07:15:00", "2023-09-29 09:45:00", "Причина: Замена кабеля")
]
cur.executemany("INSERT OR IGNORE INTO Disconnection VALUES(?, ?, ?, ?, ?);", more_Disconnection)
conn.commit()

# ShutdownLocation
more_ShutdownLocation = [
    (0, 0, 0),
    (1, 0, 3),
    (2, 1, 1),
    (3, 2, 2),
    (4, 3, 3)
]
cur.executemany("INSERT OR IGNORE INTO ShutdownLocation VALUES(?, ?, ?);", more_ShutdownLocation)
conn.commit()

# Проверка
#cur.execute("SELECT * FROM ShutdownLocation;")
#one_result = cur.fetchall()
#fethone
#fethmore
#fethall
#print(one_result)

def selectDisconnection_ShutdownLocation(namedistrict, nameresource):
    # получение id
    cur.execute(f"""
        SELECT idDistrict FROM InnerCityDistrict
            WHERE nameDistrict = '{namedistrict}'
    """)
    district = cur.fetchall()

    cur.execute(f"""
        SELECT idCommunalResource FROM CommunalResource
            WHERE type = '{nameresource}'
    """)
    resource = cur.fetchall()

    # получение улиц и времени
    cur.execute(f"""
        WITH
            t1 AS (
                SELECT idStreet FROM Street 
                    WHERE idDistrict = {district[0][0]}
            ),
            t2 AS (
                SELECT idDisconnection FROM Disconnection
                    WHERE idCommunalResource = {resource[0][0]}
            ),
            t3 AS (
                SELECT * FROM ShutdownLocation
                    WHERE idStreet IN (SELECT * FROM t1) AND idDisconnection IN (SELECT * FROM t2)
            ),
            t4 AS (
                SELECT * FROM Street
                    WHERE idStreet IN (SELECT idStreet FROM t3)
            ),
            t5 AS (
                SELECT * FROM Disconnection
                    WHERE idDisconnection IN (SELECT idDisconnection FROM t3)
            ),
            t6 AS (
                SELECT * FROM ShutdownLocation JOIN Street ON ShutdownLocation.idStreet = Street.idStreet
            ),
            t7 AS (
                SELECT * FROM t6 JOIN Disconnection ON t6.idDisconnection = Disconnection.idDisconnection
            ),
            t8 AS (
                SELECT * FROM t7 
                    WHERE nameStreet IN (SELECT nameStreet FROM t4) AND dataStart IN (SELECT dataStart FROM t5)
            )
        SELECT * FROM t8;
    """)
    result = cur.fetchall()
    nakaplenie = ''
    for r in result:
        stroka = f"Проблемная улица: {r[5]}, начало: {r[8]}, конец: {r[9]} \n"
        nakaplenie = nakaplenie + stroka

    if nakaplenie != '':
        return nakaplenie
    else:
        return "В данном районе нет проблем с данным ресурсом"

#VAR
try:
    TG_BOT_API = str(os.getenv("TG_BOT_API"))
    #TG_ID = str(os.getenv("TG_ID"))
except:
    print("VAR_Error of getting Telegram_Bot_API from .env")
is_adress = False
alarm_resours=""
alarm_district=""
alarm_adress=""
request_resours=""
request_district=""
request_data = "Не найдены"


#OBJ
try:
    bot = telebot.TeleBot(TG_BOT_API)
except:
    print("OBJ_Error of creating bot by API")

#Keyboards
#BTN
keyboard = types.ReplyKeyboardMarkup()
but1 = types.KeyboardButton("Контакты")
but2 = types.KeyboardButton("Помощь")
but3 = types.KeyboardButton("Обращение")
keyboard.row(but1,but2,but3)
#appeal step1
appeal_keyboard = types.InlineKeyboardMarkup(row_width=1)
ability_btn = types.InlineKeyboardButton(text ="Запрос доступности", callback_data="appeal_ability")
alarm_btn = types.InlineKeyboardButton(text ="Сообщение об аварии", callback_data="appeal_alarm")
contact_btn = types.InlineKeyboardButton(text ="Запрос контактных данных", callback_data="appeal_contact")
appeal_keyboard.add(ability_btn)
appeal_keyboard.add(alarm_btn)
appeal_keyboard.add(contact_btn)
#Appeal contacts
appeal_keyboard_contacts = types.InlineKeyboardMarkup(row_width=1)
gaz_contact_btn = types.InlineKeyboardButton(text ="Газоснабжение", callback_data="appeal_contact_gaz")
electro_contact_btn = types.InlineKeyboardButton(text ="Электроснабжение", callback_data="appeal_contact_electro")
water_contact_btn = types.InlineKeyboardButton(text ="Водоснабжение", callback_data="appeal_contact_water")
appeal_keyboard_contacts.add(gaz_contact_btn)
appeal_keyboard_contacts.add(electro_contact_btn)
appeal_keyboard_contacts.add(water_contact_btn)
#Appeal alarm
appeal_keyboard_alarm = types.InlineKeyboardMarkup(row_width=1)
gaz_alarm_btn = types.InlineKeyboardButton(text ="Газ", callback_data="appeal_alarm_gaz")
electro_alarm_btn = types.InlineKeyboardButton(text ="Электричество", callback_data="appeal_alarm_electro")
water_alarm_btn = types.InlineKeyboardButton(text ="Вода", callback_data="appeal_alarm_water")
appeal_keyboard_alarm.add(gaz_alarm_btn)
appeal_keyboard_alarm.add(electro_alarm_btn)
appeal_keyboard_alarm.add(water_alarm_btn)
#Appeal alarm district
appeal_keyboard_alarm_district = types.InlineKeyboardMarkup(row_width=1)
central_district_alarm_btn = types.InlineKeyboardButton(text ="Центральный район", callback_data="appeal_alarm_district_central")
laz_district_alarm_btn = types.InlineKeyboardButton(text ="Лазаревский район", callback_data="appeal_alarm_district_laz")
host_district_alarm_btn = types.InlineKeyboardButton(text ="Хостинский район", callback_data="appeal_alarm_district_host")
adler_district_alarm_btn = types.InlineKeyboardButton(text ="Адлеровский район", callback_data="appeal_alarm_district_adler")
appeal_keyboard_alarm_district.add(central_district_alarm_btn)
appeal_keyboard_alarm_district.add(laz_district_alarm_btn)
appeal_keyboard_alarm_district.add(host_district_alarm_btn)
appeal_keyboard_alarm_district.add(adler_district_alarm_btn)
#appel request
appeal_keyboard_request = types.InlineKeyboardMarkup(row_width=1)
gaz_request_btn = types.InlineKeyboardButton(text ="Газоснабжение", callback_data="appeal_request_gaz")
electro_request_btn = types.InlineKeyboardButton(text ="Электроснабжение", callback_data="appeal_request_electro")
water_request_btn = types.InlineKeyboardButton(text ="Водоснабжение", callback_data="appeal_request_water")
appeal_keyboard_request.add(gaz_request_btn)
appeal_keyboard_request.add(electro_request_btn)
appeal_keyboard_request.add(water_request_btn)
#appeal district reauest
appeal_keyboard_request_district = types.InlineKeyboardMarkup(row_width=1)
central_district_request_btn = types.InlineKeyboardButton(text ="Центральный район", callback_data="appeal_request_district_central")
laz_district_request_btn = types.InlineKeyboardButton(text ="Лазаревский район", callback_data="appeal_request_district_laz")
host_district_request_btn = types.InlineKeyboardButton(text ="Хостинский район", callback_data="appeal_request_district_host")
adler_district_request_btn = types.InlineKeyboardButton(text ="Адлеровский район", callback_data="appeal_request_district_adler")
appeal_keyboard_request_district.add(central_district_request_btn)
appeal_keyboard_request_district.add(laz_district_request_btn)
appeal_keyboard_request_district.add(host_district_request_btn)
appeal_keyboard_request_district.add(adler_district_request_btn)
#MAIN
#defs
def send_request_data(NewID):
    request_data = selectDisconnection_ShutdownLocation(request_district,request_resours)
    bot.send_message(NewID,"Проблемы с "+ request_resours+" в "+ request_district + " районе:")
    bot.send_message(NewID,request_data)

#Commands
@bot.message_handler(commands=['start'])
def start(message):
    NewID = message.chat.id
    bot.send_message(NewID, "Здравствуйте, напишите /help что бы узнать подробнее о моем функционале!", reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def help(message):
    try:
        NewID = message.chat.id
        bot.send_message(NewID, """С моей помощью вы можете
узнать, проводятся ли по вашему адресу
ремонтные или другие работы, связанные с ЖКХ, сообщить об аварии или уточнить контактную информацию организаций, предоставляющих услуги ЖКХ.""")
    except:
        bot.send_message(message.chat.id, "Прости, ошибка команды. Я сейчас не могу её обработать. Попробуй позднее.")
        print("Error of handling '/help' command")

@bot.message_handler(commands=['info'])
def info(message):
    try:
        NewID = message.chat.id
        bot.send_message(NewID,"Выберите службу:",reply_markup = appeal_keyboard_contacts)
    except:
        bot.send_message(message.chat.id, "Прости, ошибка команды. Я сейчас не могу её обработать. Попробуй позднее.")
        print("Error of handling '/info' command")

@bot.message_handler(commands=['appeal'])
def appeal(message):
    NewID = message.chat.id
    bot.send_message(NewID, "Пожалйста, выберите тип обращения:", reply_markup=appeal_keyboard)

@bot.callback_query_handler(func=lambda c:True)
def inlin(c):
    global alarm_resours
    global alarm_district
    global is_adress
    global request_resours, request_district
    if c.data=='appeal_contact':
        NewID = c.message.chat.id
        bot.send_message(NewID,"Выберите службу:",reply_markup = appeal_keyboard_contacts)
    elif c.data=='appeal_alarm':
        NewID = c.message.chat.id
        bot.send_message(NewID,"Выберите тип ресурса, с которым возникли проблемы:", reply_markup = appeal_keyboard_alarm)
    elif c.data=='appeal_ability':
        NewID = c.message.chat.id
        bot.send_message(NewID,"Выберите ресурс, доступность которого хотите проверить:", reply_markup = appeal_keyboard_request)
    elif c.data=='appeal_contact_gaz':
        NewID = c.message.chat.id
        bot.send_message(NewID,"""<b>АО «Сочигоргаз»</b>
<b>Телефон:</b> +7 (862) 296-08-04
<b>Факс:</b> +7 (862) 262-91-35
<b>E-mail:</b> info.SGG@gazpromgk.ru
<b>Адрес:</b> ул. Дмитриевой, д.56, г. Сочи, Краснодарский край, 354002
""", parse_mode='html')
    elif c.data=='appeal_contact_water':
        NewID = c.message.chat.id
        bot.send_message(NewID,"""<b>Водоконал г.Сочи</b>
<b>Телефон:</b> +7 (862) 444 05 05
<b>Адрес:</b> 354065, Россия, Краснодарский край, г. Сочи, ул. Гагарина, д.73
""", parse_mode='html')
    elif c.data=='appeal_contact_electro':
        NewID = c.message.chat.id
        bot.send_message(NewID,"""<b>Россети Кубань</b>
<b>Телефон:</b> 8 800 220 0 220
<b>Адрес:</b> ул. Конституции СССР, 42А, Сочи
""", parse_mode='html')
    elif c.data=='appeal_alarm_gaz':
        NewID = c.message.chat.id
        alarm_resours
        alarm_resours = "Газоснабжением"
        bot.send_message(NewID,"Выберите район проблемы:",reply_markup = appeal_keyboard_alarm_district)
    elif c.data=='appeal_alarm_electro':
        NewID = c.message.chat.id
        alarm_resours
        alarm_resours = "Электроснабжением"
        bot.send_message(NewID,"Выберите район проблемы:",reply_markup = appeal_keyboard_alarm_district)
    elif c.data=='appeal_alarm_water':
        NewID = c.message.chat.id
        alarm_resours
        alarm_resours = "Водоснабжением"
        bot.send_message(NewID,"Выберите район проблемы:",reply_markup = appeal_keyboard_alarm_district)
    elif c.data=='appeal_alarm_district_central':
        NewID = c.message.chat.id
        alarm_district
        alarm_district = "Центральном"
        bot.send_message(NewID,"Напишите, пожалуйста, улицу, на которой возникла проблема")
    elif c.data=='appeal_alarm_district_laz':
        NewID = c.message.chat.id
        alarm_district
        alarm_district = "Лазаревском"
        bot.send_message(NewID,"Напишите, пожалуйста, улицу, на которой возникла проблема")
        is_adress = True
    elif c.data=='appeal_alarm_district_host':
        NewID = c.message.chat.id
        alarm_district
        alarm_district = "Хостинском"
        bot.send_message(NewID,"Напишите, пожалуйста, улицу, на которой возникла проблема")
        is_adress = True
    elif c.data=='appeal_alarm_district_adler':
        NewID = c.message.chat.id
        alarm_district
        alarm_district = "Адлеровском"
        bot.send_message(NewID,"Напишите, пожалуйста, улицу, на которой возникла проблема")
        is_adress = True
    elif c.data=='appeal_request_gaz':
        NewID = c.message.chat.id
        request_resours = "Газоснабжением"
        bot.send_message(NewID,"Выберите район:",reply_markup = appeal_keyboard_request_district)
    elif c.data=='appeal_request_electro':
        NewID = c.message.chat.id
        request_resours = "Электроснабжением"
        bot.send_message(NewID,"Выберите район:",reply_markup = appeal_keyboard_request_district)
    elif c.data=='appeal_request_water':
        NewID = c.message.chat.id
        request_resours = "Водоснабжением"
        bot.send_message(NewID,"Выберите район:",reply_markup = appeal_keyboard_request_district)
    elif c.data=='appeal_request_district_central':
        NewID = c.message.chat.id
        request_district = "Центральном"
        #bot.send_message(NewID,"Заглушка", reply_markup=keyboard)
        send_request_data(NewID)
    elif c.data=='appeal_request_district_laz':
        NewID = c.message.chat.id
        request_district = "Лазаревском"
        #bot.send_message(NewID,"Заглушка", reply_markup=keyboard)
        send_request_data(NewID)
    elif c.data=='appeal_request_district_host':
        NewID = c.message.chat.id
        request_district = "Хостинском"
        #bot.send_message(NewID,"Заглушка", reply_markup=keyboard)
        send_request_data(NewID)
    elif c.data=='appeal_request_district_adler':
        NewID = c.message.chat.id
        request_district = "Адлеровском"
        #bot.send_message(NewID,"Заглушка", reply_markup=keyboard)
        send_request_data(NewID)


    


#Text    
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global is_adress
    global alarm_adress
    if is_adress == False:
        if message.text == 'Контакты':
            info(message)
        elif message.text == 'Помощь':
            help(message)
        elif message.text == 'Обращение':
            appeal(message)
        else:
            NewID = message.chat.id
            bot.send_message(NewID, """Извините, я пока не могу обработать сообщение такого вида. Попробуйте перефразировать ваше обращение""", reply_markup=keyboard)
            appeal(message)
    else:
        NewID = message.chat.id  
        alarm_adress = message.text
        is_adress = False
        bot.send_message(NewID,"Ваше заявление о проблемах с "+alarm_resours+" в "+alarm_district+" по адресу "+alarm_adress+ " было сохранено и передано в соответствующие службы!", reply_markup=keyboard)

#polling
bot.infinity_polling()