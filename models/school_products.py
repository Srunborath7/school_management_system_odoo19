from odoo import fields, models

class SchoolProduct(models.Model):
    _inherit = "product.template"

    name = fields.Char(string="Name", default="New")
    department_ids = fields.Many2one("school.department",string="Department")
    school_type = fields.Selection(
        [
            ('uniform', 'Uniform'),
            ('book', 'Book'),
            ('stationery', 'Stationery'),
            ('equipment', 'Equipment'),
        ],
        string="School Product Type"
    )
    school_note = fields.Text(
        string="School Description"
    )
    academic_level_ids = fields.Many2one("school.academic.year.level", string="Academic Year Level")

