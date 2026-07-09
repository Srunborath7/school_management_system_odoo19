from odoo import fields, models, api
from odoo.exceptions import ValidationError

class SchoolSetting(models.Model):
    _name = 'school.setting'
    _description = 'School Setting'

    name = fields.Char(string="Theme Name",required=True,default="Default Theme")
    text_color_primary= fields.Char(string="Text Color  Primary",default="#ffffff",required=True)
    text_color_secondary= fields.Char(string="Text Color Secondary",default="#000000",required=True)
    primary_color = fields.Char(string="Primary Color",default="#2d358e",required=True)
    secondary_color = fields.Char(string="Secondary Color",default="#4f5bd5",required=True)
    active = fields.Boolean(string="Active",default=False)

    @api.constrains('active')
    def _check_single_active_theme(self):
        for rec in self:
            if rec.active:
                active_count = self.search_count([
                    ('active', '=', True)
                ])

                if active_count > 1:
                    raise ValidationError(
                        "Only one theme can be active at a time."
                    )