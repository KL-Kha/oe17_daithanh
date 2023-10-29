/** @odoo-module */

import { MrpQualityCheckConfirmationDialog } from "./mrp_quality_check_confirmation_dialog";

export class MrpRegisterProductionDialog extends MrpQualityCheckConfirmationDialog {
    static template = "mrp_workorder.MrpRegisterProductionDialog";

    setup() {
        super.setup();
        const { product_qty, product_tracking } = this.recordData;
        this.quantityToProduce = product_tracking === "serial" ? 1 : product_qty;
    }

    async doActionAndClose(action, saveModel = true, reloadChecks = false) {
        if (saveModel) {
            await this.props.record.save();
            // Calls `set_qty_producing` because the onchange won't be triggered.
            await this.props.record.model.orm.call("mrp.production", "set_qty_producing", this.props.record.resIds);
        }
        await this.props.reload();
        this.props.close();
    }

    get qtyDoneInfo() {
        return {
            name: "qty_producing",
            record: this.props.record,
        };
    }

    get lotInfo() {
        return {
            name: "lot_producing_id",
            record: this.props.record,
            context: JSON.stringify({
                default_product_id: this.recordData.product_id[0],
                default_company_id: this.recordData.company_id[0],
            }),
            domain: [
                "&",
                ["product_id", "=", this.recordData.product_id[0]],
                "|",
                ["company_id", "=", false],
                ["company_id", "=", this.recordData.company_id[0]],
            ],
        };
    }
}
