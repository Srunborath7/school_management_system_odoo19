from odoo import models, fields, tools


class PurchaseAnalysisReport(models.Model):
    _name = "purchase.analysis.report"
    _description = "Purchase Analysis Report"
    _auto = False
    _order = "date_order desc"

    name = fields.Char(readonly=True)
    date_order = fields.Datetime(readonly=True)
    partner_id = fields.Many2one("res.partner", readonly=True)
    product_id = fields.Many2one("product.product", readonly=True)
    approval_state = fields.Selection(
        [
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        readonly=True,
    )
    qty_ordered = fields.Float(readonly=True)
    price_total = fields.Monetary(readonly=True)
    currency_id = fields.Many2one("res.currency", readonly=True)
    company_id = fields.Many2one("res.company", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute(f"""
            CREATE VIEW {self._table} AS
            SELECT
                row_number() OVER () AS id,
                po.name,
                po.date_order,
                po.partner_id,
                pol.product_id,
                po.approval_state,
                pol.product_qty AS qty_ordered,
                pol.price_total,
                po.currency_id,
                po.company_id
            FROM purchase_order_line pol
            JOIN purchase_order po
                ON po.id = pol.order_id
            WHERE pol.product_id IS NOT NULL
        """)