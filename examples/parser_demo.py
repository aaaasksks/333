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
