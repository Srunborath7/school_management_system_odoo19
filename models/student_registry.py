from odoo import fields, models, api
from datetime import date
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import re

class StudentRegistry(models.Model):
    _name = 'school.student.registry'
    _description = 'Student Registry'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    student_code = fields.Char(string="Student Code", readonly=True, default="New")
    DOB = fields.Date(string='DOB', required=True, default='2005-01-01', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    address = fields.Char(string='Address', tracking=True)
    enrolled_date = fields.Date(
        string="Enrolled Date",
        default=fields.Date.today,
        required=True,
        tracking=True
    )

    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('enrolled', 'Enrolled'),
            ('graduated', 'Graduated'),
            ('cancelled', 'Cancelled')
        ], string="Status", default='draft', required=True, tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender", default='male', required=True, tracking=True)
    calc_age = fields.Integer(string="Calc Age", compute='_compute_calc_age')
    theme_primary = fields.Char(compute='_compute_theme_colors')
    theme_secondary = fields.Char(compute='_compute_theme_colors')
    text_color_primary = fields.Char(compute='_compute_theme_colors')
    text_color_secondary = fields.Char(compute='_compute_theme_colors')
    _student_code_unique = models.Constraint(
        "UNIQUE(student_code)",
        "Student Code must be unique!",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",required=True
    )
    def action_enroll(self):
        for student in self:
            if not student.email:
                raise UserError("Please set an email address before enrolling %s." % student.name)
            student.status = "enrolled"
            student._send_enrollment_email()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Enrollment Successful",
                "message": "The student has been enrolled successfully and the enrollment email has been sent.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_graduate(self):
        for student in self:
            if student.status != "enrolled":
                raise UserError("Student %s is not enrolled." % student.name)
            student.write({'status': 'graduated'})
            student.message_post(body="Student graduated.")
        return True

    def action_cancel(self):
        self.write({'status': 'cancelled'})
        self.message_post(body="Student registration cancelled.")
        return True

    def action_reset_draft(self):
        self.write({'status': 'draft'})
        self.message_post(body="Student reset to draft.")
        return True

    @api.constrains('DOB')
    def _check_dob(self):
        for rec in self:
            if rec.DOB:
                age = date.today().year - rec.DOB.year
                if age < 16:
                    raise ValidationError("Student must be at least 16 years old to enroll.")

    @api.depends('DOB')
    def _compute_calc_age(self):
        today = date.today()
        for rec in self:
            if rec.DOB:
                rec.calc_age = (today.year- rec.DOB.year- ((today.month, today.day) < (rec.DOB.month, rec.DOB.day)))
            else:
                rec.calc_age = 0

    @api.depends()
    def _compute_theme_colors(self):
        theme = self.env['school.setting'].search(
            [('active', '=', True)],
        )

        for rec in self:
            rec.theme_primary = theme.primary_color
            rec.theme_secondary = theme.secondary_color
            rec.text_color_primary = theme.text_color_primary
            rec.text_color_secondary = theme.text_color_secondary


    def _send_enrollment_email(self):
        self.ensure_one()

        template = self.env.ref(
            "school_management_system.email_template_student_enrollment",
            raise_if_not_found=False
        )

        if template:
            template.send_mail(
                self.id,
                force_send=True,
                email_values={
                    "email_from": self.env.user.email,
                    "email_to": self.email,
                }
            )

        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("student_code") == "New" or not vals.get("student_code"):
                vals["student_code"] = self.env["ir.sequence"].next_by_code(
                    "school.student.registry"
                ) or "New"

        return super().create(vals_list)

    @api.constrains("email")
    def _check_email(self):
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        for rec in self:
            if rec.email:
                if not re.match(email_pattern, rec.email):
                    raise ValidationError(
                        "Please enter a valid email address.\n"
                        "Example: student@example.com"
                    )
