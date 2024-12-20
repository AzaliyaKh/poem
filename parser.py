import requests
from bs4 import BeautifulSoup
import calendar
import sqlite3
from functools import wraps

all_authors = {}
month_authors = {}

def get_poem(author, link):
    url = "https://stihi.ru" + link
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all("a", class_='poemlink')

    connection = sqlite3.connect("DataBase.db")
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Poems (
    id INTEGER PRIMARY KEY,
    article TEXT NOT NULL,
    author TEXT NOT NULL,
    text TEXT NOT NULL
    FOREIGN KEY (author) REFERENCES Authors (id)
    )
    ''')
    for row in rows:
        try:
            article = row.get_text()
            poem_link = "https://stihi.ru" + row.get('href')
            print(poem_link)
            response1 = requests.get(poem_link)
            response1.raise_for_status()

            soup1 = BeautifulSoup(response1.text, 'html.parser')
            row1 = soup1.find("div", class_='text')
            poem = row1.get_text()

            cursor.execute('INSERT INTO Poems (article, author, text) VALUES (?, ?, ?)', (article, author, poem))
        except Exception:
            continue
    #     https://stihi.ru/2024/01/21/7507
    connection.commit()
    connection.close()
    # print(response.text)



def get_author(url, month_authors):
    print(url)
    response = requests.get(url)
    response.raise_for_status()

    connection = sqlite3.connect("DataBase.db")
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Authors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
    )
    ''')

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all("a", class_='recomlink')
    for row in rows:
        author = row.get_text()
        link = row.get('href')

        if author not in all_authors:
            cursor.execute('INSERT INTO Authors (name) VALUES ("author") RETURNING id')
            author_id = cursor.fetchall()
            get_poem(author_id, link)

            if author not in month_authors:
                month_authors[author_id] = 1
            else:
                month_authors[author_id] += 1

    connection.commit()
    connection.close()

def get_best_month():
    connection = sqlite3.connect("DataBase.db")
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS BestMonth (
    id INTEGER PRIMARY KEY,
    month_num INTEGER,
    author_id TEXT NOT NULL,
    rang INTEGER NOT NULL
    FOREIGN KEY (author_id) REFERENCES Authors (id)
    )
    ''')

    for year in range(2024, 2025):
        for month in range(1, 3):
            days = calendar.monthrange(year, month)
            if month < 10:
                month = "0" + str(month)
            k = 1
            for day in range(days[1]):
                get_author(f"https://stihi.ru/authors/editor.html?year={year}&month={month}&day={day + 1}", month_authors)

            for author_id, rang in month_authors.items():
                cursor.execute('INSERT INTO BestMonth (month_num, author_id, rang) VALUES (?, ?, ?)', (month, author_id, rang))

            month_authors = {}

    connection.commit()
    connection.close()

#
# connection = sqlite3.connect("DataBase.db")
# cursor = connection.cursor()
# cursor.execute('''SELECT * FROM BestMonth ''')
# rows = cursor.fetchall()
# for row in rows:
#     print(row)