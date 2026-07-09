from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type = fields.Selection(
        [
            ('student', 'Student'),
            ('teacher', 'Teacher'),
            ('parent', 'Parent'),
        ],
        string="Customer Type"
    )

    customer_code = fields.Char(
        string="Customer Code"
    )

    credit_limit = fields.Float(
        string="Credit Limit"
    )