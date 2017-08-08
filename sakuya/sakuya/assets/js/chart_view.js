var ChartView = function(opts) {
    var self = this;
    self.opts = opts;

    self.mainId = self.opts.series[0][0];

    self.initTimeRange();
    self.initYlim();
    self.initFollow();
    self.initHide();
    self.initChartParams();
    self.initChart();
    self.initAck();

    $('td[rel="popover"]').popover({
        title: '接警人',
        placement: 'right',
        trigger: 'hover'
    });

};

ChartView.prototype = {
    constructor: ChartView,

    initTimeRange: function() {
        var self = this;

        function setDtDate() {
            if ($('#dt_start').val() == $('#dt_end').val()) {
                $('#dt_date').val($('#dt_start').val());
            } else {
                $('#dt_date').val('');
            }
        }

        function setMinMax() {
            $('#dt_start').datepicker('option', 'maxDate', $('#dt_end').val());
            $('#dt_end').datepicker('option', 'minDate', $('#dt_start').val());
        }

        $('#dt_date').datepicker({
            dateFormat: 'yy-mm-dd',
            onSelect: function(dateText, inst) {
                $('#dt_start, #dt_end').val(dateText);
                setMinMax();
                self.resetData();
            }
        });

        $('#dt_start').datepicker({
            dateFormat: 'yy-mm-dd',
            maxDate: self.opts.curDate,
            onSelect: function(dateText, inst) {
                setDtDate();
                setMinMax();
            }
        });

        $('#dt_end').datepicker({
            dateFormat: 'yy-mm-dd',
            minDate: self.opts.curDate,
            onSelect: function(dateText, inst) {
                setDtDate();
                setMinMax()
            }
        });

        $('#btn_reset').click(function() {
            self.resetData();
        });

        $('#btn_refresh').click(function() {
            self.refreshData();
        });

        $('#btngrp_date_range :button').click(function() {

            if ($(this).attr('dt_date')) {
                $('#dt_start, #dt_end').val($(this).attr('dt_date'));
            } else {
                $('#dt_start').val($(this).attr('dt_start'));
                $('#dt_end').val(self.opts.curDate);
            }

            setDtDate();
            setMinMax();
            self.resetData();
        });

        $('#cb_daily').click(function() {
            self.chartParams['daily'] = $(this).is(':checked');
            self.resetData();
        });

    },

    initYlim: function() {
        var self = this;

        $('#btn_ylim').click(function() {

            var ylim_min = $('#ylim_min').val();
            if (!ylim_min) {
                ylim_min = null;
            } else if (!ylim_min.match(/^[0-9]+$/)) {
                alert('请输入正确的下限值。');
                return false;
            } else {
                ylim_min = parseInt(ylim_min);
            }

            var ylim_max = $('#ylim_max').val();
            if (!ylim_max) {
                ylim_max = null;
            } else if (!ylim_max.match(/^[0-9]+$/)) {
                alert('请输入正确的上限值。');
                return false;
            } else {
                ylim_max = parseInt(ylim_max);
            }

            if (ylim_min != null && ylim_max != null && ylim_min >= ylim_max) {
                alert('请输入正确的上下限值。');
                return false;
            }

            self.mainChart.yAxis[0].setExtremes(ylim_min, ylim_max);

        });
    },
    initHide: function(){
        var self = this;
        $('#btn_hide').click(function() {
            var btn = $(this);
            var status = btn.attr('vstatus');
            var vstatus = status==1 ? 0 : 1;
            var txt = status==0 ? '取消隐藏' : '隐藏图表';
            $.getJSON('/chart/hide/' + self.mainId+'?status='+status+'&_r='+Math.random(), function(response) {
                if (response.status == 'ok') {
                    btn.attr('vstatus',vstatus).val(txt);
                } else {
                    alert(response.msg);
                }
            });
        });
    },
    initFollow: function() {
        var self = this;

        $('#btn_follow').click(function() {
            var btn = $(this),
                action = $(this).is('.btn-success') ? 'follow' : 'unfollow';

            $.getJSON('/chart/' + action + '/' + self.mainId+'?_r='+Math.random(), function(response) {
                if (response.status == 'ok') {
                    if (action == 'follow') {
                        btn.removeClass('btn-success').addClass('btn-info').val('取消订阅');
                        $('a.warning-tips').fadeIn();
                        $('label[for^=alert_item_]').show();
                    } else {
                        btn.removeClass('btn-info').addClass('btn-success').val('订阅图表');
                        $('a.warning-tips').fadeOut();
                        $('label[for^=alert_item_]').hide();
                    }
                } else {
                    alert(response.msg);
                }
            });

        });

        $('#alert_item_all').click(function() {

            var checked = $(this).is(':checked');
            $(':checkbox[id^="alert_item_id_"]').each(function() {

                if (checked) {
                    $(this).attr('checked', 'checked').attr('disabled', 'disabled');
                } else {
                    $(this).removeAttr('checked').removeAttr('disabled');
                }

            });

            self.changeRecv();

        });

        $(':checkbox[id^="alert_item_id_"]').click(function() {
            self.changeRecv();
        });

    },

    changeRecv: function() {
        var self = this;

        var data = {
            chart_id: self.mainId
        };

        if ($('#alert_item_all').is(':checked')) {
            data['recv_rules'] = 'all';
        } else {
            var recv_rules = [];
            $(':checkbox[id^="alert_item_id_"]').each(function() {
                if ($(this).is(':checked')) {
                    recv_rules.push($(this).attr('id').split('_')[3]);
                }
            });
            data['recv_rules'] = recv_rules.join(',');
        }
        data['_r'] = Math.random();
        $.getJSON('/chart/recv_warning', data, function(response) {

        });

    },

    initChartParams: function() {
        var self = this;

        var idList = [], deltaList = [];
        $.each(self.opts.series, function() {
            idList.push(this[0]);
            deltaList.push(this[1]);
        })

        self.chartParams = {
            id_list: idList.join(','),
            delta_list: deltaList.join(','),
            start: self.opts.curDate,
            end: self.opts.curDate,
            daily: false
        };

    },

    initChart: function() {
        var self = this;

        var series = [];
        $.each(self.opts.series, function() {
            series.push({
                seriesInfo: this,
                name: this[2],
                cursor: 'pointer',
                color: this[3]
            });
        });
        series.reverse();

        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });

        self.mainChart = new Highcharts.Chart({
            credits: {
                enabled: false
            },
            chart: {
                renderTo: 'div_main_chart',
                zoomType: 'x',
                events: {
                    selection: function(event) {
                        self.chartParams['start'] = Highcharts.dateFormat('%Y-%m-%d %H:%M', event.xAxis[0].min);
                        self.chartParams['end'] = Highcharts.dateFormat('%Y-%m-%d %H:%M', event.xAxis[0].max);
                        self.refreshData();
                        event.preventDefault();
                    }
                }
            },
            title: {
                text: null
            },
            xAxis: {
                type: 'datetime',
                maxZoom: 5 * 60000, // 5'
                title: {
                    text: null
                },
                dateTimeLabelFormats: {
                    second: '%H:%M:%S',
                    minute: '%H:%M',
                    hour: '%H:%M',
                    day: '%m-%d',
                    week: '%m-%d',
                    month: '%Y-%m',
                    year: '%Y'
                }
            },
            yAxis: {
                title: {
                    text: null
                },
                min: 0,
                labels: {
                    formatter: function() {
                        return this.value;
                    }
                }
            },
            tooltip: {
                crosshairs: true,
                shared: true,
                animation: false,
                borderColor: 'black',
                borderWidth: 1,
                borderRadius: 3,
                backgroundColor: 'beige',
                formatter: function() {
                    var html = Highcharts.dateFormat('%Y-%m-%d %H:%M', this.x);
                    $.each(this.points.reverse(), function() {
                        html += '<br>' + this.series.name + '：' +
                                '<span style="font-weight:bold;color:' + this.series.color + '">' +
                                this.y + '</span>';
                    });
                    return html;
                },
                style: {
                    "line-height": "17px"
                }
            },
            legend: {
                reversed: true
            },
            plotOptions: {
                line: {
                    lineWidth: 2,
                    marker: {
                        enabled: false,
                        states: {
                            hover: {
                                enabled: true,
                                radius: 4
                            }
                        }
                    },
                    shadow: false,
                    states: {
                        hover: {
                            lineWidth: 2
                        }
                    },
                    events: {
                        click: function(event) {

                            var dlg = $('#dlg_detail'),
                                dt = Highcharts.dateFormat('%Y-%m-%d %H:%M', event.point.x + this.options.seriesInfo[1] * 86400000),
                                data = {
                                    tid: this.options.seriesInfo[0],
                                    dt: dt
                                };

                            $('h3', dlg).eq(0).text(dt);
                            $.get('/ajax/detail', data, function(response) {

                                var dlg = $('#dlg_detail');

                                if ($('h3', dlg).eq(0).text() == dt) {
                                    var html;
                                    if (response) {
                                        html = response;
                                    } else {
                                        html = '<i class="icon-exclamation-sign"></i> 无详细信息';
                                    }
                                    $('div.modal-body', dlg).html(html);
                                }

                                dlg.modal();

                            }, 'html');

                        }
                    }
                }
            },
            series: series
        });

        self.resetData();

    },

    resetData: function() {
        var self = this,
            dt_start = $('#dt_start').val(),
            dt_end = $('#dt_end').val(),
            dt_start_obj, dt_end_obj, dt_delta;

        try {
            dt_start_obj = $.datepicker.parseDate('yy-mm-dd', dt_start);
            dt_end_obj = $.datepicker.parseDate('yy-mm-dd', dt_end);
            dt_delta = dt_end_obj - dt_start_obj;
        } catch (err) {
            alert('日期不正确');
            return false;
        }

        if (self.chartParams['daily']) {
            if (dt_delta <= 86400000 * 6) { // less than 7 days
                dt_start_obj = new Date(dt_end_obj.getTime() - 86400000 * 6);
                dt_start = $.datepicker.formatDate('yy-mm-dd', dt_start_obj);
                $('#dt_start').val(dt_start);
                $('#dt_date').val('');
            }
        } else {
            if (dt_delta > 86400000 * 29) { // more than 30 days
                self.chartParams['daily'] = true;
                $('#cb_daily').attr('checked', 'checked');
            }
        }

        self.chartParams['start'] = dt_start + ' 00:00';
        self.chartParams['end'] = dt_end + ' 23:59';

        self.refreshData();
    },

    refreshData: function() {
        var self = this;

        self.mainChart.showLoading('加载中……');

        $.getJSON('/chart/data', self.chartParams, function(response) {

            if (!$.isArray(response)) {
                self.mainChart.showLoading('系统错误，请联系管理员。');
                return;
            }

            var numSeries = self.opts.series.length,
                seriesData = [];
            for (var i = 0; i < numSeries; ++i) {
                seriesData.push([]);
            }

            $.each(response, function() {
                for (var i = 0; i < numSeries; ++i) {
                    if (this.length > i + 1) {
                        seriesData[i].push([this[0], this[i + 1]]);
                    }
                }
            });

            $.each(seriesData, function(i) {
                self.mainChart.series[numSeries - i - 1].setData(this);
            });

            self.mainChart.hideLoading();

            self.refreshSummary();
            self.refreshDataTable();
        });
    },

    refreshDataTable: function() {
        var self = this,
            numSeries = self.mainChart.series.length;

        if (numSeries == 0) {
            return;
        }

        var tbl = $('#chart-data table');
        tbl.find('tr').not(':first').remove();
        tbl.find('tr:first th:gt(3)').remove();

        $.each(self.mainChart.series, function(i) {
            var html = '<th>' + self.mainChart.series[numSeries - i - 1].name + '</th>';
            $(html).appendTo(tbl.find('tr:first'));
        });
        var t=1;
        for (var i = 60; i >0 ; i--) {

            if (self.mainChart.series[0].data.length <= i) {
                break;
            }

            var dt = new Date(self.mainChart.series[0].data[i].x);

            var html = '<tr>' +
                       '<td>' + (t) + '</td>' +
                       '<td>' + dt.getFullYear() + '-' + (dt.getMonth() + 1) + '-' + dt.getDate() + '</td>' +
                       '<td>' + dt.getHours() + '</td>' +
                       '<td>' + dt.getMinutes() + '</td>';

            $.each(self.mainChart.series, function(j) {
                var y = self.mainChart.series[numSeries - j - 1].data[i].y;
                html += '<td>' + (y == null ? '-' : y) + '</td>';
            });

            html += '</tr>';
            t+=1;
            $(html).appendTo(tbl);

        }
        /*
        for (var i = 0; i < 60; ++i) {

            if (self.mainChart.series[0].data.length <= i) {
                break;
            }

            var dt = new Date(self.mainChart.series[0].data[i].x);

            var html = '<tr>' +
                       '<td>' + (i + 1) + '</td>' +
                       '<td>' + dt.getFullYear() + '-' + (dt.getMonth() + 1) + '-' + dt.getDate() + '</td>' +
                       '<td>' + dt.getHours() + '</td>' +
                       '<td>' + dt.getMinutes() + '</td>';

            $.each(self.mainChart.series, function(j) {
                var y = self.mainChart.series[numSeries - j - 1].data[i].y;
                html += '<td>' + (y == null ? '-' : y) + '</td>';
            });

            html += '</tr>';

            $(html).appendTo(tbl);

        }*/

    },

    elSummary: null,
    refreshSummary: function() {
        var self = this;

        var curIndex, prevIndex;
        if (self.opts.series.length == 2) {
            curIndex = 1;
            prevIndex = 0;
        } else if (self.opts.series.length == 4) {
            curIndex = 3;
            prevIndex = 1;
        } else {
            return;
        }

        var curSum = 0, prevSum = 0;
        for (var i = 0; i < self.mainChart.series[0].data.length; ++i) {
            curSum += self.mainChart.series[curIndex].data[i].y;
            prevSum += self.mainChart.series[prevIndex].data[i].y;
        }

        var diff = curSum - prevSum,
            diffStr = diff > 0 ? ('+' + diff) : diff
            html = '<b>当日合计：</b>' + curSum + ' '
                 + '<b>上周合计：</b>' + prevSum + ' '
                 + '<b>差值：</b>' + diffStr;

        if (self.elSummary != null) {
            self.elSummary = self.elSummary.destroy();
        }
        self.elSummary = self.mainChart.renderer.text(html, 35, $(self.mainChart.container).height() - 25).add();

    },

    initAck: function() {
        var self = this;

        if ($('#btn_ack').length == 0) {
            return;
        }

        $('#dlg_ack').modal({
            show: false
        });

        $('#btn_ack').click(function() {
            $('#dlg_ack').modal('show');
        });

        $('select[name="cl2"]').change(function() {
            var selCl3 = $('select[name="cl3"]');
            selCl3.find('option').not(':first').remove();

            var options;
            if ($(this).val() in self.opts.cl3s) {
                options = self.opts.cl3s[$(this).val()];
            } else {
                options = [];
            }

            $.each(options, function() {
                $('<option value="' + this[0] + '">' + this[1] + '</option>').appendTo(selCl3);
            });

            if (options.length > 0) {
                selCl3.val(options[0][0]);
            }

            selCl3.change();
        });

        $('select[name="cl3"]').change(function() {
            if (!$(this).val()) { // new category
                $(':text[name="cl3_new"]').show();
            } else {
                $(':text[name="cl3_new"]').hide();
            }
        });

        $('#btn_ack_submit').click(function() {

            var data = {};
            var selCl3 = $('select[name="cl3"]');
            if (!selCl3.val()) { // new category
                var txtCl3 = $(':text[name="cl3_new"]');
                if (!txtCl3.val()) {
                    alert('请输入新栏目名称。');
                    return false;
                }
                data.cl2 = $('select[name="cl2"]').val();
                data.cl3 = txtCl3.val();
            } else {
                data.cl3 = selCl3.val();
            }

            $.post('/chart/ack/' + self.opts.chartId, data, function(response) {
                if (response.status == 'ok') {
                    window.location.reload();
                } else {
                    alert(response.msg);
                }
            }, 'json');
        });

    },

    _theEnd: undefined
};
