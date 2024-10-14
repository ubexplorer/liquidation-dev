# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class IrModel(models.Model):
    _inherit = "ir.model"

    is_base_type = fields.Boolean(
        string="Базовий тип",
        default=False,
        help="Whether this model support base type.",
    )

    def write(self, vals):
        if self and "is_base_type" in vals:
            if not all(rec.state == "manual" for rec in self):
                raise UserError(_("Only custom models can be modified."))
            if not all(rec.is_base_type <= vals["is_base_type"] for rec in self):
                raise UserError(_('Field "is_base_type" cannot be changed to "False".'))
            res = super(IrModel, self).write(vals)
            # setup models; this reloads custom models in registry
            self.pool.setup_models(self._cr)
            # update database schema of models
            models = self.pool.descendants(self.mapped("model"), "_inherits")
            self.pool.init_models(
                self._cr, models, dict(self._context, update_custom_fields=True)
            )
        else:
            res = super(IrModel, self).write(vals)
        return res

    def _reflect_model_params(self, model):
        vals = super(IrModel, self)._reflect_model_params(model)
        vals["is_base_type"] = issubclass(type(model), self.pool["base.type.abstract"])
        return vals

    @api.model
    def _instanciate(self, model_data):
        model_class = super(IrModel, self)._instanciate(model_data)
        if model_data.get("is_base_type") and model_class._name != "base.type.abstract":
            parents = model_class._inherit or []
            parents = [parents] if isinstance(parents, (str,)) else parents
            model_class._inherit = parents + ["base.type.abstract"]
        return model_class
