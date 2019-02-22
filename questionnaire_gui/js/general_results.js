(function($) {
    "use strict"; // Start of use strict

    $.get('http://localhost:8001/ranked-scores/').done(function (data) {
        console.log('All results are loaded');

        $.each(data, function (index, score) {
            $('#general-results tbody').append(`
              <tr>
                  <th scope="row">${index + 1}</th>
                  <td>${score.player}</td>
                  <td>${score.game_type}</td>
                  <td>${score.result}</td>
              </tr>`);
        });
    }).fail(function (data) {
       alert('Sorry, There is an error in the getting results.');
       console.log(data);
    });

})(jQuery);