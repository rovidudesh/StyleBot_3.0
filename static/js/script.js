$(document).ready(function() {
    // Start chat session
    $('#startChatForm').submit(function(e) {
        e.preventDefault();
        
        const gender = $('#gender').val();
        const height = $('#height').val();
        const bodyType = $('#bodyType').val();
        
        $.post('/start_chat', {
            gender: gender,
            height: height,
            body_type: bodyType
        }, function(response) {
            $('#userDetailsForm').addClass('d-none');
            $('#chatInterface').removeClass('d-none');
            addMessage(response.bot_response, false);
        }).fail(function() {
            alert('Error starting chat session. Please try again.');
        });
    });
    
    // Send message
    $('#chatForm').submit(function(e) {
        e.preventDefault();
        const message = $('#userMessage').val().trim();
        
        if (message) {
            addMessage(message, true);
            $('#userMessage').val('');
            
            $.post('/send_message', {
                message: message
            }, function(response) {
                addMessage(response.bot_response, false);
            }).fail(function() {
                addMessage("Sorry, I'm having trouble responding. Please try again.", false);
            });
        }
    });
    
    // New chat button
    $('#newChatBtn').click(function() {
        $.post('/new_chat', function() {
            $('#chatMessages').empty();
            $('#chatInterface').addClass('d-none');
            $('#userDetailsForm').removeClass('d-none');
            $('#startChatForm')[0].reset();
        });
    });
    
    // Helper function to add messages to chat
    function addMessage(message, isUser) {
        const messageClass = isUser ? 'user-message' : 'bot-message';
        const messageType = isUser ? 'You' : 'StyleBot';
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        const messageHtml = `
            <div class="message ${messageClass}">
                <strong>${messageType}</strong>
                <div>${formatMessage(message)}</div>
                <div class="message-time">${timeString}</div>
            </div>
        `;
        
        $('#chatMessages').append(messageHtml);
        $('#chatMessages').scrollTop($('#chatMessages')[0].scrollHeight);
    }
    
    // Format message (convert newlines to HTML)
    function formatMessage(text) {
        return text.replace(/\n/g, '<br>');
    }
});