from odoo import models, fields, _
# from datetime import date, datetime
# import calendar
import logging
_logger = logging.getLogger(__name__)


class Mailscheduler(models.Model):
    _name = "mail.scheduler"
    _description = "Планувальник поштових повідомлень"

    name = fields.Char("Name", required=True)
    template_id = fields.Many2one('mail.template', "E-mail Template", required=True)
    active = fields.Boolean("Active", default=True)
    interval_number = fields.Integer(default=1, help="Repeat every x.")
    interval_type = fields.Selection([('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')], string='Interval Unit', default='days')

    def _cron_days(self):
        reminder_ids = self.env['mail.scheduler'].search([('interval_type', '=', 'days'),
                                                          ('active', '=', True)])
        self._cron_run(reminder_ids)

    def _cron_weeks(self):
        reminder_ids = self.env['mail.scheduler'].search([('interval_type', '=', 'weeks'),
                                                          ('active', '=', True)])
        self._cron_run(reminder_ids)

    def _cron_months(self):
        reminder_ids = self.env['mail.scheduler'].search([('interval_type', '=', 'months'),
                                                          ('active', '=', True)])
        self._cron_run(reminder_ids)

    def _cron_run(self, records):
        for rec in records:
            rec.template_id.send_mail(rec.id, force_send=False)
            _logger.info("The Email has sent successfully!")
