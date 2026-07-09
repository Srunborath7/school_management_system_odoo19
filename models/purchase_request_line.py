from odoo import api, fields, models

class PurchaseRequestLine(models.Model):
    _name = "school.purchase.request.line"
    _description = "Purchase Request Line"

    request_id = fields.Many2one("school.purchase.request",required=True,ondelete="cascade",)
    product_id = fields.Many2one("product.product",required=True,)
    quantity = fields.Float(default=1)
    price = fields.Float()
    subtotal = fields.Float(compute="_compute_subtotal",store=True,)
    total_amount = fields.Float()

    @api.onchange("product_id")
    def _onchange_product(self):
        if self.product_id:
            self.price = self.product_id.standard_price

    @api.depends("quantity", "price")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.price
