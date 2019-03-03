(function($) {
    "use strict"; // Start of use strict

    $('#signin').submit(function (event) {
        event.preventDefault();
        var username = $('#username').val();
        $.ajax({
            url: `${userManagerUrl}/rest-auth/login/`,
            method: 'POST',
            data: {
                'username': username,
                'password': $('#password').val(),
            },
        }).done(function (data) {
            localStorage.setItem('user_key', data.key);
            $.ajax({
                url: `${gameManagerUrl}/validate-token/`,
                method: 'POST',
                data: {
                    'username': username,
                    'token': data.key,
                },
            }).done(function (data) {
               alert('You have successfully logged in.');
               localStorage.setItem('user_id', data.user_id);
               window.location.href = 'index.html';
            }).fail(function (data) {
               alert('Sorry, There is an error in the login process. Please, try again.');
               console.log(data);
            });
           alert('You have successfully logged in.');
        }).fail(function (data) {
           alert('Sorry, There is an error in the login process.');
           console.log(data);
        });
    });

})(jQuery);
