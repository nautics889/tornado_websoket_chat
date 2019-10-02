let wsConnection;

$("#connect_btn").on("click", function() {
    if (!wsConnection) {
        wsConnection = new WebSocket("ws://37.57.82.158:8990/");
        console.log(wsConnection);

        $("#connect_btn").html('Disconnect');
        $("#output").append(`<input type="text" id="message_to_send">`);
        $("#output").append(`<button id="send_btn">Send</button>`);
        $("#send_btn").on("click", function() {
            wsConnection.send(JSON.stringify({
                content: $("#message_to_send").val()
            }));
        });

        wsConnection.onmessage = function(event) {
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
                ram_chart.updateOptions({series: [msg_obj.ram_used]});
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
                type: 'radialBar'
            },
            series: [70],
            labels: ['RAM used'],
        };

        cpu_chart = new ApexCharts(document.querySelector('#cpu_chart'), cpu_chart_options);
        ram_chart = new ApexCharts(document.querySelector('#ram_chart'), ram_chart_options)

        ram_chart.render();
        cpu_chart.render();
    }
    else if (wsConnection instanceof WebSocket) {
        if(wsConnection.readyState == 1) {
            wsConnection.close();
            $("#connect_btn").html('Disconnect');
        }
    };
});
