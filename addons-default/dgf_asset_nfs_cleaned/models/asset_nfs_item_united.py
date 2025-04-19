# -*- coding: utf-8 -*-
from odoo import models, api, fields, tools


class LibraryBookRentStatistics(models.Model):
    _name = 'asset.nfs.item.united'
    _auto = False
    _rec_name = "code"
    _order = "code"
    _check_company_auto = True
    is_base_stage = True
    is_base_type = True
    

    code = fields.Char(string='Код майна', readonly=True)
    company_id = fields.Many2one("res.company", string="Назва банку", readonly=True)
    company_mfo = fields.Char(string="МФО банку", related="company_id.mfo", store=True, readonly=True)
    bal_account = fields.Char(string='Балансовий рахунок', readonly=True)
    asset_type = fields.Char(string='Код типу активу', readonly=True)
    asset_identifier = fields.Char(string='ID активу', readonly=True)
    original_description = fields.Char(string='Коротка характеристика активу (БД)', readonly=True)
    description = fields.Char(string='Коротка характеристика активу', compute='_compute_description', readonly=True)
    account_date = fields.Date(string='Балансова дата', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Код валюти', readonly=True)
    book_value = fields.Monetary(string='Балансова вартість, номінал', currency_field='currency_id', readonly=True)
    book_value_uah = fields.Float(string='Балансова вартість, UAH', digits=(15, 2), readonly=True)
    apprisal_value = fields.Float(string='Оціночна вартість, UAH', digits=(15, 2), readonly=True)
    document_id = fields.Char(string='Включено на підставі', readonly=True)
    # active = fields.Boolean(string='Активно', readonly=True)
    stage = fields.Char(string='Статус', readonly=True)
    is_closed = fields.Boolean(string='Виключено', readonly=True)
    # type_id = fields.Many2one(string='Код ознаки', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
        CREATE OR REPLACE VIEW asset_nfs_item_united AS (
        select
            cast(concat('100', anfsvd.id) as int4) as id,
            anfsvd.code as code,
            anfsvd.company_id as company_id,
            anfsvd.company_mfo as company_mfo,
            anfsvd.bal_account as bal_account,
            TRIM(anfsvd.asset_type) as asset_type,
            anfsvd.asset_identifier as asset_identifier,
            anfsvd.description as original_description,
            anfsvd.account_date as account_date,
            anfsvd.currency_id as currency_id,
            anfsvd.book_value as book_value,
            anfsvd.book_value_uah as book_value_uah,
            anfsvd.apprisal_value as apprisal_value,
            dgf_d."name" as document_id,
            bs.is_closed as is_closed,            
            bs."name" as stage
        from
            asset_nfs_list_item as anfsvd
        join base_stage bs on anfsvd.stage_id = bs.id
        join asset_nfs_request anr on anfsvd.request_id = anr.id
        join dgf_document dgf_d on anr.document_id = dgf_d.id        
        where	 
            (bs.is_closed = false or bs.is_closed is null) and 
            anfsvd.active = true
        union
        select
        	cast(concat('200', anfsod.id) as int4) as id,
            anfsod.code as code,
            anfsod.company_id as company_id,
            anfsod.company_mfo as company_mfo,
            anfsod.bal_account as bal_account,
            TRIM(anfsod.asset_type) as asset_type,
            anfsod.asset_identifier as asset_identifier,
            anfsod.description as original_description,
            anfsod.account_date as account_date,
            anfsod.currency_id as currency_id,
            anfsod.book_value as book_value,
            anfsod.book_value_uah as book_value_uah,
            anfsod.apprisal_value as apprisal_value,
            dgf_db."name" as document_id,
            bso.is_closed as is_closed,            
            bso."name" as stage
        from
            asset_blocked_list_item as anfsod
        join base_stage bso on anfsod.stage_id = bso.id
        join asset_blocked_request abr on anfsod.request_id = abr.id
        join dgf_document_blocked dgf_db on abr.document_id = dgf_db.id
        where
            (bso.is_closed = false or bso.is_closed is null) and 
            anfsod.active = true
        );
        """
        self.env.cr.execute(query)


##
        # select
        #     anfsvd.id as id,
        #     anfsvd.code as code,
        #     anfsvd.company_id as company_id,
        #     anfsvd.company_mfo as company_mfo,
        #     anfsvd.bal_account as bal_account,
        #     TRIM(anfsvd.asset_type) as asset_type,
        #     anfsvd.asset_identifier as asset_identifier,
        #     anfsvd.description as original_description,
        #     anfsvd.account_date as account_date,
        #     anfsvd.currency_id as currency_id,
        #     anfsvd.book_value as book_value,
        #     anfsvd.book_value_uah as book_value_uah,
        #     anfsvd.apprisal_value as apprisal_value,
        #     bs.is_closed as is_closed,
        #     bs."name" as stage
        # from
        #     asset_nfs_list_item as anfsvd
        # join base_stage bs on anfsvd.stage_id = bs.id
        # where	 
        #     (bs.is_closed = false or bs.is_closed is null) and 
        #     anfsvd.active = true
        # union
        # select
        #     anfsod.id as id,
        #     anfsod.code as code,
        #     anfsod.company_id as company_id,
        #     anfsod.company_mfo as company_mfo,
        #     anfsod.bal_account as bal_account,
        #     TRIM(anfsod.asset_type) as asset_type,
        #     anfsod.asset_identifier as asset_identifier,
        #     anfsod.description as original_description,
        #     anfsod.account_date as account_date,
        #     anfsod.currency_id as currency_id,
        #     anfsod.book_value as book_value,
        #     anfsod.book_value_uah as book_value_uah,
        #     anfsod.apprisal_value as apprisal_value,
        #     bso.is_closed as is_closed,            
        #     bso."name" as stage
        # from
        #     asset_blocked_list_item as anfsod
        # join base_stage bso on anfsod.stage_id = bso.id
        # where
        #     (bso.is_closed = false or bso.is_closed is null) and 
        #     anfsod.active = true
##


    def _compute_description(self):
        for record in self:            
            if record.asset_type == '101':
                result = "Об'єкт нерухомого майна"
            elif record.asset_type == '102':
                result = 'Земельна ділянка'
            elif record.asset_type == '103':
                result = 'Транспортний засіб'
            else:
                result = record.original_description
            record.description = result