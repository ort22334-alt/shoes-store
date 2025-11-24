from flask import Flask, jsonify, send_from_directory, request
import sqlite3
import os

app = Flask(__name__, static_folder='.')

# Путь к базе
DB_PATH = "shoes.db"

# Инициализация базы данных
def init_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL,
                    image_path TEXT DEFAULT 'static/placeholder.jpg'
                )
            """)
            # Тестовые данные
            conn.executemany(
                "INSERT INTO products (name, brand, price, stock) VALUES (?, ?, ?, ?)",
                [
                    ("Кроссовки Air Run", "Nike", 4999, 12),
                    ("Зимние ботинки", "Timberland", 8999, 5),
                    ("Летние сандалии", "Adidas", 3499, 18),
                ],
            )

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/products")
def get_products():
    search = request.args.get("search", "").lower()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if search:
        cursor.execute("SELECT * FROM products WHERE LOWER(name) LIKE ? OR LOWER(brand) LIKE ?", 
                       (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    products = [
        {"id": r[0], "name": r[1], "brand": r[2], "price": r[3], "stock": r[4], "image_path": r[5]}
        for r in rows
    ]
    return jsonify(products)

# Запуск
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
