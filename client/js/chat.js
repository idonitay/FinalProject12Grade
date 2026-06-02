class chat 
{
    constructor(parent)
    {
        this.parent = parent;
        this.last_sender = "";
    }

    createChatWrapper(classes)
    {
        return createDiv("chat-wrapper", this.parent, classes);
    }

    displayMessage(sender, data, message_div, id) 
    {
        const message = String(data);

        if (sender != this.last_sender)
        {
            let sender_div = createDiv("", message_div, ["chat_history_sender"])
            sender_div.textContent = sender;
            if (id != user_id)
            {
                sender_div.classList.add("not_my_message_in_chat_sender_title");
            }
        }
        
        let row = createDiv("", message_div, ["chat_history_message"])

        row.textContent = message;  

        if (message.includes("has guessed the word correctly"))
        {
            row.classList.add("correct_guess");
        }

        else if (message.includes("The word was "))
        {
            row.classList.add("reveal_word");
        }

        else if (message.includes("Round over!"))
        {
            row.classList.add("round_over");
        }
        
        else if (message.includes("has won"))
        {
            row.classList.add("endgame_message");
        }

        else if (sender == "server")
        {
            row.classList.add("server_message");
        }

        else if (id == user_id)
        {
            row.classList.add("my_message_in_chat");
            
        }
        else
        {
            row.classList.add("peer_chat_history_message");
            //sender_div.classList.add("not_my_message_in_chat_sender_title");
        }

        this.last_sender = sender;
        message_div.scrollTop = message_div.scrollHeight;
    }

    createChatInput() 
    {
        let input_wrapper = createDiv("input-wrapper", document.getElementById("chat-wrapper"), ["chat_input_wrapper"])
        let inputbox = createTextInput("chatbox-input", input_wrapper, ["chat_input"]);
        inputbox.placeholder = "כתוב ניחוש או הודעה";
        inputbox.autocomplete = "off";

        let send_button = createButton("chat-send-button", input_wrapper, "שלח", ["chat_send_button"]);
        send_button.addEventListener("click", () => {
            this.sendChatMessage(inputbox.value);
            this.clearChatInput(inputbox);
            inputbox.focus();
        });

        inputbox.addEventListener('keydown', (event) => {
            this.handleChatInputEvents(event, inputbox);
        });
    }

    handleChatInputEvents(event, input) 
    {

        if (event.key === 'Enter' && !event.isComposing)
        {
            event.preventDefault();
            this.sendChatMessage(input.value);
            this.clearChatInput(input);
        }
    }


    sendChatMessage(data)
    {
        let message = data.trim();

        if (message === "")
        {
            return;
        }

        let message_as_dict = {
            'opcode': client_2_server["Message sent"], 
            'message': message,
            'dst': "broadcast"
            
        };

        send_message_to_server(message_as_dict); 
        //chatbox.displayMessage("player", data, document.getElementById("chat-wrapper"));
    }

    clearChatInput(input) 
    {
        input.value = "";
        
    }

    clearChatHistory()
    {
        let chat_history = document.getElementById("chat-history");
        chat_history.innerHTML = "";
        this.last_sender = "";
    }

    createChatHistory(classes)
    {
        return createDiv("chat-history", document.getElementById("chat-wrapper"), classes);
    }

    createChat()
    {
        let chat_box_wrapper = this.createChatWrapper(["chat_box_wrapper", "box"]);      
        let chat_box_history = this.createChatHistory(["scroll_history_wheel"]);
        this.createChatInput();

    }

    

}
