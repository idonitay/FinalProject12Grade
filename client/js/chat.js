class chat 
{
    constructor(parent)
    {
        this.parent = parent;
    }

    createChatWrapper(classes)
    {
        createDiv("chat-wrapper", this.parent, classes);
    }

     displayMassage(sender, data, message_div) 
    {
        message = sender;
        message += ": ";
        message += data ;
        message_div.innerHTML = message;  
    }
}