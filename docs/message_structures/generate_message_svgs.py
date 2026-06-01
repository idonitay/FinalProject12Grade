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
        "file": "login.svg",
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
        "file": "message_sent.svg",
        "title": "Client message sent fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Message sent"] (1)'),
            field("message", "string", "yes", "chat text typed by the player"),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "error.svg",
        "title": "Client error message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Error"] (2)'),
            field("message", "string", "yes", "error description"),
            field("dst", "string", "yes", "intended destination"),
        ],
    },
    {
        "file": "connection_closed.svg",
        "title": "Client connection closed message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Connection closed"] (3)'),
            field("message", "string", "yes", "connection close description"),
            field("dst", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "ping.svg",
        "title": "Client ping message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Ping"] (4)'),
            field("message", "string", "yes", '"ping"'),
            field("dst", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "draw.svg",
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
        "file": "delete_canvas.svg",
        "title": "Client delete canvas message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Delete canvas"] (6)'),
            field("message", "string", "yes", 'empty string ""'),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "request_word.svg",
        "title": "Client request word message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Request word"] (7)'),
            field("message", "string", "yes", 'empty string ""'),
            field("dst", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "i_am_current_player.svg",
        "title": "Client current player message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["I am current player"] (8)'),
            field("message", "string", "yes", 'empty string ""'),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "timer_ended.svg",
        "title": "Client timer ended message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Timer ended"] (9)'),
            field("message", "string", "yes", 'empty string ""'),
            field("dst", "string", "yes", '"broadcast"'),
        ],
    },
    {
        "file": "change_username.svg",
        "title": "Client change username message fields",
        "rows": [
            field("opcode", "number", "yes", 'client_2_server["Change username"] (10)'),
            field("message", "string", "yes", "new username"),
            field("dst", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "ready.svg",
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
        "file": "connection_established.svg",
        "title": "Server connection established message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Connection Established"] (0)'),
            field("message", "string", "yes", '"connection established"'),
            field("src", "string", "yes", "client username stored by server"),
            field("server_public_key", "string", "yes", "Base64 raw ECDH P-256 public key"),
        ],
    },
    {
        "file": "message_sent.svg",
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
        "file": "error.svg",
        "title": "Server error message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Error"] (2)'),
            field("message", "string", "yes", "error description"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "connection_closed.svg",
        "title": "Server connection closed message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Connection closed"] (3)'),
            field("message", "string", "yes", "connection close description"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "pong.svg",
        "title": "Server pong message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Pong"] (4)'),
            field("message", "string", "yes", '"pong"'),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "draw.svg",
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
        "file": "delete_canvas.svg",
        "title": "Server delete canvas message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Delete canvas"] (6)'),
            field("message", "string", "yes", 'empty string ""'),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "word_was_chosen.svg",
        "title": "Server word was chosen message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Word was chosen"] (7)'),
            field("message", "string", "yes", "chosen word status text"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "there_is_a_new_current_player.svg",
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
        "file": "you_got_a_word.svg",
        "title": "Server you got a word message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["You got a word"] (9)'),
            field("message", "string", "yes", "word assigned to current player"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "a_word_was_guessed.svg",
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
        "file": "start_timer.svg",
        "title": "Server start timer message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Start timer"] (11)'),
            field("duration", "number", "yes", "timer duration in seconds"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "reveal_word.svg",
        "title": "Server reveal word message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Reveal word"] (12)'),
            field("message", "string", "yes", "reveals the word after a turn"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "update_score.svg",
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
        "file": "game_ended.svg",
        "title": "Server game ended message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["Game ended"] (14)'),
            field("message", "string", "yes", "winner announcement"),
            field("src", "string", "yes", '"server"'),
        ],
    },
    {
        "file": "first_player.svg",
        "title": "Server first player message fields",
        "rows": [
            field("opcode", "number", "yes", 'server_2_client["First player"] (15)'),
            field("src", "string", "yes", '"server"'),
        ],
    },
]


