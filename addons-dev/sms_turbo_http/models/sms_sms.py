# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import threading

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class SmsSms(models.Model):
    _inherit = "sms.sms"

    error_detail = fields.Text(readonly=True)
    message_id = fields.Text(readonly=True)
    response_status = fields.Text(readonly=True)

    def _split_batch(self):
        if self.env["sms.api"]._is_sent_with_turbosms():
            # No batch with turbosms
            for record in self:
                yield [record.id]
        else:
            yield from super()._split_batch()

    @api.model
    def _process_queue(self, limit=100, ids=None):
        """ Send immediately queued messages, committing after each message is sent.
        This is not transactional and should not be called during another transaction!

       :param list ids: optional list of emails ids to send. If passed no search
         is performed, and these ids are used instead.
        """
        if self.env["sms.api"]._is_sent_with_turbosms():
            domain = [('state', '=', 'outgoing')]

            filtered_ids = self.search(domain, limit=limit).ids  # TDE note: arbitrary limit we might have to update
            if ids:
                ids = list(set(filtered_ids) & set(ids))
            else:
                ids = filtered_ids
            ids.sort()

            res = None
            try:
                # auto-commit except in testing mode
                auto_commit = not getattr(threading.currentThread(), 'testing', False)
                res = self.browse(ids).send(delete_all=False, auto_commit=auto_commit, raise_exception=False)
            except Exception:
                _logger.exception("Failed processing SMS queue")
            return res
        else:
            return super()._process_queue()
