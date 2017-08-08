var Haopan = function(opts) {
    var self = this;
    self.opts = opts;

    self.initFilters();
    self.refreshCharts();
};

Haopan.prototype = {
    constructor: Haopan,

    initFilters: function() {
        var self = this;

        $.each(['cities', 'channels'], function() {
            self.bindFilterEvent($('#flt_' + this));
        });

        $('#flt_entries a[fltid]').live('click', function() {

            var fltid = $(this).attr('fltid');
            if (fltid == 'sum') {
                if ($(this).parent().hasClass('active')) {
                    return false;
                } else {
                    $('#flt_entries a[fltid!="sum"]').parent().remove();
                    $('#sel_entries option').removeAttr('disabled');
                    $(this).parent().addClass('active');
                }
            } else {
                $('#sel_entries option[value="' + $(this).attr('fltid') + '"]').removeAttr('disabled');
                $(this).parent().remove();
                if ($('#flt_entries li.active').length == 0) {
                    $('#flt_entries a[fltid="sum"]').parent().addClass('active');
                }
            }

            self.refreshCharts();

        });

        $('#sel_entries').change(function() {
            var fltid = $(this).val();
            if (!fltid) {
                return;
            }

            var $option = $('option:selected', this);

            var html = '<li class="active">' +
                       '<a href="javascript:void(0);" fltid="' + fltid + '">' +
                       $option.text() +
                       '</a></li>';

            $(html).insertBefore($(this).parent());

            $(this).val('');
            $option.attr('disabled', 'disabled');

            $('#flt_entries a[fltid="sum"]').parent().removeClass('active');

            self.refreshCharts();
        });

        $('#flt_charts a[fltid]').click(function() {

            var li = $(this).parent();
            if (li.hasClass('active')) {

                if ($('#flt_charts li.active').length == 1) {
                    return false;
                }
                li.removeClass('active');

            } else {

                li.addClass('active');

            }

            self.refreshCharts();

        });

    },

    bindFilterEvent: function(ul) {
        var self = this;

        $('a[fltid]', ul).click(function() {

            var fltid = $(this).attr('fltid');
            switch (fltid) {
            case 'sum':

                var li = $(this).parent();
                if (li.hasClass('active')) {
                    return false;
                }

                li.addClass('active').siblings().removeClass('active');

                break;

            case 'all':

                var li = $(this).parent();
                if (li.hasClass('active')) {
                    return false;
                }

                li.addClass('active').siblings().addClass('active');
                $('a[fltid="sum"]', ul).parent().removeClass('active');

                break;

            default:
                fltid = parseInt(fltid);

                var li = $(this).parent();
                if (li.hasClass('active')) {

                    li.removeClass('active');
                    $('a[fltid="all"]', ul).parent().removeClass('active');
                    if ($('li.active', ul).length == 0) {
                        $('a[fltid="sum"]', ul).parent().addClass('active');
                    }

                } else {

                    li.addClass('active');
                    $('a[fltid="sum"]', ul).parent().removeClass('active');
                    if ($('li.active', ul).length == $('li', ul).length - 2) {
                        $('a[fltid="all"]', ul).parent().addClass('active');
                    }

                }

            }

            self.refreshCharts();

        });
    },

    refreshCharts: function() {
        var self = this;

        var data = { prod: self.opts.prod };

        function parseFilters(ul) {
            if ($('a[fltid="sum"]', ul).parent().hasClass('active')) {
                return 0;
            }
            fltid_list = [];
            $('a[fltid]', ul).each(function() {
                var fltid = $(this).attr('fltid');
                if (fltid == 'sum' || fltid == 'all') {
                    return true;
                }
                if ($(this).parent().hasClass('active')) {
                    fltid_list.push(parseInt(fltid));
                }
            });
            return fltid_list.join(',');
        }

        $.each(['cities', 'channels', 'entries'], function() {
            data[this] = parseFilters($('#flt_' + this));
        });

        var charts = [];
        $('#flt_charts a[fltid]').each(function() {
            if ($(this).parent().hasClass('active')) {
                charts.push(parseInt($(this).attr('fltid')));
            }
        });
        data['charts'] = charts.join(',');
        data['_r'] = Math.random();
        $.getJSON('/monitor/haopan/charts', data, function(response) {
            if (response.status != 'ok') {
                alert(response.msg);
            } else {
                self.drawCharts(response.charts);
            }
        });

    },

    drawCharts: function(charts) {
        var self = this,
            ulCharts = $('#haopan_charts');

        $('li', ulCharts).remove();
        $.each(charts, function() {
            var html = '<li>' +
                       '<div class="title">' + this[0] + '</div>' +
                       '<a href="/chart/' + this[1] + '" target="_blank">' +
                       '<img data-original="/graph/haopan/list/' + this[1] + '?compzero=1&_=' + new Date().getTime()+ '" src="/assets/img/transparent.gif">' +
                       '</a>' +
                       '</li>';
            $('img', $(html).appendTo(ulCharts)).lazyload();
        });

        self.resetInterval();
    },

    reloadCharts: function() {
        var self = this;

        $('#haopan_charts img').each(function() {
            var src = $(this).attr('data-original');
            src = src.replace(/_=[0-9]+/, '_=' + new Date().getTime());
            $(this).replaceWith('<img data-original="' + src + '" src="/assets/img/transparent.gif">');
        });
        $('#haopan_charts img').lazyload();
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
