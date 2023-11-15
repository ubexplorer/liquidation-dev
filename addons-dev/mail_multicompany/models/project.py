# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class Task(models.Model):
    _inherit = "project.task"

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
