var $DOM = $(document);

$DOM.on('click', '#login_submit', function() {

	console.log("login clicked");
    var email = $(".email").val();
    var password = $(".password").val();

    if (!email) {
        alertify.set('notifier', 'position', 'top-right');
        alertify.error("Email or username is required");
        return;
    }

    if (!password || password.length < 6 || password.length > 12) {
        alertify.set('notifier', 'position', 'top-right');
        alertify.error("Password must be between 6 and 12 characters");
        return;
    }

    // Mock implementation: no server call
    alertify.set('notifier', 'position', 'top-center');
    alertify.success('Login in progress...');
    setTimeout(function() {
        window.location.href = "/";
    }, 2000);
});

$DOM.on('click', '#google_login', function() {
    alertify.set('notifier', 'position', 'top-center');
    alertify.success('Logging in with Google...');
    setTimeout(function() {
        window.location.href = "/";
    }, 2000);
});

$DOM.on('click', '#facebook_login', function() {
    alertify.set('notifier', 'position', 'top-center');
    alertify.success('Logging in with Facebook...');
    setTimeout(function() {
        window.location.href = "/";
    }, 2000);
});

$DOM.on('click', '#twitter_login', function() {
    alertify.set('notifier', 'position', 'top-center');
    alertify.success('Logging in with Twitter...');
    setTimeout(function() {
        window.location.href = "/";
    }, 2000);
});

$DOM.on('click', '#apple_login', function() {
    alertify.set('notifier', 'position', 'top-center');
    alertify.success('Logging in with Apple...');
    setTimeout(function() {
        alertify.error('Harmful ID detected, Apple ID not acceptable for login on this page');
    }, 2000);
});
