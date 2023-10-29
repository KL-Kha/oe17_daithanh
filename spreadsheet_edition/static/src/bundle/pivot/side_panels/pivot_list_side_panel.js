/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import PivotDetailsSidePanel from "./pivot_details_side_panel";

import { Component } from "@odoo/owl";

export default class PivotSidePanel extends Component {
    selectPivot(pivotId) {
        this.env.model.dispatch("SELECT_PIVOT", { pivotId });
    }

    resetSelectedPivot() {
        this.env.model.dispatch("SELECT_PIVOT");
    }

    delete(pivotId) {
        this.env.askConfirmation(_t("Are you sure you want to delete this pivot?"), () => {
            this.env.model.dispatch("REMOVE_PIVOT", { pivotId });
            this.props.onCloseSidePanel();
        });
    }
}
PivotSidePanel.template = "spreadsheet_edition.PivotSidePanel";
PivotSidePanel.components = { PivotDetailsSidePanel };
PivotSidePanel.props = { onCloseSidePanel: Function, pivot: { type: String, optional: true } };
