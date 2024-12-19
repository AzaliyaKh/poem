import requests
from bs4 import BeautifulSoup
import calendar
import sqlite3
from functools import wraps

authors = {}

DataBase = "authors.db"


def get_poem(author, link):
    url = "https://stihi.ru" + link
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all("a", class_='poemlink')

    connection = sqlite3.connect("poems_base")
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Poems (
    id INTEGER PRIMARY KEY,
    "article" TEXT NOT NULL,
    "author" TEXT NOT NULL,
    "text" TEXT NOT NULL
    )
    ''')
    for row in rows:
        article = row.get_text()
        poem_link = "https://stihi.ru" + row.get('href')
        print(poem_link)
        response1 = requests.get(poem_link)
        response1.raise_for_status()

        soup1 = BeautifulSoup(response1.text, 'html.parser')
        row1 = soup1.find("div", class_='text')
        poem = row1.get_text()

        cursor.execute('INSERT INTO Poems (article, author, text) VALUES (?, ?, ?)', (article, author, poem))

    connection.commit()
    connection.close()
    # print(response.text)



def get_author(url, authors):
    print(url)
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all("a", class_='recomlink')
    for row in rows:
        author = row.get_text()
        link = row.get('href')
        if author not in authors:
            authors[author] = 1
            # get_poem(author, link)
        else:
            authors[author] += 1
    # return authors
    # hrefs = topics.find_all('a')


connection = sqlite3.connect("poems_base.db")
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS best_month (
id INTEGER PRIMARY KEY,
month_num INTEGER,
"author" TEXT NOT NULL,
"rang" INTEGER NOT NULL
)
''')

for i in range(2024, 2025):
    for j in range(1, 3):
        days = calendar.monthrange(i, j)
        if j < 10:
            j = "0" + str(j)
        k = 1
        for day in range(days[1]):
            get_author(f"https://stihi.ru/authors/editor.html?year={i}&month={j}&day={day + 1}", authors)

        for author, rang in authors.items():
            cursor.execute('INSERT INTO best_month (month_num, author, rang) VALUES (?, ?, ?)', (j, author, rang))

        connection.commit()
        authors = {}
connection.close()


connection = sqlite3.connect("poems_base.db")
cursor = connection.cursor()
cursor.execute('''SELECT * FROM best_month ''')
rows = cursor.fetchall()
for row in rows:
    print(row)