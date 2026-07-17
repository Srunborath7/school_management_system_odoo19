from odoo import models, fields, api
from datetime import timedelta


class SchoolAttendance(models.Model):
    _name = "school.attendance"
    _description = "School Attendance"

    name = fields.Char(string="Attendance", default="New", required=True)
    group_class_id = fields.Many2one("school.class.group", string="Class Group", required=True, store=True)
    student_ids = fields.Many2many("school.student.registry", string="Students")
    curriculum_id = fields.Many2one("school.curriculum", string="Curriculum", readonly=True, store=True)
    academic_year_id = fields.Many2one("school.academic.year", string="Academic Year", readonly=True, store=True)
    session_id = fields.Many2one("school.schedule.session", string="Session", required=True)
    start_datetime = fields.Datetime(related="session_id.start_datetime", string="Start Date", store=True,
                                     readonly=True)
    end_datetime = fields.Datetime(related="session_id.end_datetime", string="End Date", store=True, readonly=True)
    course_id = fields.Many2one("school.course", string="Course", readonly=True, store=True)
    teacher_id = fields.Many2one("school.teacher", string="Teacher", readonly=True, store=True)
    room_id = fields.Many2one("school.room", string="Room", readonly=True, store=True)
    line_ids = fields.One2many("school.attendance.line", "attendance_id", string="Student Attendance")
    session_ids = fields.Many2many("school.schedule.session", string="All Sessions", readonly=True, copy=False)
    week_start = fields.Date(string="Week Start", compute="_compute_week")
    week_end = fields.Date(string="Week End", compute="_compute_week")

    @api.depends("start_datetime")
    def _compute_week(self):
        for rec in self:
            if rec.start_datetime:
                date = rec.start_datetime.date()
                rec.week_start = (date - timedelta(days=date.weekday()))
                rec.week_end = (rec.week_start + timedelta(days=6))
            else:
                rec.week_start = False
                rec.week_end = False

    @api.onchange("group_class_id")
    def _onchange_group_class_id(self):
        self.session_id = False
        self.session_ids = [(5, 0, 0)]
        self.line_ids = [(5, 0, 0)]
        self.course_id = False
        self.teacher_id = False
        self.room_id = False
        if not self.group_class_id:
            self.curriculum_id = False
            self.academic_year_id = False
            return {
                "domain": {
                    "session_id": []
                }
            }
        self.curriculum_id = (self.group_class_id.curriculum_id)
        self.academic_year_id = (self.curriculum_id.academic_year_id)
        domain = [
            (
                "schedule_id.class_group_id",
                "=",
                self.group_class_id.id
            )
        ]
        if self.academic_year_id.start_date:
            domain.append(
                (
                    "start_datetime",
                    ">=",
                    fields.Datetime.to_datetime(
                        self.academic_year_id.start_date
                    )
                )
            )

        if self.academic_year_id.end_date:
            domain.append(
                (
                    "end_datetime",
                    "<=",
                    fields.Datetime.to_datetime(
                        self.academic_year_id.end_date
                    )
                )
            )
        return {
            "domain": {
                "session_id": domain
            }
        }

    @api.onchange("session_id")
    def _onchange_session(self):
        self.line_ids = [(5, 0, 0)]
        if not self.session_id:
            return
        session = self.session_id
        self.course_id = session.course_id
        self.teacher_id = session.teacher_id
        self.room_id = session.room_id
        self.curriculum_id = (session.schedule_id.curriculum_id)
        self.academic_year_id = (self.curriculum_id.academic_year_id)
        sessions = self.env["school.schedule.session"].search([
            (
                "course_id",
                "=",
                session.course_id.id
            ),

            (
                "schedule_id.class_group_id",
                "=",
                session.schedule_id.class_group_id.id
            )

        ])
        self.session_ids = [
            (
                6,
                0,
                sessions.ids
            )
        ]
        students = (
            session.schedule_id
            .class_group_id
            .student_ids
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
                        "state": "present"
                    }
                )
            )

        self.line_ids = lines

    @api.model_create_multi
    def create(self, vals_list):

        records = super().create(vals_list)

        for rec in records:

            if rec.name == "New":
                rec.name = (
                        self.env["ir.sequence"]
                        .next_by_code("school.attendance")
                        or "New"
                )

            if rec.session_id:
                session = rec.session_id

                # get all sessions
                sessions = self.env[
                    "school.schedule.session"
                ].search([
                    (
                        "course_id",
                        "=",
                        session.course_id.id
                    ),
                    (
                        "schedule_id.class_group_id",
                        "=",
                        session.schedule_id.class_group_id.id
                    ),
                ])
                rec.write({
                    "session_ids": [
                        (
                            6,
                            0,
                            sessions.ids
                        )
                    ],
                    "course_id":
                        session.course_id.id,

                    "teacher_id":
                        session.teacher_id.id,

                    "room_id":
                        session.room_id.id,

                    "curriculum_id":
                        session.schedule_id.curriculum_id.id,

                    "academic_year_id":
                        session.schedule_id.curriculum_id.academic_year_id.id,

                    "group_class_id":
                        session.schedule_id.class_group_id.id,
                })
        return records

class SchoolAttendanceLine(models.Model):
    _name = "school.attendance.line"
    _description = "Attendance Line"

    attendance_id = fields.Many2one( "school.attendance",string="Attendance")
    student_id = fields.Many2one("school.student.registry",string="Student")
    gender = fields.Selection(related="student_id.gender",readonly=True )
    phone = fields.Char(related="student_id.phone", readonly=True)
    email = fields.Char(related="student_id.email",readonly=True)
    state = fields.Selection(
        [
            ("present", "Present"),
            ("absent", "Absent"),
            ("late", "Late"),
            ("permission", "Permission")
        ],
        default="present",
        string="Status"
    )
    reason = fields.Text(string="Reason")
    display_date = fields.Date(string="Date",compute="_compute_display_date",store=True)
    @api.depends("attendance_id.start_datetime")
    def _compute_display_date(self):
        for line in self:
            if line.attendance_id.start_datetime:
                line.display_date = (line.attendance_id.start_datetime.date())
            else:
                line.display_date = False
