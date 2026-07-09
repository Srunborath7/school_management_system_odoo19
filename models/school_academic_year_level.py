from odoo import fields, models, api

class SchoolAcademicYearLevel(models.Model):
    _name = 'school.academic.year.level'
    _description = 'School Academic Year Level'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    year = fields.Integer(string='Year Of Study', required=True, tracking=True)
    semester = fields.Integer(string='Semester', required=True, tracking=True)
    degree = fields.Selection([
        ('bachelor','Bachelor Degree'),
        ('master','Master Degree'),
        ('phd','PhD Degree'),
    ],string='Degree',default='bachelor',tracking=True)
    description = fields.Text(string='Description')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('cancel', 'Cancel'),
    ],string='Status', default='draft', required=True, tracking=True)

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            year = vals.get('year', '')
            semester = vals.get('semester', '')
            vals['name'] = f"Year {year} - Semester {semester}"
        return super().create(vals)
