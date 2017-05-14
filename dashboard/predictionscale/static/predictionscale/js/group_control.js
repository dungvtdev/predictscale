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
        if (!data)
            return

        for (var d in data) {
            pbar = $('instance-process[data-id=' + d.id + '] .progress-bar')
            lstatus = $('instance-process[data-id=' + d.id + '] .instance-status')
            pbar.css('width', d.process + '%')
            lstatus.text = d.status
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

    function update(){
        next_seconds = pullData(url)   
        if(next_seconds <=0){
            next_seconds = 4
        }
        setTimeout(update, next_seconds * 1000)   
    }

    update()
});