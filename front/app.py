from flask import Flask, g, render_template, request
import sqlite3
import os

app = Flask(__name__)
DATABASE = './mnt/data/db.sqlite3'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/board')
def board():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    cursor = db.execute('SELECT title, url FROM search_post LIMIT ? OFFSET ?', (per_page, offset))
    posts = cursor.fetchall()
    total_posts = db.execute('SELECT COUNT(*) FROM search_post').fetchone()[0]
    total_pages = (total_posts + per_page - 1) // per_page
    return render_template('board.html', posts=posts, page=page, total_pages=total_pages)

if __name__ == '__main__':
    app.run(debug=True)
