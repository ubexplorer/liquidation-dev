import json
import os
import io
import base64
from urllib.request import urlopen

from odoo import models, fields, _

URLOPEN_TIMEOUT = 10


class UploadUktzedCode(models.TransientModel):
    _name = 'upload.uktzed.code'
    _description = 'Upload Uktzed wizard'

    upload_code = fields.Selection(
        required=True, default='module', selection=[
            ('module', _('Load from module')),
            ('file', _('Load from file')),
            ('url', _('Load from link')), ], )
    file = fields.Binary(string='Json File')
    url = fields.Char()
    comment = fields.Char(readonly=1)

    def upload(self):
        for obj in self:
            comment = \
                obj.upload_code == 'module' and obj.load_json(
                    open(os.path.join(os.path.dirname(__file__),
                                      "..", "data", "data.json"))) \
                or obj.upload_code == 'file' \
                and obj.load_json(io.BytesIO(base64.decodebytes(obj.file))) \
                or obj.upload_code == 'url' and obj.load_in_url(obj.url)
            obj.write({'comment': comment})
            return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'upload.uktzed.code',
                'res_id': obj.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

    def load_json(self, file):
        try:
            for f in json.loads(json.dumps(json.load(file))):
                self.upload_json(f)
        except Exception as error:
            return error
        return 'Done'

    def load_in_url(self, url):
        try:
            # bandit: B310
            response = urlopen(url, timeout=URLOPEN_TIMEOUT)  # nosec
            for obj in json.loads(response.read()):
                self.upload_json(obj)
        except Exception as error:
            return error
        return 'Done'

    def upload_json(self, data):
        name = data.get('name')
        title = data.get('title')
        parent_id = False
        parent_id_name = data.get('parent_id')
        if parent_id_name:
            parent = self.sudo().env['kw.uktzed.code'].search([
                ('name', '=', parent_id_name)], limit=1)
            parent_id = parent.id if parent else False
        if name or title:
            self.sudo().env['kw.uktzed.code'].create(
                {'name': name, 'title': title, 'parent_id': parent_id})
