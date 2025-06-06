from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m


class RequestKind(models.Model):
    # pylint: disable=too-many-locals
    _name = 'request.kind'
    _inherit = [
        'mail.thread',
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code',
        'generic.mixin.track.changes',
    ]
    _description = 'Request kind'
    _order = 'sequence ASC'

    # Defined in generic.mixin.name_with_code
    name = fields.Char(string='Kind')
    code = fields.Char()

    description = fields.Text(translate=True)
    active = fields.Boolean(index=True, default=True)
    request_type_ids = fields.One2many(
        'request.type', 'kind_id', string='Request Types')
    request_type_count = fields.Integer(
        compute='_compute_request_type_count', readonly=True)
    request_ids = fields.One2many(
        'request.request', 'kind_id', string='Requests')
    request_count = fields.Integer(
        compute='_compute_request_count', readonly=True)

    sequence = fields.Integer(index=True, default=5)

    request_open_count = fields.Integer(
        compute="_compute_request_count", readonly=True)
    request_closed_count = fields.Integer(
        compute="_compute_request_count", readonly=True)
    # Open requests
    request_open_today_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="New Requests For Today")
    request_open_last_24h_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="New Requests For Last 24 Hour")
    request_open_week_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="New Requests For Week")
    request_open_month_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="New Requests For Month")
    # Closed requests
    request_closed_today_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="Closed Requests For Today")
    request_closed_last_24h_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="Closed Requests For Last 24 Hour")
    request_closed_week_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="Closed Requests For Week")
    request_closed_month_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="Closed Requests For Month")
    # Deadline requests
    request_deadline_today_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="Deadline Requests For Today")
    request_deadline_last_24h_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="Deadline Requests For Last 24 Hour")
    request_deadline_week_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="Deadline Requests For Week")
    request_deadline_month_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="Deadline Requests For Month")
    # Unassigned requests
    request_unassigned_count = fields.Integer(
        compute="_compute_request_count", readonly=True,
        string="Unassigned Requests")

    menuitem_id = fields.Many2one(
        'ir.ui.menu')
    menuaction_id = fields.Many2one(
        'ir.actions.act_window')
    menuitem_name = fields.Char(
        related='menuitem_id.name', readonly=False)
    menuaction_name = fields.Char(
        related='menuaction_id.name', readonly=False)
    menuitem_toggle = fields.Boolean(
        compute='_compute_menuitem_toggle',
        inverse='_inverse_menuitem_toggle',
        string='Show Menuitem',
        help="Show/Hide menuitem for requests of this kind. "
             "To see new menuitem, please reload the page."
    )

    @api.depends('request_type_ids')
    def _compute_request_type_count(self):
        mapped_data = read_counts_for_o2m(
            records=self,
            field_name='request_type_ids')
        for record in self:
            record.request_type_count = mapped_data.get(record.id, 0)

    @api.depends('request_ids')
    def _compute_request_count(self):
        now = datetime.now()
        today_start = now.replace(
            hour=0, minute=0, second=0, microsecond=0)
        yesterday = now - relativedelta(days=1)
        week_ago = now - relativedelta(weeks=1)
        month_ago = now - relativedelta(months=1)
        mapped_data_all = read_counts_for_o2m(
            records=self,
            field_name='request_ids')
        mapped_data_closed = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('closed', '=', True)])
        mapped_data_open = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('closed', '=', False)])
        mapped_data_open_today = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('date_created', '>=', today_start),
                    ('closed', '=', False)])
        mapped_data_open_last_24h = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('date_created', '>', yesterday),
                    ('closed', '=', False)])
        mapped_data_open_week = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('date_created', '>', week_ago),
                    ('closed', '=', False)])
        mapped_data_open_month = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('date_created', '>', month_ago),
                    ('closed', '=', False)])
        mapped_data_closed_today = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('date_closed', '>=', today_start),
                    ('closed', '=', True)])
        mapped_data_closed_24h = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('date_closed', '>', yesterday),
                    ('closed', '=', True)])
        mapped_data_closed_week = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('date_closed', '>', week_ago),
                    ('closed', '=', True)])
        mapped_data_closed_month = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('date_closed', '>', month_ago),
                    ('closed', '=', True)])
        mapped_deadline_today = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('deadline_date', '>=', today_start),
                    ('closed', '=', False)])
        mapped_deadline_24 = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('deadline_date', '>', yesterday),
                    ('closed', '=', False)])
        mapped_deadline_week = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('deadline_date', '>', week_ago),
                    ('closed', '=', False)])
        mapped_deadline_month = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('deadline_date', '>', month_ago),
                    ('closed', '=', False)])
        mapped_unassigned = read_counts_for_o2m(
            records=self,
            field_name='request_ids',
            domain=[('user_id', '=', False)])
        for record in self:
            record.request_count = mapped_data_all.get(record.id, 0)
            record.request_closed_count = mapped_data_closed.get(record.id, 0)
            record.request_open_count = mapped_data_open.get(record.id, 0)

            # Open requests
            record.request_open_today_count = mapped_data_open_today.get(
                record.id, 0)
            record.request_open_last_24h_count = mapped_data_open_last_24h.get(
                record.id, 0)
            record.request_open_week_count = mapped_data_open_week.get(
                record.id, 0)
            record.request_open_month_count = mapped_data_open_month.get(
                record.id, 0)
            # Closed requests
            record.request_closed_today_count = mapped_data_closed_today.get(
                record.id, 0)
            record.request_closed_last_24h_count = mapped_data_closed_24h.get(
                record.id, 0)
            record.request_closed_week_count = mapped_data_closed_week.get(
                record.id, 0)
            record.request_closed_month_count = mapped_data_closed_month.get(
                record.id, 0)
            # Deadline requests
            record.request_deadline_today_count = mapped_deadline_today.get(
                record.id, 0)
            record.request_deadline_last_24h_count = mapped_deadline_24.get(
                record.id, 0)
            record.request_deadline_week_count = mapped_deadline_week.get(
                record.id, 0)
            record.request_deadline_month_count = mapped_deadline_month.get(
                record.id, 0)
            # Unassigned requests
            record.request_unassigned_count = mapped_unassigned.get(
                record.id, 0)

    @api.depends('menuitem_id')
    def _compute_menuitem_toggle(self):
        for rec in self:
            rec.menuitem_toggle = bool(rec.menuitem_id)

    def _inverse_menuitem_toggle(self):
        for rec in self:
            if rec.menuitem_toggle:
                rec.menuaction_id = rec._create_menuaction()
                rec.menuitem_id = rec._create_menuitem()
            else:
                rec.menuitem_id.unlink()
                rec.menuaction_id.unlink()

    def _create_menuaction(self):
        self.ensure_one()
        return self.env.ref(
            'dgf_request_base.action_request_window'
        ).copy({
            'name': self.name,
            'domain': [('kind_id', '=', self.id)],
        })

    def _create_menuitem(self):
        self.ensure_one()
        parent_menu = self.env.ref('dgf_request_base.menu_request')
        return self.env['ir.ui.menu'].create({
            'name': self.name,
            'parent_id': parent_menu.id,
            'action': ('ir.actions.act_window,%d' %
                       self.menuaction_id.id),
            'sequence': 100 + self.sequence,
        })

    def action_show_request_type(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_type_window',
            context=dict(
                self.env.context,
                default_kind_id=self.id),
            domain=[('kind_id', '=', self.id)])

    def action_show_all_requests(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_request_window',
            context=dict(
                self.env.context,
                search_default_kind_id=self.id),
            domain=[('kind_id', '=', self.id)])

    def action_show_open_requests(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_request_window',
            context=dict(
                self.env.context,
                search_default_filter_open=1,
                search_default_kind_id=self.id),
            domain=[('kind_id', '=', self.id)])

    def action_show_closed_requests(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_request_window',
            context=dict(
                self.env.context,
                search_default_filter_closed=1,
                search_default_kind_id=self.id),
            domain=[('kind_id', '=', self.id)])

    def action_kind_request_open_today_count(self):
        self.ensure_one()
        today_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            domain=[
                ('date_created', '>=', today_start),
                ('closed', '=', False),
                ('kind_id', '=', self.id)])

    def action_kind_request_open_last_24h_count(self):
        self.ensure_one()
        yesterday = datetime.now() - relativedelta(days=1)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            domain=[
                ('date_created', '>', yesterday),
                ('closed', '=', False),
                ('kind_id', '=', self.id)])

    def action_kind_request_open_week_count(self):
        self.ensure_one()
        week_ago = datetime.now() - relativedelta(weeks=1)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            domain=[
                ('date_created', '>', week_ago),
                ('closed', '=', False),
                ('kind_id', '=', self.id)])

    def action_kind_request_open_month_count(self):
        self.ensure_one()
        month_ago = datetime.now() - relativedelta(months=1)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            domain=[
                ('date_created', '>', month_ago),
                ('closed', '=', False),
                ('kind_id', '=', self.id)])

    def action_kind_request_closed_today_count(self):
        self.ensure_one()
        today_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            context={'search_default_filter_closed': 1},
            domain=[
                ('date_closed', '>=', today_start),
                ('closed', '=', True),
                ('kind_id', '=', self.id)])

    def action_kind_request_closed_last_24h_count(self):
        self.ensure_one()
        yesterday = datetime.now() - relativedelta(days=1)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            context={'search_default_filter_closed': 1},
            domain=[
                ('date_closed', '>', yesterday),
                ('closed', '=', True),
                ('kind_id', '=', self.id)])

    def action_kind_request_closed_week_count(self):
        self.ensure_one()
        week_ago = datetime.now() - relativedelta(weeks=1)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            context={'search_default_filter_closed': 1},
            domain=[
                ('date_closed', '>', week_ago),
                ('closed', '=', True),
                ('kind_id', '=', self.id)])

    def action_kind_request_closed_month_count(self):
        self.ensure_one()
        month_ago = datetime.now() - relativedelta(months=1)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            context={'search_default_filter_closed': 1},
            domain=[
                ('date_closed', '>', month_ago),
                ('closed', '=', True),
                ('kind_id', '=', self.id)])

    def action_kind_request_deadline_today_count(self):
        self.ensure_one()
        today_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            domain=[
                ('deadline_date', '>=', today_start),
                ('closed', '=', False),
                ('kind_id', '=', self.id)])

    def action_kind_request_deadline_last_24h_count(self):
        self.ensure_one()
        yesterday = datetime.now() - relativedelta(days=1)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            domain=[
                ('deadline_date', '>', yesterday),
                ('closed', '=', False),
                ('kind_id', '=', self.id)])

    def action_kind_request_deadline_week_count(self):
        self.ensure_one()
        week_ago = datetime.now() - relativedelta(weeks=1)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            domain=[
                ('deadline_date', '>', week_ago),
                ('closed', '=', False),
                ('kind_id', '=', self.id)])

    def action_kind_request_deadline_month_count(self):
        self.ensure_one()
        month_ago = datetime.now() - relativedelta(months=1)
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            domain=[
                ('deadline_date', '>', month_ago),
                ('closed', '=', False),
                ('kind_id', '=', self.id)])

    def action_kind_request_unassigned_count(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'dgf_request_base.action_stat_request_count',
            domain=[
                ('user_id', '=', False),
                ('kind_id', '=', self.id)])
