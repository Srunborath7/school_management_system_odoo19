from odoo import models, fields, api


class SchoolSchedule(models.Model):
    _name = "school.schedule"
    _description = "School Weekly Schedule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    name = fields.Char(
        string="Schedule Name",
        default="New",
        required=True,
        tracking=True,
    )

    curriculum_id = fields.Many2one(
        "school.curriculum",
        string="Curriculum",
        required=True,
        tracking=True,
    )

    class_group_id = fields.Many2one(
        "school.class.group",
        string="Class",
        required=True,
        tracking=True,
    )

    line_ids = fields.One2many(
        "school.schedule.line",
        "schedule_id",
        string="Timetable",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("done", "Done"),
        ],
        default="draft",
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("school.schedule")
                    or "New"
                )
        return super().create(vals_list)

    @api.onchange("curriculum_id")
    def _onchange_curriculum(self):
        if not self.curriculum_id:
            self.line_ids = [(5, 0, 0)]
            return

        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
        ]

        lines = []

        for index, course in enumerate(self.curriculum_id.course_ids):
            lines.append(
                (
                    0,
                    0,
                    {
                        "course_id": course.id,
                        "day": days[index % len(days)],
                    },
                )
            )

        self.line_ids = [(5, 0, 0)] + lines

    def action_set_draft(self):
        self.state = "draft"

    def action_activate(self):
        self.state = "active"

    def action_done(self):
        self.state = "done"