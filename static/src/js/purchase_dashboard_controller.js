/** @odoo-module **/

console.log("Purchase Dashboard Controller JS Loaded");


import { ListController } from "@web/views/list/list_controller";
import { onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { renderToElement } from "@web/core/utils/render";


export class PurchaseDashboardController extends ListController {


    setup() {

        super.setup();


        console.log(
            "Purchase Dashboard Controller Started"
        );


        this.orm = useService("orm");


        onMounted(async () => {


            console.log(
                "Purchase Dashboard Mounted"
            );


            try {


                const data = await this.orm.call(
                    "purchase.order",
                    "get_dashboard_data",
                    []
                );


                console.log(
                    "Dashboard Data:",
                    data
                );



                const dashboard =
                    renderToElement(
                        "school_management_system.PurchaseDashboard",
                        {
                            purchaseData: data,
                        }
                    );



                if (dashboard) {


                    const list =
                        this.el.querySelector(
                            ".o_list_view"
                        );


                    if (list) {

                        list.prepend(
                            dashboard
                        );

                    } else {

                        this.el.prepend(
                            dashboard
                        );

                    }


                }


            } catch (error) {


                console.error(
                    "Purchase Dashboard Error:",
                    error
                );


            }


        });


    }


}