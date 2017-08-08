$(function() {

    var $warn = $('#header_warn'),
        $content = $('#header_warn_content');

    $warn.click(function() {
        window.location = '/alert';
    }).hover(function() {
        $content.css({
            left: $warn.position().left - $content.width() / 2,
            top: $(document).scrollTop() + $warn.position().top + 50
        }).show();
    }, function() {
        $content.hide();
    });

    function checkEvents() {

        $.getJSON('/ajax/events', function(data) {
            var msg = [];
            if (data.warning > 0) {
                msg.push(data.warning + ' 警告');
            }
            if (data.critical > 0) {
                msg.push(data.critical + ' 严重');
            }
            if (msg.length == 0) {
                $warn.addClass('ok').removeClass('error');
                $content.text('系统正常');

            } else {
                $warn.addClass('error').removeClass('ok');
                $content.text(msg.join(', '));
            }
        });

    }
    checkEvents();
    setInterval(checkEvents, 60000);
});
