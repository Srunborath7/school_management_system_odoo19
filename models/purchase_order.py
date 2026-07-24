from odoo import models, fields, api


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"


    approval_state = fields.Selection(

        [
            ('pending','Pending Approval'),
            ('approved','Approved'),
            ('rejected','Rejected'),

        ],

        string="Approval Status",

        default="pending",

        tracking=True
    )


    approved_by = fields.Many2one(
        "res.users",
        string="Approved By",
        readonly=True
    )


    approved_date = fields.Datetime(
        string="Approved Date",
        readonly=True
    )


    approval_notes = fields.Text(
        string="Approval Notes"
    )


    email = fields.Char(
        string="Email",
        copy=False
    )


    requester_id = fields.Many2one(

        "res.users",

        string="Requester",

        default=lambda self:self.env.user,

        required=True

    )



    def action_custom_approve(self):

        for order in self:

            order.write({

                "approval_state":"approved",

                "approved_by":self.env.user.id,

                "approved_date":fields.Datetime.now(),

            })


        return True



    def action_custom_reject(self):

        for order in self:

            order.write({

                "approval_state":"rejected"

            })


        return True

    @api.model
    def get_dashboard_data(self):
        return {
            "draft": self.search_count([("state", "=", "draft")]),
            "sent": self.search_count([("state", "=", "sent")]),
            "purchase": self.search_count([("state", "=", "purchase")]),
            "done": self.search_count([("state", "=", "done")]),
            "cancel": self.search_count([("state", "=", "cancel")]),
        }