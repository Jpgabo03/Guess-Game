import socket
import random
import os

host = "0.0.0.0"
port = 7777
banner = """
== Guessing Game v1.0 == """

difficulty_levels = {
    'easy': (1, 50),   
    'medium': (1, 100),  
    'hard': (1, 500)   
}

leaderboard = "leaderboard.txt"

def generate_random_int(low, high):
    return random.randint(low, high)

def update_user_score(username, score, difficulty):
    user_data = {}

    # Read existing user data if the file exists
    if os.path.exists(leaderboard):
        with open(leaderboard, "r") as file:
            for line in file:
                name, prev_score, prev_difficulty = line.strip().split(",")
                user_data[name] = (int(prev_score), prev_difficulty)

    # Update user score with the new entry
    user_data[username] = (score, difficulty)

    # Sort user data based on score (lowest to highest)
    sorted_data = sorted(user_data.items(), key=lambda item: item[1][0])  # Extract score from tuple

    # Write sorted data back to the file
    with open(leaderboard, "w") as file:
        for name, (prev_score, prev_difficulty) in sorted_data:
            file.write(f"{name},{prev_score},{prev_difficulty}\n")


def handle_client_connection(conn, addr):
    try:
        conn.sendall(banner.encode())

        while True:
            
            conn.sendall(b"Do you want to play again? (yes/no): ")
            play_again_choice = conn.recv(1024).decode().strip().lower()
            if play_again_choice != "yes":
                break  
    except ConnectionResetError:
        print("Connection reset by the client.")
    except ConnectionAbortedError:
        print("Connection aborted by the client.")

    conn.close()
    print(f"Connection with {addr} closed")

def send_leaderboard(conn):
    if os.path.exists(leaderboard):
        with open(leaderboard, "r") as file:
            leaderboard_data = file.read()
            conn.sendall(leaderboard_data.encode())
    else:
        conn.sendall(b"Leaderboard is empty.")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)

print(f"server is listening on port {port}")

while True:
    conn, addr = s.accept()
    print(f"Connection from {addr}")

    conn.sendall(banner.encode())

    username = conn.recv(1024).decode().strip()
    difficulty_choice = conn.recv(1024).decode().strip().lower()

    while difficulty_choice not in difficulty_levels:
        conn.sendall(b"Invalid difficulty level! Choose again: ")
        difficulty_choice = conn.recv(1024).decode().strip().lower()
    
    conn.sendall(b"Let's start guessing!")
    low, high = difficulty_levels[difficulty_choice]
    guessme = generate_random_int(low, high)
    tries = 0

    
    while True:
        client_input = conn.recv(1024)
        if not client_input:
            break
        guess = int(client_input.decode().strip())
        print(f"{username} guessed: {guess}")
        tries += 1

        if guess == guessme:
            conn.sendall(f"Correct Answer, {username}! You won in {tries} tries!\n".encode())
            update_user_score(username, tries, difficulty_choice)
            break
        elif guess > guessme:
            conn.sendall(b"Guess Lower!")
        elif guess < guessme:
            conn.sendall(b"Guess Higher!")

    send_leaderboard(conn)
    conn.close()
    print(f"Connection with {addr} closed")


