$("#connect_btn").on("click", function() {
    let socket = new WebSocket("ws://37.57.82.158:8990/");
    $("#connect_btn").html('Disconnect');

    socket.onmessage = function(event){
        $("#output").append(`<p>${event.data}</p>`)
    };
});
