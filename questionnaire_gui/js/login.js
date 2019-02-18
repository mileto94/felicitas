(function($) {
    "use strict"; // Start of use strict

    $('#signin').submit(function (event) {
        event.preventDefault();

        $.ajax({
            url: 'http://localhost:8002/rest-auth/login/',
            method: 'POST',
            data: {
                'username': $('#username').val(),
                'password': $('#password').val(),
            },
        }).done(function (data) {
            localStorage.setItem('user_key', data.key);
           alert('You have successfully logged in.');
        }).fail(function (data) {
           alert('Sorry, There is an error in the registration process.');
           console.log(data)
        });
    });

})(jQuery);
