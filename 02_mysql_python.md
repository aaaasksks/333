# MySQL и Python. Подключение и базовые операции

В этом конспекте мы сделаем небольшую базу данных для книг. Научимся создавать таблицу, добавлять записи, читать их, изменять и удалять. Потом подключим базу к Python.

Для начала нужен установленный MySQL Server. MySQL Workbench можно использовать для выполнения SQL, но это отдельная программа. Сам сервер хранит данные.

## 1. Как устроена база данных

База данных содержит таблицы. Таблица похожа на список, в котором у каждого элемента одинаковые поля.

Пример таблицы `books`:

| id | title | author | price |
| --- | --- | --- | --- |
| 1 | Python с нуля | Анна | 350.00 |
| 2 | Основы SQL | Иван | 280.00 |

Одна строка называется записью. `id` помогает найти конкретную запись.

Основные SQL-команды:

- `CREATE` создает базу или таблицу.
- `INSERT` добавляет запись.
- `SELECT` читает записи.
- `UPDATE` изменяет существующие данные.
- `DELETE` удаляет записи.

Последние четыре операции часто называют CRUD. Это сокращение от Create, Read, Update, Delete.

## 2. Подготовка MySQL

Нужно установить и запустить MySQL Server. Для работы подойдет MySQL 8 или более новая совместимая версия. Проверить установку можно командой:

```bash
mysql --version
```

Если команда не находится, это не всегда означает, что сервера нет. Возможно, программа `mysql` не добавлена в PATH. Можно открыть MySQL Workbench и выполнить SQL там.

Создадим учебную базу. Подключитесь к серверу из терминала:

```bash
mysql -u root -p
```

Введите пароль администратора MySQL. Он может отличаться от пароля вашего компьютера.

Далее выполните следующие команды в MySQL. Это учебные данные, пароль `study_pass` подходит только для работы на своем компьютере.

```sql
CREATE DATABASE IF NOT EXISTS study_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'student'@'localhost'
    IDENTIFIED BY 'study_pass';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE
    ON study_db.* TO 'student'@'localhost';

USE study_db;
```

Мы создали базу `study_db` и отдельного пользователя `student`. Если такой пользователь уже существует, команда `CREATE USER IF NOT EXISTS` не изменит его пароль. В этом случае нужно использовать пароль существующего пользователя или настроить его отдельно.

Те же команды находятся в `examples/setup.sql`. В MySQL Workbench можно открыть этот файл и выполнить его целиком.

## 3. Создание таблицы

В той же базе выполните:

```sql
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
```

Обозначения:

- `INT` хранит целое число.
- `AUTO_INCREMENT` сам выдает следующий `id`.
- `PRIMARY KEY` означает уникальный ключ записи.
- `VARCHAR(150)` хранит текст длиной до 150 символов.
- `NOT NULL` запрещает оставлять поле без значения `NULL`.
- `DECIMAL(10, 2)` подходит для денежных сумм, в нем две цифры после точки.

Проверить, появилась ли таблица:

```sql
SHOW TABLES;
DESCRIBE books;
```

## 4. Добавление данных. INSERT

```sql
INSERT INTO books (title, author, price)
VALUES ('Python с нуля', 'Анна', 350.00);
```

Здесь мы указали столбцы и их значения. `id` писать не нужно, MySQL назначит его сам.

Несколько записей можно добавить одной командой:

```sql
INSERT INTO books (title, author, price)
VALUES
    ('Основы SQL', 'Иван', 280.00),
    ('Алгоритмы', 'Мария', 500.00);
```

Если выполнить эти команды повторно, появятся новые записи с другими `id`. Таблица `books` в нашем примере разрешает одинаковые названия книг.

## 5. Чтение данных. SELECT

Все записи:

```sql
SELECT * FROM books;
```

Только нужные столбцы:

```sql
SELECT title, price FROM books;
```

Фильтр по цене:

```sql
SELECT * FROM books WHERE price >= 300;
```

Сортировка по цене, от дорогих к дешевым:

```sql
SELECT * FROM books ORDER BY price DESC;
```

Только две записи:

```sql
SELECT * FROM books LIMIT 2;
```

Поиск названий, которые содержат `Python`:

```sql
SELECT * FROM books WHERE title LIKE '%Python%';
```

В `LIKE` знак `%` означает любое количество символов. Для точного поиска по `id` обычно используют `WHERE id = 1`.

## 6. Изменение данных. UPDATE

```sql
UPDATE books
SET price = 320.00
WHERE id = 1;
```

Команда изменяет цену книги с `id = 1`.

**Важно:** перед `UPDATE` и `DELETE` всегда проверяйте условие `WHERE`. Без него можно изменить или удалить все строки таблицы.

