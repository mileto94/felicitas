(function($) {
    "use strict"; // Start of use strict

    $('#game-name').text(`${localStorage.getItem('game_type_name')}`);
    $('#polls-count').text(`${localStorage.getItem('polls_count')}`);
    $('#total-polls').text(`${localStorage.getItem('game_polls_count')}`);

    $.ajax({
        url: 'http://localhost:8001/start-game/',
        method: 'POST',
        data: JSON.stringify({
            "token": localStorage.getItem('user_key'),
            "player": localStorage.getItem('user_id'),
            "game_type": localStorage.getItem('game_type_id')
        }),
        dataType: 'json',
        contentType: 'application/json'
    }).then(function (data) {
        localStorage.setItem('game_id', data.id);
        localStorage.setItem('result', data.result);
        localStorage.setItem('fished', data.finished);
        localStorage.setItem('poll_id', data.poll.id);

       $('#poll-name').text(data.poll.title);

       $.each(data.poll.answers, function (index, answer) {
           $('#poll-answers').append(`
                <div class="form-check">
                  <input class="form-check-input answer" type="radio" name="answers" id="exampleRadios${answer.id}" value="${answer.title}">
                  <label class="form-check-label" for="exampleRadios${answer.title}">
                    ${answer.title}
                  </label>
                </div>`
           );

        });
    });


    $('#vote-btn').click(function (event) {
        event.preventDefault();

        $.ajax({
        url: 'http://localhost:8001/poll-vote/',
        method: 'POST',
        data: JSON.stringify({
            "token": localStorage.getItem('user_key'),
            "player": localStorage.getItem('user_id'),
            "game_type": localStorage.getItem('game_type_id'),
            "vote": $('.answer:checked').val(),
            "game": localStorage.getItem('game_id'),
            "poll": localStorage.getItem('poll_id')
        }),
        dataType: 'json',
        contentType: 'application/json'
    }).then(function (data) {

        if(data.finished) {
            if(confirm("Your game is over. Do you want to see all results?")) {
                window.location.href = 'results.html';
            } else {
                window.location.href = 'index.html';
            }
        }
        console.log(data);
        localStorage.setItem('game_id', data.id);
        localStorage.setItem('result', data.result);
        localStorage.setItem('fished', data.finished);
        localStorage.setItem('poll_id', data.poll.id);

       $('#poll-name').text(data.poll.title);

       $.each(data.poll.answers, function (index, answer) {
           $('#poll-answers').append(`
                <div class="form-check">
                  <input class="form-check-input" type="radio" name="exampleRadios" id="exampleRadios${answer.id}" value="${answer.title}">
                  <label class="form-check-label" for="exampleRadios${answer.title}">
                    ${answer.title}
                  </label>
                </div>`
           );

        });
    });
    });
})(jQuery);
