/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useBus, useService } from "@web/core/utils/hooks";
import { cleanDomFromBootstrap } from "@web/legacy/utils";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { computeAppsAndMenuItems, reorderApps } from "@web/webclient/menus/menu_helpers";
import { AppCreator } from "./app_creator/app_creator";
import { Editor } from "./editor/editor";
import { StudioNavbar } from "./navbar/navbar";
import { StudioHomeMenu } from "./studio_home_menu/studio_home_menu";

import { Component, onWillStart, onMounted, onPatched, onWillUnmount } from "@odoo/owl";

export class StudioClientAction extends Component {
    setup() {
        const user = useService("user");
        const homemenuConfig = JSON.parse(user.settings?.homemenu_config || "null");
        this.studio = useService("studio");
        useBus(this.studio.bus, "UPDATE", () => {
            this.render();
            cleanDomFromBootstrap();
        });

        this.menus = useService("menu");
        this.actionService = useService("action");
        let apps = computeAppsAndMenuItems(this.menus.getMenuAsTree("root")).apps;
        if (homemenuConfig) {
            reorderApps(apps, homemenuConfig);
        }
        this.homeMenuProps = {
            apps: apps,
        };
        useBus(this.env.bus, "MENUS:APP-CHANGED", () => {
            apps = computeAppsAndMenuItems(this.menus.getMenuAsTree("root")).apps;
            if (homemenuConfig) {
                reorderApps(apps, homemenuConfig);
            }
            this.homeMenuProps = {
                apps: apps,
            };
            this.render();
        });

        onWillStart(this.onWillStart);
        onMounted(this.onMounted);
        onPatched(this.onPatched);
        onWillUnmount(this.onWillUnmount);
    }

    onWillStart() {
        return this.studio.ready;
    }

    onMounted() {
        this.studio.pushState();
        document.body.classList.add("o_in_studio"); // FIXME ?
    }

    onPatched() {
        this.studio.pushState();
    }

    onWillUnmount() {
        document.body.classList.remove("o_in_studio");
    }

    async onNewAppCreated({ action_id, menu_id }) {
        await this.menus.reload();
        this.menus.setCurrentMenu(menu_id);
        const action = await this.actionService.loadAction(action_id);

        let initViewType = "form";
        if (!action.views.some((vTuple) => vTuple[1] === initViewType)) {
            initViewType = action.views[0][1];
        }

        this.studio.setParams({
            mode: this.studio.MODES.EDITOR,
            editorTab: "views",
            action,
            viewType: initViewType,
        });
    }
}
StudioClientAction.template = "web_studio.StudioClientAction";
StudioClientAction.props = { ...standardActionServiceProps };
StudioClientAction.components = {
    StudioNavbar,
    StudioHomeMenu,
    Editor,
    AppCreator,
};
StudioClientAction.target = "fullscreen";

registry.category("lazy_components").add("StudioClientAction", StudioClientAction);
// force: true to bypass the studio lazy loading action next time and just use this one directly
registry.category("actions").add("studio", StudioClientAction, { force: true });
