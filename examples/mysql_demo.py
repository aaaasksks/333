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
