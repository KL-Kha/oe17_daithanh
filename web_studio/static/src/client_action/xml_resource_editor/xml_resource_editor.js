/** @odoo-module */
import { Component, onWillStart, onWillUpdateProps, toRaw, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { ResizablePanel } from "./resizable_panel/resizable_panel";
import { CodeEditor } from "@web/core/code_editor/code_editor";
import { SelectMenu } from "@web/core/select_menu/select_menu";
import { useService } from "@web/core/utils/hooks";

class ViewSelector extends SelectMenu {
    static template = "web_studio.ViewSelector";
    static choiceItemTemplate = "web_studio.ViewSelector.ChoiceItemRecursive";
    static props = {
        ...SelectMenu.props,
        choices: {
            optional: true,
            type: Array,
            element: {
                type: Object,
                shape: {
                    value: true,
                    label: { type: String },
                    resource: { optional: true },
                },
            },
        },
    };

    getMainViews() {
        return this.state.displayedOptions.filter((opt) => opt.resource.isMainResource);
    }

    getInherited(choice) {
        const inheritedChoices = this.state.displayedOptions.filter(
            (opt) => (opt.resource.inherit_id || [])[0] === choice.resource.id
        );
        if (inheritedChoices.length) {
            inheritedChoices.forEach((opt) => (opt.resource.relatedChoice = choice.resource.id));
        }
        return inheritedChoices;
    }

    getComposedBy(choice) {
        const resource = choice.resource;
        if (!resource.called_xml_ids) {
            return [];
        }
        const composedChoices = this.state.displayedOptions.filter((opt) =>
            resource.called_xml_ids.includes(opt.resource.xml_id)
        );
        if (composedChoices.length) {
            composedChoices.forEach((opt) => (opt.resource.relatedChoice = resource.id));
        }
        return composedChoices;
    }

    // Parents of displayed options must also be visible when doing a search
    // Based on the filtered choices, they must be added from the list of choices
    sliceDisplayedOptions() {
        const childChoices = this.state.choices.filter((c) => c.resource.relatedChoice);
        childChoices.forEach((c) => this.addRelatedChoice(c.resource.relatedChoice));
        super.sliceDisplayedOptions();
    }

    addRelatedChoice(parentId) {
        if (this.state.choices.findIndex((c) => c.resource.id === parentId) === -1) {
            const parent = this.props.choices.find((c) => c.resource.id === parentId);
            if (!parent.resource.isMainResource) {
                this.addRelatedChoice(parent.resource.relatedChoice);
            }
            this.state.choices.push(parent);
        }
    }
}

export class XmlResourceEditor extends Component {
    static template = "web_studio.XmlResourceEditor";
    static components = { ResizablePanel, CodeEditor, SelectMenu: ViewSelector };
    static props = {
        onClose: { type: Function },
        onCodeChange: { type: Function, optional: true },
        onSave: { type: Function, optional: true },
        mainResourceId: { type: true },
        defaultResourceId: { type: true, optional: true },
        canSave: { type: Boolean, optional: true },
        minWidth: { type: Number, optional: true },
    };
    static defaultProps = {
        canSave: true,
        minWidth: 400,
    };

    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            resourcesOptions: [],
            currentResourceId: null,
            _codeChanges: null,
        });
        onWillStart(() => this.loadResources(this.props.mainResourceId));

        onWillUpdateProps(async (nextProps) => {
            this.state._codeChanges = null;
            if (nextProps.mainResourceId !== this.props.mainResourceId) {
                await this.loadResources(nextProps.mainResourceId);
            }
        });

        this.hiddenAlerts = useState({});
        this.alerts = [
            {
                message: _t(
                    "Editing a built-in file through this editor is not advised, as it will prevent it from being updated during future App upgrades."
                ),
            },
        ];
    }

    get minWidth() {
        return this.props.minWidth;
    }

    get arch() {
        const currentResourceId = this.state.currentResourceId;
        if (!currentResourceId) {
            return "";
        }
        return this.tempCode || this.getResourceFromId(currentResourceId).arch;
    }

    get tempCode() {
        if (!this.state.currentResourceId) {
            return "";
        }
        return this.state._codeChanges && this.state._codeChanges[this.state.currentResourceId];
    }

    set tempCode(value) {
        if (!this.state.currentResourceId) {
            return;
        }
        this.state._codeChanges = this.state._codeChanges || {};
        this.state._codeChanges[this.state.currentResourceId] = value;
    }

    getResourceFromId(resourceId) {
        const opt = this.state.resourcesOptions.find((opt) => opt.value === resourceId) || {};
        return opt.resource;
    }

    onFormat() {
        this.tempCode = window.vkbeautify.xml(this.tempCode || this.arch, 4);
    }

    hideAlert(alert) {
        this.hiddenAlerts[alert.message] = true;
    }

    shouldShowAlert(alert) {
        return !(this.hiddenAlerts[alert.message] === true);
    }

    onCloseClick() {
        this.props.onClose();
    }

    onCodeChange(code) {
        this.tempCode = code;
        if ("onCodeChange" in this.props) {
            this.props.onCodeChange({ ...toRaw(this.state._codeChanges) });
        }
    }

    onSaveClick() {
        if (!this.tempCode) {
            return;
        }
        const resource = this.getResourceFromId(this.state.currentResourceId);
        this.props.onSave({
            resourceId: resource.id,
            newCode: this.tempCode,
            oldCode: resource.oldArch,
        });
    }

    onResourceChange(resourceId) {
        this.state.currentResourceId = resourceId;
    }

    async loadResources(resourceId) {
        const resources = await this.rpc("/web_studio/get_xml_editor_resources", {
            key: resourceId,
        });

        const resourcesOptions = resources.views.map((res) => ({
            label: `${res.name} (${res.xml_id})`,
            value: res.id,
            resource: {
                ...res,
                oldArch: res.arch,
                isMainResource:
                    res.key === resourceId || res.id === resourceId || res.xml_id === resourceId,
            },
        }));

        this.state.resourcesOptions = resourcesOptions;
        if (resourcesOptions.length >= 1) {
            let defaultResource;
            if (this.props.defaultResourceId || resources.main_view_key) {
                const defaultId = this.props.defaultResourceId || resources.main_view_key;
                defaultResource = resourcesOptions.find(
                    (opt) =>
                        opt.resource.id === defaultId ||
                        opt.resource.xml_id === defaultId ||
                        opt.resource.key === defaultId
                );
            }
            defaultResource = defaultResource || resourcesOptions[0];
            this.state.currentResourceId = defaultResource.value;
        }

        return resourcesOptions;
    }
}
