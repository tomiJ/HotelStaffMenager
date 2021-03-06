$(function() {

   var calendar = $('#calendar').fullCalendar('getCalendar');

  // page is now ready, initialize the calendar...

  $('#calendar').fullCalendar({
      header: {
        left: 'prev,next today',
        center: 'title',
        right: 'month,basicWeek,basicDay'
      },
      navLinks: true, // can click day/week names to navigate views
      editable: false,
      eventLimit: true, // allow "more" link when too many events
      events: {
        url: "/getReservationList"
      }

  })

});