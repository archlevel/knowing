var Search = function(opts) {
    var self = this;
    self.opts = opts;

    self.initChartList();
};

Search.prototype = {
    constructor: Search,

    initChartList: function() {
        var self = this;

        $('#chart_list img').lazyload();

        setInterval(function() {
            self.refreshCharts();
        }, 60000);
    },

    refreshCharts: function() {
        var self = this;

        $('#chart_list img').each(function() {
            var src = $(this).attr('data-original');
            src = src.replace(/_=[0-9]+/, '_=' + new Date().getTime());
            $(this).replaceWith('<img data-original="' + src + '" src="/assets/img/transparent.gif">');
        });
        $('#chart_list img').lazyload();
    },

    _theEnd: undefined
};
