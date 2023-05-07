$(document).ready(function() {
    $("#send-message-button").click(function() {
        let message = $("#message-input-field").val();
        let csrf_token = $("[name='csrfmiddlewaretoken']").val();
        let url = "/";
        $.ajax({
            type: "POST",
            url: url,
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'message': message
            },
            success: function(response) {
                const responseText = response.response;
                UserQuestionSend();
                sendChatbotMessage(responseText);
                // Handle the response here
            },
            error: function(response) {
                console.log(response);
                UserQuestionSend();
                // Handle the error here
            }
        });
    });
});