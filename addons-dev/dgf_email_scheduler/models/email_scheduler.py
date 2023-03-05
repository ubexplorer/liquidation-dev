from odoo import models , fields , _
from datetime import date, datetime
import calendar
import logging
_logger = logging.getLogger(__name__)

# _intervalTypes = {
#     'days': lambda interval: relativedelta(days=interval),
#     'hours': lambda interval: relativedelta(hours=interval),
#     'weeks': lambda interval: relativedelta(days=7*interval),
#     'months': lambda interval: relativedelta(months=interval),
#     'minutes': lambda interval: relativedelta(minutes=interval),
# }


class Mailscheduler(models.Model):
    _name = "mail.scheduler"

    name = fields.Char("Name", required=True)
    template_id = fields.Many2one('mail.template', "E-mail Template", required=True)
    active = fields.Boolean("Active", default=True)
    interval_number = fields.Integer(default=1, help="Repeat every x.")
    interval_type = fields.Selection([('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')], string='Interval Unit', default='days')

    def _cron_days(self):
        reminder_ids = self.env['mail.scheduler'].search([('interval_type', '=', 'days')])
        for rec in reminder_ids:
            rec.template_id.send_mail(rec.id, force_send=True)
            _logger.info("The Email has sent successfully!!")

    def _cron_weeks(self):
        reminder_ids = self.env['mail.scheduler'].search([('interval_type', '=', 'weeks')])
        for rec in reminder_ids:
            rec.template_id.send_mail(rec.id, force_send=True)
            _logger.info("The Email has sent successfully!!")

    def _cron_months(self):
        reminder_ids = self.env['mail.scheduler'].search([('interval_type', '=', 'months')])
        for rec in reminder_ids:
            rec.template_id.send_mail(rec.id, force_send=True)
            _logger.info("The Email has sent successfully!!")
