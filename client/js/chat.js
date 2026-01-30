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
        message += ": ";
        message += data ;
        message_div.innerHTML = message;  
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
            console.log('Enter key pressed!');
            this.sendChatMessage();
            this.clearChatInput(input);
        }
    }


    sendChatMessage()
    {

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