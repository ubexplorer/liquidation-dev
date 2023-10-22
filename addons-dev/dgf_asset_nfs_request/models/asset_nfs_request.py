# -*- coding: utf-8 -*-

import ast

from datetime import date, datetime, timedelta
import base64

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class AssetNfsRequest(models.Model):
    _inherit = 'asset.nfs.request'
    is_base_stage = False

    base_request_id = fields.Many2one('dgf.base.request', string='Заявка щодо активу', required=True, ondelete='restrict', delegate=True)
    category_id = fields.Many2one('dgf.base.request.category', string='Категорія заявки', default=lambda self: self.env.ref('dgf_asset_nfs_request.category_asset_nfs').id)
