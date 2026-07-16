from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PurchaseRequest(models.Model):
    _name = "school.purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Request No",readonly=True,default="/",copy=False,)
    email = fields.Char(string="Email",default="",copy=False,)
    requester_id = fields.Many2one("res.users",default=lambda self: self.env.user,required=True,)
    department = fields.Many2one('school.department',string="Department")
    request_date = fields.Date(default=fields.Date.today)
    state = fields.Selection([
        ("draft", "Draft"),
        ("submit", "Submitted"),
        ("approve", "Approved"),
        ("reject", "Rejected"),
    ], default="draft", tracking=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
    ], string="Priority", default='0')
    line_ids = fields.One2many("school.purchase.request.line","request_id",string="Products",)
    total_amount = fields.Float(compute="_compute_total",store=True,)
    approved_by = fields.Many2one("res.users",string="Approved By",readonly=True,tracking=True)
    approval_date = fields.Date(string="Approval Date",readonly=True,tracking=True)

    @api.depends("line_ids.subtotal")
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(
                rec.line_ids.mapped("subtotal")
            )

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]

        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = sequence.next_by_code("school.purchase.request") or "/"

        return super().create(vals_list)

    @api.constrains("request_date")
    def _check_date(self):
        for rec in self:
            if rec.request_date > fields.Date.today():
                raise ValidationError(
                    "Request date cannot be in the future."
                )

    def action_submit(self):
        self.state = "submit"

    def action_approve(self):
        for rec in self:
            rec.write({
                "state": "approve",
                "approved_by": self.env.user.id,
                "approval_date": fields.Date.today(),
            })

            rec.message_post(
                body="Purchase Request Approved."
            )

            rec._send_purchase_approval_email()

        return True

    def _send_purchase_approval_email(self):
        self.ensure_one()

        self.write({
            "state": "approve",
            "approved_by": self.env.user.id,
            "approval_date": fields.Datetime.now(),
        })

        template = self.env.ref(
            "school_management_system.email_purchase_request_approved",
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

    def action_reject(self):
        self.state = "reject"

    def action_draft(self):
        self.state = "draft"
