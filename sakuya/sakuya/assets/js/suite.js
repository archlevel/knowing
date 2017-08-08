var Suite = function(opts) {
    var self = this;
    self.opts = opts;

    self.initCharts();
    self.initDlgDetail();
};

Suite.prototype = {
    constructor: Suite,

    initCharts: function() {
        var self = this;

        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });

        self.charts = {};
        $.each(self.opts.charts, function(index, chart) {

            var chartId = 'chart_' + index;
            self.charts[chartId] = {
                info: chart
            };

            var html = '<div class="suite-chart-item">' +
                       '<div id="' + chartId + '" style="width:850px;height:320px;"></div>' +
                       '</div>';
            $(html).appendTo('div.suite-charts');

            var idList = [], deltaList = [], series = [];
            $.each(chart.series, function() {
                idList.push(this[1]);
                deltaList.push(0);
                series.push({
                    seriesInfo: this,
                    name: this[0],
                    type: this[2],
                    hasDetail: self.opts.hasDetail,
                    cursor: 'pointer',
                    events: {
                        click: function(event) {
                            var point = event.point,
                                series = point.series;

                            if (!series.options.hasDetail) {
                                return false;
                            }

                            self.drillDown(point.x, series.options.seriesInfo[1], series.name);
                        }
                    }
                });
            });
            series.reverse();

            self.charts[chartId].params = {
                id_list: idList.join(','),
                delta_list: deltaList.join(','),
                start: self.opts.curDate + ' 00:00',
                end: self.opts.curDate + ' 23:59'
            };

            self.charts[chartId].object = new Highcharts.Chart({
                credits: {
                    enabled: false
                },
                chart: {
                    renderTo: chartId
                },
                title: {
                    text: chart.title
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
                            return this.value / 100+ '%';
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
                                    (this.y / 100) + '%</span>';
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
                                    enabled: false
                                }
                            }
                        },
                        shadow: false,
                        states: {
                            hover: {
                                lineWidth: 2
                            }
                        }
                    },
                    area: {
                        lineWidth: 2,
                        marker: {
                            enabled: false,
                            states: {
                                hover: {
                                    enabled: false
                                }
                            }
                        },
                        shadow: false,
                        states: {
                            hover: {
                                lineWidth: 2
                            }
                        }
                    }
                },
                series: series
            });

            self.resetData(chartId);

        });

    },

    resetData: function(chartId) {
        var self = this;

        self.refreshData(chartId);
    },

    refreshData: function(chartId) {
        var self = this,
            chart = self.charts[chartId];

        if (!chart) {
            return;
        }

        chart.object.showLoading('加载中……');

        $.getJSON('/chart/data', chart.params, function(response) {

            if (!$.isArray(response)) {
                chart.object.showLoading('系统错误，请联系管理员。');
                return;
            }

            var numSeries = chart.info.series.length,
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
                chart.object.series[numSeries - i - 1].setData(this);
            });

            chart.object.hideLoading();
        });
    },

    drillDown: function(millitime, id, name) {
        var self = this,
            dlg = $('#dlg_detail'),
            dt = Highcharts.dateFormat('%Y-%m-%d %H:%M', millitime);

        dlg.find('h3').text(name + ' (' + dt + ')');

        var chartInfo = {

            credits: {
                enabled: false
            },
            chart: {
                renderTo: 'chart_detail',
                type: 'bar'
            },
            title: {
                text: null
            },
            xAxis: {
                title: {
                    text: null
                },
                categories: []
            },
            yAxis: {
                title: {
                    text: null
                },
                min: 0,
                labels: {
                    formatter: function() {
                        return this.value / 100 + '%';
                    }
                }
            },
            legend: {
                enabled: false
            },
            tooltip: {
                enabled: false
            },
            plotOptions: {
                bar: {
                    lineWidth: 2,
                    marker: {
                        enabled: false,
                        states: {
                            hover: {
                                enabled: false
                            }
                        }
                    },
                    shadow: false,
                    states: {
                        hover: {
                            lineWidth: 2
                        }
                    },
                    dataLabels: {
                        enabled: true,
                        formatter: function() {
                            return this.y / 100 + '%';
                        }
                    }
                }
            },
            series: [{
                name: name,
                data: []
            }]
        };

        var data = {
            tid: id,
            dt: dt
        };

        $.getJSON('/ajax/detail', data, function(response) {

            if (!response) {
                return;
            }

            $.each(response, function() {
                chartInfo.xAxis.categories.push(this[0]);
                chartInfo.series[0].data.push(this[1]);
            });

            self.chartDetail = new Highcharts.Chart(chartInfo);

            $('#dlg_detail').modal('show');
        });

    },

    initDlgDetail: function() {
        var self = this;

        $('#dlg_detail').modal({
            show: false
        }).on('hidden', function() {
            self.chartDetail.destroy();
        });
    },

    _theEnd: undefined
};
