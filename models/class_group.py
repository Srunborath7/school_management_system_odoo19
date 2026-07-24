from odoo import fields, models, api

class ClassGroup(models.Model):
    _name = 'school.class.group'
    _description = 'School Class Group'

    name = fields.Char(string="Name", default="New Class")
    room_id = fields.Many2one('school.room', string="Room")
    curriculum_id = fields.Many2one('school.curriculum',string="Curriculum",required=True)
    enrollment_id = fields.Many2one('school.enrollment',string="Enrollment", store=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
    ], default='active')
    description = fields.Text(string="Description")
    student_ids = fields.Many2many('school.student.registry',compute="_compute_students",string="Students")
    student_count = fields.Integer(string="Student Count",compute="_compute_students")

    @api.depends('curriculum_id')
    def _compute_students(self):
        Enrollment = self.env['school.enrollment']

        for rec in self:
            students = self.env['school.student.registry']

            if rec.curriculum_id:
                enrollments = Enrollment.search([
                    ('curriculum_id', '=', rec.curriculum_id.id)
                ])
                students = enrollments.mapped('student_id')

            rec.student_ids = students
            rec.student_count = len(students)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == "New Class":
                curriculum = False
                if vals.get('curriculum_id'):
                    curriculum = self.env['school.curriculum'].browse(vals['curriculum_id'])

                if curriculum and curriculum.major_id:
                    prefix = ''.join(
                        word[0].upper()
                        for word in curriculum.major_id.name.split()
                    )
                    count = self.search_count([
                        ('curriculum_id.major_id', '=', curriculum.major_id.id)
                    ]) + 1

                    vals['name'] = f"{prefix}G{count:03d}"
                else:
                    vals['name'] = "GRP001"

        return super().create(vals_list)

    def action_view_students(self):
        self.ensure_one()
        enrollments = self.env['school.enrollment'].search([('curriculum_id', '=', self.curriculum_id.id)])
        students = enrollments.mapped('student_id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'school.student.registry',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', students.ids)],
        }
