from flask import Flask, request, redirect, render_template, url_for, send_file
import sqlite3
import string
import random
import qrcode
from io import BytesIO

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def generate_short_url(length=6):
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(length))
    return short_url


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        length = int(request.form['length']) if 'length' in request.form and request.form['length'].isdigit() else 6
        short_url = generate_short_url(length)

        # Сохраняем ссылки в базе данных
        conn = get_db_connection()
        conn.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)',
                     (original_url, short_url))
        conn.commit()
        conn.close()

        return render_template('index.html', short_url=short_url)
    return render_template('index.html')

@app.route('/<short_url>')
def redirect_url(short_url):
    conn = get_db_connection()
    url_data = conn.execute('SELECT original_url FROM urls WHERE short_url = ?',
                            (short_url,)).fetchone()
    conn.close()
    if url_data:
        return redirect(url_data['original_url'])
    else:
        return '<h1>URL не найден</h1>'

@app.route('/qr/<short_url>')
def generate_qr_code(short_url):
    url = f"{request.host_url}{short_url}"
    qr = qrcode.make(url)
    qr_io = BytesIO()
    qr.save(qr_io, 'PNG')
    qr_io.seek(0)
    return send_file(qr_io, mimetype='image/png')

def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY, original_url TEXT, short_url TEXT)')
    conn.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
