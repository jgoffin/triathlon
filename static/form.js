// this is the id of the form
$("#myForm").submit(function(e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.

    var form = $(this);
    var url = form.attr('action');

    $.ajax({
           type: "POST",
           url: url,
           data: form.serialize(), // serializes the form's elements.
           success: function(data)
           {
               console.log(data);
               $("#prediction").show();
               hours = Math.floor(data/3600);
               minutes = Math.floor((data - 3600*hours)/60);
               seconds = Math.round(data - 3600*hours - 60*minutes)
               $("#message").text(hours + " hours, "+minutes+" minutes, and "+seconds+" seconds");
               $(window).scrollTop($('#prediction').offset().top)
           },
           error: function(jqXHR, textStatus, errorThrown)
           {
                alert(errorThrown);
           }
         });
});

$('.timepicker1').timepicker({
    timeFormat: 'HH:mm:ss',
    interval: 60,
    minTime: '00:00:00',
    maxTime: '3:00:00',
    defaultTime: '00:00:00',
    startTime: '00:00:00',
    dynamic: false,
    dropdown: false,
    scrollbar: false
});
$('.timepicker2').timepicker({
    timeFormat: 'mm:ss',
    interval: 0,
    minTime: '00:00',
    maxTime: '30:00',
    defaultTime: '00:00',
    startTime: '00:00',
    dynamic: false,
    dropdown: false,
    scrollbar: false
});
