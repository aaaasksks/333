class BookNotFoundError(Exception):
    pass


class Book:
    def __init__(self, title, author):
        if not title.strip():
            raise ValueError("Название книги не может быть пустым")
        self.title = title
        self.author = author

    def info(self):
        return f"{self.title}, автор: {self.author}"


class EBook(Book):
    def __init__(self, title, author, file_size_mb):
        super().__init__(title, author)
        if file_size_mb <= 0:
            raise ValueError("Размер файла должен быть больше нуля")
        self.file_size_mb = file_size_mb

    def info(self):
        return f"{super().info()}, файл: {self.file_size_mb} МБ"


class Library:
    def __init__(self):
        self.books = []

    def add(self, book):
        self.books.append(book)

    def find(self, title):
        for book in self.books:
            if book.title == title:
                return book
        raise BookNotFoundError(f"Книга '{title}' не найдена")


library = Library()
library.add(Book("Python с нуля", "Анна"))
library.add(EBook("SQL для начинающих", "Иван", 3))

for book in library.books:
    print(book.info())

try:
    print(library.find("Нет такой книги").info())
except BookNotFoundError as error:
    print("Ошибка:", error)
