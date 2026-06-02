from pathlib import Path
from xml.sax.saxutils import escape

BASE_DIR = Path(__file__).resolve().parent

CLIENT_DIR = BASE_DIR / "client messages"
SERVER_DIR = BASE_DIR / "Server messages"

def field(name, type_name, required, meaning):
    return {
        "name": name,
        "type": type_name,
        "required": required,
        "meaning": meaning,
    }

CLIENT_MESSAGES = [
    {
        "file": "login.html",
        "title": "Client login message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["login"] (0)'),
            field("message", "string", "yes", '"Handshake request"'),
            field("src", "string", "yes", "client username"),
            field("dst", "string", "yes", '"server"'),
            field("id", "number", "yes", "random client id"),
            field("public_key", "string", "yes", "Base64 raw ECDH P-256 public key"),
        ],
    },
    {
        "file": "message_sent.html",
        "title": "Client message sent fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Message sent"] (1)'),
            field("message", "string", "yes", "chat text typed by the player"),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "error.html",
        "title": "Client error message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Error"] (2)'),
            field("message", "string", "yes", "error description"),
            field("dst", "string", "yes", "intended destination"),
        ],
    },
    {
        "file": "connection_closed.html",
        "title": "Client connection closed message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Connection closed"] (3)'),
            field("message", "string", "yes", "connection close description"),
            field("dst", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "ping.html",
        "title": "Client ping message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Ping"] (4)'),
            field("message", "string", "yes", '"ping"'),
            field("dst", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "draw.html",
        "title": "Client draw message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Draw"] (5)'),
            field("message", "object", "yes", "brush stroke payload"),
            field("message.pointA", "object", "yes", "first point"),
            field("message.pointA.x", "number", "yes", "x coordinate"),
            field("message.pointA.y", "number", "yes", "y coordinate"),
            field("message.pointB", "object", "yes", "second point"),
            field("message.pointB.x", "number", "yes", "x coordinate"),
            field("message.pointB.y", "number", "yes", "y coordinate"),
            field("message.color", "string", "yes", "CSS color value"),
            field("message.size", "number", "yes", "brush size"),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "delete_canvas.html",
        "title": "Client delete canvas message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Delete canvas"] (6)'),
            field("message", "string", "yes", 'empty string ""'),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "request_word.html",
        "title": "Client request word message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Request word"] (7)'),
            field("message", "string", "yes", 'empty string ""'),
            field("dst", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "i_am_current_player.html",
        "title": "Client current player message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["I am current player"] (8)'),
            field("message", "string", "yes", 'empty string ""'),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "timer_ended.html",
        "title": "Client timer ended message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Timer ended"] (9)'),
            field("message", "string", "yes", 'empty string ""'),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "change_username.html",
        "title": "Client change username message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Change username"] (10)'),
            field("message", "string", "yes", "new username"),
            field("dst", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "ready.html",
        "title": "Client ready message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Ready"] (11)'),
            field("message", "string", "yes", 'empty string ""'),
            field("dst", "string", "yes", '"server"'),
        ],
    },
]

