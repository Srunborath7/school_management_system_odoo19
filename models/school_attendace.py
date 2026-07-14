from odoo import models, fields, api

class SchoolAttendance(models.Model):
    _name = "school.attendance"
    _description = "School Attendance"

    name = fields.Char(string="Attendance",default="New",required=True,)
    group_class_id = fields.Many2one("school.class.group",string="Class Group",required=True,)
    student_ids = fields.Many2many("school.student.registry",string="Students",)
    curriculum_id = fields.Many2one("school.curriculum",string="Curriculum",readonly=True,)
    academic_year_id = fields.Many2one("school.academic.year",string="Academic Year",readonly=True,)
    session_id = fields.Many2one("school.schedule.session",string="Session")
    course_id = fields.Many2one("school.course",string="Course",readonly=True,)
    teacher_id = fields.Many2one("school.teacher",string="Teacher",readonly=True,)
    room_id = fields.Many2one("school.room",string="Room",readonly=True,)
    line_ids = fields.One2many("school.attendance.line","attendance_id",string="Attendance",)

    @api.onchange("group_class_id")
    def _onchange_group_class(self):

        self.session_id = False

        self.course_id = False
        self.teacher_id = False
        self.room_id = False

        self.line_ids = [(5, 0, 0)]

        if not self.group_class_id:
            self.curriculum_id = False
            self.academic_year_id = False

            return {
                "domain": {
                    "session_id": []
                }
            }

        self.curriculum_id = (
            self.group_class_id.curriculum_id
        )

        self.academic_year_id = (
            self.curriculum_id.academic_year_id
        )

        return {
            "domain": {
                "session_id": [
                    (
                        "schedule_id.class_group_id",
                        "=",
                        self.group_class_id.id
                    )
                ]
            }
        }

    # When select session
    @api.onchange("session_id")
    def _onchange_session(self):

        self.course_id = False
        self.teacher_id = False
        self.room_id = False

        self.line_ids = [(5, 0, 0)]

        if not self.session_id:
            return

        self.course_id = (
            self.session_id.course_id
        )

        self.teacher_id = (
            self.session_id.teacher_id
        )

        self.room_id = (
            self.session_id.room_id
        )

        if self.session_id.schedule_id:
            self.curriculum_id = (
                self.session_id.schedule_id.curriculum_id
            )

            self.academic_year_id = (
                self.curriculum_id.academic_year_id
            )

        students = (
            self.curriculum_id.student_ids
        )

        self.student_ids = [
            (
                6,
                0,
                students.ids
            )
        ]

        lines = []

        for student in students:
            lines.append(
                (
                    0,
                    0,
                    {
                        "student_id": student.id,
                        "state": "present",
                    }
                )
            )

        self.line_ids = lines
class SchoolAttendanceLine(models.Model):
    _name = 'school.attendance.line'
    _description = 'School Attendance Line'

    attendance_id = fields.Many2one("school.attendance", string="Attendance")
    student_id = fields.Many2one("school.student.registry", string="Student")
    gender = fields.Selection(related="student_id.gender",string="Gender",readonly=True,)
    phone = fields.Char(related="student_id.phone",string="Phone",readonly=True,)
    email = fields.Char(related="student_id.email",string="Email",readonly=True,)
    state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('permission','Permission')
    ], string="Status", default='present')
    reason = fields.Text(string="Reason")


