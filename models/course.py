from odoo import fields, models, api

class Course(models.Model):
    _name = 'school.course'
    _description = 'Student Course'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Course Name",required=True, tracking=True )
    description = fields.Text(string="Description",required=True, tracking=True)
    creation_date = fields.Datetime(string="Create Date",default=fields.Datetime.now, tracking=True)
    credits = fields.Integer(string="Credits",default=3,tracking=True)
    code = fields.Char(string="Course Code",readonly=True,required=True, tracking=True)
    _sql_constraints = [(
        'code_name_unique',
        'UNIQUE (code)',
        'Course Code must be unique',
    )]

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            if not vals.get('code') and vals.get('name'):
                initials = ''.join(
                    word[0].upper()
                    for word in vals['name'].split()
                )

                sequence = self.env['ir.sequence'].next_by_code(
                    'school.course'
                )

                number = ''.join(filter(str.isdigit, sequence))

                vals['code'] = f"CS{initials}{number}"

        return super().create(vals_list)