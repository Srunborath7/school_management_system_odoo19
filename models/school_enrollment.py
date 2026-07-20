from odoo import models, fields, api

class SchoolEnrollment(models.Model):
    _name = "school.enrollment"
    _description = "School Enrollment"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", default="New" , tracking=True, readonly=True)
    student_id = fields.Many2one('school.student.registry', string="Student")
    batch_id = fields.Many2one('school.batch', string="Batch")
    curriculum_id = fields.Many2one('school.curriculum', string="Curriculum")
    course_ids = fields.Many2many("school.course",related="curriculum_id.course_ids",string="Courses")
    course_name = fields.Char(string="Course Names",compute="_compute_course_name",store=True,)
    academic_program = fields.Char(related="curriculum_id.academic_program_id.name", string="Academic Program")
    major = fields.Char(related="curriculum_id.major_id.name", string="Major")
    academic_year = fields.Char(related="curriculum_id.academic_year_id.name", string="Academic Year")
    academic_year_level = fields.Char(related="curriculum_id.academic_level_id.name" , string="Academic Year Level")
    description = fields.Char(string="Description")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('closed', 'Closed'),
    ], default='draft', tracking=True)

    @api.model
    def create(self, vals):
        # if vals.get("name", "New") == "New":
        #     vals["name"] = self.env["ir.sequence"].next_by_code(
        #         "school.enrollment"
        #     ) or "New"
        # return super().create(vals)
        for val in vals:
            if val.get("name", "New") == "New":
                val["name"] = self.env["ir.sequence"].next_by_code(
                     "school.enrollment"
                ) or "New"
        return super().create(vals)

    @api.depends("course_ids", "course_ids.name")
    def _compute_course_name(self):
        for rec in self:
            rec.course_name = ", ".join(rec.course_ids.mapped("name"))

    def action_active(self):
        self.write({'status': 'active'})
        self.message_post(body="Enrollment status has been activated.")

    def action_inactive(self):
        self.write({'status': 'inactive'})
        self.message_post(body="Enrollment status has been set to inactive.")

    def action_closed(self):
        self.write({'status': 'closed'})
        self.message_post(body="Enrollment status has been closed.")

    def action_reset_draft(self):
        self.write({'status': 'draft'})
        self.message_post(body="Enrollment status has been reset to draft.")