## 7. Удаление данных. DELETE

```sql
DELETE FROM books WHERE id = 1;
```

Эта команда удалит одну запись, если запись с таким `id` есть.

Перед удалением полезно выполнить:

```sql
SELECT * FROM books WHERE id = 1;
```

Так вы увидите, какую запись собираетесь удалить.

## 8. Подключаем Python к MySQL

Сам Python не содержит готового драйвера для MySQL. Поэтому для подключения установим одну библиотеку. Это не относится к парсеру из следующего конспекта: сам HTML-парсер будет написан только на стандартной библиотеке Python.

В терминале:

```bash
python -m pip install mysql-connector-python
```

Для подключения используем:

```python
import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="student",
    password="study_pass",
    database="study_db",
)

print("Подключились к MySQL")
connection.close()
```

Здесь показан учебный пароль. Для настоящего проекта пароль не нужно записывать прямо в код и отправлять в Git.

`connection` это соединение с сервером. Когда работа закончена, его надо закрыть.

### Что такое cursor

`cursor` нужен, чтобы отправлять SQL-команды через соединение.

```python
cursor = connection.cursor()
cursor.execute("SELECT title, price FROM books")
rows = cursor.fetchall()

for row in rows:
    print(row)

cursor.close()
```

Этот фрагмент выполняйте после создания `connection`, но до `connection.close()`.

`fetchall()` возвращает все полученные строки. `fetchone()` возвращает одну следующую строку или `None`, если строк больше нет.

## 9. Добавление записи из Python

```python
cursor = connection.cursor()

sql = "INSERT INTO books (title, author, price) VALUES (%s, %s, %s)"
values = ("Новая книга", "Олег", 420.00)

cursor.execute(sql, values)
connection.commit()

print("Новый id:", cursor.lastrowid)
cursor.close()
```

`%s` это место для значения. Драйвер сам передает значения из `values`. Так безопаснее, чем собирать SQL через f-строку из пользовательского ввода.

`commit()` сохраняет изменения. Если его забыть, изменения в таблицах InnoDB обычно не будут сохранены, потому что автосохранение в Connector/Python по умолчанию выключено.

Несколько записей:

```python
books = [
    ("Книга 1", "Алина", 100.00),
    ("Книга 2", "Роман", 150.00),
]

cursor = connection.cursor()
cursor.executemany(
    "INSERT INTO books (title, author, price) VALUES (%s, %s, %s)",
    books,
)
connection.commit()
cursor.close()
```

## 10. Чтение, изменение и удаление через Python

Чтение с условием:

```python
cursor = connection.cursor(dictionary=True)
cursor.execute(
    "SELECT id, title, price FROM books WHERE price >= %s",
    (300,),
)

for book in cursor.fetchall():
    print(book["id"], book["title"], book["price"])

cursor.close()
```

С `dictionary=True` каждая строка приходит как словарь. Для новичка это удобнее, чем искать поля по номеру.

Обратите внимание на `(300,)`. Запятая нужна, чтобы Python считал значение кортежем из одного элемента.

Изменение:

```python
cursor = connection.cursor()
cursor.execute(
    "UPDATE books SET price = %s WHERE id = %s",
    (390.00, 2),
)
connection.commit()
cursor.close()
```

Удаление:

```python
cursor = connection.cursor()
cursor.execute("DELETE FROM books WHERE id = %s", (2,))
connection.commit()
cursor.close()
```

Во всех запросах значения передаются отдельно. Никогда не делайте так с вводом пользователя:

```python
# Так делать не нужно:
# cursor.execute(f"SELECT * FROM books WHERE title = '{user_text}'")
```

## 11. Ошибки и откат изменений

Сервер может быть выключен, пароль может быть неверным, а SQL может содержать ошибку. Поэтому при работе с базой нужно обрабатывать исключения.

```python
import mysql.connector

connection = None
try:
    connection = mysql.connector.connect(
        host="localhost",
        user="student",
        password="study_pass",
        database="study_db",
    )
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO books (title, author, price) VALUES (%s, %s, %s)",
            ("Тест", "Анна", 200.00),
        )
        connection.commit()
    except mysql.connector.Error:
        connection.rollback()
        raise
    finally:
        cursor.close()
except mysql.connector.Error as error:
    print("Ошибка MySQL:", error)
finally:
    if connection is not None:
        connection.close()
```

- `commit()` подтверждает изменения.
- `rollback()` отменяет неподтвержденные изменения текущей транзакции.
- `finally` помогает закрыть курсор и соединение даже при ошибке.

Для `SELECT` обычно не нужен `commit()`. Он нужен при сохранении изменений, таких как `INSERT`, `UPDATE` и `DELETE`.

