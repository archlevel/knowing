var ChartEdit = function(opts) {
    var self = this;
    self.storm = opts.storm;
    self.users = opts.users;

    self.initStorm();
    self.initWarning();

    // validation
    $('#btn_submit').click(function() {

        var txtName = $(':text[name="name"]');
        if (!txtName.val()) {
            alert('请输入图表名称。');
            txtName.focus();
            return false;
        }

        var selCid = $('select[name="cid"]');
        if (!selCid.val()) {
            alert('请选择所属栏目。');
            selCid.focus();
            return false;
        }

        var txtOwner = $(':text[name="owner_name"]');
            hidOwner = $(':hidden[name="owner"]');
        if (!txtOwner.is('[readonly]') && !hidOwner.val()) {
            alert('请输入创建人。');
            txtOwner.focus();
            return false;
        }

    });

    // users autocomplete
    if (!$(':text[name="owner_name"]').is('[readonly]')) {
        var source = [];
        $.each(self.users, function() {
            source.push({label: this.truename, data: this.username});
        });
        $(':text[name="owner_name"]').autocomplete({
            source: source,
            select: function(event, ui) {
                $(':hidden[name="owner"]').val(ui.item.data).attr('display_value', ui.item.label);
            },
            change: function(event, ui) {
                $(this).val($(':hidden[name="owner"]').attr('display_value'));
            }
        });
    }

};

