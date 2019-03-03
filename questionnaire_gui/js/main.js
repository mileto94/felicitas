(function($) {
    "use strict"; // Start of use strict
    var userManagerUrl = 'https://e3aqa83by0.execute-api.us-east-2.amazonaws.com/production',
        gameManagerUrl = 'https://xymwo33qdh.execute-api.us-east-2.amazonaws.com/production',
        gameSetupUrl = 'https://0vquql6thh.execute-api.us-east-2.amazonaws.com/production';
    updateUserControls();
})(jQuery);

function logOut() {
    $.ajax({
        url: `${userManagerUrl}/rest-auth/logout/`,
        method: 'POST',
        data: {},
    }).done(function (data) {
        $.ajax({
            url: `${gameManagerUrl}/log-out/`,
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