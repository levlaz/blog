(function () {
    'use strict';

    function replyForm(comment, postId, commentId) {

        var formTemplate
        =   '<form action="/comment/{{postId}}/{{commentId}}" method="POST">'
        +   '<input type="text" name="author" placeholder="Your Name (optional)">'
        +   '<br />'
        +   '<input type="text" name="email" placeholder="Your Email (optional)">'
        +   '<input type="text" name="website" placeholder="Your Website (optional)">'
        +   '<br />'
        +   '<textarea name="comment_body" rows=5 cols=80 placeholder="Your Comment" required></textarea>'
        +   '<br />'
        +   '<input type="submit" value="Add Comment">'
        +   '</form>'

        var form = formTemplate;

        form = form.replace('{{postId}}', postId);
        form = form.replace('{{commentId}}', commentId);

        var replyDiv = document.createElement('div');

        replyDiv.innerHTML = form;

        comment.parentNode.insertBefore(replyDiv, comment.nextSibling);
    }

    window.addEventListener('load', function() {
        var replyButtons = document.getElementsByClassName('replyButton');

        Array.prototype.forEach.call(replyButtons, function(replyButton) {
            var commentId = replyButton.attributes.commentId.value;
            var postId = replyButton.attributes.postId.value;

            replyButton.addEventListener('click', function() {
                replyForm(replyButton, postId, commentId);
            });

        });

    });

})();