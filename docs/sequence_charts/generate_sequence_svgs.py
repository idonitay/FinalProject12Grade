from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape


BASE_DIR = Path(__file__).resolve().parent

DEFAULT_PARTICIPANTS = {
    "client": {"name": "Browser client", "x": 260},
    "server": {"name": "WebSocket server", "x": 940},
}

BROADCAST_PARTICIPANTS = {
    "client": {"name": "Sender client", "x": 180},
    "server": {"name": "WebSocket server", "x": 600},
    "clients": {"name": "All connected clients", "x": 1020},
}

TURN_PARTICIPANTS = {
    "client": {"name": "Timer client", "x": 200},
    "server": {"name": "WebSocket server", "x": 520},
    "clients": {"name": "All connected clients", "x": 860},
    "target": {"name": "Target player client", "x": 1220},
}

DISCONNECT_PARTICIPANTS = {
    "client": {"name": "Leaving client", "x": 180},
    "server": {"name": "WebSocket server", "x": 600},
    "remaining": {"name": "Remaining client", "x": 1020},
}


def message(source, target, label, detail="", secure=False):
    return {
        "kind": "message",
        "source": source,
        "target": target,
        "label": label,
        "detail": detail,
        "secure": secure,
    }


def step(actor, label, detail=""):
    return {
        "kind": "step",
        "actor": actor,
        "label": label,
        "detail": detail,
    }


def note(actor, label):
    return {
        "kind": "note",
        "actor": actor,
        "label": label,
    }


def group(label, rows):
    return {
        "kind": "group",
        "label": label,
        "rows": rows,
    }


