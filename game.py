import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
import json
import os
import hashlib

# Создаем или подключаемся к базе данных
conn = sqlite3.connect('tamagotchi.db')
cursor = conn.cursor()

# Создаем таблицы для питомца и игроков, если они не существуют
cursor.execute('''
CREATE TABLE IF NOT EXISTS pet (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    hunger INTEGER DEFAULT 90,
    happiness INTEGER DEFAULT 50,
    energy INTEGER DEFAULT 50,
    owner_id INTEGER,
    FOREIGN KEY (owner_id) REFERENCES players (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    score INTEGER DEFAULT 0
)
''')
conn.commit()

def hash_password(password):
    """Хеширует пароль с использованием SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

class TamagotchiApp:
    def __init__(self, master):
        self.master = master
        master.title("Tamagotchi Game")
        
        self.current_player_id = None

        # Загрузка изображений
        self.bg_image = ImageTk.PhotoImage(Image.open("background.jpg"))
        self.pet_image = ImageTk.PhotoImage(Image.open("normal.png"))

        # Создание Canvas для размещения изображений
        self.canvas = tk.Canvas(master, width=900, height=720)
        self.canvas.pack()

        # Установка фонового изображения
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)

        # Установка изображения питомца
        self.pet_image_id = self.canvas.create_image(700, 570, image=self.pet_image)

        # Рейтинг игрока
        self.rating_label = tk.Label(master, text="Рейтинг: 0", bg='lightblue', font=("Arial", 12))
        self.canvas.create_window(50, 20, window=self.rating_label)

        # Текстовое обучение
        self.instructions_label = tk.Label(master, text="Инструкция:\n1. Создайте питомца.\n2. Ухаживайте за ним.\n3. Играйте, кормите и укладывайте спать.", bg='lightblue', font=("Arial", 12))
        self.canvas.create_window(700, 400, window=self.instructions_label)

        # Создание виджетов
        self.label = tk.Label(master, text="Введите имя вашего питомца:", bg='lightblue', font=("Arial", 12))
        self.canvas.create_window(400, 50, window=self.label)

        self.name_entry = tk.Entry(master)
        self.canvas.create_window(400, 80, window=self.name_entry)

        self.create_button = tk.Button(master, text="Создать питомца", command=self.create_pet, state=tk.DISABLED, bg='lightgreen', font=("Arial", 12))
        self.canvas.create_window(400, 120, window=self.create_button)

        self.username_label = tk.Label(master, text="Введите имя пользователя:", bg='lightblue', font=("Arial", 12))
        self.canvas.create_window(400, 160, window=self.username_label)

        self.username_entry = tk.Entry(master)
        self.canvas.create_window(400, 190, window=self.username_entry)

        self.password_label = tk.Label(master, text="Введите пароль:", bg='lightblue', font=("Arial", 12))
        self.canvas.create_window(400, 220, window=self.password_label)

        self.password_entry = tk.Entry(master, show='*')
        self.canvas.create_window(400, 250, window=self.password_entry)

        self.register_button = tk.Button(master, text="Зарегистрироваться", command=self.register_player, bg='lightgreen', font=("Arial", 12))
        self.canvas.create_window(400, 290, window=self.register_button)

        self.login_button = tk.Button(master, text="Войти", command=self.login_user, bg='lightgreen', font=("Arial", 12))
        self.canvas.create_window(400 , 330, window=self.login_button)

        self.status_label = tk.Label(master, text="", bg='lightblue', font=("Arial", 12))
        self.canvas.create_window(400, 370, window=self.status_label)

        self.feed_button = tk.Button(master, text="Покормить питомца", command=self.feed_pet, state=tk.DISABLED, bg='lightgreen', font=("Arial", 12))
        self.canvas.create_window(400, 410, window=self.feed_button)

        self.play_button = tk.Button(master, text="Играть с питомцем", command=self.play_with_pet, state=tk.DISABLED, bg='lightgreen', font=("Arial", 12))
        self.canvas.create_window(400, 450, window=self.play_button)

        self.rest_button = tk.Button(master, text="Уложить питомца спать", command=self.rest_pet, state=tk.DISABLED, bg='lightgreen', font=("Arial", 12))
        self.canvas.create_window(400, 490, window=self.rest_button)

        self.save_button = tk.Button(master, text="Сохранить состояние", command=self.save_pet, bg='lightgreen', font=("Arial", 12))
        self.canvas.create_window(400, 530, window=self.save_button)

        self.load_button = tk.Button(master, text="Загрузить состояние", command=self.load_pet, bg='lightgreen', font=("Arial", 12))
        self.canvas.create_window(400, 570, window=self.load_button)

        self.schema_button = tk.Button(master, text="Показать схему БД", command=self.show_db_schema, bg='lightgreen', font=("Arial", 12))
        self.canvas.create_window(400, 610, window=self.schema_button)

        self.quit_button = tk.Button(master, text="Выйти", command=master.quit, bg='lightcoral', font=("Arial", 12))
        self.canvas.create_window(400, 650, window=self.quit_button)

        self.update_status()

    def show_db_schema(self):
        schema = ""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            schema += f"Таблица: {table[0]}\n"
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            for column in columns:
                schema += f"  - {column[1]}: {column[2]}\n"
            schema += "\n"
        
        self.display_schema(schema)

    def display_schema(self, schema):
        schema_window = tk.Toplevel(self.master)
        schema_window.title("Схема базы данных")
        text_area = scrolledtext.ScrolledText(schema_window, width=60, height=20)
        text_area.pack()
        text_area.insert(tk.END, schema)
        text_area.config(state=tk.DISABLED)

    def register_player(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            try:
                hashed_password = hash_password(password)
                cursor.execute('INSERT INTO players (username, password) VALUES (?, ?)', (username, hashed_password))
                conn.commit()
                self.current_player_id = cursor.lastrowid
                self.create_button.config(state=tk.NORMAL)
                self.username_entry.config(state=tk.DISABLED)
                self.password_entry.config(state=tk.DISABLED)
                self.register_button.config(state=tk.DISABLED)
                self.login_button.config(state=tk.DISABLED)
                messagebox.showinfo("Регистрация", f"Игрок {username} зарегистрирован.")
            except sqlite3.IntegrityError:
                messagebox.showwarning("Ошибка", "Имя пользователя уже занято.")
        else:
            messagebox.showwarning("Внимание", "Пожалуйста, введите имя пользователя и пароль.")

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            hashed_password = hash_password(password)
            cursor.execute('SELECT id FROM players WHERE username = ? AND password = ?', (username, hashed_password))
            user = cursor.fetchone()
            if user:
                self.current_player_id = user[0]
                self.create_button.config(state=tk.NORMAL)
                self.username_entry.config(state=tk.DISABLED)
                self.password_entry.config(state=tk.DISABLED)
                self.register_button.config(state=tk.DISABLED)
                self.login_button.config(state=tk.DISABLED)
                messagebox.showinfo("Вход", f"Добро пожаловать, {username}!")
                self.update_rating()  # Обновляем рейтинг при входе
            else:
                messagebox.showwarning("Ошибка", "Неверное имя пользователя или пароль.")
        else:
            messagebox.showwarning("Внимание", "Пожалуйста, введите имя пользователя и пароль.")

    def create_pet(self):
        name = self.name_entry.get()
        if name and self.current_player_id is not None:
            cursor.execute('INSERT INTO pet ( name, owner_id) VALUES (?, ?)', (name, self.current_player_id))
            conn.commit()
            self.name_entry.config(state=tk.DISABLED)
            self.create_button.config(state=tk.DISABLED)
            self.feed_button.config(state=tk.NORMAL)
            self.play_button.config(state=tk.NORMAL)
            self.rest_button.config(state=tk.NORMAL)
            self.update_status()
            self.show_instructions()  # Показать инструкции после создания питомца
        else:
            messagebox.showwarning("Внимание", "Пожалуйста, введите имя питомца и зарегистрируйтесь.")

    def show_instructions(self):
        instructions_window = tk.Toplevel(self.master)
        instructions_window.title("Инструкции")
        instructions_text = "Инструкции:\n1. Ухаживайте за питомцем.\n2. Кормите его, играйте и укладывайте спать.\n3. Следите за его состоянием."
        text_area = scrolledtext.ScrolledText(instructions_window, width=50, height=10)
        text_area.pack()
        text_area.insert(tk.END, instructions_text)
        text_area.config(state=tk.DISABLED)
        close_button = tk.Button(instructions_window, text="Закрыть", command=instructions_window.destroy)
        close_button.pack()

    def update_status(self):
        cursor.execute('SELECT * FROM pet WHERE owner_id = ?', (self.current_player_id,))
        pet = cursor.fetchone()
        if pet:
            self.status_label.config(text=f"Имя: {pet[1]}, Голод: {pet[2]}, Счастье: {pet[3]}, Энергия: {pet[4]}")
            self.update_pet_image()
            self.update_rating()  # Обновляем рейтинг при изменении статуса питомца
            if pet[2] >= 100 or pet[3] <= 0:
                messagebox.showinfo("Игра окончена", "Ваш питомец погиб!")
                self.update_score()
                self.master.quit()
        else:
            self.status_label.config(text="У вас нет питомца!")

    def update_pet_image(self):
        cursor.execute('SELECT * FROM pet WHERE owner_id = ?', (self.current_player_id,))
        pet = cursor.fetchone()
        if pet:
            if pet[2] > 50:  # Голод больше 50
                self.pet_image = ImageTk.PhotoImage(Image.open("hungry.png"))  # Изображение голодного питомца
            elif pet[3] <= 0:  # Грустный
                self.pet_image = ImageTk.PhotoImage(Image.open("sad.png"))  # Изображение грустного питомца
            else:
                self.pet_image = ImageTk.PhotoImage(Image.open("normal.png"))  # Нормальное изображение питомца

            self.canvas.itemconfig(self.pet_image_id, image=self.pet_image)

    def update_rating(self):
        cursor.execute('SELECT score FROM players WHERE id = ?', (self.current_player_id,))
        score = cursor.fetchone()
        if score:
            self.rating_label.config(text=f"Рейтинг: {score[0]}")

    def feed_pet(self):
        cursor.execute('UPDATE pet SET hunger = hunger - 10 WHERE hunger > 0 AND owner_id = ?', (self.current_player_id,))
        conn.commit()
        self.update_status()

    def play_with_pet(self):
        cursor.execute('UPDATE pet SET happiness = happiness + 10 WHERE happiness < 100 AND owner_id = ?', (self.current_player_id,))
        conn.commit()
        
        if os.path.exists("nice.png"):
            self.canvas.itemconfig(self.pet_image_id, image=ImageTk.PhotoImage(Image.open("nice.png")))  # Меняем изображение на nice.png
        else:
            messagebox.showwarning("Ошибка", "Изображение nice.png не найдено.")

        self.master.after(2000, self.restore_pet_image)  # Возвращаем изображение через 2 секунды

    def restore_pet_image(self):
        self.update_pet_image()  # Восстанавливаем изображение питомца

    def rest_pet(self):
        cursor.execute('UPDATE pet SET energy = energy + 10 WHERE energy < 100 AND owner_id = ?', (self.current_player_id,))
        conn.commit()
        self.update_status()

    def update_score(self):
        cursor.execute('UPDATE players SET score = score + 100 WHERE id = ?', (self.current_player_id,))
        conn.commit()

    def save_pet(self):
        cursor.execute('SELECT * FROM pet WHERE owner_id = ?', (self.current_player_id,))
        pet = cursor.fetchone()
        if pet:
            pet_data = {
                'name': pet[1],
                'hunger': pet[2],
                'happiness': pet[3],
                'energy': pet[4]
            }
            with open ('pet_state.json', 'w') as f:
                json.dump(pet_data, f)
            messagebox.showinfo("Сохранение", "Состояние питомца сохранено.")
        else:
            messagebox.showwarning("Внимание", "У вас нет питомца для сохранения.")

    def load_pet(self):
        if os.path.exists('pet_state.json'):
            with open('pet_state.json', 'r') as f:
                pet_data = json.load(f)
                cursor.execute('INSERT INTO pet (name, hunger, happiness, energy, owner_id) VALUES (?, ?, ?, ?, ?)',
                               (pet_data['name'], pet_data['hunger'], pet_data['happiness'], pet_data['energy'], self.current_player_id))
                conn.commit()
                self.update_status()
                messagebox.showinfo("Загрузка", "Состояние питомца загружено.")
        else:
            messagebox.showwarning("Внимание", "Нет сохраненного состояния питомца.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TamagotchiApp(root)
    root.mainloop()