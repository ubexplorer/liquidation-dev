# -*- coding: utf-8 -*-

import datetime
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
from odoo.http import request
from odoo import api, fields, models, _


class DeadLineReminder(models.Model):
    _inherit = "project.task"

    task_reminder = fields.Boolean("Reminder")
    template_id = fields.Many2one('mail.template', "E-mail Template", required=True)

    @api.model
    def _cron_deadline_reminder(self):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        for task in self.env['project.task'].search([('date_deadline', '!=', None),
                                                     ('task_reminder', '=', True), ('user_id', '!=', None)]):
            reminder_date = task.date_deadline
            today = datetime.now().date()

            # if reminder_date == today and task:
            #     template_id = self.env['ir.model.data'].get_object_reference(
            #         'task_deadline_reminder',
            #         'email_template_edi_deadline_reminder')[1]
            #     if template_id:
            #         email_template_obj = self.env['mail.template'].browse(template_id)
            #         values = email_template_obj.generate_email(task.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
            #         msg_id = self.env['mail.mail'].create(values)
            #         if msg_id:
            #             msg_id._send()

            # alternative
            if reminder_date == today and task:
                template_id = task.template_id
                recepients = task.allowed_user_ids
                email_to = []
                task_manager = task.user_id.email_formatted
                for recepient in recepients:
                    email_to.append(recepient.email_formatted)
                if template_id:
                    email_values = {'email_to': ','.join(email_to),
                                    'email_from': task_manager,
                                    'email_cc': task_manager,
                                    'reply_to': task_manager,
                                    }
                    # email_values = {
                    #     'subject': None,
                    #     'email_from': None,
                    #     'email_to': None,
                    #     'partner_to': None,
                    #     'email_cc': None,
                    #     'reply_to': None,
                    #     'scheduled_date': None,
                    # }
                    template_id.send_mail(task.id, force_send=False, raise_exception=False, email_values=email_values, notif_layout=False)
        return True
