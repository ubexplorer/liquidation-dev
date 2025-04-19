# -*- coding: utf-8 -*-

# pip install transliterate
from transliterate import translit, get_available_language_codes
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _name = "account.journal"
    _inherit = ['account.journal']

    # alias_name_unicode = fields.Char('Alias Name Unicode', copy=False, compute='_compute_alias_name', inverse='_inverse_type', help="It creates draft invoices and bills by sending an email.", readonly=False)
    alias_name_unicode = fields.Char('Alias Name Unicode', copy=False, help="It creates draft invoices and bills by sending an email.", readonly=False)

    def _get_alias_values(self, type, alias_name=None):
        text = "Lorem ipsum dolor sit amet"
        alias_name_unicode = translit(text, 'ru')
        print(alias_name_unicode)
        # if not alias_name:
        #     alias_name = self.name
        #     if self.company_id != self.env.ref('base.main_company'):
        #         alias_name += '-' + str(self.company_id.name)
        return super(AccountJournal, self)._get_alias_values(self, type, alias_name=alias_name_unicode)
