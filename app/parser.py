import requests
from bs4 import BeautifulSoup
import calendar
import sqlite3

all_authors = {}
month_authors = {}

def get_poem(author_id, link):
    connection = sqlite3.connect("DataBase.db")
    cursor = connection.cursor()

    # проверка: есть ли автор в базе данных
    if cursor.execute("SELECT author_id FROM Poems WHERE author_id=?", [author_id]).fetchone() is not None:
        return

    url = "https://stihi.ru" + link
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all("a", class_='poemlink')

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

            cursor.execute('INSERT INTO Poems (article, author_id, text) VALUES (?, ?, ?)', (article, author_id, poem))
        except Exception:
            continue

    connection.commit()
    connection.close()

def get_author(url):
    print(url)
    response = requests.get(url)
    response.raise_for_status()

    # записываем в БД всех авторов, сохраняя в список аввторов их id
    connection = sqlite3.connect("DataBase.db")
    cursor = connection.cursor()

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all("a", class_='recomlink')
    for row in rows:
        author = row.get_text()

        if author not in all_authors:
            cursor.execute('INSERT INTO Authors (name) VALUES (?) RETURNING id', [author])
            author_id = cursor.fetchone()[0]
            all_authors[author] = author_id

        if all_authors[author] not in month_authors:
            month_authors[all_authors[author]] = 1
        else:
            month_authors[all_authors[author]] += 1

    connection.commit()
    connection.close()

    # повторно проходимся по списку, чтобы записать стихи каждого поэта
    # (выделено в отдельный цикл для предотвращения конфликтов потоков)
    for row in rows:
        author = row.get_text()
        link = row.get('href')

        get_poem(all_authors[author], link)

def get_best_month():
    connection = sqlite3.connect("DataBase.db")
    cursor = connection.cursor()


    for year in range(2024, 2025):
        for month in range(1, 2):
            days = calendar.monthrange(year, month)
            if month < 10:
                month = "0" + str(month)
            k = 1
            for day in range(k):
            # for day in range(days[1]):
                get_author(f"https://stihi.ru/authors/editor.html?year={year}&month={month}&day={day + 1}")
            print(month_authors)
            for author_id, rang in month_authors.items():
                cursor.execute('INSERT INTO BestMonth (month_num, author_id, rang) VALUES (?, ?, ?)', (month, author_id, rang))
            print(month_authors)
            month_authors.clear()


    connection.commit()
    connection.close()

if __name__ == "__main__":
    get_best_month()