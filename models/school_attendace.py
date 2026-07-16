from openpyxl.worksheet import related

from odoo import models, fields, api

class SchoolAttendance(models.Model):
    _name = "school.attendance"
    _description = "School Attendance"

    name = fields.Char(string="Attendance",default="New",required=True,)
    group_class_id = fields.Many2one("school.class.group",string="Class Group",required=True,store=True)
    student_ids = fields.Many2many("school.student.registry",string="Students",)
    curriculum_id = fields.Many2one("school.curriculum",string="Curriculum",readonly=True,store=True)
    academic_year_id = fields.Many2one("school.academic.year",string="Academic Year",readonly=True,store=True)
    session_id = fields.Many2one("school.schedule.session",string="Session")
    start_datetime = fields.Datetime( related="session_id.start_datetime", string="Start Date",readonly=True, store=True)
    end_datetime = fields.Datetime(related="session_id.end_datetime", string="End Date", readonly=True, store=True)
    course_id = fields.Many2one("school.course",string="Course",readonly=True,store=True)
    teacher_id = fields.Many2one("school.teacher",string="Teacher",readonly=True,store=True)
    room_id = fields.Many2one("school.room",string="Room",readonly=True,store=True)
    line_ids = fields.One2many("school.attendance.line","attendance_id",string="Attendance",)

    @api.onchange("group_class_id")
    def _onchange_group_class_id(self):
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

        self.curriculum_id = self.group_class_id.curriculum_id
        self.academic_year_id = self.curriculum_id.academic_year_id

        domain = [
            ("schedule_id.class_group_id", "=", self.group_class_id.id),
        ]

        # Filter sessions within Academic Year
        if self.academic_year_id.start_date:
            domain.append((
                "start_datetime",
                ">=",
                fields.Datetime.to_datetime(self.academic_year_id.start_date)
            ))

        if self.academic_year_id.end_date:
            domain.append((
                "end_datetime",
                "<=",
                fields.Datetime.to_datetime(self.academic_year_id.end_date)
            ))

        return {
            "domain": {
                "session_id": domain
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

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get("name") == "New":
                vals["name"] = (
                        self.env["ir.sequence"]
                        .next_by_code("school.attendance")
                        or "New"
                )

            session_id = vals.get("session_id")

            if session_id:
                session = self.env["school.schedule.session"].browse(session_id)

                vals.update({
                    "course_id": session.course_id.id,
                    "teacher_id": session.teacher_id.id,
                    "room_id": session.room_id.id,
                })

                if session.schedule_id:
                    curriculum = session.schedule_id.curriculum_id

                    vals.update({
                        "curriculum_id": curriculum.id,
                        "academic_year_id": curriculum.academic_year_id.id,
                        "group_class_id": session.schedule_id.class_group_id.id,
                    })

        return super().create(vals_list)

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
    date = fields.Date(
        string="Date",
        compute="_compute_date",
        store=True
    )

    @api.depends("attendance_id.start_datetime")
    def _compute_date(self):
        for line in self:
            if line.attendance_id.start_datetime:
                line.date = line.attendance_id.start_datetime.date()
            else:
                line.date = False


