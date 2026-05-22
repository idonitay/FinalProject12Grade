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
        let message = sender;
        console.log(sender  )
        

        if (sender != this.last_sender)
        {
            let sender_div = createDiv("", message_div, ["chat_history_sender"])
            sender_div.innerHTML = sender;
            if (id != user_id)
            {
                sender_div.classList.add("not_my_message_in_chat_sender_title");
            }
        }
        
        let row = createDiv("", message_div, ["chat_history_message"])

        row.innerHTML = data;  

        if (data.includes("has guessed the word correctly"))
        {
            row.classList.add("correct_guess");
        }

        else if (data.includes("The word was "))
        {
            row.classList.add("reveal_word");
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
    }

    createChatInput() 
    {
        let input_wrapper = createDiv("input-wrapper", document.getElementById("chat-wrapper"), [])
        let inputbox = createTextInput("chatbox-input", input_wrapper, ["chat_input"]);
        inputbox.addEventListener('keydown', (event) => {
            this.handleChatInputEvents(event, inputbox);
        });
    }

    handleChatInputEvents(event, input) 
    {

        if (event.key === 'Enter')
        {
            this.sendChatMessage(input.value);
            this.clearChatInput(input);
        }
    }


    sendChatMessage(data)
    {
        let message_as_dict = {
            'opcode': client_2_server["Message sent"], 
            'message': data,
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
        chatbox.innerHTML = "";
    }

    createChatHistory(classes)
    {
        return createDiv("chat-history", document.getElementById("chat-wrapper"), classes);
    }

    createChat()
    {
        let chat_box_wrapper = this.createChatWrapper(["box"]);      
        let chat_box_history = this.createChatHistory(["scroll_history_wheel"]);
        this.createChatInput();

    }

    

}