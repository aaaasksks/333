# Учебный проект. Парсер товаров с сохранением в MySQL

Теперь используем вместе темы из предыдущих конспектов. Напишем программу, которая открывает HTML-каталог, читает товары, создает объекты Python и сохраняет информацию в MySQL.

Это небольшой проект, поэтому весь Python-код находится в одном файле. Так проще проследить ход выполнения. Когда разберетесь, его можно разделить на несколько файлов.

## 1. Что должна делать программа

У нас есть каталог из трех товаров. Для каждого товара указаны код, название, цена и, иногда, скидка.

Программа должна:

1. Прочитать файл `catalog.html`.
2. Найти в HTML карточки товаров.
3. Создать объекты `Product` или `DiscountProduct`.
4. Посчитать цену с учетом скидки.
5. Подключиться к MySQL и сохранить товары.
6. Прочитать таблицу из базы и показать результат.

Схема работы:

```text
catalog.html
     |
     v
CatalogParser
     |
     v
Product / DiscountProduct
     |
     v
ProductRepository
     |
     v
MySQL, таблица products
     |
     v
Вывод товаров в терминал
```

## 2. Файлы проекта

В архиве есть папка `examples`:

```text
examples/
    setup.sql
    catalog.html
    project.py
    oop_demo.py
    mysql_demo.py
    parser_demo.py
```

Для итогового проекта нужны только первые три файла. Остальные оставлены для практики по отдельным темам.

## 3. Подготовка

Нужны Python, MySQL Server и пакет для подключения к MySQL:

```bash
python -m pip install mysql-connector-python
```

HTML-парсер в проекте использует стандартный `html.parser`. Дополнительный пакет нужен только для работы с MySQL.

Создайте базу и таблицы. Если вы еще не выполняли команды из второго конспекта, подключитесь к MySQL как администратор и запустите SQL из `examples/setup.sql`.

В MySQL Workbench можно открыть файл `setup.sql` и выполнить все команды. Либо в консоли клиента MySQL выполните команды ниже:

```sql
CREATE DATABASE IF NOT EXISTS study_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'student'@'localhost'
    IDENTIFIED BY 'study_pass';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE
    ON study_db.* TO 'student'@'localhost';

USE study_db;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
```

Код `sku` уникальный. Если запустить парсер повторно, существующий товар обновится, а не добавится второй раз. Это пригодится, когда мы будем менять цены в HTML.

Пароль `study_pass` используется только как пример для локального обучения. Для реального проекта создают свой пароль и хранят его вне кода.

## 4. Исходный HTML

Посмотрите файл `examples/catalog.html`. Одна карточка товара выглядит так:

```html
<article class="product" data-sku="P002" data-discount="10">
    <h2 class="name">Синяя <strong>ручка</strong></h2>
    <span class="price">50.00</span>
</article>
```

- `class="product"` говорит парсеру, где начинается карточка.
- `data-sku="P002"` хранит код товара.
- `data-discount="10"` означает скидку 10 процентов.
- `h2` содержит название.
- `span` содержит исходную цену.

У ручки исходная цена 50.00. После скидки 10 процентов получится 45.00.

В учебном HTML всего три товара. Файл можно открыть в браузере или редакторе, но для работы программы браузер не нужен.

## 5. Класс Product

Начнем с обычного товара. У него есть код, название и цена. Метод `final_price()` возвращает цену, которую мы будем сохранять в базе.

```python
from decimal import Decimal, InvalidOperation


class CatalogError(Exception):
    pass


class Product:
    def __init__(self, sku, name, price):
        if not sku.strip() or not name.strip():
            raise CatalogError("У товара должны быть код и название")

        try:
            parsed_price = Decimal(price.strip().replace(",", "."))
        except InvalidOperation as error:
            raise CatalogError(f"Неверная цена у товара {sku}") from error

        if not parsed_price.is_finite() or parsed_price < 0:
            raise CatalogError(f"Цена должна быть неотрицательной: {sku}")

        self.sku = sku.strip()
        self.name = name.strip()
        self.price = parsed_price

    def final_price(self):
        return self.price.quantize(Decimal("0.01"))
```

Здесь несколько знакомых вещей:

- `class Product` создает класс.
- `__init__` сохраняет данные в объекте.
- `final_price()` это метод класса.
- `CatalogError` это собственное исключение.
- `raise` сообщает, что данные неправильные.

