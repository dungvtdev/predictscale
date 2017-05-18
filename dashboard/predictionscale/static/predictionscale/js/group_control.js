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

    function fillData(data) {
        console.log(data)
        if (!data)
            return 2
        if (!('process' in data))
            return 2
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
        return data['next']
    }

    var url = $('#group-control').data('url')
    function pullData(url) {
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                next_secs = fillData(data)
                if(next_secs==0)
                    next_secs = 30
                setTimeout(pullData(url), next_secs*1000)
            }
        })
    }

    pullData(url)
});