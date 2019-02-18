(function($) {
    "use strict"; // Start of use strict

    $('#signin').submit(function (event) {
        event.preventDefault();
        var username = $('#username').val();
        $.ajax({
            url: 'http://localhost:8002/rest-auth/login/',
            method: 'POST',
            data: {
                'username': username,
                'password': $('#password').val(),
            },
        }).done(function (data) {
            localStorage.setItem('user_key', data.key);
            $.ajax({
                url: 'http://localhost:8001/validate-token/',
                method: 'POST',
                data: {
                    'username': username,
                    'token': data.key,
                },
            }).done(function (data) {
               alert('You have successfully logged in.');
               localStorage.setItem('user_id', data.user_id);
            }).fail(function (data) {
               alert('Sorry, There is an error in the registration process. Please, try again.');
               console.log(data);
            });
           alert('You have successfully logged in.');
        }).fail(function (data) {
           alert('Sorry, There is an error in the registration process.');
           console.log(data);
        });
    });

})(jQuery);