Для цены используем `Decimal`, а не `float`. Это удобно при расчетах денежных сумм. Например, `Decimal("50.00")` хранит десятичное значение без обычных для `float` погрешностей двоичного представления.

## 6. Наследование. Товар со скидкой

Скидочный товар похож на обычный. У него есть те же поля, но итоговая цена вычисляется иначе.

```python
class DiscountProduct(Product):
    def __init__(self, sku, name, price, discount):
        super().__init__(sku, name, price)
        try:
            self.discount = int(discount)
        except ValueError as error:
            raise CatalogError(f"Неверная скидка у товара {sku}") from error
        if not 0 <= self.discount <= 100:
            raise CatalogError(f"Скидка должна быть от 0 до 100: {sku}")

    def final_price(self):
        factor = (Decimal(100) - Decimal(self.discount)) / Decimal(100)
        return (self.price * factor).quantize(Decimal("0.01"))
```

`DiscountProduct(Product)` наследует основные поля от `Product`.

`super().__init__(...)` создает общую часть товара. Затем дочерний класс сохраняет скидку и переопределяет метод `final_price()`.

Проверка:

```python
item = DiscountProduct("P002", "Синяя ручка", "50.00", "10")
print(item.final_price())  # 45.00
```

Теперь при работе с товаром можно всегда вызывать `product.final_price()`. Объект сам решит, нужно ли применять скидку. Это и есть практический смысл переопределения метода.

## 7. Класс парсера

Дальше нужен класс, который наследуется от `HTMLParser` и собирает товары из HTML. Его зовут `CatalogParser`.

Внутри него три основных метода:

- `handle_starttag` находит начало карточки, название и цену.
- `handle_data` собирает текст.
- `handle_endtag` завершает карточку и создает объект товара.

Когда заканчивается тег `article`, парсер смотрит на скидку. Если она равна нулю, он создает `Product`. Иначе создает `DiscountProduct`.

Если название пустое или цена неправильная, конструктор товара вызовет `CatalogError`. Так мы сразу заметим ошибку в данных, а не сохраним неправильную запись.

## 8. Класс для работы с MySQL

`ProductRepository` отвечает только за базу данных. Сам парсер ничего не знает про SQL. Это упрощает программу.

В репозитории есть два метода:

- `save_all(products)` записывает товары.
- `get_all()` читает все товары.

При сохранении используется запрос с параметрами `%s`. Значения не вставляются в SQL через f-строки.

```sql
INSERT INTO products (sku, name, price)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE name = %s, price = %s
```

Это означает: если товара с таким `sku` еще нет, добавляем его. Если он уже есть, обновляем название и цену. В коде значения передаются отдельно, вторым аргументом `cursor.execute(...)`.

После успешной записи вызываем `commit()`. Если MySQL сообщает об ошибке, вызываем `rollback()`, чтобы откатить неподтвержденные изменения.

## 9. Полный код project.py

Ниже вся программа. Файл с тем же кодом находится в `examples/project.py`. Не нужно перепечатывать его вручную, можно сначала запустить готовый, а потом разбирать функции по одной.

