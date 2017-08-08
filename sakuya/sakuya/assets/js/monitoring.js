var Monitoring = function(opts) {
    var self = this;

    self.opts = opts;
    self.refreshCharts();
    setTimeout(function() {
        window.location.reload();
    }, 60000);

};

Monitoring.prototype = {
    constrcutor: Monitoring,

    refreshCharts: function() {
        var self = this,
            ulCharts = $('#ul_charts');
        cate = '';
        if(self.opts['cate']) cate = self.opts['cate'];
        $.getJSON('/monitoring/get_charts'+ cate, function(response) {

            var now = new Date().getTime();

            for (var i = 0; i < response.length; ++i) {

                var li = $('li', ulCharts).eq(i),
                    html = '<li>' +
                           '<div class="title">' + response[i].name + '</div>' +
                           '<a href="/chart/' + response[i].id + '" target="_blank">' +
                           '<img data-original="/graph/haopan/list/' + response[i].id + '?_=' + now + '"' +
                           ' src="/assets/img/transparent.gif">' +
                           '</a></li>',
                    liNew = $(html);

                if (li.length > 0) { // refresh

                    li.replaceWith(liNew);

                } else { // add

                    liNew.appendTo(ulCharts);

                }

                if (response[i].critical) {
                    liNew.addClass('critical');
                }

            }

            // clear unused
            while ($('li', ulCharts).length > response.length) {
                $('li', ulCharts).last().remove();
            }

            // load images
            $('li img', ulCharts).lazyload();

        });
    },

    _theEnd: undefined
};
