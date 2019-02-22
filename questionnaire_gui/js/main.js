(function($) {
    "use strict"; // Start of use strict
    updateUserControls();
})(jQuery);

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
           updateUserControls();
           window.location.href = 'index.html';
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


function updateUserControls() {
    if(localStorage.getItem('user_key')) {
        $('#log-out-btn').show();
        $('#log-in-btn').hide();
        $('#register-btn').hide();
    } else {
        $('#log-out-btn').hide();
        $('#log-in-btn').show();
        $('#register-btn').show();
    }
}