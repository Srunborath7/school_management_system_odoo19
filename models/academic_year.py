from odoo import fields, models

class AcademicYear(models.Model):
    _name = 'school.academic.year'
    _description = 'Academic Year'
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", tracking=True)
    start_date = fields.Date(string="Start Date",required=True, tracking=True)
    end_date = fields.Date(string="End Date",required=True , tracking=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
    ], default='draft', tracking=True)
    description = fields.Text(string="Description")

    def action_active(self):
        self.write({'status': 'active'})
        self.message_post(
            body="Academic Year has been activated."
        )

    def action_completed(self):
        self.write({'status': 'completed'})
        self.message_post(
            body="Academic Year has been completed."
        )

    def action_inactive(self):
        self.write({'status': 'inactive'})
        self.message_post(
            body="Academic Year has been set to inactive."
        )

    def action_closed(self):
        self.write({'status': 'closed'})
        self.message_post(
            body="Academic Year has been closed."
        )

    def action_reset_draft(self):
        self.write({'status': 'draft'})
        self.message_post(
            body="Academic Year has been reset to draft."
        )
