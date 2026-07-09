from odoo import fields, models

class Batch(models.Model):
    _name = 'school.batch'
    _description = 'Batch'
    _inherit = ['mail.thread']

    name = fields.Char(string="Batch Name")
    academic_program_ids = fields.Many2one("school.academic.program", string="Academic Program", required=True, tracking=True)
    academic_year_ids = fields.Many2one("school.academic.year", string="Academic Year", required=True, tracking=True)
    note = fields.Char(string="Note")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
    ])

    def action_active(self):
        self.write({'status': 'active'})

    def action_completed(self):
        self.write({'status': 'completed'})

    def action_inactive(self):
        self.write({'status': 'inactive'})

    def action_reset_draft(self):
        self.write({'status': 'draft'})
