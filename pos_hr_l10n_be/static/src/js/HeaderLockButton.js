/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
    import HeaderLockButton from "point_of_sale.HeaderLockButton";
    import Registries from "point_of_sale.Registries";

    const PosHrHeaderLockButton = HeaderLockButton =>
        class extends HeaderLockButton {
            async showLoginScreen() {
                const insz = this.env.pos.get_cashier().insz_or_bis_number;
                if (this.env.pos.config.blackbox_pos_production_id && !insz) {
                    await this.showPopup('ErrorPopup', {
                        title: _t('Fiscal Data Module error'),
                        body: _t('INSZ or BIS number not set for current cashier.'),
                    });
                } else if (
                    this.env.pos.config.blackbox_pos_production_id &&
                    this.env.pos.check_if_user_clocked()
                ) {
                    await this.showPopup('ErrorPopup', {
                        title: _t('POS error'),
                        body: _t('You need to clock out before closing the POS.'),
                    });
                } else {
                    await super.showLoginScreen();
                }
            }
        };

    Registries.Component.extend(HeaderLockButton, PosHrHeaderLockButton);

    export default HeaderLockButton;
