/** @odoo-module **/


console.log(
    "Purchase Dashboard View JS Loaded"
);



import { registry } from "@web/core/registry";

import { listView } from "@web/views/list/list_view";

import {
    PurchaseDashboardController
}
from "./purchase_dashboard_controller";



export const PurchaseDashboardListView = {


    ...listView,


    Controller:
        PurchaseDashboardController,


};



registry.category("views").add(
        "purchase_approval_dashboard_list",
        PurchaseDashboardListView
    );
console.log(
    "Purchase Dashboard View Registered"
);