SEQUENCES = [
    {
        "file": "encryption_setup.svg",
        "title": "Encryption setup sequence",
        "description": "ECDH handshake, key derivation, and first encrypted ready packet.",
        "rows": [
            message(
                "client",
                "server",
                "Open WebSocket connection",
                "GET /ws upgrade; server creates WebSocketResponse and WebSocketWrapper.",
            ),
            step(
                "client",
                "Generate client ECDH key pair",
                "WebCrypto ECDH P-256; private key is stored temporarily as window.pendingPrivateKey.",
            ),
            message(
                "client",
                "server",
                "Plain login / handshake request",
                'JSON opcode 0, message "Handshake request", src, dst "server", id, public_key.',
            ),
            step(
                "server",
                "Generate server ECDH key pair",
                "Import the client public_key as a P-256 encoded point.",
            ),
            step(
                "server",
                "Derive server session keys",
                'ECDH shared secret, then HKDF-SHA256 length 64, salt None, info "handshake data".',
            ),
            note(
                "server",
                "The first 32 derived bytes become wrapper.aes_key; the last 32 become wrapper.hmac_key.",
            ),
            step(
                "server",
                "Process login fields",
                "Store the username and random client id on the WebSocketWrapper.",
            ),
            message(
                "server",
                "client",
                "Plain connection established response",
                'JSON opcode 0, message "connection established", src, server_public_key.',
            ),
            step(
                "client",
                "Derive client session keys",
                'Import server_public_key, run ECDH, then HKDF with the same salt and info values.',
            ),
            note(
                "client",
                "The derived AES-GCM key is used for encrypt/decrypt; the derived HMAC-SHA256 key is used for sign/verify.",
            ),
            step(
                "client",
                "Save keys and clear pending private key",
                "saveKeys stores the keys in the current tab context, then pendingPrivateKey is deleted.",
            ),
            message(
                "client",
                "server",
                "Encrypted ready packet",
                "send_server_ready_message sends opcode 11 inside {iv, data, signature}.",
                secure=True,
            ),
            step(
                "server",
                "Verify and decrypt ready packet",
                "Verify HMAC over IV + ciphertext, decrypt with AES-GCM, then handle opcode 11.",
            ),
            group(
                "Only when this is the first connected client",
                [
                    message(
                        "server",
                        "client",
                        "Encrypted first-player message",
                        "Opcode 15 is sent through send_message_to_player_wrapper.",
                        secure=True,
                    )
                ],
            ),
        ],
    },
    {
        "file": "ready_first_player.svg",
        "title": "Ready and first-player sequence",
        "description": "The post-handshake Ready message and the optional first-player response.",
        "rows": [
            message(
                "client",
                "server",
                "Encrypted Ready message",
                'Opcode 11, empty message, dst "server"; sent after the client saves session keys.',
                secure=True,
            ),
            step(
                "server",
                "Verify, decrypt, and handle Ready",
                "The server only sends a response when there is exactly one connected wrapper.",
            ),
            group(
                "If this is the only connected client",
                [
                    message(
                        "server",
                        "client",
                        "Encrypted First player message",
                        "Opcode 15 is sent through send_message_to_player_wrapper.",
                        secure=True,
                    ),
                    step(
                        "client",
                        "Create start-game button",
                        "The client handles opcode 15 by calling create_start_game_button.",
                    ),
                ],
            ),
        ],
    },
    {
        "file": "change_username.svg",
        "title": "Change username sequence",
        "description": "A player changes the username stored on the server wrapper.",
        "rows": [
            step(
                "client",
                "Type username and press Enter",
                "The browser updates the local username variable immediately.",
            ),
            message(
                "client",
                "server",
                "Encrypted Change username message",
                'Opcode 10, message is the new username, dst "server".',
                secure=True,
            ),
            step(
                "server",
                "Update wrapper username",
                "handle_user_message stores message as source_wrapper.username and returns no response.",
            ),
            note(
                "client",
                "No server confirmation is sent; future messages use the new username.",
            ),
        ],
    },
    {
        "file": "chat_message.svg",
        "title": "Chat message sequence",
        "description": "A normal chat message is broadcast to every connected client.",
        "participants": BROADCAST_PARTICIPANTS,
        "rows": [
            step(
                "client",
                "Type chat text and press Enter",
                "chat.sendChatMessage builds opcode 1 with dst broadcast.",
            ),
            message(
                "client",
                "server",
                "Encrypted Message sent packet",
                "Payload contains the typed chat text.",
                secure=True,
            ),
            step(
                "server",
                "Verify, decrypt, and inspect text",
                "If the text is not the active word, the server builds server opcode 1.",
            ),
            message(
                "server",
                "clients",
                "Encrypted Message sent broadcast",
                "broadcast_message encrypts a separate envelope for each connected wrapper.",
                secure=True,
            ),
            step(
                "clients",
                "Decrypt and display chat message",
                "Each browser appends the text to chat history using src and id.",
            ),
        ],
    },
    {
        "file": "correct_guess.svg",
        "title": "Correct guess sequence",
        "description": "A chat message can become a correct word guess and update scores.",
        "participants": {
            "client": {"name": "Guessing client", "x": 180},
            "server": {"name": "WebSocket server", "x": 600},
            "clients": {"name": "All connected clients", "x": 1020},
        },
        "rows": [
            message(
                "client",
                "server",
                "Encrypted Message sent packet",
                "Opcode 1 carries the guessed text.",
                secure=True,
            ),
            step(
                "server",
                "Compare guess with active word",
                "The server hashes the guess and the word with SHA-256, then uses hmac.compare_digest.",
            ),
            group(
                "If this is the player's first correct guess",
                [
                    step(
                        "server",
                        "Award points and mark answered",
                        "source_wrapper.score += 100, source_wrapper.answered = True.",
                    ),
                    message(
                        "server",
                        "clients",
                        "Encrypted Update score broadcast",
                        "Opcode 13 carries score, index, and player_name.",
                        secure=True,
                    ),
                    message(
                        "server",
                        "clients",
                        "Encrypted word-guessed broadcast",
                        "Opcode 10 announces that the player guessed correctly.",
                        secure=True,
                    ),
                    step(
                        "clients",
                        "Update scoreboard and chat",
                        "Clients handle opcode 13 in the scoreboard and opcode 10 in chat history.",
                    ),
                ],
            ),
            group(
                "If the player already answered, or the current player submitted the word",
                [
                    message(
                        "server",
                        "clients",
                        "Encrypted already-guessed notice",
                        "Opcode 1 broadcasts a message saying the player has already guessed correctly.",
                        secure=True,
                    )
                ],
            ),
            note(
                "server",
                "After each secure message, the server checks if everyone answered; if true, finish_turn runs.",
            ),
        ],
    },
    {
        "file": "drawing.svg",
        "title": "Drawing sequence",
        "description": "A brush stroke from the current player is broadcast to all clients.",
        "participants": {
            "client": {"name": "Current player client", "x": 180},
            "server": {"name": "WebSocket server", "x": 600},
            "clients": {"name": "All connected clients", "x": 1020},
        },
        "rows": [
            step(
                "client",
                "Drag on the canvas",
                "The browser draws the local line and builds a brush stroke payload when canDraw is true.",
            ),
            message(
                "client",
                "server",
                "Encrypted Draw packet",
                "Opcode 5 carries pointA, pointB, color, and size with dst broadcast.",
                secure=True,
            ),
            step(
                "server",
                "Return draw broadcast response",
                "handle_user_message copies the stroke payload into server opcode 5.",
            ),
            message(
                "server",
                "clients",
                "Encrypted Draw broadcast",
                "Each connected wrapper receives its own encrypted envelope.",
                secure=True,
            ),
            step(
                "clients",
                "Draw the received line",
                "Clients handle opcode 5 by calling drawLine with the received stroke payload.",
            ),
        ],
    },
    {
        "file": "request_word.svg",
        "title": "Request word sequence",
        "description": "The current player asks the server for the word to draw.",
        "participants": {
            "client": {"name": "Current player client", "x": 260},
            "server": {"name": "WebSocket server", "x": 940},
        },
        "rows": [
            message(
                "client",
                "server",
                "Encrypted Request word packet",
                'Opcode 7, empty message, dst "server".',
                secure=True,
            ),
            step(
                "server",
                "Choose a random word",
                "The server selects random.choice(words) and stores it in the global word variable.",
            ),
            message(
                "server",
                "client",
                "Encrypted You got a word response",
                "Opcode 9 carries the selected word only to the requesting player.",
                secure=True,
            ),
            step(
                "client",
                "Show the word and enable drawing",
                "The client displays the word and sets canDraw = true.",
            ),
        ],
    },
    {
        "file": "current_player.svg",
        "title": "Current player sequence",
        "description": "A client declares itself as current player and the server starts the turn.",
        "participants": {
            "client": {"name": "Current player client", "x": 180},
            "server": {"name": "WebSocket server", "x": 600},
            "clients": {"name": "All connected clients", "x": 1020},
        },
        "rows": [
            message(
                "client",
                "server",
                "Encrypted I am current player packet",
                "Opcode 8, empty message, dst broadcast.",
                secure=True,
            ),
            step(
                "server",
                "Send timer as side effect",
                "handle_user_message calls send_start_timer_message before returning the current-player response.",
            ),
            message(
                "server",
                "clients",
                "Encrypted Start timer broadcast",
                "Opcode 11 carries duration_in_seconds; clients start the timer and clear the canvas.",
                secure=True,
            ),
            step(
                "server",
                "Mark turn state",
                "current_turn_index increments and source_wrapper.answered is set true.",
            ),
            message(
                "server",
                "clients",
                "Encrypted new current-player broadcast",
                "Opcode 8 announces the current player and includes current_round_index.",
                secure=True,
            ),
            step(
                "clients",
                "Update turn display",
                "Clients clear the displayed word, update the round counter, add a chat notice, and set canDraw false.",
            ),
            note(
                "server",
                "After the response is sent, websocket_handler also checks whether everyone answered; if true, finish_turn runs.",
            ),
        ],
    },
    {
        "file": "delete_canvas_current_behavior.svg",
        "title": "Delete canvas sequence",
        "description": "Current runtime behavior for the Delete canvas client message.",
        "participants": BROADCAST_PARTICIPANTS,
        "rows": [
            step(
                "client",
                "Clear local canvas",
                "The trash button clears the sender immediately before sending the message.",
            ),
            message(
                "client",
                "server",
                "Encrypted Delete canvas packet",
                "Opcode 6, empty message, dst broadcast.",
                secure=True,
            ),
            step(
                "server",
                "No Delete canvas handler",
                "handle_user_message has no branch for client opcode 6, so it returns an unknown response.",
            ),
            message(
                "server",
                "clients",
                "Encrypted unknown broadcast",
                "Because the request dst was broadcast, the unknown response is broadcast to connected clients.",
                secure=True,
            ),
            step(
                "clients",
                "Log unidentified message",
                "The client switch has no case for opcode unknown, so other clients do not clear from this packet.",
            ),
        ],
    },
    {
        "file": "timer_ended_turn_transition.svg",
        "title": "Timer ended and turn transition sequence",
        "description": "The timer ending triggers reveal word, next player selection, and possible endgame.",
        "participants": TURN_PARTICIPANTS,
        "width": 1400,
        "rows": [
            step(
                "client",
                "Timer reaches zero",
                "start_timer stops the interval and calls send_timer_ended_message.",
            ),
            message(
                "client",
                "server",
                "Encrypted Timer ended packet",
                "Opcode 9, empty message, dst broadcast.",
                secure=True,
            ),
            step(
                "server",
                "Run finish_turn",
                "The server resets answered flags, reveals the word, chooses next player, starts timer, then checks endgame.",
            ),
            message(
                "server",
                "clients",
                "Encrypted Reveal word broadcast",
                'Opcode 12 sends "The word was ..." to chat history.',
                secure=True,
            ),
            step(
                "server",
                "Choose next player",
                "The old current player is cleared; the next wrapper becomes current_player and answered.",
            ),
            message(
                "server",
                "clients",
                "Encrypted new current-player broadcast",
                "Opcode 8 announces the next current player and current_round_index.",
                secure=True,
            ),
            message(
                "server",
                "target",
                "Encrypted You got a word direct message",
                "Opcode 9 sends the new word only to the new current player.",
                secure=True,
            ),
            message(
                "server",
                "clients",
                "Encrypted Start timer broadcast",
                "Opcode 11 starts the next turn timer for everyone.",
                secure=True,
            ),
            step(
                "server",
                "Increment turn index",
                "current_turn_index increments after the next timer has been sent.",
            ),
            group(
                "If current_turn_index is greater than amount_of_turns",
                [
                    message(
                        "server",
                        "clients",
                        "Encrypted Game ended broadcast",
                        "Opcode 14 announces the winner or winners.",
                        secure=True,
                    ),
                    step(
                        "server",
                        "Reset game-start state",
                        "current_turn_index is reset to 0.",
                    ),
                    message(
                        "server",
                        "target",
                        "Encrypted First player message",
                        "Opcode 15 is sent to web_socket_wrappers_array[0].",
                        secure=True,
                    ),
                ],
            ),
        ],
    },
    {
        "file": "ping_current_behavior.svg",
        "title": "Ping sequence",
        "description": "Current runtime behavior for the Ping client message.",
        "rows": [
            message(
                "client",
                "server",
                "Encrypted Ping packet",
                'Opcode 4, message "ping", dst "server".',
                secure=True,
            ),
            step(
                "server",
                "No Ping handler",
                "handle_user_message has no branch for client opcode 4, so it returns an unknown response.",
            ),
            message(
                "server",
                "client",
                "Encrypted unknown response",
                "The response is sent directly to the source wrapper.",
                secure=True,
            ),
            step(
                "client",
                "Log unidentified message",
                "The client has a Pong case, but no Pong is emitted by the server in the current code.",
            ),
        ],
    },
    {
        "file": "disconnect.svg",
        "title": "Disconnect sequence",
        "description": "A WebSocket disconnect removes the wrapper and may promote the remaining client.",
        "participants": DISCONNECT_PARTICIPANTS,
        "rows": [
            message(
                "client",
                "server",
                "WebSocket closes",
                "The close event can be a browser close, refresh, or network disconnect.",
            ),
            step(
                "server",
                "Remove wrapper",
                "The finally block removes the wrapper and recalculates amount_of_turns.",
            ),
            group(
                "If exactly one client remains",
                [
                    message(
                        "server",
                        "remaining",
                        "Encrypted First player message",
                        "Opcode 15 is sent to the remaining client.",
                        secure=True,
                    ),
                    step(
                        "remaining",
                        "Create start-game button",
                        "The remaining browser handles opcode 15 by calling create_start_game_button.",
                    ),
                ],
            ),
            note(
                "client",
                "No application-level Connection closed opcode is sent by the browser in the current code.",
            ),
        ],
    },
    {
        "file": "declared_unused_messages.svg",
        "title": "Declared messages without active sequence",
        "description": "Opcodes that exist in the tables but are not produced by the current runtime paths.",
        "rows": [
            note(
                "client",
                "Client Error and Connection closed opcodes are declared, but no client code sends them.",
            ),
            note(
                "server",
                "Server Error, Connection closed, Pong, Word was chosen, and Delete canvas opcodes are declared, but the current server code does not emit them.",
            ),
            note(
                "server",
                "Client Ping and Delete canvas messages currently fall through to the unknown-response path.",
            ),
        ],
    },
]


