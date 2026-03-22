class chat 
{
    constructor(parent)
    {
        this.parent = parent;
    }

    createChatWrapper(classes)
    {
        return createDiv("chat-wrapper", this.parent, classes);
    }

     displayMessage(sender, data, message_div) 
    {
        let message = sender;
        let row = createDiv("", message_div, ["chat_history_message"])
        message += ": ";
        message += data ;
        row.innerHTML = message;  
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
        let chat_box_wrapper = this.createChatWrapper([]);      
        let chat_box_history = this.createChatHistory([]);
        let chat_box_input = this.createChatInput();

    }

    

}