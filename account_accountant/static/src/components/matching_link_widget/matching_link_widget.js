/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

class MatchingLink extends Component {
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
    }

    async reconcile() {
        this.action.doAction("account_accountant.action_move_line_posted_unreconciled", {
            additionalContext: {
                search_default_partner_id: this.props.record.data.partner_id[0],
                search_default_account_id: this.props.record.data.account_id[0],
            },
        });
    }

    async viewMatch() {
        const action = await this.orm.call("account.move.line", "open_reconcile_view", [this.props.record.resId], {});
        this.action.doAction(action, { additionalContext: { is_matched_view: true }});
    }
}

MatchingLink.template = "account_accountant.MatchingLink";
registry.category("fields").add("matching_link_widget", {
    component: MatchingLink,
});
