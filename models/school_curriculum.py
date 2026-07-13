from odoo import models, fields, api

class SchoolCurriculum(models.Model):
    _name = 'school.curriculum'
    _description = 'School Curriculum'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Curriculum Name",default="New",tracking=True)
    major_id = fields.Many2one('school.major',string="Major",required=True,tracking=True)
    academic_program_id = fields.Many2one('school.academic.program',string="Academic Program",required=True,tracking=True)
    academic_year_id = fields.Many2one('school.academic.year',string="Academic Year",required=True,tracking=True)
    academic_level_id = fields.Many2one('school.academic.year.level',string="Academic Year Level",required=True,tracking=True)
    course_ids = fields.Many2many('school.course','school_curriculum_course_rel','curriculum_id','course_id',string="Courses",tracking=True)
    total_credit = fields.Integer(string="Total Credit",compute="_compute_total_credit",store=True)
    description = fields.Text(string="Description")
    enrollment_ids = fields.One2many('school.enrollment','curriculum_id',string="Enrollments")
    student_ids = fields.Many2many('school.student.registry',compute="_compute_students",string="Students")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('closed', 'Closed'),
    ], default='draft', tracking=True)
    start_date = fields.Date(
        related="academic_year_id.start_date",
        string="Start Date",
        readonly=True
    )

    end_date = fields.Date(
        related="academic_year_id.end_date",
        string="End Date",
        readonly=True
    )

    @api.depends('enrollment_ids.student_id')
    def _compute_students(self):
        for rec in self:
            rec.student_ids = rec.enrollment_ids.mapped('student_id')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "school.curriculum"
                ) or "New"
        return super().create(vals_list)

    @api.depends('course_ids')
    def _compute_total_credit(self):
        for rec in self:
            rec.total_credit = sum(rec.course_ids.mapped('credits'))

    def action_active(self):
        self.write({'status': 'active'})
        self.message_post(body="Curriculum has been activated.")

    def action_inactive(self):
        self.write({'status': 'inactive'})
        self.message_post(body="Curriculum has been set to inactive.")

    def action_closed(self):
        self.write({'status': 'closed'})
        self.message_post(body="Curriculum has been closed.")

    def action_reset_draft(self):
        self.write({'status': 'draft'})
        self.message_post(body="Curriculum has been reset to draft.")