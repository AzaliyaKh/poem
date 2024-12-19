from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
conn = sqlite3.connect('poem_base')

@app.route('/')
def best_authors():
    cur = conn.cursor()
    cur.execute("SELECT author FROM best_month")
    authors = cur.fetchall()
    return render_template('best_authors.html', authors=authors)