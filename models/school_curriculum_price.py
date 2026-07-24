from odoo import api, fields, models

class SchoolCurriculumPrice(models.Model):
    _name = "school.curriculum.price"
    _description = "School Curriculum Price"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", default="New")
    curriculum_id = fields.Many2one('school.curriculum', string="Curriculum")

    price = fields.Float(string="Price")
    discount = fields.Float(string="Discount")

    payment_term = fields.Selection([
        ('yearly', 'Yearly'),
        ('semester', 'Semester'),
        ('monthly', 'Monthly'),
    ], default='semester', string="Payment Term")

    amount = fields.Float(string="Amount")
    note = fields.Text(string="Note")

    @api.onchange('price', 'discount', 'payment_term')
    def _onchange_amount(self):
        for rec in self:
            total = rec.price - rec.discount

            if rec.payment_term == 'monthly':
                rec.amount = total / 12
            elif rec.payment_term == 'semester':
                rec.amount = total / 2
            else:  # yearly
                rec.amount = total

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "school.curriculum.price"
                ) or "New"
        return super().create(vals_list)