```python
import os
import sys
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import mysql.connector


class CatalogError(Exception):
    pass


class Product:
    def __init__(self, sku, name, price):
        if not sku.strip() or not name.strip():
            raise CatalogError("У товара должны быть код и название")

        try:
            parsed_price = Decimal(price.strip().replace(",", "."))
        except InvalidOperation as error:
            raise CatalogError(f"Неверная цена у товара {sku}") from error

        if not parsed_price.is_finite() or parsed_price < 0:
            raise CatalogError(f"Цена должна быть неотрицательной: {sku}")

        self.sku = sku.strip()
        self.name = name.strip()
        self.price = parsed_price

    def final_price(self):
        return self.price.quantize(Decimal("0.01"))


class DiscountProduct(Product):
    def __init__(self, sku, name, price, discount):
        super().__init__(sku, name, price)
        try:
            self.discount = int(discount)
        except ValueError as error:
            raise CatalogError(f"Неверная скидка у товара {sku}") from error
        if not 0 <= self.discount <= 100:
            raise CatalogError(f"Скидка должна быть от 0 до 100: {sku}")

    def final_price(self):
        factor = (Decimal(100) - Decimal(self.discount)) / Decimal(100)
        return (self.price * factor).quantize(Decimal("0.01"))


class CatalogParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.products = []
        self.current = None
        self.field = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()

        if tag == "article" and "product" in classes:
            self.current = {
                "sku": attributes.get("data-sku", ""),
                "discount": attributes.get("data-discount", "0"),
                "name": "",
                "price": "",
            }
            return

        if self.current is None:
            return
        if tag == "h2" and "name" in classes:
            self.field = "name"
        elif tag == "span" and "price" in classes:
            self.field = "price"

    def handle_data(self, data):
        if self.current is not None and self.field is not None:
            self.current[self.field] += data

    def handle_endtag(self, tag):
        if tag == "h2" and self.field == "name":
            self.field = None
        elif tag == "span" and self.field == "price":
            self.field = None
        elif tag == "article" and self.current is not None:
            data = self.current
            if data["discount"] == "0":
                product = Product(data["sku"], data["name"], data["price"])
            else:
                product = DiscountProduct(
                    data["sku"], data["name"], data["price"],
                    data["discount"],
                )
            self.products.append(product)
            self.current = None
            self.field = None


def read_html(source):
    if source.startswith(("https://", "http://")):
        request = Request(source, headers={"User-Agent": "StudyParser/1.0"})
        with urlopen(request, timeout=10) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset)
    return Path(source).read_text(encoding="utf-8")


class ProductRepository:
    def __init__(self, connection):
        self.connection = connection

    def save_all(self, products):
        cursor = self.connection.cursor()
        try:
            for product in products:
                cursor.execute(
                    "INSERT INTO products (sku, name, price) "
                    "VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE name = %s, price = %s",
                    (
                        product.sku,
                        product.name,
                        product.final_price(),
                        product.name,
                        product.final_price(),
                    ),
                )
            self.connection.commit()
        except mysql.connector.Error:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def get_all(self):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT sku, name, price FROM products ORDER BY sku"
            )
            return cursor.fetchall()
        finally:
            cursor.close()


def main():
    source = (
        sys.argv[1]
        if len(sys.argv) > 1
        else str(Path(__file__).with_name("catalog.html"))
    )
    try:
        html = read_html(source)
        parser = CatalogParser()
        parser.feed(html)
        if not parser.products:
            raise CatalogError("В каталоге не найдены товары")

        connection = mysql.connector.connect(
            host="localhost",
            user="student",
            password=os.getenv("MYSQL_PASSWORD", "study_pass"),
            database="study_db",
        )
        try:
            repository = ProductRepository(connection)
            repository.save_all(parser.products)
            for row in repository.get_all():
                print(row["sku"], row["name"], row["price"])
        finally:
            connection.close()
    except (CatalogError, OSError, UnicodeError, URLError,
            mysql.connector.Error) as error:
        print("Не удалось выполнить проект:", error)


if __name__ == "__main__":
    main()
```

## 10. Как запустить проект

Откройте терминал в папке с конспектами.

Сначала убедитесь, что MySQL Server запущен и SQL из `setup.sql` выполнен. Затем установите драйвер и запустите программу:

```bash
python -m pip install mysql-connector-python
python examples/project.py
```

Если используется пароль, отличный от учебного, задайте переменную окружения до запуска.

macOS или Linux:

```bash
export MYSQL_PASSWORD="ваш_пароль"
python examples/project.py
```

Windows PowerShell:

```powershell
$env:MYSQL_PASSWORD="ваш_пароль"
python examples/project.py
```

Ожидаемый вывод для неизмененного каталога, если таблица `products` до этого была пустой:

```text
P001 Блокнот 120.00
P002 Синяя ручка 45.00
P003 Карандаш 30.00
```

В таблице хранится цена после скидки. Исходную цену и размер скидки отдельно мы пока не сохраняем. Это можно сделать как дополнительное задание.

Проверить результат в MySQL:

```sql
USE study_db;
SELECT sku, name, price FROM products ORDER BY sku;
```

### Проверка повторного запуска

Запустите `python examples/project.py` еще раз. Новые строки для `P001`, `P002`, `P003` не должны появиться: у таблицы есть уникальный столбец `sku`, а запрос обновляет найденные товары.

Теперь откройте `examples/catalog.html`, измените цену блокнота с `120.00` на `150.00` и запустите программу еще раз. В базе у `P001` станет новая цена.

## 11. Как все части связаны между собой

Проследим один товар, синюю ручку.

**Шаг 1.** Функция `read_html()` читает HTML. По умолчанию это файл `catalog.html`. Она умеет также загружать страницу по URL с помощью стандартного `urllib.request`.

