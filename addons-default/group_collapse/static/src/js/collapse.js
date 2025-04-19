odoo.define('haseca.FormRenderer', function (require) {
"use strict";

var FormRenderer = require('web.FormRenderer');

FormRenderer.include({
    events: _.extend({}, FormRenderer.prototype.events, {
        'click .o_group_collapse': '_onClickGroupCollapse',
    }),

    _renderInnerGroup: function (node) {
        if (!this.group_id) {
            this.group_id = 1;
        }
        var self = this;
        var $result = $('<table/>', {class: 'o_group o_inner_group'});
        var $tbody = $('<tbody />').appendTo($result);
        this._handleAttributes($result, node);
        this._registerModifiers(node, this.state, $result);

        var col = parseInt(node.attrs.col, 10) || this.INNER_GROUP_COL;

        if (node.attrs.string) {
            var $sep = $('<tr class="o_group_collapse" data-toggle="collapse" data-target="#o_group_'+ self.group_id +'"/>');
            var $td = $('<td colspan="'+col + '" style="width: 100%;"/>');
            var $header = $('<span class="o_horizontal_separator">'+ node.attrs.string +'<i class="fa fa-caret-down ml-2"></i></span>');
            $td.append($header);
            $sep.append($td);
            $sep.css('cursor', 'pointer');
            $result.append($sep);
        }

        var rows = [];
        var $currentRow = $('<tr/>');
        var currentColspan = 0;
        node.children.forEach(function (child) {
            if (child.tag === 'newline') {
                rows.push($currentRow);
                $currentRow = $('<tr/>');
                currentColspan = 0;
                return;
            }

            var colspan = parseInt(child.attrs.colspan, 10);
            var isLabeledField = (child.tag === 'field' && child.attrs.nolabel !== '1');
            if (!colspan) {
                if (isLabeledField) {
                    colspan = 2;
                } else {
                    colspan = 1;
                }
            }
            var finalColspan = colspan - (isLabeledField ? 1 : 0);
            currentColspan += colspan;

            if (currentColspan > col) {
                rows.push($currentRow);
                $currentRow = $('<tr/>');
                currentColspan = colspan;
            }

            var $tds;
            if (child.tag === 'field') {
                $tds = self._renderInnerGroupField(child);
            } else if (child.tag === 'label') {
                $tds = self._renderInnerGroupLabel(child);
            } else {
                var $td = $('<td/>');
                var $child = self._renderNode(child);
                if ($child.hasClass('o_td_label')) { // transfer classname to outer td for css reasons
                    $td.addClass('o_td_label');
                    $child.removeClass('o_td_label');
                }
                $tds = $td.append($child);
            }
            if (finalColspan > 1) {
                $tds.last().attr('colspan', finalColspan);
            }

            _.each($tds, function (td) {
                td.setAttribute('id', 'o_group_' + self.group_id);
                td.classList.add('show');
            })

            $currentRow.append($tds);
        });
        rows.push($currentRow);

        _.each(rows, function ($tr) {
            var nonLabelColSize = 100 / (col - $tr.children('.o_td_label').length);
            _.each($tr.children(':not(.o_td_label)'), function (el) {
                var $el = $(el);
                $el.css('width', ((parseInt($el.attr('colspan'), 10) || 1) * nonLabelColSize) + '%');
            });
            $tbody.append($tr);
        });
        this.group_id += 1;

        return $result;
    },

    _onClickGroupCollapse: function(e) {
        var target = e.currentTarget;
        var i = target.querySelector('i');
        if (i.style.transform === 'rotateZ(180deg)') {
            i.style.transform = '';
        } else {
            i.style.transform = 'rotateZ(180deg)';
        }
    }
});

});