SERVER_MESSAGES = [
    {
        "file": "connection_established.html",
        "title": "Server connection established message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Connection Established"] (0)'),
            field("message", "string", "yes", '"connection established"'),
            field("src", "string", "yes", "client username stored by server"),
            field("server_public_key", "string", "yes", "Base64 raw ECDH P-256 public key"),
        ],
    },
    {
        "file": "message_sent.html",
        "title": "Server message sent fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Message sent"] (1)'),
            field("message", "string", "yes", "chat text or already-guessed notice"),
            field("src", "string", "yes", "sender username"),
            field("id", "number", "yes", "sender client id"),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "error.html",
        "title": "Server error message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Error"] (2)'),
            field("message", "string", "yes", "error description"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "connection_closed.html",
        "title": "Server connection closed message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Connection closed"] (3)'),
            field("message", "string", "yes", "connection close description"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "pong.html",
        "title": "Server pong message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Pong"] (4)'),
            field("message", "string", "yes", '"pong"'),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "draw.html",
        "title": "Server draw message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Draw"] (5)'),
            field("message", "object", "yes", "brush stroke payload"),
            field("message.pointA", "object", "yes", "first point"),
            field("message.pointA.x", "number", "yes", "x coordinate"),
            field("message.pointA.y", "number", "yes", "y coordinate"),
            field("message.pointB", "object", "yes", "second point"),
            field("message.pointB.x", "number", "yes", "x coordinate"),
            field("message.pointB.y", "number", "yes", "y coordinate"),
            field("message.color", "string", "yes", "CSS color value"),
            field("message.size", "number", "yes", "brush size"),
            field("src", "string", "yes", "sender username"),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "delete_canvas.html",
        "title": "Server delete canvas message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Delete canvas"] (6)'),
            field("message", "string", "yes", 'empty string ""'),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "word_was_chosen.html",
        "title": "Server word was chosen message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Word was chosen"] (7)'),
            field("message", "string", "yes", "chosen word status text"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "there_is_a_new_current_player.html",
        "title": "Server new current player message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["There is a new current player"] (8)'),
            field("message", "string", "yes", "current player announcement"),
            field("src", "string", "yes", '"server"'),
            field("id", "number", "optional", "new current player's client id"),
            field("current_round_index", "number", "yes", "round number shown by the client"),
            field("dst", "string", "optional", '"broadcast" when routed from request'),
        ],
    },
    {
        "file": "you_got_a_word.html",
        "title": "Server you got a word message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["You got a word"] (9)'),
            field("message", "string", "yes", "word assigned to current player"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "a_word_was_guessed.html",
        "title": "Server word guessed message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["A word was guessed"] (10)'),
            field("message", "string", "yes", "correct guess announcement"),
            field("src", "string", "yes", '"server"'),
            field("id", "number", "yes", "guesser client id"),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "start_timer.html",
        "title": "Server start timer message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Start timer"] (11)'),
            field("duration", "number", "yes", "timer duration in seconds"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "reveal_word.html",
        "title": "Server reveal word message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Reveal word"] (12)'),
            field("message", "string", "yes", "reveals the word after a turn"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "update_score.html",
        "title": "Server update score message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Update score"] (13)'),
            field("score", "number", "yes", "new score value"),
            field("index", "number", "yes", "scoreboard row index"),
            field("player_name", "string", "yes", "player whose score changed"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "game_ended.html",
        "title": "Server game ended message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Game ended"] (14)'),
            field("message", "string", "yes", "winner announcement"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "first_player.html",
        "title": "Server first player message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["First player"] (15)'),
            field("src", "string", "yes", '"server"'),
        ],
    },
]

CSS_STYLES = """
    body { font-family: sans-serif; margin: 2em; color: #334155; line-height: 1.5; }
    .message-structure { margin-bottom: 3em; }
    h2 { border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5em; margin-top: 2em; }
    h3 { color: #1e293b; margin-bottom: 1em; }
    table { border-collapse: collapse; width: 100%; max-width: 1000px; border: 1px solid #c9d1dd; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); }
    th { background-color: #f1f5f9; text-align: left; padding: 12px 16px; font-size: 13px; font-weight: 700; border: 1px solid #c9d1dd; }
    td { padding: 14px 16px; border: 1px solid #c9d1dd; font-size: 14px; }
    .name { font-weight: 700; color: #111827; }
    .type, .required { color: #1f2937; }
    .meaning { color: #4b5563; }
"""

def render_html_fragment(title, rows):
    parts = [
        f'  <div class="message-structure">',
        f'    <h3>{escape(title)}</h3>',
        '    <table>',
        '      <thead>',
        '        <tr>',
        '          <th>Name</th>',
        '          <th>Type</th>',
        '          <th>Required</th>',
        '          <th>Value / Meaning</th>',
        '        </tr>',
        '      </thead>',
        '      <tbody>'
    ]

    for row in rows:
        parts.extend([
            '        <tr>',
            f'          <td class="name">{escape(row["name"])}</td>',
            f'          <td class="type">{escape(row["type"])}</td>',
            f'          <td class="required">{escape(row["required"])}</td>',
            f'          <td class="meaning">{escape(row["meaning"])}</td>',
            '        </tr>'
        ])

    parts.extend([
        '      </tbody>',
        '    </table>',
        '  </div>'
    ])
    return "\n".join(parts)

def write_combined_html(file_path, title, messages):
    parts = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '  <meta charset="utf-8">',
        f'  <title>{escape(title)}</title>',
        f'  <style>{CSS_STYLES}</style>',
        '</head>',
        '<body>',
        f'  <h1>{escape(title)}</h1>'
    ]

    for msg in messages:
        parts.append(render_html_fragment(msg["title"], msg["rows"]))

    parts.extend([
        '</body>',
        '</html>'
    ])
    file_path.write_text("\n".join(parts) + "\n", encoding="utf-8")

def main():
    write_combined_html(BASE_DIR / "client_messages.html", "Client Messages Protocol", CLIENT_MESSAGES)
    write_combined_html(BASE_DIR / "server_messages.html", "Server Messages Protocol", SERVER_MESSAGES)

if __name__ == "__main__":
    main()
