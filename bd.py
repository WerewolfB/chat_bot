import sqlite3

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

#print(selectDisconnection_ShutdownLocation("Центральный","Электричество"))