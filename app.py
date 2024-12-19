from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
# conn = sqlite3.connect('poems_base.db')

@app.route('/')
def best_authors():
    conn = sqlite3.connect('poems_base.db')
    cur = conn.cursor()
    cur.execute("SELECT author FROM best_month ORDER BY rang")
    authors = cur.fetchall()
    conn.close()
    print(authors)

    return render_template('best_authors.html', authors=authors[:25])

@app.route(f'/author/<author_name>')
def author(author_name):
    conn = sqlite3.connect('poems_base.db')
    cur = conn.cursor()
    cur.execute("SELECT article, poem FROM Poems WHERE author = author_name")
    rows = cur.fetchall()
    poems = []
    for row in rows:
        poem = {
            "article": row[0],
            "poem": row[0],

        }
        poems.append(poem)
    conn.close()
    print(poems)

    return render_template('authors.html', poems=poems)

if __name__ == "__main__":
    app.run(debug=True)
