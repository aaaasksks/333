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
