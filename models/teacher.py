from odoo import fields, models, api

class Teacher(models.Model):
    _name = 'school.teacher'
    _description = 'School Teacher'
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", tracking=True)
    teacher_code = fields.Char(string="Teacher Code", tracking=True, default="New", readonly=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ],string="Gender",default='male',required=True, tracking=True)
    email = fields.Char(string="Email", tracking=True)
    phone = fields.Char(string="Phone", tracking=True)
    address = fields.Char(string="Address", tracking=True)
    department_ids = fields.Many2one('school.department',string="Department", required=True, tracking=True)
    start_date = fields.Datetime(string="Start Date", tracking=True)
    user_id = fields.Many2one("res.users",string="Related User",help="User account linked to this teacher")
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('retired', 'Retired'),
    ], string="Status", default='active', tracking=True)
    note = fields.Char(string="Note", tracking=True)
    
    def action_active(self):
        self.write({'status': 'active'})
        self.message_post(body="Student status changed to Active")

    def action_inactive(self):
        self.write({'status': 'inactive'})
        self.message_post(body="Student status changed to Inactive")

    def action_retired(self):
        self.write({'status': 'retired'})
        self.message_post(body="Student status changed to Retired")

    def action_reset_draft(self):
        self.write({'status': 'active'})
        self.message_post(body="Student status reset to Active")

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            if vals.get("teacher_code", "New") == "New":
                vals["teacher_code"] = self.env["ir.sequence"].next_by_code(
                    "school.teacher"
                ) or "New"

        return super().create(vals_list)