def render_svg(title, rows):
    width = 1040
    margin = 24
    table_width = width - (margin * 2)
    header_height = 44
    row_height = 56
    table_height = header_height + (len(rows) * row_height)
    height = table_height + (margin * 2)
    x_name = 48
    x_type = 288
    x_required = 440
    x_meaning = 568
    col_name = 264
    col_type = 416
    col_required = 544
    y_top = margin
    y_header_bottom = y_top + header_height
    y_bottom = y_top + table_height

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{escape(title)}</title>',
        f'  <desc id="desc">Field names and types for {escape(title)}.</desc>',
        "  <defs>",
        "    <style>",
        "      .background { fill: #ffffff; }",
        "      .outer { fill: #ffffff; stroke: #c9d1dd; stroke-width: 1.5; }",
        "      .head { fill: #f1f5f9; }",
        "      .line { stroke: #d7dde7; stroke-width: 1; }",
        "      .head-text { fill: #334155; font: 700 13px Arial, sans-serif; }",
        "      .name { fill: #111827; font: 700 15px Arial, sans-serif; }",
        "      .type { fill: #1f2937; font: 14px Arial, sans-serif; }",
        "      .note { fill: #4b5563; font: 14px Arial, sans-serif; }",
        "    </style>",
        "  </defs>",
        "",
        f'  <rect class="background" x="0" y="0" width="{width}" height="{height}"/>',
        f'  <rect class="outer" x="{margin}" y="{margin}" width="{table_width}" height="{table_height}" rx="8"/>',
        "",
        f'  <rect class="head" x="{margin}" y="{margin}" width="{table_width}" height="{header_height}" rx="8"/>',
        f'  <line class="line" x1="{margin}" y1="{y_header_bottom}" x2="{width - margin}" y2="{y_header_bottom}"/>',
        "",
        f'  <text class="head-text" x="{x_name}" y="52">Name</text>',
        f'  <text class="head-text" x="{x_type}" y="52">Type</text>',
        f'  <text class="head-text" x="{x_required}" y="52">Required</text>',
        f'  <text class="head-text" x="{x_meaning}" y="52">Value / Meaning</text>',
        "",
        f'  <line class="line" x1="{col_name}" y1="{margin}" x2="{col_name}" y2="{y_bottom}"/>',
        f'  <line class="line" x1="{col_type}" y1="{margin}" x2="{col_type}" y2="{y_bottom}"/>',
        f'  <line class="line" x1="{col_required}" y1="{margin}" x2="{col_required}" y2="{y_bottom}"/>',
        "",
    ]

    for index, row in enumerate(rows):
        row_top = y_header_bottom + (index * row_height)
        baseline = row_top + 34
        parts.extend(
            [
                f'  <text class="name" x="{x_name}" y="{baseline}">{escape(row["name"])}</text>',
                f'  <text class="type" x="{x_type}" y="{baseline}">{escape(row["type"])}</text>',
                f'  <text class="type" x="{x_required}" y="{baseline}">{escape(row["required"])}</text>',
                f'  <text class="note" x="{x_meaning}" y="{baseline}">{escape(row["meaning"])}</text>',
            ]
        )
        if index != len(rows) - 1:
            separator_y = row_top + row_height
            parts.append(
                f'  <line class="line" x1="{margin}" y1="{separator_y}" x2="{width - margin}" y2="{separator_y}"/>'
            )
        parts.append("")

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def write_messages(directory, messages):
    directory.mkdir(parents=True, exist_ok=True)
    for stale_svg in directory.glob("*.svg"):
        stale_svg.unlink()

    for message in messages:
        svg = render_svg(message["title"], message["rows"])
        (directory / message["file"]).write_text(svg, encoding="utf-8")


def main():
    write_messages(CLIENT_DIR, CLIENT_MESSAGES)
    write_messages(SERVER_DIR, SERVER_MESSAGES)


if __name__ == "__main__":
    main()
