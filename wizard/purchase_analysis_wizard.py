from odoo import fields, models

class PurchaseAnalysisWizard(models.TransientModel):
    _name = "purchase.analysis.wizard"
    _description = "Purchase Analysis Report"


    date_from = fields.Date(
        string="Date From"
    )

    date_to = fields.Date(
        string="Date To"
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Vendor"
    )

    def action_print_xlsx(self):
        self.ensure_one()
        return self.env.ref(
            "school_management_system.purchase_analysis_xlsx"
        ).report_action(self)