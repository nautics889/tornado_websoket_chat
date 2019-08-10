let ws_connection;

$("#connect_btn").on("click", function() {
    if (!ws_connection) {
        ws_connection = new WebSocket("ws://localhost:8990/");
        console.log(ws_connection);

        $("#connect_btn").html('Disconnect');
        $("#output").append(`<input type="text" id="message_to_send">`)
        $("#output").append(`<button id="send_btn">Send</button>`)
        $("#send_btn").on("click", function() {
            ws_connection.send(JSON.stringify({
                content: $("#message_to_send").val()
            }));
        })

        ws_connection.onmessage = function(event) {
            $("#output").append(`<p>${event.data}</p>`)
        };
    }
    else if (ws_connection instanceof WebSocket) {
        if(ws_connection.readyState == 1) {
            ws_connection.close();
            console.log(ws_connection);
            $("#connect_btn").html('Disconnect');
        }
    };
});

