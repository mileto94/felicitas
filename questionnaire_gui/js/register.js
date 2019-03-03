(function($) {
    "use strict"; // Start of use strict

    $('#signup').submit(function (event) {
        event.preventDefault();

        $.ajax({
            url: `${userManagerUrl}/rest-auth/registration/`,
            method: 'POST',
            data: {
                'email': $('#email').val(),
                'username': $('#username').val(),
                'password1': $('#password1').val(),
                'password2': $('#password2').val(),
            },
        }).done(function (data) {
            localStorage.setItem('user_key', data.key);
           alert('You have successfully registered. You should log in now.');
           window.location.href = 'login.html';
        }).fail(function (data) {
           alert('Sorry, There is an error in the registration process.');
           console.log(data)
        });
    });

})(jQuery);
