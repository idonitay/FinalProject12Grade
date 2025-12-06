// Create a WebSocket connection to your server
const socket = new WebSocket("ws://localhost:8080/ws");

// Fired when the connection is opened
socket.addEventListener("open", () => {
    console.log("Connected to server!");

    // Send a message to the server
    send_message_to_server({'opcode':0, 'message': "Hello server!"});
});

// Fired when a message comes from the server
socket.addEventListener("message", (event) => {

    let response = JSON.parse(event.data);
    console.log("Message from server:", response);
});

// Fired if an error happens
socket.addEventListener("error", (error) => {
    console.error("WebSocket error:", error);
});

// Fired when the connection closes
socket.addEventListener("close", () => {
    console.log("Disconnected from server");
});


function send_message_to_server(json_obj)
{
    let message_as_str = JSON.stringify(json_obj);
    socket.send(message_as_str);
}
