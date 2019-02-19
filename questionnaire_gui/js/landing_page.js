(function($) {
    "use strict"; // Start of use strict

    $.ajax('http://localhost:8000/games-list/').then(function (data) {
       $.each(data.games, function (index, game) {
           $('#games-list').append(`
                <div class="col-md-4 col-sm-6 portfolio-item">
                  <a class="portfolio-link" data-toggle="modal" href="#portfolioModal${game.id}">
                    <div class="portfolio-hover">
                      <div class="portfolio-hover-content">
                        <i class="fas fa-plus fa-3x"></i>
                      </div>
                    </div>
                    <img class="img-fluid" src="${game.image}" alt="${game.name} logo">
                  </a>
                  <div class="portfolio-caption">
                    <h4>${game.name}</h4>
                    <p class="text-muted">${game.description}</p>
                  </div>
                </div>`
           );


           $('#modals-list').append(`
              <!-- Modal 1 -->
              <div class="portfolio-modal modal fade" id="portfolioModal${game.id}" tabindex="-1" role="dialog" aria-hidden="true">
                <div class="modal-dialog">
                  <div class="modal-content">
                    <div class="close-modal" data-dismiss="modal">
                      <div class="lr">
                        <div class="rl"></div>
                      </div>
                    </div>
                    <div class="container">
                      <div class="row">
                        <div class="col-lg-8 mx-auto">
                          <div class="modal-body">
                            <!-- Project Details Go Here -->
                            <h2 class="text-uppercase">${game.name}</h2>
                            <p class="item-intro text-muted">Total questions: ${game.polls_count}</p>
                            <img class="img-fluid d-block mx-auto" src="${game.image}" alt="">
                            <p>${game.description}</p>
                            <button class="btn btn-primary" type="button" onclick="startGame(${game.id}, '${game.name}', ${game.polls_count})">
                              <i class="fas fa-play-circle"></i>
                              Start Game</button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>`
           );

        });
    });
})(jQuery);

function startGame(game_type_id, game_name, game_polls_count) {
    localStorage.setItem('game_type_id', game_type_id);
    localStorage.setItem('game_type_name', game_name);
    localStorage.setItem('game_polls_count', game_polls_count);
    localStorage.setItem('polls_count', 0);
    window.location.href='play_game.html';
}

function logOut() {
    $.ajax({
        url: 'http://localhost:8002/rest-auth/logout/',
        method: 'POST',
        data: {},
    }).done(function (data) {
        $.ajax({
            url: 'http://localhost:8001/log-out/',
            method: 'POST',
            data: {
                'user_id': localStorage.getItem('user_id'),
                'token': localStorage.getItem('user_key'),
            },
        }).done(function (data) {
           alert('You have successfully logged out.');
           localStorage.clear();
        }).fail(function (data) {
           alert('Sorry, There is an error in the log out process. Please, try again.');
           console.log(data);
        });
       alert('You have successfully logged out.');
    }).fail(function (data) {
       alert('Sorry, There is an error in the log out process.');
       console.log(data);
    });
}
