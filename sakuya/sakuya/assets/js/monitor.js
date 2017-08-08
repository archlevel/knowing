var Monitor = function(opts) {
    var self = this;
    self.opts = opts;
    self.initCharts();
};

Monitor.prototype = {
    constructor: Monitor,

    initCharts: function() {
        var self = this;

        $('#monitor_charts img').lazyload();
        self.resetInterval();
    },

    reloadCharts: function() {
        var self = this;

        $('#monitor_charts img').each(function() {
            var src = $(this).attr('data-original');
            src = src.replace(/_=[0-9]+/, '_=' + new Date().getTime());
            $(this).replaceWith('<img data-original="' + src + '" src="/assets/img/transparent.gif">');
        });
        $('#monitor_charts img').lazyload();
    },

    _interval: null,
    resetInterval: function() {
        var self = this;

        if (self._interval != null) {
            clearInterval(self._interval);
        }

        self._interval = setInterval(function() {
            self.reloadCharts();
        }, 60000);
    },

    _theEnd: undefined
};
