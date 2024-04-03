
import tkinter as tk
import random
import mysql.connector
from mysql.connector import Error
import datetime

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='2048_game',
            user='root',
            password='root'
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def initialize_board():
    board = [[0] * 4 for _ in range(4)]
    add_new_tile(board)
    add_new_tile(board)
    return board

def add_new_tile(board):
    empty_cells = [(i, j) for i in range(4) for j in range(4) if board[i][j] == 0]
    if empty_cells:
        row, col = random.choice(empty_cells)
        board[row][col] = random.choice([2, 4])

def move_left(board):
    for row in board:
        row[:] = [cell for cell in row if cell != 0]
        for i in range(len(row) - 1):
            if row[i] == row[i + 1]:
                row[i], row[i + 1] = row[i] * 2, 0
        row[:] = [cell for cell in row if cell != 0]
        row += [0] * (4 - len(row))

def is_game_over(board):
    for row in board:
        if 0 in row:
            return False
        for i in range(len(row) - 1):
            if row[i] == row[i + 1]:
                return False
    return True

def update_high_score(connection, player_name, score):
    try:
        cursor = connection.cursor()
        current_datetime = datetime.datetime.now()
        cursor.execute("INSERT INTO high_scores (player_name, score, date_time) VALUES (%s, %s, %s)", (player_name, score, current_datetime))
        connection.commit()
        print("New high score recorded!")
    except Error as e:
        print(f"Error updating high score: {e}")

def get_high_score(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT player_name, score FROM high_scores ORDER BY score DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            return result
        else:
            return None
    except Error as e:
        print(f"Error getting high score: {e}")
        return None

def add_player_history(connection, player_name, score):
    try:
        cursor = connection.cursor()
        current_datetime = datetime.datetime.now()
        cursor.execute("INSERT INTO player_history (player_name, score, date_time) VALUES (%s, %s, %s)", (player_name, score, current_datetime))
        connection.commit()
        print("Player history added successfully!")
    except Error as e:
        print(f"Error adding player history: {e}")

def get_player_history(connection, player_name):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT score, date_time FROM player_history WHERE player_name = %s ORDER BY date_time DESC", (player_name,))
        result = cursor.fetchall()
        if result:
            print(f"Player {player_name} history:")
            for row in result:
                print(f"Score: {row[0]}, Date/Time: {row[1]}")
        else:
            print(f"No history found for player {player_name}")
    except Error as e:
        print(f"Error getting player history: {e}")

def play_game():
    root = tk.Tk()
    root.title("2048")

    player_name_label = tk.Label(root, text="Enter your name:", font=("Helvetica", 12))
    player_name_label.grid(row=0, column=0, columnspan=2)

    player_name_entry = tk.Entry(root, font=("Helvetica", 12))
    player_name_entry.grid(row=0, column=2, columnspan=2)

    start_game_button = tk.Button(root, text="Start Game", font=("Helvetica", 12), command=lambda: start_game(player_name_entry.get(), root))
    start_game_button.grid(row=0, column=4, columnspan=2)

    root.mainloop()

def start_game(player_name, root):
    root.destroy()
    connection = connect_to_database()
    if connection is None:
        return

    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS high_scores (id INT AUTO_INCREMENT PRIMARY KEY, player_name VARCHAR(255), score INT, date_time DATETIME)")
        cursor.execute("CREATE TABLE IF NOT EXISTS player_history (id INT AUTO_INCREMENT PRIMARY KEY, player_name VARCHAR(255), score INT, date_time DATETIME)")
    except Error as e:
        print(f"Error creating table: {e}")

    global score
    score = 0

    def on_key(event):
        global score
        move = event.keysym
        if move in ['Up', 'Down', 'Left', 'Right']:
            if move == 'Up':  
                board[:] = [list(x) for x in zip(*board[::-1])]
                move_left(board)
                board[:] = [list(x) for x in zip(*board[::-1])]
            elif move == 'Down':  
                board[:] = [list(x) for x in zip(*board[::-1])]
                move_left(board)
                board[:] = [list(x) for x in zip(*board[::-1])]
            elif move == 'Left':  
                move_left(board)
            elif move == 'Right':  
                board[:] = [row[::-1] for row in board]
                move_left(board)
                board[:] = [row[::-1] for row in board]

            add_new_tile(board)
            score = max([max(row) for row in board])
            score_label.config(text=f"Score: {score}")
            update_display()
            if is_game_over(board):
                print("Game Over!")
                print(f"Your score: {score}")
                update_high_score(connection, player_name, score)
                add_player_history(connection, player_name, score)
                high_scorer = get_high_score(connection)
                if score >= 2048:
                    print("Congratulations! You won!")
                else:
                    game_over_label.config(text="Game Over")  # Display "Game Over" message
                    root.unbind("<Key>")  # Unbind the event handler to stop the game

    def update_display():
        player_name_label.config(text=f"Player: {player_name}")
        high_score_label.config(text=f"High Score: {high_scorer[1] if high_scorer else 'None'} by {high_scorer[0] if high_scorer else 'None'}")
        for i in range(4):
            for j in range(4):
                cell_value = board[i][j]
                if cell_value == 0:
                    labels[i][j].config(text="", bg="gray")
                else:
                    labels[i][j].config(text=str(cell_value), bg=tile_colors[cell_value])

    root = tk.Tk()
    root.title("2048")

    global board
    board = initialize_board()

    player_name_label = tk.Label(root, text=f"Player: {player_name}", font=("Helvetica", 12))
    player_name_label.grid(row=0, column=0, columnspan=4)

    high_scorer = get_high_score(connection)
    high_score_label = tk.Label(root, text=f"High Score: {high_scorer[1] if high_scorer else 'None'} by {high_scorer[0] if high_scorer else 'None'}", font=("Helvetica", 12))
    high_score_label.grid(row=1, column=0, columnspan=4)

    score_label = tk.Label(root, text=f"Score: {score}", font=("Helvetica", 12))
    score_label.grid(row=2, column=0, columnspan=4)

    game_over_label = tk.Label(root, text="", font=("Helvetica", 24, "bold"), fg="red")
    game_over_label.grid(row=3, column=0, columnspan=4)

    tile_colors = {
        0: "#CDC1B4",
        2: "#EEE4DA",
        4: "#EDE0C8",
        8: "#F2B179",
        16: "#F59563",
        32: "#F67C5F",
        64: "#F65E3B",
        128: "#EDCF72",
        256: "#EDCC61",
        512: "#EDC850",
        1024: "#EDC53F",
        2048: "#EDC22E"
    }

    labels = [[None] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            labels[i][j] = tk.Label(root, text="", font=("Helvetica", 32, "bold"), width=4, height=2,
                                     relief="ridge", borderwidth=2, bg="gray")
            labels[i][j].grid(row=i+4, column=j, padx=5, pady=5)

    update_display()

    root.bind("<Key>", on_key)
    root.mainloop()

if __name__ == "__main__":
    play_game()
