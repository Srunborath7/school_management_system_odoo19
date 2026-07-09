from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    name = fields.Char(string="Purchase Order")
    approval_state = fields.Selection([
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string="Approval Status", default='pending', tracking=True)
    approved_by = fields.Many2one('res.users', string="Approved By", readonly=True)
    approved_date = fields.Datetime(string="Approved On", readonly=True)
    approval_notes = fields.Text(string="Approval Notes")
    email = fields.Char(string="Email", default="", copy=False, )
    requester_id = fields.Many2one("res.users", default=lambda self: self.env.user, required=True, )

    def action_custom_approve(self):
        self.write({
            'approval_state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })

    def action_custom_reject(self):
        self.write({'approval_state': 'rejected'})

    def action_rfq_send(self):
        self.ensure_one()

        self.write({
            "approval_state": "approved",
            "approved_by": self.env.user.id,
            "approved_date": fields.Datetime.now(),
        })

        template = self.env.ref(
            "school_management_system.email_purchase_order_approved",
            raise_if_not_found=False
        )

        if template:
            template.send_mail(
                self.id,
                force_send=True,
                email_values={
                    "email_from": self.env.user.email,
                    "email_to": self.requester_id.email,
                }
            )

        return True
