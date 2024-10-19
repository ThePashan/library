import tkinter as tk
import psycopg2
from ebooklib import epub
import hashlib
from tkinter import messagebox

# Создание соединения с базой данных и создание таблиц
conn = psycopg2.connect(
    dbname="library",
    user="library",
    password="123",
    host="localhost"
)
c = conn.cursor()
# Таблица для хранения пользователей
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT)''')
# Таблица для хранения книг
c.execute('''CREATE TABLE IF NOT EXISTS books
             (title TEXT, author TEXT, year INTEGER)''')
conn.commit()

# Функция для хэширования паролей
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Функция для регистрации нового пользователя
def register():
    username = username_entry.get()
    password = password_entry.get()
    try:
        # Добавление нового пользователя в базу данных
        c.execute("INSERT INTO users VALUES (%s, %s)", (username, hash_password(password)))
        conn.commit()
        clear_auth_entries()
        messagebox.showinfo("Registration", "Registration successful!")
    except psycopg2.IntegrityError:
        # Если пользователь уже существует, откат транзакции
        conn.rollback()
        messagebox.showerror("Registration", "Username already exists!")

# Функция для входа пользователя
def login():
    username = username_entry.get()
    password = password_entry.get()
    # Проверка наличия пользователя с введёнными данными
    c.execute("SELECT * FROM users WHERE username=%s AND password=%s",
              (username, hash_password(password)))
    user = c.fetchone()
    if user:
        messagebox.showinfo("Login", "Login successful!")
        # Скрыть фрейм авторизации и показать основной интерфейс
        auth_frame.pack_forget()
        main_frame.pack()
        update_listbox()
    else:
        messagebox.showerror("Login", "Invalid username or password")

# Функция для очистки полей ввода на форме авторизации
def clear_auth_entries():
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

# Функция для добавления книги
def add_book():
    title = title_entry.get()
    author = author_entry.get()
    year = year_entry.get()
    # Добавление книги в базу данных
    c.execute("INSERT INTO books VALUES (%s, %s, %s)", (title, author, year))
    conn.commit()
    clear_entries()
    update_listbox()

# Функция для удаления книги
def delete_book():
    selected_book = listbox.get(tk.ACTIVE)
    # Удаление выбранной книги из базы данных
    c.execute("DELETE FROM books WHERE title=%s", (selected_book,))
    conn.commit()
    update_listbox()

# Функция для поиска книг
def search_book():
    title_term = title_search_entry.get()
    author_term = author_search_entry.get()
    year_term = year_search_entry.get()
    
    query = "SELECT * FROM books WHERE TRUE"
    params = []
    
    if title_term:
        query += " AND title LIKE %s"
        params.append('%' + title_term + '%')
    
    if author_term:
        query += " AND author LIKE %s"
        params.append('%' + author_term + '%')
    
    if year_term:
        query += " AND year::text LIKE %s"
        params.append('%' + year_term + '%')
    
    # Выполнение запроса и обновление списка книг
    c.execute(query, params)
    books = c.fetchall()
    listbox.delete(0, tk.END)
    for book in books:
        listbox.insert(tk.END, book[0])

# Функция для очистки полей ввода книг
def clear_entries():
    title_entry.delete(0, tk.END)
    author_entry.delete(0, tk.END)
    year_entry.delete(0, tk.END)

# Функция для обновления списка книг в Listbox
def update_listbox():
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    listbox.delete(0, tk.END)
    for book in books:
        listbox.insert(tk.END, book[0])

# Функция для загрузки книги в формате EPUB
def load_epub():
    filepath = filepath_entry.get()
    book = epub.read_epub(filepath)
    
    # Получение метаданных книги
    title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else 'Unknown Title'
    author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else 'Unknown Author'
    year = book.get_metadata('DC', 'date')[0][0][:4] if book.get_metadata('DC', 'date') else 'Unknown Year'

    # Заполнение полей ввода метаданными книги
    title_entry.delete(0, tk.END)
    author_entry.delete(0, tk.END)
    year_entry.delete(0, tk.END)

    title_entry.insert(0, title)
    author_entry.insert(0, author)
    year_entry.insert(0, year)

# Создание графического интерфейса
root = tk.Tk()
root.title("Library")

# Фрейм для авторизации
auth_frame = tk.Frame(root)
auth_frame.pack()

# Метка и поле для ввода имени пользователя
username_label = tk.Label(auth_frame, text="Username:")
username_label.grid(row=0, column=0)
username_entry = tk.Entry(auth_frame)
username_entry.grid(row=0, column=1)

# Метка и поле для ввода пароля
password_label = tk.Label(auth_frame, text="Password:")
password_label.grid(row=1, column=0)
password_entry = tk.Entry(auth_frame, show="*")
password_entry.grid(row=1, column=1)

# Кнопка для регистрации
register_button = tk.Button(auth_frame, text="Register", command=register)
register_button.grid(row=2, column=0)

# Кнопка для входа
login_button = tk.Button(auth_frame, text="Login", command=login)
login_button.grid(row=2, column=1)

# Фрейм для основного интерфейса
main_frame = tk.Frame(root)

# Поля для добавления книги
title_label = tk.Label(main_frame, text="Title:")
title_label.grid(row=0, column=0)
title_entry = tk.Entry(main_frame)
title_entry.grid(row=0, column=1)

author_label = tk.Label(main_frame, text="Author:")
author_label.grid(row=1, column=0)
author_entry = tk.Entry(main_frame)
author_entry.grid(row=1, column=1)

year_label = tk.Label(main_frame, text="Year:")
year_label.grid(row=2, column=0)
year_entry = tk.Entry(main_frame)
year_entry.grid(row=2, column=1)

# Поле для ввода пути к EPUB
filepath_label = tk.Label(main_frame, text="EPUB File Path:")
filepath_label.grid(row=3, column=0)
filepath_entry = tk.Entry(main_frame)
filepath_entry.grid(row=3, column=1)

# Кнопка для загрузки EPUB
load_button = tk.Button(main_frame, text="Load EPUB", command=load_epub)
load_button.grid(row=3, column=2)

# Кнопка для добавления книги
add_button = tk.Button(main_frame, text="Add Book", command=add_book)
add_button.grid(row=4, column=0, columnspan=3)

# Кнопка для удаления книги
delete_button = tk.Button(main_frame, text="Delete Book", command=delete_book)
delete_button.grid(row=5, column=0, columnspan=3)

# Поля для поиска
title_search_label = tk.Label(main_frame, text="Search by Title:")
title_search_label.grid(row=6, column=0)
title_search_entry = tk.Entry(main_frame)
title_search_entry.grid(row=6, column=1)

author_search_label = tk.Label(main_frame, text="Search by Author:")
author_search_label.grid(row=7, column=0)
author_search_entry = tk.Entry(main_frame)
author_search_entry.grid(row=7, column=1)

year_search_label = tk.Label(main_frame, text="Search by Year:")
year_search_label.grid(row=8, column=0)
year_search_entry = tk.Entry(main_frame)
year_search_entry.grid(row=8, column=1)

# Кнопка для выполнения поиска
search_button = tk.Button(main_frame, text="Search", command=search_book)
search_button.grid(row=9, column=0, columnspan=3)

# Listbox для отображения списка книг
listbox = tk.Listbox(main_frame)
listbox.grid(row=10, column=0, columnspan=3)

# Запуск главного цикла приложения
root.mainloop()

# Закрытие соединения с базой данных при выходе
conn.close()
