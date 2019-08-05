$("#connect_btn").on("click", function() {
    let socket = new WebSocket("ws://37.57.82.158:8990/");

    $("#disconnect_btn").on("click", function() {
        socket.close();
        console.log('test');
    });

//    $("#connect_btn").html('Disconnect');
//    $("#output").append(`<input type="text" id="message_to_send">`)
//    $("#output").append(`<button id="send_btn">Send</button>`)
//    $("#send_btn").on("click", function() {
//        socket.send(JSON.stringify({
//            content: $("#message_to_send").val()
//        }));
//    })
//
//    socket.onmessage = function(event) {
//        $("#output").append(`<p>${event.data}</p>`)
//    };
});

