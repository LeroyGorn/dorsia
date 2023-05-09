$(window).on("load", function() {
    function* getMessageGenerator(messages) {
      let index = 0;
      while (index < messages.length) {
        yield messages[index];
        index++;
      }
    }
    const messageGenerator = getMessageGenerator(user_history);

    for (let i = 0; i < user_history.length; i++) {
      const message = messageGenerator.next().value;
      console.log(message)
      if (message === ''){
          sendChatbotMessage('');
      } else {
          if (i % 2 == 0) {
              setTimeout(function () {
                  UserQuestionSend(message);
              }, i * 1000);
          } else {
              setTimeout(function () {
                  sendChatbotMessage(message);
              }, i * 1000);
          }
      }
    }
    function sendMessage() {
        let message = $("#message-input-field").val();
        let csrf_token = $("[name='csrfmiddlewaretoken']").val();
        let url = "/chat";
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
            },
            error: function(response) {
                alert("Error processing your request. Please try again later.");
            }
        });
    }

    $("#send-message-button").click(sendMessage);

    $("#message-input-field").on('keydown', function(event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            sendMessage();
        }
    });

});