## 12. Полная программа с четырьмя операциями

Файл `examples/mysql_demo.py` показывает, как разделить действия с базой на небольшие функции. Его удобно запустить после выполнения `setup.sql`.

```bash
python examples/mysql_demo.py
```

Программа добавляет учебную запись, читает таблицу, изменяет цену и удаляет эту учебную запись. Другие книги она не удаляет.

Полный код:

```python
import os
from decimal import Decimal

import mysql.connector


def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="student",
        password=os.getenv("MYSQL_PASSWORD", "study_pass"),
        database="study_db",
    )


def add_book(connection, title, author, price):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO books (title, author, price) VALUES (%s, %s, %s)",
            (title, author, price),
        )
        book_id = cursor.lastrowid
        connection.commit()
        return book_id
    except mysql.connector.Error:
        connection.rollback()
        raise
    finally:
        cursor.close()


def get_books(connection, min_price=0):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, title, author, price FROM books "
            "WHERE price >= %s ORDER BY id",
            (min_price,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def update_price(connection, book_id, new_price):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE books SET price = %s WHERE id = %s",
            (new_price, book_id),
        )
        connection.commit()
    except mysql.connector.Error:
        connection.rollback()
        raise
    finally:
        cursor.close()


def delete_book(connection, book_id):
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        connection.commit()
    except mysql.connector.Error:
        connection.rollback()
        raise
    finally:
        cursor.close()


def main():
    connection = None
    try:
        connection = connect_db()
        book_id = add_book(
            connection, "Учебная книга", "Мария", Decimal("400.00")
        )
        print("Добавили книгу с id:", book_id)
        print("Книги:", get_books(connection))

        update_price(connection, book_id, Decimal("350.00"))
        print("После изменения:", get_books(connection))

        delete_book(connection, book_id)
        print("Учебную запись удалили")
    except mysql.connector.Error as error:
        print("Ошибка MySQL:", error)
    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
```

## 13. Как организовать работу с базой в проекте

Пока проект маленький, можно хранить функции `add_book`, `get_books`, `update_price`, `delete_book` в одном файле. Когда проект станет больше, их можно вынести в отдельный файл `database.py`.

Обычный порядок работы такой:

1. Подключились к MySQL.
2. Создали курсор.
3. Выполнили запрос.
4. Прочитали результат или вызвали `commit()`.
5. Закрыли курсор.
6. Закрыли соединение, когда оно больше не нужно.

Для реального проекта создают отдельного пользователя MySQL с правами только на нужную базу. Пароль хранят вне исходного кода, например в переменных окружения. В примере ниже переменная `MYSQL_PASSWORD` может заменить учебный пароль:

```python
import os

password = os.getenv("MYSQL_PASSWORD", "study_pass")
```

Сменить пароль при запуске можно так:

```bash
# macOS и Linux
export MYSQL_PASSWORD="ваш_пароль"
```

```powershell
# Windows PowerShell
$env:MYSQL_PASSWORD="ваш_пароль"
```

Это команды для терминала, не для Python-файла. В учебных примерах используется `study_pass`, если переменная не задана.

## 14. Задания для практики

1. Создайте таблицу `students` с полями `id`, `name`, `age`.
2. Добавьте через SQL трех студентов.
3. Найдите студентов старше 18 лет с помощью `SELECT` и `WHERE`.
4. Напишите Python-функцию, которая добавляет студента, используя `%s`.
5. Измените возраст одного студента, затем удалите его по `id`.
6. Выключите сервер MySQL и посмотрите, какое исключение появляется при подключении. Потом включите сервер обратно.

## 15. Частые ошибки

**Access denied:** неверный логин, пароль или права пользователя MySQL. Проверьте их и попробуйте подключиться через MySQL Workbench или клиент `mysql`.

**Unknown database:** база `study_db` еще не создана или в названии ошибка.

**Can't connect to MySQL server:** сервер не запущен или указаны неверные адрес и порт.

**ModuleNotFoundError: No module named 'mysql':** библиотека установлена не в тот Python, из которого запускается программа. Попробуйте `python -m pip install mysql-connector-python`.

**Запись не появилась:** проверьте, вызван ли `connection.commit()`.

**Ошибка SQL около %s:** в Connector/Python значения должны идти вторым аргументом `execute()`. Не подставляйте их вручную в строку.

### Справка

- [Официальная документация MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/)
- [Подключение к MySQL](https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html)
- [Выполнение SQL-запросов](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html)

Здесь важно освоить не все команды MySQL, а базовый цикл: подключиться, выполнить запрос, получить данные, сохранить изменения и закрыть соединение.
