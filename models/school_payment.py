from odoo import api, fields, models


class SchoolPayment(models.Model):
    _inherit = "sale.order"

    student_ids = fields.Many2one("school.student.registry",string="Student",required=True)
    payment_type = fields.Selection([
        ('payment_term', 'Payment Term'),
        ('late_payment', 'Penalty for Late Payment'),
        ('certificate_fee', 'Certificate Fee'),
        ('replacement_fee', 'Replacement Fee'),
    ], default='payment_term')

    payment_term = fields.Selection([
        ('yearly', 'Yearly'),
        ('semester', 'Semester'),
        ('monthly', 'Monthly'),
    ], default='semester')

    curriculum_ids = fields.Many2one(
        'school.curriculum',
        string="Curriculum"
    )

    @api.onchange("student_ids")
    def _onchange_student_ids(self):
        if self.student_ids.partner_id:
            self.partner_id = self.student_ids.partner_id
            self.partner_invoice_id = self.student_ids.partner_id
            self.partner_shipping_id = self.student_ids.partner_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            student_id = vals.get("student_ids")
            if student_id:
                student = self.env["school.student.registry"].browse(student_id)

                # Create partner if missing
                if not student.partner_id:
                    partner = self.env["res.partner"].create({
                        "name": student.name,
                        "phone": student.phone,
                        "email": student.email,
                    })

                    student.partner_id = partner.id

                partner = student.partner_id

                # Set all required sale order partners
                vals["partner_id"] = partner.id
                vals["partner_invoice_id"] = partner.id
                vals["partner_shipping_id"] = partner.id

        return super().create(vals_list)

    @api.onchange("payment_term")
    def _onchange_payment_term(self):
        if self.payment_type != "payment_term":
            return

        for line in self.order_line:

            if not line.curriculum_ids:
                continue

            curriculum_price = self.env["school.curriculum.price"].search([
                ("curriculum_id", "=", line.curriculum_ids.id),
                ("payment_term", "=", self.payment_term),
            ], limit=1)

            if curriculum_price:
                line.curriculum_price_ids = curriculum_price.id
                line.price_unit = curriculum_price.amount

class SchoolPaymentLine(models.Model):
    _inherit = "sale.order.line"

    curriculum_ids = fields.Many2one(
        "school.curriculum",
        string="Curriculum"
    )

    curriculum_price_ids = fields.Many2one(
        "school.curriculum.price",
        string="Curriculum Price"
    )

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get("curriculum_ids") and not vals.get("name"):

                curriculum = self.env["school.curriculum"].browse(
                    vals["curriculum_ids"]
                )

                if curriculum.academic_level_id:
                    vals["name"] = curriculum.academic_level_id.name
                else:
                    vals["name"] = curriculum.name

        return super().create(vals_list)

    @api.onchange("curriculum_ids")
    def _onchange_curriculum(self):

        if not self.curriculum_ids:
            return

        # Find or create product
        product = self.env["product.product"].search([
            ("name", "=", self.curriculum_ids.name)
        ], limit=1)

        if not product:
            product = self.env["product.product"].create({
                "name": self.curriculum_ids.name,
                "type": "service",
                "sale_ok": True,
                "list_price": 0,
            })

        self.product_id = product.id

        # Description
        if self.curriculum_ids.academic_level_id:
            self.name = self.curriculum_ids.academic_level_id.name
        else:
            self.name = self.curriculum_ids.name

        # Price
        curriculum_price = self.env["school.curriculum.price"].search([
            ("curriculum_id", "=", self.curriculum_ids.id),
            ("payment_term", "=", self.order_id.payment_term),
        ], limit=1)

        if curriculum_price:
            self.curriculum_price_ids = curriculum_price.id
            self.price_unit = curriculum_price.amount