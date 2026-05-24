let server_2_client = {
    "Connection Established": 0,
    "Message sent": 1,
    "Error": 2,
    "Connection closed": 3,
    "Pong": 4,
    "Draw": 5,
    "Delete canvas": 6,
    "Word was chosen": 7,
    "There is a new current player": 8,
    "You got a word": 9,
    "A word was guessed": 10,
    "Start timer": 11,
    "Reveal word": 12,
    "Update score": 13,
    "Game ended" : 14,
}


let client_2_server = {
    "login": 0,
    "Message sent": 1,
    "Error": 2,
    "Connection closed": 3,
    "Ping": 4,
    "Draw": 5,
    "Delete canvas": 6,
    "Request word": 7,
    "I am current player": 8,
    "Timer ended": 9,
    "Change username": 10,
}
