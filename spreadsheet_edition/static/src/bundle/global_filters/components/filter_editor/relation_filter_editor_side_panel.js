/** @odoo-module */

import { RecordsSelector } from "@spreadsheet/global_filters/components/records_selector/records_selector";
import { ModelSelector } from "@web/core/model_selector/model_selector";
import AbstractFilterEditorSidePanel from "./filter_editor_side_panel";
import FilterEditorFieldMatching from "./filter_editor_field_matching";

import { useState } from "@odoo/owl";

/**
 * @typedef {import("@spreadsheet/data_sources/metadata_repository").Field} Field
 * @typedef {import("@spreadsheet/global_filters/plugins/global_filters_core_plugin").GlobalFilter} GlobalFilter

 *
 * @typedef RelationState
 * @property {Array} defaultValue
 * @property {Array} displayNames
 * @property {{label?: string, technical?: string}} relatedModel
 */

/**
 * This is the side panel to define/edit a global filter of type "relation".
 */
export default class RelationFilterEditorSidePanel extends AbstractFilterEditorSidePanel {
    setup() {
        super.setup();

        this.type = "relation";
        /** @type {RelationState} */
        this.relationState = useState({
            defaultValue: [],
            displayNames: [],
            relatedModel: {
                label: undefined,
                technical: undefined,
            },
        });

        this.ALLOWED_FIELD_TYPES = ["many2one", "many2many", "one2many"];
    }

    get missingModel() {
        return this.genericState.saved && !this.relationState.relatedModel.technical;
    }

    get missingRequired() {
        return super.missingRequired || this.missingModel;
    }

    /**
     * @override
     */
    get filterValues() {
        const values = super.filterValues;
        return {
            ...values,
            defaultValue: this.relationState.defaultValue,
            defaultValueDisplayNames: this.relationState.displayNames,
            modelName: this.relationState.relatedModel.technical,
        };
    }

    shouldDisplayFieldMatching() {
        return this.fieldMatchings.length && this.relationState.relatedModel.technical;
    }

    /**
     * List of model names of all related models of all pivots
     * @returns {Array<string>}
     */
    get relatedModels() {
        const all = this.fieldMatchings.map((object) => Object.values(object.fields()));
        return [
            ...new Set(
                all
                    .flat()
                    .filter((field) => field.relation)
                    .map((field) => field.relation)
            ),
        ];
    }

    /**
     * @override
     * @param {GlobalFilter} globalFilter
     */
    loadSpecificFilterValues(globalFilter) {
        this.relationState.defaultValue = globalFilter.defaultValue;
        this.relationState.relatedModel.technical = globalFilter.modelName;
    }

    async onWillStart() {
        await super.onWillStart();
        await this.fetchModelFromName();
    }

    /**
     * Get the first field which could be a relation of the current related
     * model
     *
     * @param {Object.<string, Field>} fields Fields to look in
     * @returns {field|undefined}
     */
    _findRelation(fields) {
        const field = Object.values(fields).find(
            (field) =>
                field.searchable && field.relation === this.relationState.relatedModel.technical
        );
        return field;
    }

    async onModelSelected({ technical, label }) {
        if (!this.genericState.label) {
            this.genericState.label = label;
        }
        if (this.relationState.relatedModel.technical !== technical) {
            this.relationState.defaultValue = [];
        }
        this.relationState.relatedModel.technical = technical;
        this.relationState.relatedModel.label = label;

        for (const [index, object] of Object.entries(this.fieldMatchings)) {
            const field = this._findRelation(object.fields());
            this.onSelectedField(index, field ? field.name : undefined, field);
        }
    }

    async fetchModelFromName() {
        if (!this.relationState.relatedModel.technical) {
            return;
        }
        const result = await this.orm.call("ir.model", "display_name_for", [
            [this.relationState.relatedModel.technical],
        ]);
        this.relationState.relatedModel.label = result[0] && result[0].display_name;
        if (!this.genericState.label) {
            this.genericState.label = this.relationState.relatedModel.label;
        }
    }

    /**
     * @param {Field} field
     * @returns {boolean}
     */
    isFieldValid(field) {
        const relatedModel = this.relationState.relatedModel.technical;
        return super.isFieldValid(field) && (!relatedModel || field.relation === relatedModel);
    }

    /**
     * @override
     * @param {Field} field
     * @returns {boolean}
     */
    matchingRelation(field) {
        return field.relation === this.relationState.relatedModel.technical;
    }

    /**
     * @param {{id: number, display_name: string}[]} value
     */
    onValuesSelected(value) {
        this.relationState.defaultValue = value.map((record) => record.id);
        this.relationState.displayNames = value.map((record) => record.display_name);
    }
}

RelationFilterEditorSidePanel.template = "spreadsheet_edition.RelationFilterEditorSidePanel";
RelationFilterEditorSidePanel.components = {
    ...AbstractFilterEditorSidePanel.components,
    ModelSelector,
    RecordsSelector,
    FilterEditorFieldMatching,
};
