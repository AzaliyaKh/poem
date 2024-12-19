from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
# conn = sqlite3.connect('poems_base.db')

@app.route('/')
def best_authors():
    conn = sqlite3.connect('poems_base.db')
    cur = conn.cursor()
    cur.execute("SELECT author FROM best_month")
    authors = cur.fetchall()
    conn.close()
    print(authors)

    return render_template('best_authors.html', authors=authors)

if __name__ == "__main__":
    app.run(debug=True)
