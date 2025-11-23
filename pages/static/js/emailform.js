function sendMessage() {
    var $btn = $(".contact_form button");
    var $response = $("#response");

    // Disable button while sending
    $btn.prop('disabled', true).find('.lnk').text('Sending...');
    $response.text('');

    $.ajax({
        type: 'POST',
        url: 'sendmessage',
        data: {
            csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
            name: document.getElementsByName("name")[0].value,
            email: document.getElementsByName("email")[0].value,
            message: document.getElementsByName("message")[0].value,
        },
        success: function (response) {
            $response.css('color', '#4CAF50').text(response.msg);
            $("#contact")[0].reset();
        },
        error: function (xhr) {
            var msg = 'Sorry, there was an error. Please email me directly at joaoariedi@gmail.com';
            if (xhr.responseJSON && xhr.responseJSON.msg) {
                msg = xhr.responseJSON.msg;
            }
            $response.css('color', '#f44336').text(msg);
        },
        complete: function () {
            $btn.prop('disabled', false).find('.lnk').text('Send Message');
        }
    });
}