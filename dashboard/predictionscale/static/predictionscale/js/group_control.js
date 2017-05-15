$(document).ready(function () {
    // processes = $('div.instance-process')

    var data = [
        {
            id: "{instance_id}",
            process: 0,
            message: '',
            status: 'running',
            next: 'next seconds',
        }
    ]

    var next_seconds = 0;

    function fillData(data) {
        console.log(data)
        if (!data)
            return
        if (!('process' in data))
            return
        data = data['process']
        for (var i = 0; i < data.length; i++) {
            var d = data[i]
            pbar = $('.instance-process[data-id=' + d.instance_id + '] .progress-bar')
            lstatus = $('.instance-process[data-id=' + d.instance_id + '] .instance-status')
            lmsg = $('.instance-process[data-id=' + d.instance_id + '] .instance-message')

            pbar.css('width', d.process + '%')
            lstatus.text(d.status)
            lmsg.text(d.message)
        }
    }

    var url = $('#group-control').data('url')
    function pullData(url) {
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                fillData(data)
            }
        })
    }

    function update() {
        pullData(url)
        setTimeout(update, 2000)
    }

    update()
});