def text_lines(text, width):
    return wrap(text, width=width, break_long_words=False, replace_whitespace=False) or [""]


def draw_text(parts, lines, x, y, css_class, line_height=18, anchor="middle"):
    for index, line in enumerate(lines):
        parts.append(
            f'  <text class="{css_class}" x="{x}" y="{y + (index * line_height)}" text-anchor="{anchor}">{escape(line)}</text>'
        )


def event_height(row):
    if row["kind"] == "group":
        return 52 + sum(event_height(child) for child in row["rows"]) + 18

    if row["kind"] == "message":
        label_count = len(text_lines(row["label"], 44))
        detail_count = len(text_lines(row["detail"], 72)) if row["detail"] else 0
        return max(82, 58 + (label_count * 18) + (detail_count * 17))

    if row["kind"] == "step":
        label_count = len(text_lines(row["label"], 38))
        detail_count = len(text_lines(row["detail"], 42)) if row["detail"] else 0
        return max(82, 46 + (label_count * 18) + (detail_count * 15))

    if row["kind"] == "note":
        line_count = len(text_lines(row["label"], 45))
        return max(72, 52 + (line_count * 16))

    return 76


def render_message(parts, row, y, participants):
    source = participants[row["source"]]
    target = participants[row["target"]]
    x1 = source["x"]
    x2 = target["x"]
    label_y = y
    label_lines = text_lines(row["label"], 44)
    detail_lines = text_lines(row["detail"], 72) if row["detail"] else []
    detail_y = label_y + (len(label_lines) * 18) + 5
    arrow_y = detail_y + (len(detail_lines) * 17) + 18
    direction = 1 if x2 > x1 else -1
    marker = "url(#arrow-secure)" if row["secure"] else "url(#arrow-plain)"
    css_class = "arrow-secure" if row["secure"] else "arrow-plain"
    label_class = "label secure-label" if row["secure"] else "label"

    draw_text(parts, label_lines, (x1 + x2) // 2, label_y, label_class)

    if detail_lines:
        draw_text(parts, detail_lines, (x1 + x2) // 2, detail_y, "detail", 17)

    parts.append(
        f'  <line class="{css_class}" x1="{x1 + (22 * direction)}" y1="{arrow_y}" x2="{x2 - (28 * direction)}" y2="{arrow_y}" marker-end="{marker}"/>'
    )


def render_step(parts, row, y, participants):
    actor = participants[row["actor"]]
    x = actor["x"]
    box_width = actor.get("step_width", 350)
    label_width = actor.get("label_width", 38)
    detail_width = actor.get("detail_width", 42)
    label_lines = text_lines(row["label"], label_width)
    detail_lines = text_lines(row["detail"], detail_width) if row["detail"] else []
    box_height = max(54, 28 + (len(label_lines) * 18) + (8 if detail_lines else 0) + (len(detail_lines) * 15))
    box_x = x - (box_width // 2)
    box_y = y - 18

    parts.append(f'  <rect class="step-box" x="{box_x}" y="{box_y}" width="{box_width}" height="{box_height}" rx="8"/>')
    draw_text(parts, label_lines, x, y + 1, "label")
    if detail_lines:
        detail_y = y + 1 + (len(label_lines) * 18) + 8
        draw_text(parts, detail_lines, x, detail_y, "detail", 15)


def render_note(parts, row, y, participants):
    actor = participants[row["actor"]]
    x = actor["x"]
    box_width = actor.get("note_width", 360)
    line_width = actor.get("note_line_width", 45)
    lines = text_lines(row["label"], line_width)
    box_height = 28 + (len(lines) * 16)
    box_x = x - (box_width // 2)
    box_y = y - 18

    parts.append(f'  <rect class="note-box" x="{box_x}" y="{box_y}" width="{box_width}" height="{box_height}" rx="8"/>')
    draw_text(parts, lines, x, y + 5, "note-text", 16)


def render_group(parts, row, y, participants, diagram_width):
    child_start_y = y + 52
    group_height = event_height(row) - 18
    group_margin = 104
    group_width = diagram_width - (group_margin * 2)
    parts.append(f'  <rect class="group-box" x="{group_margin}" y="{y - 8}" width="{group_width}" height="{group_height}" rx="10"/>')
    parts.append(f'  <rect class="group-title-bg" x="{group_margin}" y="{y - 8}" width="{group_width}" height="34" rx="10"/>')
    draw_text(parts, [row["label"]], 126, y + 14, "group-title", anchor="start")

    current_y = child_start_y
    for child in row["rows"]:
        render_row(parts, child, current_y, participants, diagram_width)
        current_y += event_height(child)


def render_row(parts, row, y, participants, diagram_width):
    if row["kind"] == "message":
        render_message(parts, row, y, participants)
    elif row["kind"] == "step":
        render_step(parts, row, y, participants)
    elif row["kind"] == "note":
        render_note(parts, row, y, participants)
    elif row["kind"] == "group":
        render_group(parts, row, y, participants, diagram_width)
    else:
        raise ValueError(f"Unknown row kind: {row['kind']}")


def render_svg(sequence):
    width = sequence.get("width", 1200)
    participants = sequence.get("participants", DEFAULT_PARTICIPANTS)
    header_height = 118
    footer_margin = 42
    body_height = sum(event_height(row) for row in sequence["rows"])
    height = header_height + body_height + footer_margin
    lifeline_top = 86
    lifeline_bottom = height - 28

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{escape(sequence["title"])}</title>',
        f'  <desc id="desc">{escape(sequence["description"])}</desc>',
        "  <defs>",
        "    <marker id=\"arrow-plain\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"8\" markerHeight=\"8\" orient=\"auto-start-reverse\">",
        "      <path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"arrow-head-plain\"/>",
        "    </marker>",
        "    <marker id=\"arrow-secure\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"8\" markerHeight=\"8\" orient=\"auto-start-reverse\">",
        "      <path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"arrow-head-secure\"/>",
        "    </marker>",
        "    <style>",
        "      .background { fill: #ffffff; }",
        "      .title { fill: #111827; font: 700 24px Arial, sans-serif; }",
        "      .subtitle { fill: #4b5563; font: 14px Arial, sans-serif; }",
        "      .participant { fill: #f8fafc; stroke: #cbd5e1; stroke-width: 1.5; }",
        "      .participant-text { fill: #111827; font: 700 15px Arial, sans-serif; }",
        "      .lifeline { stroke: #cbd5e1; stroke-width: 1.5; stroke-dasharray: 6 8; }",
        "      .arrow-plain { stroke: #2563eb; stroke-width: 2; }",
        "      .arrow-secure { stroke: #059669; stroke-width: 2.25; }",
        "      .arrow-head-plain { fill: #2563eb; }",
        "      .arrow-head-secure { fill: #059669; }",
        "      .step-box { fill: #f8fafc; stroke: #d1d5db; stroke-width: 1.25; }",
        "      .note-box { fill: #fff7ed; stroke: #fed7aa; stroke-width: 1.25; }",
        "      .group-box { fill: #f8fafc; stroke: #cbd5e1; stroke-width: 1.25; stroke-dasharray: 8 6; }",
        "      .group-title-bg { fill: #e2e8f0; }",
        "      .label { fill: #111827; font: 700 14px Arial, sans-serif; }",
        "      .secure-label { fill: #047857; }",
        "      .detail { fill: #4b5563; font: 13px Arial, sans-serif; }",
        "      .note-text { fill: #7c2d12; font: 13px Arial, sans-serif; }",
        "      .group-title { fill: #334155; font: 700 13px Arial, sans-serif; }",
        "    </style>",
        "  </defs>",
        "",
        f'  <rect class="background" x="0" y="0" width="{width}" height="{height}"/>',
        f'  <text class="title" x="{width // 2}" y="36" text-anchor="middle">{escape(sequence["title"])}</text>',
        f'  <text class="subtitle" x="{width // 2}" y="60" text-anchor="middle">{escape(sequence["description"])}</text>',
        "",
    ]

    for participant in participants.values():
        participant_width = participant.get("participant_width", 220)
        box_x = participant["x"] - (participant_width // 2)
        parts.append(
            f'  <rect class="participant" x="{box_x}" y="78" width="{participant_width}" height="44" rx="8"/>'
        )
        parts.append(
            f'  <text class="participant-text" x="{participant["x"]}" y="106" text-anchor="middle">{escape(participant["name"])}</text>'
        )
        parts.append(
            f'  <line class="lifeline" x1="{participant["x"]}" y1="{lifeline_top}" x2="{participant["x"]}" y2="{lifeline_bottom}"/>'
        )

    current_y = header_height + 32
    for row in sequence["rows"]:
        render_row(parts, row, current_y, participants, width)
        current_y += event_height(row)

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    for stale_svg in BASE_DIR.glob("*.svg"):
        stale_svg.unlink()

    for sequence in SEQUENCES:
        svg = render_svg(sequence)
        (BASE_DIR / sequence["file"]).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
