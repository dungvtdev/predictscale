$(document).ready(function () {
    var data = $("div#service-data div")

    var default_data = {
        period: data.data("period"),
        dataLength: data.data("data-length"),
        recentPoint: data.data("recent-point"),
        periodicNumber: data.data("periodic-number"),
        neuralSize: data.data("neural-size"),
        predictLength: data.data("predict-length"),
        updateInTime: data.data("update-in-time"),
    }

    function filldata() {
        $.each(default_data, function (key, val) {
            $('form#settingForm input[name="' + key + '"]').val(val);
        })
    }

    var btn_refesh = $('form#settingForm button#refresh')
    btn_refesh.click(function(){
        filldata();
    });

    filldata()
});