ChartEdit.prototype = {
    constructor: ChartEdit,

    initStorm: function() {
        var self = this,
            cgList = ['datasource', 'rule_type', 'field', 'filters', 'misc'],
            selDatasource = $('select[name="storm_datasource"]'),
            selRuleType = $('select[name="storm_rule_type"]'),
            selField = $('select[name="storm_field"]'),
            ulFilters = $('#ul_storm_filters');

        function resetField() {
            $('option', selField).not(':first').remove();
            selField.attr('disabled', 'disabled');
        }

        function resetFilters() {
            $('li', ulFilters).not(':last').remove();
        }

        $('#use_storm_yes').click(function() {
            $.each(cgList, function() {
                $('#cg_storm_' + this).show();
            });
        });

        $('#use_storm_no').click(function() {
            $(cgList).each(function() {
                $('#cg_storm_' + this).hide();
            });
        });

        selDatasource.change(function() {
            selRuleType.val('');
            resetField();
            resetFilters();
        });

        selRuleType.change(function() {

            resetField();

            var ruleTypeString = $(this).val();
            if (!ruleTypeString) {
                return;
            }

            var ruleType = self.storm.rule_types[ruleTypeString];
            if (ruleType[1] !== false) {
                var datasourceString = selDatasource.val();
                $.each(self.storm.datasource_field_list[datasourceString], function() {
                    if (ruleType[1] === true
                            || ruleType[1] == self.storm.datasources[datasourceString][this][0]) {

                        $('<option value="' + this + '">' + this + '</option>').appendTo(selField);
                    }
                });
                selField.removeAttr('disabled');
            }

        });

        $('#btn_add_filter').click(function() {
            self.addFilter();
        });

        // validation
        $('#btn_submit').click(function() {

            if ($('#use_storm_yes').is(':checked')) {

                if (!selDatasource.val()) {
                    alert('请选择数据源。');
                    return false;
                }

                if (!selRuleType.val()) {
                    alert('请选择类型。');
                    return false;
                }

                if (selRuleType.val() != 'count' && !selField.val()) {
                    alert('请选择字段。');
                    return false;
                }

                if ($('li', ulFilters).length == 1) {
                    alert('请添加过滤条件。');
                    return false;
                }

                var passed = true;
                $('li', ulFilters).not(':last').each(function() {

                    if (!$('select[name^="storm_filter_field"]', this).val()) {
                        alert('请选择过滤字段。');
                        passed = false;
                        return false;
                    }

                    if (!$('select[name^="storm_filter_operator"]', this).val()) {
                        alert('请选择过滤操作符。');
                        passed = false;
                        return false;
                    }

                    if (!$(':text[name^="storm_filter_content"]', this).val()) {
                        alert('请输入过滤条件内容。');
                        passed = false;
                        return false;
                    }

                });

                if (!passed) {
                    return false;
                }

            }

        });

    },

    filterId: 0,
    addFilter: function(filter) {

        var datasourceString = $('select[name="storm_datasource"]').val();
        if (!datasourceString) {
            alert('请选择数据源。');
            return false;
        }

        var self = this;

        self.filterId++;
        var html = '<li class="filter">' +
                   '  <input type="hidden" name="storm_filter_id[]" value="' + self.filterId +'">' +
                   '  <input type="button" value="删除" class="btn opfilter" delete="delete">' +
                   '  <select name="storm_filter_field[]" class="input-medium">' +
                   '     <option value="">请选择</option>' +
                   '  </select>' +
                   '  <select name="storm_filter_operator[]" class="input-medium">' +
                   '     <option value="">请选择</option>' +
                   '  </select>' +
                   '  <input type="text" name="storm_filter_content[]" placeholder="内容">' +
                   '  <label for="storm_filter_negative_' + self.filterId + '" class="checkbox inline" style="display: none;">' +
                   '    <input type="checkbox" id="storm_filter_negative_' + self.filterId + '" name="storm_filter_negative[]" value="' + self.filterId + '">' +
                   '    取反' +
                   '  </label>' +
                   '</li>',
            li = $(html),
            btnFilterDelete = $(':button[delete]', li),
            selFilterField = $('select[name^=storm_filter_field]', li),
            selFilterOperator = $('select[name^=storm_filter_operator]', li),
            txtFilterContent = $(':text[name^=storm_filter_content]', li),
            cbFilterNegative = $(':checkbox[name^=storm_filter_negative]', li);

        $.each(self.storm.datasource_field_list[datasourceString], function() {
            $('<option value="' + this + '">' + this + '</option>').appendTo(selFilterField);
        });

        btnFilterDelete.click(function() {
            $(this).parent().remove();
        });

        function resetFilterOperator() {
            $('option', selFilterOperator).not(':first').remove();
        }

        selFilterField.change(function() {
           resetFilterOperator();
           var fieldString = $(this).val();
           var field = self.storm.datasources[datasourceString][fieldString];
           $.each(self.storm.operator_list[field[0]], function() {
               $('<option value="' + this + '">' + self.storm.operators[field[0]][0][this] + '</option>').appendTo(selFilterOperator);
           })

           if (self.storm.operators[field[0]][1]) {
               cbFilterNegative.parent().show();
           } else {
               cbFilterNegative.parent().hide();
           }
        });

        li.insertBefore($('#ul_storm_filters li:last'));

        if (filter) {
            selFilterField.val(filter[0]).change();
            selFilterOperator.val(filter[1]).change();
            if ($.isArray(filter[3])) {
                txtFilterContent.val(filter[3].join(','));
            } else {
                txtFilterContent.val(filter[3]);
            }
            if (filter[2]) {
                cbFilterNegative.attr('checked', 'checked');
            }
        }

    },

    initWarning: function() {
        var self = this;

        $('#btn_add_warning_rule').click(function() {
            self.resetWarning();
            $('#dlg_warning_rule').modal();
        });

        $('#txt_warn_duration_start, #txt_warn_duration_end').timepicker({
            timeFormat: 'HH:mm'
        });

        $('#rb_wt_hwm, #rb_wt_lwm, #rb_wt_range').click(function() {

            switch ($(this).attr('id')) {
            case 'rb_wt_hwm':
                $('#cg_warn_hwm').show();
                $('#spn_warn_hwm').text('（绝对值）');
                $('#cg_warn_lwm').hide();
                break;

            case 'rb_wt_lwm':
                $('#cg_warn_lwm').show();
                $('#spn_warn_lwm').text('（绝对值）');
                $('#cg_warn_hwm').hide();
                break;

            case 'rb_wt_range':
                $('#cg_warn_hwm, #cg_warn_lwm').show();
                $('#spn_warn_hwm, #spn_warn_lwm').text('（百分比）');
                break;
            }

        });

        $('#btn_warn_ok').click(function() {

            // validate
            var durationStart = $('#txt_warn_duration_start').val();
            var durationEnd = $('#txt_warn_duration_end').val();
            var ptrnDuration = /^[0-9]{2}:[0-9]{2}$/;
            if (!ptrnDuration.test(durationStart)) {
                alert('开始时间不正确。');
                return false;
            }
            if (!ptrnDuration.test(durationEnd)) {
                alert('结束时间不正确。');
                return false;
            }
            if (durationEnd < durationStart) {
                alert('结束时间须大于开始时间。');
                return false;
            }

            var warnType = null;
            $(':radio[name="warn_type"]').each(function() {
                if ($(this).is(':checked')) {
                    warnType = $(this).val();
                    return false;
                }
            });
            if (!warnType) {
                alert('请选择报警模式。');
                return false;
            }

            var hwmWarning = $('#txt_warn_hwm_warning').val();
            var hwmCritical = $('#txt_warn_hwm_critical').val();
            var lwmWarning = $('#txt_warn_lwm_warning').val();
            var lwmCritical = $('#txt_warn_lwm_critical').val();
            var ptrnInt = /^[0-9]+$/;
            function checkHwm() {
                if (!ptrnInt.test(hwmWarning)) {
                    alert('请输入上限警告阈值。');
                    return false;
                }
                if (!ptrnInt.test(hwmCritical)) {
                    alert('请输入上限崩溃阈值。');
                    return false;
                }
                if (parseInt(hwmCritical) < parseInt(hwmWarning)) {
                    alert('上限崩溃阈值须大于警告阈值。')
                    return false;
                }
                return true;
            }
            function checkLwm(reverse) {
                if (!ptrnInt.test(lwmWarning)) {
                    alert('请输入下限警告阈值。');
                    return false;
                }
                if (!ptrnInt.test(lwmCritical)) {
                    alert('请输入下限崩溃阈值。');
                    return false;
                }
                if (!reverse) {
                    if (parseInt(lwmCritical) > parseInt(lwmWarning)) {
                        alert('下限崩溃阈值须小于警告阈值。')
                        return false;
                    }
                } else {
                    if (parseInt(lwmCritical) < parseInt(lwmWarning)) {
                        alert('下限崩溃阈值须大于警告阈值。')
                        return false;
                    }
                }
                return true;
            }

            switch (warnType) {
            case 'HWM':
                if (!checkHwm()) {
                    return false;
                }
                lwmWarning = lwmCritical = 0;
                break;

            case 'LWM':
                if (!checkLwm()) {
                    return false;
                }
                hwmWarning = hwmCritical = 0;
                break;

            case 'RANGE':
                if (!checkHwm() || !checkLwm(true)) {
                    return false;
                }
                break;
            }

            var latency = $('#txt_warn_latency').val();
            var interval = $('#txt_warn_interval').val();
            if (!ptrnInt.test(latency)) {
                alert('延迟时间不正确。');
                return false;
            }
            if (!ptrnInt.test(latency)) {
                alert('间隔时间不正确。');
                return false;
            }

            $('#dlg_warning_rule').modal('hide');

            var params = {
                duration_start: durationStart,
                duration_end: durationEnd,
                type: warnType,
                hwm_warning: hwmWarning,
                hwm_critical: hwmCritical,
                lwm_warning: lwmWarning,
                lwm_critical: lwmCritical,
                latency: latency,
                interval: interval
            };

            var editing = $('#dlg_warning_rule').data('editing');
            if (editing) {
                params['id'] = $(':hidden[name="warn_id[]"]', editing).val();
            } else {
                params['id'] = 0;
            }

            self.addWarningRule(params, editing);

        });

        // validation
        $('#btn_submit').click(function() {

            if ($('#alert_enable_yes').is(':checked')) {
                if ($('#ul_warning_rules li').length == 1) {
                    alert('请添加报警规则。');
                    return false;
                }
            }

        });
    },

    resetWarning: function(params, editing) {

        if (!$.isPlainObject(params)) {
            params = {
                duration_start: '00:00',
                duration_end: '23:59',
                type: 'HWM',
                hwm_warning: '',
                hwm_critical: '',
                lwm_warning: '',
                lwm_critical: '',
                latency: '5',
                interval: '5'
            };
        }

        $('#txt_warn_duration_start').val(params.duration_start);
        $('#txt_warn_duration_end').val(params.duration_end);

        switch (params.type) {
        case 'HWM':
            $('#rb_wt_hwm').attr('checked', 'checked').triggerHandler('click');
            $('#txt_warn_hwm_warning').val(params.hwm_warning);
            $('#txt_warn_hwm_critical').val(params.hwm_critical);
            $('#txt_warn_lwm_warning, #txt_warn_lwm_critical').val('');
            break;
        case 'LWM':
            $('#rb_wt_lwm').attr('checked', 'checked').triggerHandler('click');
            $('#txt_warn_lwm_warning').val(params.lwm_warning);
            $('#txt_warn_lwm_critical').val(params.lwm_critical);
            $('#txt_warn_hwm_warning, #txt_warn_hwm_critical').val('');
            break;
        case 'RANGE':
            $('#rb_wt_range').attr('checked', 'checked').triggerHandler('click');
            $('#txt_warn_hwm_warning').val(params.hwm_warning);
            $('#txt_warn_hwm_critical').val(params.hwm_critical);
            $('#txt_warn_lwm_warning').val(params.lwm_warning);
            $('#txt_warn_lwm_critical').val(params.lwm_critical);
            break;
        default:
            return false;
        }

        $('#txt_warn_latency').val(params.latency);
        $('#txt_warn_interval').val(params.interval);

        if (editing) {
            $('#dlg_warning_rule h3').text('修改报警规则');
            $('#dlg_warning_rule').data('editing', editing);
        } else {
            $('#dlg_warning_rule h3').text('添加报警规则');
            $('#dlg_warning_rule').removeData('editing');
        }

    },

    addWarningRule: function (params, editing) {
        var self = this;

        var hidden = [['id', params.id]];
        var html = '<li class="rule">' +
                   '<input type="button" value="编辑" class="btn oprule" warn_edit="warn_edit">&nbsp;&nbsp;' +
                   '<input type="button" value="删除" class="btn oprule" warn_delete="warn_delete">&nbsp;&nbsp;&nbsp;' +
                   params.duration_start + '～' + params.duration_end + '，';
        hidden.push(['duration_start', params.duration_start]);
        hidden.push(['duration_end', params.duration_end]);

        switch (params.type) {
        case 'HWM':
            html += '上限模式，警告 ' + params.hwm_warning + '，崩溃 ' + params.hwm_critical + '，';
            hidden.push(['type', 'HWM']);
            hidden.push(['hwm_warning', params.hwm_warning]);
            hidden.push(['hwm_critical', params.hwm_critical]);
            hidden.push(['lwm_warning', '']);
            hidden.push(['lwm_critical', '']);
            break;

        case 'LWM':
            html += '下限模式，警告 ' + params.lwm_warning + '，崩溃 ' + params.lwm_critical + '，';
            hidden.push(['type', 'LWM']);
            hidden.push(['hwm_warning', '']);
            hidden.push(['hwm_critical', '']);
            hidden.push(['lwm_warning', params.lwm_warning]);
            hidden.push(['lwm_critical', params.lwm_critical]);
            break;

        case 'RANGE':
            html += '范围模式，警告 -' + params.lwm_warning + '%～' + params.hwm_warning + '%' + '，' +
                    '崩溃 -' + params.lwm_critical + '%～' + params.hwm_critical + '%' + '，';
            hidden.push(['type', 'RANGE']);
            hidden.push(['hwm_warning', params.hwm_warning]);
            hidden.push(['hwm_critical', params.hwm_critical]);
            hidden.push(['lwm_warning', params.lwm_warning]);
            hidden.push(['lwm_critical', params.lwm_critical]);
            break;
        }

        html += '延迟 ' + params.latency + ' 分钟，间隔 ' + params.interval + ' 分钟' + '</li>';
        hidden.push(['latency', params.latency]);
        hidden.push(['interval', params.interval]);

        var $html = $(html);

        $.each(hidden, function() {
            $('<input type="hidden">').attr('name', 'warn_' + this[0] + '[]').attr('value', this[1]).appendTo($html);
        });

        $(':button[warn_delete]', $html).click(function() {
            if (confirm('确定要删除这条报警规则吗？')) {
                $(this).parent().remove();
            }
        });

        $(':button[warn_edit]', $html).click(function() {
            self.resetWarning(params, $html);
            $('#dlg_warning_rule').modal();
        });

        if (editing) {
            editing.replaceWith($html);
        } else {
            $html.insertBefore($('#ul_warning_rules li').last());
        }

    },

    _theEnd: undefined
};
