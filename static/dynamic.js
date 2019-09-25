let ws_connection;
let chart;

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
            msg_obj = JSON.parse(event.data)
            if (msg_obj.type == "performance_info_message") {
                cpu_chart.updateOptions({series: [{
                    name: 'cpu_usage',
                    data: msg_obj.cpu_usage
                }],
                yaxis: {
                    max: 100
                },
                xaxis: {
                    categories: msg_obj.number_of_cores
                }});
                ram_chart.updateOptions({series: [msg_obj.ram_used, msg_obj.ram_available]});
            }
            else {
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
                };
            };
        };
        var cpu_chart_options = {
            yaxis: {
                max: 100
            },
            chart: {
                type: 'bar'
            },
            series: [{
                name: 'cpu_usage',
                data: [0,0,0,0]
            }],
            xaxis: {
                categories: [1,2,3,4]
            }
        };

        var ram_chart_options = {
            chart: {
                width: 380,
                type: 'pie'
            },
            labels: ['Used', 'Free'],
            series: [0, 0],
            responsive: [{
                breakpoint: 480,
                options: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }]
        };

        cpu_chart = new ApexCharts(document.querySelector('#cpu_chart'), cpu_chart_options);
        ram_chart = new ApexCharts(document.querySelector('#ram_chart'), ram_chart_options)

        ram_chart.render();
        cpu_chart.render();
    }
    else if (ws_connection instanceof WebSocket) {
        if(ws_connection.readyState == 1) {
            ws_connection.close();
            $("#connect_btn").html('Disconnect');
        }
    };
});
