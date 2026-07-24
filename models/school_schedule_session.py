from odoo import models, fields, api

class SchoolScheduleSession(models.Model):

    _name = "school.schedule.session"
    _description = "School Schedule Session"
    _order = "start_datetime"

    name = fields.Char(compute="_compute_name",store=True)
    schedule_id = fields.Many2one("school.schedule",string="Schedule",required=True,ondelete="cascade",index=True,)
    class_group_id = fields.Many2one("school.class.group",related="schedule_id.class_group_id",string="Class",store=True,readonly=True,)
    color = fields.Integer(string="Color Index",compute="_compute_color",store=True,)
    schedule_line_id = fields.Many2one("school.schedule.line",string="Schedule Line",required=True,ondelete="cascade",index=True,)
    start_datetime = fields.Datetime(string="Start Date Time",required=True,)
    end_datetime = fields.Datetime(string="End Date Time",required=True,)
    start_time = fields.Float(related="schedule_line_id.start_time",string="Start Time",readonly=True,)
    end_time = fields.Float(related="schedule_line_id.end_time",string="End Time",readonly=True,)
    course_id = fields.Many2one(related="schedule_line_id.course_id",string="Course",store=True,readonly=True,)
    teacher_id = fields.Many2one(related="schedule_line_id.teacher_id",string="Teacher",store=True,readonly=True,)
    room_id = fields.Many2one(related="schedule_line_id.room_id",string="Room",store=True,readonly=True,)
    day = fields.Selection(related="schedule_line_id.day",string="Day",store=True,readonly=True,)
    curriculum_ids = fields.Many2one("school.curriculum",related="schedule_id.curriculum_id",string="Curriculum",store=True,readonly=True,)
    attendance_created = fields.Boolean(string="Attendance Created",compute="_compute_attendance_created",)

    @api.depends("schedule_line_id.day")
    def _compute_color(self):
        day_colors = {
            "monday": 1,  # Red
            "tuesday": 2,  # Blue
            "wednesday": 3,  # Green
            "thursday": 4,  # Orange
            "friday": 5,  # Purple
            "saturday": 6,  # Yellow
            "sunday": 7,  # Pink
        }
        for rec in self:
            rec.color = day_colors.get(
                rec.schedule_line_id.day,
                0
            )

    @api.depends("course_id", "start_datetime")
    def _compute_name(self):
        for rec in self:
            if rec.start_datetime:
                rec.name = (
                    f"{rec.course_id.name} - "
                    f"{rec.start_datetime.strftime('%d/%m/%Y')}"
                )
            else:
                rec.name = "Session"

    def action_create_attendance_from_session(self):

        self.ensure_one()

        attendance = self.env["school.attendance"].search([
            ("session_id", "=", self.id)
        ], limit=1)

        if not attendance:

            students = (
                self.schedule_id.class_group_id.student_ids
            )

            attendance = self.env["school.attendance"].create({

                "session_id": self.id,

                "group_class_id":
                    self.schedule_id.class_group_id.id,

                "curriculum_id":
                    self.schedule_id.curriculum_id.id,

                "academic_year_id":
                    self.schedule_id.curriculum_id.academic_year_id.id,

                "course_id":
                    self.course_id.id,

                "teacher_id":
                    self.teacher_id.id,

                "room_id":
                    self.room_id.id,

                "student_ids":
                    [(6, 0, students.ids)],

            })

            lines = []

            for student in students:
                lines.append(
                    (0, 0, {
                        "student_id": student.id,
                        "state": "present",
                    })
                )

            attendance.line_ids = lines

        return {
            "type": "ir.actions.act_window",
            "name": "Attendance",
            "res_model": "school.attendance",
            "view_mode": "form",
            "res_id": attendance.id,
        }

    def _compute_attendance_created(self):

        Attendance = self.env["school.attendance"]

        for session in self:
            attendance = Attendance.search([
                ("session_id", "=", session.id)
            ], limit=1)

            session.attendance_created = bool(attendance)