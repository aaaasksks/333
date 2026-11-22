# ООП в Python. Самое нужное для начала

Этот конспект рассчитан на тех, кто уже знает переменные, `if`, циклы и функции. Здесь только четыре темы: классы, методы, наследование и исключения.

Лучше не читать все подряд. Запускайте каждый пример и меняйте в нем по одной строке. Так быстрее становится понятно, как работает код.

## 1. Класс и объект

Допустим, в программе есть книги. У каждой книги есть название и автор. Можно хранить их в отдельных переменных, но с классом удобнее.

Класс описывает, какие данные и действия будут у объекта. Объект это конкретная книга, созданная по этому описанию.

```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author


book1 = Book("Python с нуля", "Анна")
book2 = Book("Изучаем SQL", "Иван")

print(book1.title)   # Python с нуля
print(book2.author)  # Иван
```

Разберем строки.

- `class Book:` создает класс с именем `Book`.
- `__init__` срабатывает, когда мы создаем новый объект.
- `title` и `author` это значения, которые мы передаем при создании.
- `self.title` и `self.author` это данные, которые сохраняются внутри конкретного объекта. Их называют атрибутами.
- `book1` и `book2` это два разных объекта. Изменение одного не меняет другой.

Проверим последнее утверждение.

```python
book1.title = "Новый учебник"
print(book1.title)  # Новый учебник
print(book2.title)  # Изучаем SQL
```

### Зачем нужен self

`self` указывает на объект, с которым мы работаем. Внутри класса пишем `self.title`, чтобы обратиться к названию именно этой книги.

При вызове `Book("Python", "Анна")` Python сам передает созданный объект в параметр `self`. Писать `self` при создании объекта не нужно.

## 2. Методы

Метод это обычная функция, которую мы написали внутри класса. Обычно метод работает с данными объекта.

```python
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

    def show_info(self):
        print(f"Студент: {self.name}, оценка: {self.grade}")

    def change_grade(self, new_grade):
        self.grade = new_grade


student = Student("Алина", 4)
student.show_info()
student.change_grade(5)
student.show_info()
```

Результат:

```text
Студент: Алина, оценка: 4
Студент: Алина, оценка: 5
```

Здесь `show_info()` выводит информацию, а `change_grade()` изменяет ее. Вызов метода выглядит так: `student.show_info()`.

Метод может возвращать результат через `return`.

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


rect = Rectangle(3, 4)
print(rect.area())  # 12
```

Если результат нужен в другом месте программы, чаще удобно использовать `return`, а не `print` внутри метода.

## 3. Наследование

Иногда несколько классов очень похожи. Например, есть обычные книги и электронные книги. У обеих есть название и автор, но у электронной книги еще есть размер файла.

Вместо повторения кода можно создать один класс на основе другого.

```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def info(self):
        return f"{self.title}, автор: {self.author}"


class EBook(Book):
    def __init__(self, title, author, file_size_mb):
        super().__init__(title, author)
        self.file_size_mb = file_size_mb

    def info(self):
        return f"{super().info()}, файл: {self.file_size_mb} МБ"


paper = Book("Python", "Анна")
digital = EBook("SQL", "Иван", 3)

print(paper.info())
print(digital.info())
```

Результат:

```text
Python, автор: Анна
SQL, автор: Иван, файл: 3 МБ
```

Что здесь важно:

- `EBook(Book)` означает, что `EBook` наследуется от `Book`.
- `super().__init__(...)` вызывает создание основных данных, которое уже есть у родительского класса.
- В `EBook` мы добавляем свой атрибут `file_size_mb`.
- Метод `info()` есть у обоих классов. В дочернем классе мы изменили его работу. Это называется переопределением метода.
- `super().info()` вызывает версию метода из родительского класса.

Наследование полезно, когда есть общая логика и небольшие отличия. Не нужно создавать наследников для каждой мелочи.

## 4. Исключения и try/except

Ошибка не всегда означает, что программа написана неправильно. Пользователь может ввести текст вместо числа или запросить книгу, которой нет.

В Python для таких ситуаций есть исключения.

```python
try:
    age = int(input("Сколько вам лет? "))
    print("Ваш возраст:", age)
except ValueError:
    print("Нужно ввести целое число")
```

Если введено `20`, программа выведет число. Если введено `привет`, `int()` вызовет `ValueError`, и выполнится блок `except`.

Можно обработать разные ошибки отдельно.

```python
try:
    number = int(input("Введите число: "))
    result = 100 / number
except ValueError:
    print("Это не целое число")
except ZeroDivisionError:
    print("На ноль делить нельзя")
else:
    print("Результат:", result)
finally:
    print("Проверка закончена")
```

- `try` содержит код, где может произойти ошибка.
- `except` обрабатывает конкретное исключение.
- `else` выполняется, если исключения не было.
- `finally` выполняется в любом случае. Его часто используют, чтобы закрыть файл или соединение с базой.

Не стоит ставить пустой `except:` вокруг всей программы. Он может скрыть настоящую ошибку, которую нужно исправить.

## 5. Как создать свое исключение

Иногда нужно сообщить об ошибке, связанной с правилами нашей программы. Для этого создают свой класс исключения.

```python
class BookNotFoundError(Exception):
    pass


class Library:
    def __init__(self):
        self.books = []

    def add(self, title):
        self.books.append(title)

    def find(self, title):
        if title not in self.books:
            raise BookNotFoundError(f"Книга '{title}' не найдена")
        return title


library = Library()
library.add("Python")

try:
    print(library.find("SQL"))
except BookNotFoundError as error:
    print("Ошибка:", error)
```

`raise` означает: создать исключение и сообщить, что дальнейшее выполнение в этом месте невозможно.

`BookNotFoundError(Exception)` тоже пример наследования. Мы создали свой вид ошибки на основе стандартного класса `Exception`.

## 6. Полный пример

В файле `examples/oop_demo.py` собраны все темы сразу. Там есть обычная книга, электронная книга, библиотека и собственное исключение.

Запуск из папки с конспектами:

```bash
python examples/oop_demo.py
```

Полный код примера:

```python
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
```

## 7. Что стоит попробовать самому

1. Создайте класс `Car` с атрибутами `brand` и `year`. Добавьте метод `info()`.
2. Создайте класс `ElectricCar(Car)` с дополнительным атрибутом `battery`. Переопределите `info()`.
3. В `Car` добавьте проверку: если год меньше 1886, вызывайте `ValueError`.
4. Создайте два объекта и убедитесь, что у каждого свои атрибуты.

Как проверить себя: создание объекта работает через имя класса, метод вызывается через точку, наследник использует `super()`, а неверные данные приводят к понятной ошибке.

## 8. Частые ошибки

**Забыли self:** внутри метода написали `print(name)` вместо `print(self.name)`. Python не знает, откуда брать переменную `name`.

**Забыли скобки:** `student.show_info` это ссылка на метод. Для запуска нужны `student.show_info()`.

**Не вызвали super():** в наследнике написали новый `__init__`, но не создали родительские атрибуты. Тогда, например, `self.title` может отсутствовать.

**Путают класс и объект:** `Student` это описание, а `Student("Алина", 4)` создает объект.

**Ловят все ошибки подряд:** используйте `except ValueError`, `except BookNotFoundError` и другие подходящие типы. Так легче понять причину проблемы.

После этого конспекта достаточно уметь самостоятельно написать небольшой класс, добавить ему два метода, создать наследника и обработать ошибку.
