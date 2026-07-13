from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class SchoolScheduleLine(models.Model):
    _name = "school.schedule.line"
    _description = "Schedule Line"

    _order = "day,start_time"
    schedule_id = fields.Many2one("school.schedule", string="Schedule", required=True, ondelete="cascade", )
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
        required=True,
    )
    course_id = fields.Many2one("school.course", string="Course", required=True, )
    teacher_id = fields.Many2one("school.teacher", string="Teacher", required=True, )
    room_id = fields.Many2one("school.room", string="Room", required=True, )
    start_time = fields.Float(string="Start Time", required=True, )
    end_time = fields.Float(string="End Time", required=True, )
    duration = fields.Float(compute="_compute_duration", store=True, )
    start_datetime = fields.Datetime(compute="_compute_datetime", store=True, )
    end_datetime = fields.Datetime(compute="_compute_datetime", store=True, )

    @api.depends("start_time", "end_time")
    def _compute_duration(self):
        for rec in self:
            rec.duration = (rec.end_time - rec.start_time)

    @api.depends("schedule_id.curriculum_id.academic_year_id.start_date", "day", "start_time", "end_time", )
    def _compute_datetime(self):
        day_mapping = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        for rec in self:
            rec.start_datetime = False
            rec.end_datetime = False
            if not rec.schedule_id:
                continue
            academic_year = (rec.schedule_id.curriculum_id.academic_year_id)
            if not academic_year:
                continue
            if not academic_year.start_date:
                continue
            start_date = fields.Date.to_date(academic_year.start_date)

            # Find correct weekday
            target_day = day_mapping.get(rec.day)
            if target_day is None:
                continue
            days_difference = (target_day - start_date.weekday()) % 7
            class_date = (start_date + timedelta(days=days_difference))
            start_hour = int(rec.start_time)
            start_minute = int((rec.start_time % 1) * 60)
            end_hour = int(rec.end_time)

            end_minute = int(
                (rec.end_time % 1) * 60
            )

            rec.start_datetime = datetime(
                class_date.year,
                class_date.month,
                class_date.day,
                start_hour,
                start_minute,
            )

            rec.end_datetime = datetime(
                class_date.year,
                class_date.month,
                class_date.day,
                end_hour,
                end_minute,
            )

    @api.constrains("start_time","end_time")
    def _check_time(self):
        for rec in self:
            if rec.end_time <= rec.start_time:
                raise ValidationError(
                    "End time must be greater than start time."
                )
