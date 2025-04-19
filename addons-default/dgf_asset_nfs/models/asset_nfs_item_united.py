# -*- coding: utf-8 -*-
from odoo import models, api, fields, tools


class LibraryBookRentStatistics(models.Model):
    _name = 'asset.nfs.item.united'
    _auto = False
    _rec_name = "code"
    _order = "code"
    is_base_stage = True
    is_base_type = True

    code = fields.Char(string='Код майна', readonly=True)
    company_id = fields.Many2one("res.company", string="Назва банку", readonly=True)
    company_mfo = fields.Char(string="МФО банку", related="company_id.mfo", store=True, readonly=True)
    bal_account = fields.Char(string='Балансовий рахунок', readonly=True)
    asset_type = fields.Char(string='Код типу активу', readonly=True)
    asset_identifier = fields.Char(string='ID активу', readonly=True)
    description = fields.Char(string='Коротка характеристика активу', readonly=True)
    account_date = fields.Date(string='Балансова дата', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Код валюти', readonly=True)
    book_value = fields.Monetary(string='Балансова вартість, номінал', currency_field='currency_id', readonly=True)
    book_value_uah = fields.Float(string='Балансова вартість, UAH', digits=(15, 2), readonly=True)
    apprisal_value = fields.Float(string='Оціночна вартість, UAH', digits=(15, 2), readonly=True)
    # active = fields.Boolean(string='Активно', readonly=True)
    stage = fields.Char(string='Статус', readonly=True)
    # type_id = fields.Many2one(string='Код ознаки', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
        CREATE OR REPLACE VIEW asset_nfs_item_united AS (
        select
            anfsvd.id as id,
            anfsvd.code as code,
            anfsvd.company_id as company_id,
            anfsvd.company_mfo as company_mfo,
            anfsvd.bal_account as bal_account,
            anfsvd.asset_type as asset_type,
            anfsvd.asset_identifier as asset_identifier,
            anfsvd.description as description,
            anfsvd.account_date as account_date,
            anfsvd.currency_id as currency_id,
            anfsvd.book_value as book_value,
            anfsvd.book_value_uah as book_value_uah,
            anfsvd.apprisal_value as apprisal_value,
            'Включено' as stage
        from
            asset_nfs_list_item as anfsvd
        join base_stage bs on anfsvd.stage_id = bs.id
        where
        	bs.code in ('include')
        union
        select
            anfsod.id as id,
            anfsod.code as code,
            anfsod.company_id as company_id,
            anfsod.company_mfo as company_mfo,
            anfsod.bal_account as bal_account,
            anfsod.asset_type as asset_type,
            anfsod.asset_identifier as asset_identifier,
            anfsod.description as description,
            anfsod.account_date as account_date,
            anfsod.currency_id as currency_id,
            anfsod.book_value as book_value,
            anfsod.book_value_uah as book_value_uah,
            anfsod.apprisal_value as apprisal_value,
            'Включено' as stage
        from
            asset_blocked_list_item as anfsod
        join base_stage bso on anfsod.stage_id = bso.id
        where
        	bso.code in ('include', 'transferred')
        );
        """
        self.env.cr.execute(query)
