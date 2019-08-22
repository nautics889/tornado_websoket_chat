let ws_connection;

$("#connect_btn").on("click", function() {
    if (!ws_connection) {
        ws_connection = new WebSocket("ws://37.57.82.158:8990/");
        console.log(ws_connection);

        $("#connect_btn").html('Disconnect');
        $("#output").append(`<input type="text" id="message_to_send">`);
        $("#output").append(`<button id="send_btn">Send</button>`);
        $("#send_btn").on("click", function() {
            ws_connection.send(JSON.stringify({
                content: $("#message_to_send").val()
            }));
        });

        ws_connection.onmessage = function(event) {
            msg = $(`<p class="msg">${event.data}</p>`).appendTo("#output");
            msg.animate(
                {
                    right: '150px',
                    opacity: 1
                },
                800
            );

            number_of_messages = $(".msg").length
            if (number_of_messages > 5) {
                $(".msg").slice(0, number_of_messages - 5).animate(
                    {
                        left: '150px',
                        opacity: 0
                    },
                    300, function() {
                        $(this).animate({height: '0px', margin: '0px'}, 100, function() {
                            $(this).remove();
                        });
                    }
                );
//                $(".msg").slice(number_of_messages - 5).animate(
//                    {
//                        bottom: $(".msg").outerHeight(true),
//                    },
//                    800
//                );
            };
        };
    }
    else if (ws_connection instanceof WebSocket) {
        if(ws_connection.readyState == 1) {
            ws_connection.close();
            $("#connect_btn").html('Disconnect');
        }
    };
});
