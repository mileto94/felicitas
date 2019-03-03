(function($) {
    "use strict"; // Start of use strict

    $.get(`${gameManagerUrl}/ranked-scores/${localStorage.game_type_id}`).done(function (data) {
        console.log('All results are loaded');
        $('#game-type-name').text(localStorage.game_type_name);
        $.each(data, function (index, score) {
            $('#ranked-results').append(`
              <li class="list-group-item d-flex justify-content-between align-items-center">
                ${score.player}
                <span class="badge badge-success">${score.result}</span>
              </li>`);
        });
    }).fail(function (data) {
       alert('Sorry, There is an error in the getting results.');
       console.log(data);
    });

})(jQuery);