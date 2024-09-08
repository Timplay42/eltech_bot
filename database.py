import sqlite3
import datetime


# Функция, которая создает таблицу в бд с переменными: Глава, Тема, Описание, Айди_Фото, Время добавления записи
def insert_blob(chapter, nameId, description, photoId):
    try:
        conn = sqlite3.connect('db/UserDB.db')
        cur = conn.cursor()
        print("Подключен к SQLite")
        cur.execute("""CREATE TABLE IF NOT EXISTS data2 (chapter TEXT, nameId TEXT PRIMARY KEY, description TEXT NOT NULL, photoId TEXT, eventTime timestamp)""")
        conn.commit()
        current_unix_time = datetime.datetime.now()
        current_unix_time = current_unix_time.replace(microsecond=0)
        sqlite_insert_blob_query = """INSERT INTO data2 (chapter, nameId, description, photoId, eventTime) VALUES (?, ?, ?, ?, ?)"""
        print("таблица создана")
        data_tuple = (chapter, nameId, description, photoId, current_unix_time)
        cur.execute(sqlite_insert_blob_query, data_tuple)
        conn.commit()
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


# Функция, которая собирает все данные из таблицы где в столбике nameId есть текст от пользователя
def select_data(user_text):
    try:
        conn = sqlite3.connect('db/UserDB.db')
        cur = conn.cursor()
        cur.execute("""SELECT * FROM data2 WHERE nameId=?""", (user_text,))
        data = cur.fetchone()
        return data

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


# Функция, которая выводит последнюю запись из бд
def check_value_table():
    try:
        conn = sqlite3.connect('db/UserDB.db')
        cur = conn.cursor()
        cur.execute("""SELECT * FROM data2 ORDER BY eventTime DESC LIMIT 1;""")
        data = cur.fetchone()
        return data
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
        return False
    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


# Функция, которая проверяет есть ли в бд запись с выбранным значением nameId, если есть, то возвращает True, иначе False
def check(user_text) -> bool:
    try:
        conn = sqlite3.connect('db/UserDB.db')
        cur = conn.cursor()
        cur.execute("""SELECT * FROM data2 WHERE nameId=?""", (user_text,))
        data = cur.fetchone()
        if data:
            return True
        else:
            return False
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


# Функция, которая собирает все темы с выбранной главой
# Возвращает массив данных
def get_topic(chapter_name):
    try:
        conn = sqlite3.connect('db/UserDB.db')
        cur = conn.cursor()
        cur.execute("""SELECT nameId FROM data2 WHERE chapter = ?""", (chapter_name,))
        data = cur.fetchall()
        return data
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


# Функция, которая собирает все главы и возвращает массив с уникальными значениями
def get_chapter():
    try:
        conn = sqlite3.connect('db/UserDB.db')
        cur = conn.cursor()
        cur.execute("""SELECT DISTINCT chapter FROM data2""")
        data = cur.fetchall()
        return data
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


# Функция для удаления записи по выбранной теме
def delete_data(nameId):
    try:
        conn = sqlite3.connect('db/UserDB.db')
        cur = conn.cursor()
        # Проверяется есть ли такая запись по выбранной теме
        # Если есть, то запись удаляется и возвращается True
        # Иначе False
        if check(nameId):
            cur.execute("""DELETE FROM data2 WHERE nameId = ?""", (nameId,))
            conn.commit()
            return True
        else:
            return False
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
        return False
    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


def deep_search(keyword):
    try:
        conn = sqlite3.connect('db/UserDB.db')
        cur = conn.cursor()
        cur.execute("SELECT chapter, nameid FROM data2 WHERE description LIKE ?", ('%' + keyword + '%',))
        results = cur.fetchall()
        conn.close()
        return results
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
        return False
    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


# Функция для обновления записи
# Тимур обисни
def update_data(elements_db):
    try:
        conn = sqlite3.connect('db/UserDB.db')
        cur = conn.cursor()
        current_unix_time = datetime.datetime.now()
        current_unix_time = current_unix_time.replace(microsecond=0)
        
        if len(elements_db) == 4:
            if elements_db[1] == "" and elements_db[2] == "":
                cur.execute("""UPDATE data2 SET description = ?, eventTime = ? WHERE nameId = ?""", (elements_db[3], current_unix_time, elements_db[0]))
                conn.commit()
                return True
            if elements_db[1] != "" and elements_db[2] == "":
                cur.execute("""UPDATE data2 SET chapter = ?, description = ?, eventTime = ? WHERE nameId = ?""", (elements_db[1] ,elements_db[3], current_unix_time, elements_db[0]))
                conn.commit()
                return True
            if elements_db[1] == "" and elements_db[2] != "":
                cur.execute("""UPDATE data2 SET nameId = ?, description = ?, eventTime = ? WHERE nameId = ?""", (elements_db[2] ,elements_db[3], current_unix_time, elements_db[0]))
                conn.commit()
                return True
            #{'topic_name': 'Резистор', 'user_chapter': '', 'new_topic_name': ''}
            #     0        1   2       3               4
            #['Резистор', '', '', 'приветики', 'AgACAgIAAxkBAAIE8GXniD_iR8uEeMfMbAP_8svPjSBeAAIH1zEb5wI4S3Cg1OwHH-8EAQADAgADeAADNAQ']
        elif len(elements_db) == 5:
            if elements_db[1] == "" and elements_db[2] == "":
                cur.execute("""UPDATE data2 SET description = ?, photoId = ?, eventTime = ? WHERE nameId = ?""", (elements_db[3] ,elements_db[4], current_unix_time, elements_db[0]))
                conn.commit()
                return True
            if elements_db[1] == "" and elements_db[2] != "":
                cur.execute("""UPDATE data2 SET nameId = ?, description = ?, photoId = ?, eventTime = ? WHERE nameId = ?""", (elements_db[2], elements_db[3] ,elements_db[4], current_unix_time, elements_db[0]))
                conn.commit()
                return True
            if elements_db[1] != "" and elements_db[2] == "":
                cur.execute("""UPDATE data2 SET chapter = ?, description = ?, photoId = ?, eventTime = ? WHERE nameId = ?""", (elements_db[1], elements_db[3] ,elements_db[4], current_unix_time, elements_db[0]))
                conn.commit()
                return True
            if elements_db[1] != "" and elements_db[2] != "":
                cur.execute("""UPDATE data2 SET chapter = ?, nameId = ?, description = ?, photoId = ?, eventTime = ? WHERE nameId = ?""", (elements_db[1], elements_db[2], elements_db[3] ,elements_db[4], current_unix_time, elements_db[0]))
                conn.commit()
                return True
        
        else:
            conn.commit()
            return False
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
        return False
    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")