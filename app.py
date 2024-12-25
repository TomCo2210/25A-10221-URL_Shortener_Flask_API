from flask import Flask, request, jsonify, redirect
from flasgger import Swagger
import sqlite3
import hashlib


app = Flask(__name__)
swagger = Swagger(app)

def create_table():
    connection = get_db_connection()
    connection.execute('''CREATE TABLE IF NOT EXISTS url_mapping (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_url TEXT NOT NULL,
                        short_url TEXT NOT NULL)''')
    connection.commit()
    connection.close()


def get_db_connection():
    connection = sqlite3.connect('url.db')
    connection.row_factory = sqlite3.Row
    return connection


def generate_short_url(original_url):
    hash_object = hashlib.md5(original_url.encode())
    return hash_object.hexdigest()[:8]


@app.route('/shorten', methods=['POST'])
def shorten():
    """
    Shorten the URL
    --- 
    parameters:
      - name: url
        in: body
        required: true
        example: { "url": "https://www.google.com" }
    responses:
        200:
            description: Shortened URL
            example: http://localhost:5000/abc123
    """
    original_url = request.json['url']
    shorten_url = generate_short_url(original_url)

    db_connection = get_db_connection()

    db_connection.execute('INSERT INTO url_mapping (original_url, short_url) VALUES (?, ?)', (original_url, shorten_url))
    db_connection.commit()
    db_connection.close()

    return jsonify({'short_url': shorten_url})


@app.route('/shorten/<short_url>', methods=['GET'])
def redirect_url(short_url):
    """
    Get the original URL
    ---
    parameters:
        - name: short_url
          in: path
          type: string
          required: true

    responses:
        200:
            description: Redirect to the original URL
        404:
            description: URL not found
    """
    db_connection = get_db_connection()
    url_data = db_connection.execute('SELECT original_url FROM url_mapping WHERE short_url = ?', (short_url,)).fetchone()
    # print(url_data)
    db_connection.close()

    if url_data:
        return redirect(url_data['original_url'])
        # return jsonify({'original_url': url_data['original_url']}), 200
    return jsonify({'error': 'URL not found'}), 404

if __name__ == '__main__':
    create_table()
    app.run(debug=True,host='0.0.0.0',port=5000)
