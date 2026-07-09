from odoo import models


class PurchaseAnalysisXlsx(models.AbstractModel):
    _name = "report.school_management.purchase_analysis_xlsx"
    _description = "Purchase Analysis XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(
            self,
            workbook,
            data,
            records):


        sheet = workbook.add_worksheet(
            "Purchase Analysis"
        )


        header = workbook.add_format({
            "bold": True,
            "bg_color": "#DDDDDD"
        })


        sheet.write(
            0,
            0,
            "Vendor",
            header
        )

        sheet.write(
            0,
            1,
            "Product",
            header
        )

        sheet.write(
            0,
            2,
            "Quantity",
            header
        )

        sheet.write(
            0,
            3,
            "Total",
            header
        )


        row = 1


        for order in records:


            for line in order.order_line:


                sheet.write(
                    row,
                    0,
                    order.partner_id.name or ""
                )


                sheet.write(
                    row,
                    1,
                    line.product_id.name or ""
                )


                sheet.write(
                    row,
                    2,
                    line.product_qty
                )


                sheet.write(
                    row,
                    3,
                    line.price_subtotal
                )


                row += 1