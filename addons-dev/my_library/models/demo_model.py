# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DemoModel(models.Model):
    _name = 'demo.model'
    _description = 'Library Demo Model'
    _order = 'write_date desc, name'
    _rec_name = 'short_name'

    name = fields.Char('Title', required=True)
    short_name = fields.Char('Short Title')
    author_ids = fields.Many2many('res.partner', string='Authors')
    notes = fields.Text('Internal Notes')
    state = fields.Selection(
        [("draft", "Not Available"), ("available", "Available"), ("lost", "Lost")],
        string="State",
        default="draft",
    )
    description = fields.Html('Description')
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages')
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4))

    pages = fields.Integer('Number of Pages',
                           groups='base.group_user',
                           states={'lost': [('readonly', True)]},
                           help='Total book page count', company_dependent=False)

# Demo fields
    # Basic Field
    boolean = fields.Boolean('Boolean')
    Char = fields.Char('Char')
    Float = fields.Float('Float')
    Integer = fields.Integer('Integer')
    short_name = fields.Binary('Binary')
    Html = fields.Html('Html')
    Monetary = fields.Monetary(
        string="Capital amount",
        currency_field="monetary_currency_id",
        help="Publicly registered capital amount.",
    )
    monetary_currency_id = fields.Many2one(
        comodel_name="res.currency", string="Capital currency"
    )
    Selection = fields.Selection([('a', 'A'), ('b', 'B')], string='Selection')
    Text = fields.Text('Text')
    Date = fields.Date('Date')
    Datetime = fields.Datetime('Datetime')
    # Relational Fields
    # short_name = fields.Many2one('Title')
    # short_name = fields.One2many('Title')
    # short_name = fields.Many2many('Title')
    # # Pseudo-relational fields
    # short_name = fields.Reference('Title')
    # short_name = fields.Many2oneReference('Title')
    # # Computed Fields
    # total = fields.Float(compute='_compute_total')
    # # Related fields. # The nickname will only be recomputed when the partner_id is modified (depends=['partner_id'])
    # nickname = fields.Char(related='partner_id.name', store=True, depends=['partner_id'])

    # Reserved Field names
    active = fields.Boolean(default=True)
    # state = fields.Selection(
    #     [("draft", "To Approve"), ("confirmed", "Approved"), ("cancel", "Archived")],
    #     string="Related State",
    #     default="confirmed",
    # )
    # parent_id
    # parent_path
    # company_id

    @api.depends('value', 'tax')
    def _compute_total(self):
        for record in self:
            record.total = record.value + record.value * record.tax

    # Override default implementation of name_get(), which uses the _rec_name attribute to find which field holds the data, which is used to generate the display name.
    def name_get(self):
        result = []
        for record in self:
            rec_name = "{0} ({1})".format(record.name, record.date_release)
            result.append((record.id, rec_name))
        return result
