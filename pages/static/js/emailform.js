function sendMessage() {

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
            $("#response").text(response.msg);
            $("#contact")[0].reset();
        }
    });
}