# Парсер на Python без внешних библиотек

Парсер это программа, которая получает текст в определенном формате и достает из него нужные данные. Например, из HTML-страницы можно получить названия товаров, цены и ссылки.

Для начала не нужны `requests`, `BeautifulSoup` или `selenium`. Мы используем инструменты, которые уже входят в Python:

- `pathlib` для чтения локальных файлов.
- `urllib.request` для загрузки страниц по адресу.
- `html.parser` для разбора HTML.
- `json` для данных в формате JSON.

Ничего устанавливать через `pip` для этого конспекта не нужно.

## 1. Что именно мы будем разбирать

Возьмем простой HTML:

```html
<article class="product" data-sku="P001">
    <h2 class="name">Блокнот</h2>
    <span class="price">120.00</span>
</article>
```

Нас интересуют три значения:

```text
Код: P001
Название: Блокнот
Цена: 120.00
```

HTML состоит из тегов, текста и атрибутов. Например, `article` это тег, `class="product"` это атрибут, а `Блокнот` это текст внутри тега `h2`.

## 2. Сначала читаем HTML из файла

В папке `examples` уже есть файл `catalog.html`. Откройте его в редакторе и посмотрите, как записаны товары.

Самый простой способ прочитать файл:

```python
from pathlib import Path

html = Path("examples/catalog.html").read_text(encoding="utf-8")
print(html[:200])
```

Запускать этот пример нужно из папки, в которой находятся конспекты и каталог `examples`.

`read_text()` возвращает строку. `encoding="utf-8"` говорит, как прочитать русские буквы.

Первый раз удобнее учиться на локальном HTML. Тогда результат не зависит от интернета, блокировок сайта или изменений его оформления.

## 3. Как скачать HTML-страницу

Когда парсер работает с сайтом, страницу сначала нужно загрузить. Для этого есть `urllib.request`.

```python
from urllib.request import Request, urlopen

url = "https://example.com/"
request = Request(url, headers={"User-Agent": "StudyParser/1.0"})

with urlopen(request, timeout=10) as response:
    charset = response.headers.get_content_charset() or "utf-8"
    html = response.read().decode(charset)

print(html[:200])
```

- `Request(...)` создает запрос к странице.
- `urlopen(...)` отправляет запрос.
- `timeout=10` не дает программе бесконечно ждать ответ.
- `read()` получает данные в байтах.
- `decode(...)` превращает байты в обычный текст.
- `with` закрывает ответ после чтения.

`example.com` здесь только для тренировки загрузки. Это не каталог с товарами.

Сетевая ошибка не должна ломать всю программу без понятного сообщения:

```python
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

try:
    with urlopen("https://example.com/", timeout=10) as response:
        print("Ответ сервера:", response.status)
except HTTPError as error:
    print("Сайт вернул код ошибки:", error.code)
except URLError as error:
    print("Не удалось открыть сайт:", error.reason)
```

## 4. Как работает HTMLParser

Модуль `html.parser` умеет разбирать HTML по частям. Мы создаем собственный класс, который наследуется от `HTMLParser`.

```python
from html.parser import HTMLParser


class SimpleParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Открылся тег:", tag)

    def handle_data(self, data):
        if data.strip():
            print("Текст:", data.strip())

    def handle_endtag(self, tag):
        print("Закрылся тег:", tag)


parser = SimpleParser()
parser.feed("<h2>Блокнот</h2>")
```

Результат:

```text
Открылся тег: h2
Текст: Блокнот
Закрылся тег: h2
```

Python сам вызывает три метода, когда встречает нужную часть HTML:

- `handle_starttag()` при открывающем теге.
- `handle_data()` при текстовом содержимом.
- `handle_endtag()` при закрывающем теге.

`feed()` передает HTML парсеру.

## 5. Как получить атрибуты тега

При открытии тега парсер получает `attrs`. Это список пар: имя атрибута и его значение.

```python
from html.parser import HTMLParser


class AttributeParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == "article":
            attributes = dict(attrs)
            print(attributes.get("data-sku"))


parser = AttributeParser()
parser.feed('<article class="product" data-sku="P001"></article>')
```

Результат: `P001`.

`dict(attrs)` превращает пары в словарь. Метод `.get()` возвращает значение по ключу. Если атрибута нет, можно задать значение по умолчанию: `attributes.get("data-sku", "")`.

## 6. Парсер учебного каталога

В `examples/catalog.html` есть три товара. Нам нужно собрать код, название и цену каждого товара в один словарь.

Здесь пригодится переменная `current`. Она хранит товар, который мы читаем сейчас. Переменная `field` запоминает, читаем мы название или цену.

Полный рабочий пример находится в `examples/parser_demo.py`.

Запуск:

```bash
python examples/parser_demo.py
```

Код:

```python
from html.parser import HTMLParser
from pathlib import Path


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
            product = {
                key: value.strip()
                for key, value in self.current.items()
            }
            if all(product.values()):
                self.products.append(product)
            self.current = None
            self.field = None


file_path = Path(__file__).with_name("catalog.html")
html = file_path.read_text(encoding="utf-8")

parser = CatalogParser()
parser.feed(html)

for product in parser.products:
    print(product)
```

