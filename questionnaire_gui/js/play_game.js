(function($) {
    "use strict"; // Start of use strict

    $('#game-name').text(`${localStorage.getItem('game_type_name')}`);
    $('#polls-counter').text(`${localStorage.getItem('polls_counter')}`);
    $('#total-polls').text(`${localStorage.getItem('game_polls_count')}`);

    if(!localStorage.getItem('user_id')) {
        alert('You have to register or login in order to play');
        window.location.href = 'login.html';
    }

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
        localStorage.setItem('polls_counter', data.polls_counter);
        $('#polls-counter').text(data.polls_counter);

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
    }).catch(function (data) {
        console.log(data);
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
            if(confirm(`Congratulations! You've completed the game with score ${localStorage.getItem('result')}. Do you want to see all results?`)) {
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
        localStorage.setItem('polls_counter', data.polls_counter);

        $('#poll-name').text(data.poll.title);
        $('#polls-counter').text(`${localStorage.getItem('polls_counter')}`);

        $('#poll-answers').text('');
        $.each(data.poll.answers, function (index, answer) {
            $('#poll-answers').append(`
                 <div class="form-check">
                   <input class="form-check-input answer" type="radio" name="exampleRadios" id="exampleRadios${answer.id}" value="${answer.title}">
                   <label class="form-check-label" for="exampleRadios${answer.title}">
                     ${answer.title}
                   </label>
                 </div>`
            );

        });
    });
    });
})(jQuery);


function endGame() {
    if(confirm('Are you sure you want to end your game?')) {
        $.ajax({
            url: 'http://localhost:8001/end-game/',
            method: 'POST',
            data: JSON.stringify({
                "token": localStorage.getItem('user_key'),
                "id": localStorage.getItem('game_id'),
            }),
            dataType: 'json',
            contentType: 'application/json'
        }).then(function (data) {

            if(confirm(`We're sorry you're leaving! You've completed the game with score ${localStorage.getItem('result')}. Do you want to see all results?`)) {
                window.location.href = 'results.html';
            } else {
                window.location.href = 'index.html';
            }
            console.log(data);
            localStorage.setItem('game_id', data.id);
            localStorage.setItem('result', data.result);
            localStorage.setItem('fished', data.finished);
            localStorage.setItem('poll_id', data.poll.id);
            localStorage.setItem('polls_counter', data.polls_counter);
        });
    }
}
