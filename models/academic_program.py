from odoo import fields, models, api
import re

class AcademicProgram(models.Model):
    _name = 'school.academic.program'
    _description = 'Academic Program'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, tracking=True)
    code = fields.Char(string="Code",readonly=True,copy=False,default="New",tracking=True)
    department_ids = fields.Many2one('school.department', string="Departments" , tracking=True)
    academic_year_ids = fields.Many2one('school.academic.year',string="Academic Year",required=True, tracking=True)
    duration = fields.Integer(string="Duration (Years)")
    total_credits = fields.Integer(string="Total Credits", default=3)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
    ], default='draft', string="Status", tracking=True)
    description = fields.Text(string="Description")

    def action_active(self):
        self.write({'status': 'active'})

    def action_completed(self):
        self.write({'status': 'completed'})

    def action_inactive(self):
        self.write({'status': 'inactive'})

    def action_closed(self):
        self.write({'status': 'closed'})

    def action_reset_draft(self):
        self.write({'status': 'draft'})

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            if not vals.get('code'):
                name = vals.get('name') or ''

                words = re.findall(r'[A-Za-z]+', name)

                prefix = ''.join(
                    word[0].upper()
                    for word in words[:3]
                )

                sequence = self.env['ir.sequence'].next_by_code(
                    'school.academic.program'
                ) or '001'

                vals['code'] = f"{prefix}{sequence}"

        return super().create(vals_list)