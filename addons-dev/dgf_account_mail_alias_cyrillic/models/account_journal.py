# -*- coding: utf-8 -*-
# pip install translitua
from translitua import translit
from odoo import models


class AccountJournal(models.Model):
    _inherit = ['account.journal']
    # TODO: move logic to default value of alias_name_unicode & self.alias_name = alias_name_unicode
    # alias_name_unicode = fields.Char('Alias Name Unicode', copy=False, compute='_compute_alias_name_unicode', inverse='_inverse_type_unicode', help="It creates draft invoices and bills by sending an email.", readonly=False)

    def _update_mail_alias(self):
        if self.company_id != self.env.ref('base.main_company'):
            alias_name_unicode = str(self.type)
            alias_name_unicode += '-' + str(translit(src=self.company_id.name))
            alias_name_unicode = alias_name_unicode.replace('\"', '').replace('\'', '')
            self.alias_name = alias_name_unicode

        return super(AccountJournal, self)._update_mail_alias(self)