**Шаг 2.** `CatalogParser` находит `article` с кодом `P002`. Из тегов получает название `Синяя ручка` и цену `50.00`.

**Шаг 3.** Парсер видит `data-discount="10"` и создает `DiscountProduct`. Здесь используется наследование.

**Шаг 4.** Метод `final_price()` вычисляет `45.00`. Здесь работает метод дочернего класса.

**Шаг 5.** `ProductRepository.save_all()` выполняет параметризованный SQL-запрос и сохраняет `P002`, название и `45.00` в MySQL.

**Шаг 6.** `ProductRepository.get_all()` делает `SELECT`. Программа выводит сохраненные строки в терминал.

**Шаг 7.** Если во время обработки обнаружится неверная цена, возникнет `CatalogError`. Если проблема с MySQL, возникнет исключение драйвера MySQL. В `main()` эти ошибки выводятся понятным сообщением.

Так каждая часть программы делает свою работу. Класс товара отвечает за данные и цену. Парсер отвечает за HTML. Репозиторий отвечает за SQL.

## 12. Где здесь ООП, MySQL, парсер и исключения

| Тема | Где используется |
| --- | --- |
| Классы | `Product`, `DiscountProduct`, `CatalogParser`, `ProductRepository` |
| Методы | `__init__`, `final_price`, `save_all`, `get_all` |
| Наследование | `DiscountProduct(Product)`, `CatalogParser(HTMLParser)` |
| Исключения | `CatalogError`, `raise`, `try`, `except`, `finally` |
| MySQL | подключение, `INSERT`, `UPDATE` при повторной записи, `SELECT`, `commit`, `rollback` |
| Парсер | `read_html`, `HTMLParser`, `handle_starttag`, `handle_data`, `handle_endtag` |

## 13. Если появилась ошибка

**ModuleNotFoundError: No module named 'mysql':** установите драйвер в тот же Python, которым запускаете проект: `python -m pip install mysql-connector-python`.

**Access denied for user 'student':** проверьте пароль и права пользователя в MySQL. При необходимости задайте `MYSQL_PASSWORD`.

**Unknown database 'study_db' или таблица products не найдена:** сначала выполните `examples/setup.sql`.

**Не удалось выполнить проект: ... Неверная цена:** проверьте значения внутри `<span class="price">` в HTML.

**В таблице старые значения:** проверьте, что вы редактировали именно файл `examples/catalog.html`, а не его копию в другой папке.

**Товары не найдены:** откройте HTML и проверьте, что карточки имеют `class="product"`, название находится в `h2 class="name"`, а цена в `span class="price"`.

## 14. Небольшие задания по готовому проекту

Делайте задания по одному, после каждого запускайте программу.

1. Добавьте четвертый товар с кодом `P004` и ценой `75.00`.
2. Установите скидку 20 процентов на карандаш. Проверьте итоговую цену в MySQL.
3. Сделайте метод `get_by_sku(sku)` в `ProductRepository`. Он должен находить один товар через `SELECT ... WHERE sku = %s` и `fetchone()`.
4. Добавьте метод `delete_by_sku(sku)`, который удаляет только один товар по коду. Не забывайте `commit()`.
5. Добавьте в таблицу поле `original_price DECIMAL(10, 2)` и сохраняйте отдельно цену до скидки. Для этого придется изменить SQL таблицы и метод `save_all()`.
6. Попробуйте передать название без текста или отрицательную цену и посмотрите, какое исключение выдаст программа.

Для четвертого задания пригодится такой фрагмент:

```python
def delete_by_sku(self, sku):
    cursor = self.connection.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE sku = %s", (sku,))
        self.connection.commit()
    except mysql.connector.Error:
        self.connection.rollback()
        raise
    finally:
        cursor.close()
```

Этот метод нужно добавить внутрь класса `ProductRepository`. В нашем готовом проекте удаление специально не вызывается автоматически, чтобы не стирать товары при каждом запуске.

## 15. Что студент должен уметь после проекта

Не обязательно запоминать весь код. Важно понимать последовательность действий:

- Откуда программа берет данные.
- Как парсер превращает HTML в значения.
- Почему товар хранится в объекте класса.
- Чем отличается обычный товар от товара со скидкой.
- Как подготовить SQL и передать значения через `%s`.
- Зачем нужны `commit()`, `rollback()` и обработка ошибок.

Если вы можете самостоятельно добавить новое поле товара, показать его в выводе и сохранить в базу, значит основные идеи усвоены.
