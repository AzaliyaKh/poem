from flask import Flask, render_template
import sqlite3
import datetime

app = Flask(__name__)

def create_db():
    conn = sqlite3.connect("DataBase.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Poems (
        id INTEGER PRIMARY KEY,
        article TEXT NOT NULL,
        author_id TEXT NOT NULL,
        text TEXT NOT NULL,
        FOREIGN KEY (author_id) REFERENCES Authors (id)
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Authors (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BestMonth (
        id INTEGER PRIMARY KEY,
        month_num INTEGER,
        author_id TEXT,
        rang INTEGER,
        FOREIGN KEY (author_id) REFERENCES Authors (id)
        )
        ''')
    conn.commit()
    conn.close()

@app.route('/')
def best_authors():
    conn = sqlite3.connect('DataBase.db')
    cur = conn.cursor()
    current_month = datetime.datetime.now().month
    cur.execute('''
    SELECT Authors.name, Authors.id
    FROM BestMonth 
    INNER JOIN Authors ON BestMonth.author_id = Authors.id
    WHERE BestMonth.month_num = ?
    ORDER BY BestMonth.rang DESC 
    ''', [current_month])
    rows = cur.fetchall()

    authors = []
    for row in rows:
        author = {
            'name': row[0],
            'id': row[1]
        }
        authors.append(author)
    conn.close()

    return render_template('best_authors.html', authors=authors)

@app.route('/<author_id>')
def author(author_id):
    if not author_id.isnumeric():
        return render_template('authors.html')

    conn = sqlite3.connect('DataBase.db')
    cur = conn.cursor()

    poems = []
    cur.execute("SELECT article, text FROM Poems WHERE author_id = ?", (author_id,))
    rows = cur.fetchall()

    for row in rows:
        text = row[1].split('\n')
        poem = {
            "article": row[0],
            "text": text,
        }
        poems.append(poem)

    cur.execute("SELECT name FROM Authors WHERE id = ?", (author_id,))
    author = cur.fetchall()[0][0]

    return render_template('authors.html', poems=poems, author=author)

if __name__ == "__main__":
    create_db()
    app.run(debug=True)
