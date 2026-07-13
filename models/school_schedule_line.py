from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolScheduleLine(models.Model):
    _name = "school.schedule.line"
    _description = "School Schedule Detail"
    _order = "day,start_time"

    schedule_id = fields.Many2one(
        "school.schedule",
        string="Schedule",
        required=True,
        ondelete="cascade",
    )

    day = fields.Selection(
        [
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        ],
        string="Day",
        required=True,
    )

    course_id = fields.Many2one(
        "school.course",
        string="Course",
        required=True,
    )

    teacher_id = fields.Many2one(
        "school.teacher",
        string="Teacher",
        required=True,
    )

    room_id = fields.Many2one(
        "school.room",
        string="Room",
        required=True,
    )

    start_time = fields.Float(
        string="Start Time",
        required=True,
    )

    end_time = fields.Float(
        string="End Time",
        required=True,
    )

    duration = fields.Float(
        string="Duration",
        compute="_compute_duration",
        store=True,
    )
    start_datetime = fields.Datetime(
        string="Start",
        compute="_compute_datetime",
        store=True,
    )

    end_datetime = fields.Datetime(
        string="End",
        compute="_compute_datetime",
        store=True,
    )
    @api.depends("start_time", "end_time")
    def _compute_duration(self):
        for rec in self:
            rec.duration = max(rec.end_time - rec.start_time, 0)

    @api.constrains("start_time", "end_time")
    def _check_time(self):
        for rec in self:
            if rec.end_time <= rec.start_time:
                raise ValidationError(
                    "End Time must be greater than Start Time."
                )

    @api.constrains(
        "teacher_id",
        "day",
        "start_time",
        "end_time",
    )
    def _check_teacher_conflict(self):
        for rec in self:
            if not rec.teacher_id:
                continue

            conflict = self.search(
                [
                    ("id", "!=", rec.id),
                    ("teacher_id", "=", rec.teacher_id.id),
                    ("day", "=", rec.day),
                    ("start_time", "<", rec.end_time),
                    ("end_time", ">", rec.start_time),
                ],
                limit=1,
            )

            if conflict:
                raise ValidationError(
                    "Teacher already has another class during this time."
                )

    @api.constrains(
        "room_id",
        "day",
        "start_time",
        "end_time",
    )
    def _check_room_conflict(self):
        for rec in self:
            if not rec.room_id:
                continue

            conflict = self.search(
                [
                    ("id", "!=", rec.id),
                    ("room_id", "=", rec.room_id.id),
                    ("day", "=", rec.day),
                    ("start_time", "<", rec.end_time),
                    ("end_time", ">", rec.start_time),
                ],
                limit=1,
            )

            if conflict:
                raise ValidationError(
                    "Room is already occupied during this time."
                )