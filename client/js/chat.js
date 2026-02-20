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

     displayMassage(sender, data, message_div) 
    {
        let message = sender;
        let row = createDiv("", message_div, [])
        message += ": ";
        message += data ;
        row.innerHTML = message;  
    }

    createChatInput() 
    {
        let inputbox = createTextInput("chatbox-input", this.parent, []);
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
            'message': data
        };

        send_message_to_server(message_as_dict); 
        chatbox.displayMassage("player", data, document.getElementById("chat-wrapper"));
    }

    clearChatInput(input) 
    {
        input.value = "";
        
    }

    clearChatHistory()
    {

    }

    createChatHistory(classes)
    {
        return createDiv("chat-history", document.getElementById("chat-wrapper"), classes);
    }

    createChat()
    {
        let chat_box_wrapper = this.createChatWrapper([]);
        let chat_box_input = this.createChatInput();
        let chat_box_history = this.clearChatHistory([])

    }

    

}