Результат:

```text
{'sku': 'P001', 'name': 'Блокнот', 'price': '120.00'}
{'sku': 'P002', 'name': 'Синяя ручка', 'price': '50.00'}
{'sku': 'P003', 'name': 'Карандаш', 'price': '30.00'}
```

Разберем, что делает этот класс.

1. Нашли тег `<article class="product">`. Создали пустой словарь `current`.
2. Нашли `<h2 class="name">`. Запомнили, что сейчас читаем название.
3. Метод `handle_data()` добавил текст к названию.
4. Нашли `<span class="price">`. Запомнили, что сейчас читаем цену.
5. Когда закончился `article`, сохранили словарь в список `products`.
6. Перешли к следующему товару.

Обратите внимание на строку `self.current[self.field] += data`. Мы не заменяем текст, а добавляем его. В HTML название может содержать вложенный тег:

```html
<h2 class="name">Синяя <strong>ручка</strong></h2>
```

Текст может прийти в метод `handle_data()` по частям. Поэтому его нужно собирать.

Также обратите внимание на проверку `if all(product.values())`. В этом учебном примере мы пропускаем товар, если у него пустые код, название или цена. В реальном проекте иногда лучше выдавать понятное исключение, чтобы не потерять запись незаметно. В четвертом конспекте сделаем именно так.

Этот учебный парсер рассчитан на показанную структуру карточек. Для произвольного HTML может понадобиться более подробное отслеживание вложенных тегов. Это нормально: парсер обычно пишут под конкретный формат страницы.

## 7. А если сайт отдает JSON

Иногда данные проще получить в формате JSON. Это текст с объектами и списками, который часто используется в API.

Например:

```json
[
    {"name": "Блокнот", "price": 120},
    {"name": "Ручка", "price": 50}
]
```

Разбор JSON есть в стандартной библиотеке Python:

```python
import json

text = '[{"name": "Блокнот", "price": 120}, {"name": "Ручка", "price": 50}]'
products = json.loads(text)

for product in products:
    print(product["name"], product["price"])
```

Результат:

```text
Блокнот 120
Ручка 50
```

`json.loads()` превращает строку JSON в списки и словари Python. Если сайт предоставляет открытый API, часто лучше использовать его, чем разбирать HTML. Но сначала проверьте условия использования API.

## 8. Почему не стоит разбирать HTML через обычный split

Например, искать название через `html.split("<h2>")` неудобно. Тег может содержать атрибуты, пробелы и вложенные элементы. Из-за небольшой перемены в HTML программа перестанет работать.

Регулярные выражения из модуля `re` полезны для простых строк с известным форматом, например для поиска номера заказа:

```python
import re

text = "Заказ №12345 принят"
match = re.search(r"№(\d+)", text)
if match:
    print(match.group(1))  # 12345
```

Для HTML лучше использовать `HTMLParser`. Он понимает, где начинается тег, где его атрибуты и где текст.

## 9. Что важно знать о парсинге сайтов

Не всякий сайт получится разобрать таким способом. `urllib` скачивает ответ сервера, но не запускает JavaScript, как браузер. Если товары появляются только после работы JavaScript, в полученном HTML их может не быть.

Также соблюдайте несколько простых правил:

- Сначала проверьте, разрешено ли автоматическое получение данных по правилам сайта и `robots.txt`.
- Не отправляйте десятки запросов подряд. Между запросами можно делать паузу через `time.sleep(1)`.
- Не пытайтесь обходить капчи, блокировки и закрытые разделы.
- Для обучения используйте локальные файлы или страницы, на которых разрешено практиковаться.

## 10. Задания

1. Добавьте в `catalog.html` четвертый товар.
2. Измените цену одного товара и запустите `parser_demo.py` повторно.
3. Добавьте в HTML тег `<span class="category">Канцелярия</span>` и научите парсер собирать категорию.
4. Сделайте вывод только тех товаров, у которых цена больше 50. Подсказка: `float(product["price"]) > 50`.
5. Напишите простой парсер, который собирает все ссылки `<a href="...">` со страницы.

## 11. Частые ошибки

**Вместо русского текста странные символы:** проверьте кодировку. Для учебного файла используйте `encoding="utf-8"`.

**Список товаров пустой:** посмотрите исходный HTML. Возможно, на странице другие классы или теги.

**Слова в названии пропали:** не перезаписывайте название в `handle_data()`, а добавляйте очередной кусочек через `+=`.

**Получили HTTP 403 или 429:** сайт ограничивает автоматические запросы. Не нужно пытаться обойти ограничение. Используйте разрешенный источник или локальный HTML.

**На сайте товар есть, но в загруженном HTML его нет:** возможно, сайт рисует товары с помощью JavaScript. `urllib` его не выполняет.

### Справка

- [html.parser в документации Python](https://docs.python.org/3/library/html.parser.html)
- [urllib.request в документации Python](https://docs.python.org/3/library/urllib.request.html)
- [Модуль json](https://docs.python.org/3/library/json.html)

Следующий конспект объединяет ООП, этот HTML-парсер и базу MySQL в одну программу.
