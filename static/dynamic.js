let wsConnection;

$('#connect_btn').on('click', function () {
  if (!wsConnection) {
    wsConnection = new WebSocket('ws://37.57.82.158:8990/')

    $('#connect_btn').html('Disconnect')
    $('#output').append('<input type="text" id="message_to_send">')
    $('#output').append('<button id="send_btn">Send</button>')
    $('#send_btn').on('click', function () {
      wsConnection.send(JSON.stringify({
        content: $('#message_to_send').val()
      }))
    })

    wsConnection.onmessage = function (event) {
      let msgObj = JSON.parse(event.data)
      if (msgObj.type === 'performance_info_message') {
        cpuChart.updateOptions({
          series: [{
            name: 'cpu_usage',
            data: msgObj.cpu_usage
          }],
          yaxis: {
            max: 100
          },
          xaxis: {
            categories: msgObj.number_of_cores
          }
        })
        ramChart.updateOptions({ series: [msgObj.ram_used] })
      } else {
        let msg = $(`<p class="msg">${event.data}</p>`).appendTo('#output')
        msg.animate(
          {
            right: '150px',
            opacity: 1
          },
          800
        )

        number_of_messages = $('.msg').length
        if (number_of_messages > 5) {
          $('.msg').slice(0, number_of_messages - 5).animate(
            {
              left: '150px',
              opacity: 0
            },
            300, function () {
              $(this).animate({ height: '0px', margin: '0px' }, 100, function () {
                $(this).remove()
              })
            }
          )
        };
      };
    }
    var cpuChartOptions = {
      yaxis: {
        max: 100
      },
      chart: {
        type: 'bar'
      },
      series: [{
        data: [0, 0, 0, 0]
      }],
      xaxis: {
        categories: [1, 2, 3, 4]
      }
    }

    var ramChartOptions = {
      chart: {
        width: 380,
        type: 'radialBar'
      },
      series: [70],
      labels: ['RAM used']
    }

    const cpuChart = new ApexCharts(document.querySelector('#cpu_chart'), cpuChartOptions)
    const ramChart = new ApexCharts(document.querySelector('#ram_chart'), ramChartOptions)

    ramChart.render()
    cpuChart.render()
  } else if (wsConnection instanceof WebSocket) {
    if (wsConnection.readyState === 1) {
      wsConnection.close()
      $('#connect_btn').html('Disconnect')
    }
  };
})
