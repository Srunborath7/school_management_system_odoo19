from odoo import models, fields, api
from datetime import datetime, timedelta
import pytz

from odoo.orm.decorators import readonly


class SchoolSchedule(models.Model):

    _name = "school.schedule"
    _description = "School Schedule"
    _inherit = ["mail.thread","mail.activity.mixin"]

    name = fields.Char(string="Schedule Name",default="New", readonly=True,required=True,tracking=True,)
    curriculum_id = fields.Many2one("school.curriculum",string="Curriculum",required=True,tracking=True,)
    academic_year_id = fields.Many2one("school.academic.year",string="Academic Year",related="curriculum_id.academic_year_id",store=True,readonly=True,tracking=True,)
    start_date = fields.Date(string="Start Date",related="academic_year_id.start_date",store=True,readonly=True,)
    end_date = fields.Date(string="End Date",related="academic_year_id.end_date",store=True,readonly=True,)
    class_group_id = fields.Many2one("school.class.group",string="Class Group",required=True,tracking=True,)
    line_ids = fields.One2many("school.schedule.line","schedule_id",string="Timetable", )
    session_ids = fields.One2many("school.schedule.session","schedule_id",string="Sessions",)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("done", "Done"),
        ],default="draft",tracking=True,)
    student_ids = fields.Many2many("school.student.registry", related="curriculum_id.student_ids", string="Students", readonly=True,)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"]
                    .next_by_code("school.schedule") or "New"
                )

        return super().create(vals_list)

    @api.onchange("curriculum_id")
    def _onchange_curriculum(self):
        if not self.curriculum_id:
            self.line_ids = [
                (5, 0, 0)
            ]

            return
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
        ]
        lines = []
        for index, course in enumerate(
            self.curriculum_id.course_ids
        ):lines.append((0,0,{"course_id": course.id,"day": days[index % len(days)],}))
        self.line_ids = [
            (5, 0, 0)
        ] + lines

    # Generate all classes from academic year
    def action_generate_sessions(self):
        Session = self.env["school.schedule.session"]

        day_mapping = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        tz = pytz.timezone(self.env.user.tz or "UTC")

        for schedule in self:

            if not schedule.start_date or not schedule.end_date:
                continue

            start_date = fields.Date.to_date(schedule.start_date)
            end_date = fields.Date.to_date(schedule.end_date)

            # Delete old sessions
            Session.search([
                ("schedule_id", "=", schedule.id)
            ]).unlink()

            for line in schedule.line_ids:

                if not line.day:
                    continue

                current_date = start_date
                target_day = day_mapping[line.day]

                while current_date <= end_date:

                    if current_date.weekday() == target_day:
                        start_hour = int(line.start_time)
                        start_minute = int(round((line.start_time % 1) * 60))

                        end_hour = int(line.end_time)
                        end_minute = int(round((line.end_time % 1) * 60))

                        # Local datetime
                        local_start = tz.localize(
                            datetime(
                                current_date.year,
                                current_date.month,
                                current_date.day,
                                start_hour,
                                start_minute,
                            )
                        )

                        local_end = tz.localize(
                            datetime(
                                current_date.year,
                                current_date.month,
                                current_date.day,
                                end_hour,
                                end_minute,
                            )
                        )

                        # Convert to UTC for Odoo
                        start_dt = local_start.astimezone(pytz.UTC).replace(tzinfo=None)
                        end_dt = local_end.astimezone(pytz.UTC).replace(tzinfo=None)

                        Session.create({
                            "schedule_id": schedule.id,
                            "schedule_line_id": line.id,
                            "start_datetime": start_dt,
                            "end_datetime": end_dt,
                        })

                    current_date += timedelta(days=1)

    def action_activate(self):
        self.state = "active"

    def action_done(self):
        self.state = "done"

    def action_draft(self):
        self.state = "draft"