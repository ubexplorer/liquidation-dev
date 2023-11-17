# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class Project(models.Model):
    _inherit = [
        'project.project',
        'mail.alias.mixin',
        'mail.thread',
        ]

    alias_enabled = fields.Boolean(string='Use email alias', compute='_compute_alias_enabled', readonly=False)
    alias_id = fields.Many2one('mail.alias', string='Alias', ondelete="restrict", required=True,
        help="Internal email associated with this project. Incoming emails are automatically synchronized "
             "with Tasks (or optionally Issues if the Issue Tracker module is installed).")
    
    @api.onchange('alias_enabled')
    def _onchange_alias_name(self):
        if not self.alias_enabled:
            self.alias_name = False

    def _compute_alias_enabled(self):
        for project in self:
            project.alias_enabled = project.alias_domain and project.alias_id.alias_name

    def _compute_alias_enabled(self):
        for project in self:
            project.alias_enabled = project.alias_domain and project.alias_id.alias_name

    def _alias_get_creation_values(self):
        values = super(Project, self)._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('project.task').id
        if self.id:
            values['alias_defaults'] = defaults = ast.literal_eval(self.alias_defaults or "{}")
            defaults['project_id'] = self.id
        return values


class Task(models.Model):
    _inherit = [
        'project.task',
        'mail.alias.mixin',
        'mail.thread',
        ]


    def _notify_get_reply_to(self, default=None, records=None, company=None, doc_names=None):
        """ Override to set alias of tasks to their project if any. """
        aliases = self.sudo().mapped('project_id')._notify_get_reply_to(default=default, records=None, company=company, doc_names=None)
        res = {task.id: aliases.get(task.project_id.id) for task in self}
        leftover = self.filtered(lambda rec: not rec.project_id)
        if leftover:
            res.update(super(Task, leftover)._notify_get_reply_to(default=default, records=None, company=company, doc_names=doc_names))
        return res

    def email_split(self, msg):
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        # check left-part is not already an alias
        aliases = self.mapped('project_id.alias_name')
        return [x for x in email_list if x.split('@')[0] not in aliases]

    # @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        email_to = tools.email_split(msg.get('to'))[0]
        company_fetchmail_server = self.env['fetchmail.server'].search([('user', 'ilike', email_to)], limit=1)
        msg_company_id = company_fetchmail_server.company_id.id
        if custom_values is None:
            custom_values = {}
        if msg_company_id:
            defaults = {
                'company_id': msg_company_id if msg_company_id else False
            }
        defaults.update(custom_values or {})
        task = super(Task, self).message_new(msg, custom_values=defaults)
        return task
