from odoo import models, fields, api

class SchoolScheduleSession(models.Model):

    _name = "school.schedule.session"
    _description = "School Schedule Session"
    _order = "start_datetime"

    _rec_name = "course_id"
    schedule_id = fields.Many2one("school.schedule",string="Schedule",required=True,ondelete="cascade",index=True,)
    color = fields.Integer(string="Color Index",compute="_compute_color",store=True,)
    schedule_line_id = fields.Many2one("school.schedule.line",string="Schedule Line",required=True,ondelete="cascade",index=True,)
    start_datetime = fields.Datetime(string="Start Time",required=True,)
    end_datetime = fields.Datetime(string="End Time",required=True,)
    start_time = fields.Float(related="schedule_line_id.start_time",readonly=True,)
    end_time = fields.Float(related="schedule_line_id.end_time",readonly=True,)
    course_id = fields.Many2one(related="schedule_line_id.course_id",string="Course",store=True,readonly=True,)
    teacher_id = fields.Many2one(related="schedule_line_id.teacher_id",string="Teacher",store=True,readonly=True,)
    room_id = fields.Many2one(related="schedule_line_id.room_id",string="Room",store=True,readonly=True,)
    day = fields.Selection(related="schedule_line_id.day",string="Day",store=True,readonly=True,)
    curriculum_ids = fields.Many2one("school.curriculum",string="Curriculum",store=True,readonly=True,)
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