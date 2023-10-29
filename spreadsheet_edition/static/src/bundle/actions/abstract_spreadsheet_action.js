/** @odoo-module **/
import {
    onMounted,
    onWillStart,
    useState,
    Component,
    useSubEnv,
    onWillUnmount,
    status,
} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { useSetupAction } from "@web/webclient/actions/action_hook";
import { _t } from "@web/core/l10n/translation";
import { downloadFile } from "@web/core/network/download";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

import { UNTITLED_SPREADSHEET_NAME } from "@spreadsheet/helpers/constants";
import * as spreadsheet from "@odoo/o-spreadsheet";
import { migrate } from "@spreadsheet/o_spreadsheet/migration";
import { DataSources } from "@spreadsheet/data_sources/data_sources";
import { initCallbackRegistry } from "@spreadsheet/o_spreadsheet/init_callbacks";

import { RecordFileStore } from "../image/record_file_store";

const { createCurrencyFormat } = spreadsheet.helpers;
const uuidGenerator = new spreadsheet.helpers.UuidGenerator();

const { Model } = spreadsheet;
/**
 * @typedef SpreadsheetRecord
 * @property {number} id
 * @property {string} name
 * @property {string} data
 * @property {Object[]} revisions
 * @property {boolean} snapshot_requested
 * @property {Boolean} isReadonly
 */

export class AbstractSpreadsheetAction extends Component {
    setup() {
        if (!this.props.action.params) {
            // the action is coming from a this.trigger("do-action", ... ) of owl (not wowl and not legacy)
            this.params = this.props.action.context;
        } else {
            // the action is coming from wowl
            this.params = this.props.action.params;
        }
        this.isEmptySpreadsheet = this.params.is_new_spreadsheet || false;
        this.resId =
            this.params.spreadsheet_id ||
            this.params.active_id || // backward compatibility. spreadsheet_id used to be active_id
            (this.props.state && this.props.state.resId); // used when going back to a spreadsheet via breadcrumb
        this.shareId = this.params.share_id || this.props.state?.shareId;
        this.accessToken = this.params.access_token || this.props.state?.accessToken;
        this.router = useService("router");
        this.actionService = useService("action");
        this.notifications = useService("notification");
        this.orm = useService("orm");
        this.http = useService("http");
        this.user = useService("user");
        this.ui = useService("ui");
        this.fileStore = new RecordFileStore(this.resModel, this.resId, this.http, this.orm);
        const spreadsheetService = useService("spreadsheet_collaborative");
        this.transportService = spreadsheetService.makeCollaborativeChannel(
            this.resModel,
            this.resId,
            this.shareId,
            this.accessToken
        );
        useSetupAction({
            beforeLeave: this._leaveSpreadsheet.bind(this),
            beforeUnload: this._leaveSpreadsheet.bind(this),
            getLocalState: () => {
                return {
                    resId: this.resId,
                    shareId: this.shareId,
                    accessToken: this.accessToken,
                };
            },
        });
        useSubEnv({
            download: this.download.bind(this),
            downloadAsJson: this.downloadAsJson.bind(this),
        });
        this.state = useState({
            spreadsheetName: UNTITLED_SPREADSHEET_NAME,
        });

        onWillStart(async () => {
            await this.fetchData();
            this.createModel();
            await this.execInitCallbacks();
        });
        onMounted(() => {
            this.router.pushState({
                spreadsheet_id: this.resId,
                access_token: this.accessToken,
                share_id: this.shareId,
            });
            this.env.config.setDisplayName(this.state.spreadsheetName);
            this.model.on("unexpected-revision-id", this, this.onUnexpectedRevisionId.bind(this));
        });
        onWillUnmount(() => {
            this.model.off("unexpected-revision-id", this);
        });
    }

    get controlPanelProps() {
        return {
            model: this.model,
            isReadonly: this.isReadonly,
            onSpreadsheetNameChanged: this._onSpreadSheetNameChanged.bind(this),
            spreadsheetName: this.state.spreadsheetName,
            userLocale: this.record.user_locale,
        };
    }

    async fetchData() {
        // if we are returning to the spreadsheet via the breadcrumb, we don't want
        // to do all the "creation" options of the actions
        if (!this.props.state) {
            await Promise.all([this._setupPreProcessingCallbacks()]);
        }
        if (status(this) === "destroyed") {
            return;
        }
        const [record] = await Promise.all([this._fetchData()]);
        this._initializeWith(record);
    }

    createModel() {
        const dataSources = new DataSources(this.env);
        dataSources.addEventListener("data-source-updated", () => {
            const sheetId = this.model.getters.getActiveSheetId();
            this.model.dispatch("EVALUATE_CELLS", { sheetId });
        });
        const defaultCurrency = this.record.default_currency;
        const defaultCurrencyFormat = defaultCurrency
            ? createCurrencyFormat({
                  symbol: defaultCurrency.symbol,
                  position: defaultCurrency.position,
                  decimalPlaces: defaultCurrency.decimalPlaces,
              })
            : undefined;
        this.model = new Model(
            migrate(this.spreadsheetData),
            {
                custom: { env: this.env, orm: this.orm, dataSources },
                external: {
                    fileStore: this.fileStore,
                    loadCurrencies: this.loadCurrencies.bind(this),
                    loadLocales: this.loadLocales.bind(this),
                },
                defaultCurrencyFormat,
                transportService: this.transportService,
                client: {
                    id: uuidGenerator.uuidv4(),
                    name: this.user.name,
                    userId: this.user.userId,
                },
                mode: this.isReadonly ? "readonly" : "normal",
                snapshotRequested: this.snapshotRequested,
            },
            this.stateUpdateMessages
        );
        if (this.env.debug) {
            // eslint-disable-next-line no-import-assign
            spreadsheet.__DEBUG__ = spreadsheet.__DEBUG__ || {};
            spreadsheet.__DEBUG__.model = this.model;
        }
    }

    async execInitCallbacks() {
        if (this.asyncInitCallback) {
            await this.asyncInitCallback(this.model);
        }
        if (this.initCallback) {
            this.initCallback(this.model);
        }
    }

    async _setupPreProcessingCallbacks() {
        if (this.params.preProcessingAction) {
            const initCallbackGenerator = initCallbackRegistry
                .get(this.params.preProcessingAction)
                .bind(this);
            this.initCallback = await initCallbackGenerator(this.params.preProcessingActionData);
        }
        if (this.params.preProcessingAsyncAction) {
            const initCallbackGenerator = initCallbackRegistry
                .get(this.params.preProcessingAsyncAction)
                .bind(this);
            this.asyncInitCallback = await initCallbackGenerator(
                this.params.preProcessingAsyncActionData
            );
        }
    }

    /**
     * @protected
     * @abstract
     * @param {SpreadsheetRecord} record
     */
    _initializeWith(record) {
        this.state.spreadsheetName = record.name;
        this.spreadsheetData = record.data;
        this.stateUpdateMessages = record.revisions;
        this.snapshotRequested = record.snapshot_requested;
        this.isReadonly = record.isReadonly;
        this.record = record;
    }

    /**
     * Make a copy of the current document
     * @protected
     */
    async makeCopy() {
        const { data, thumbnail } = this.getSaveData();
        const defaultValues = {
            spreadsheet_data: JSON.stringify(data),
            spreadsheet_snapshot: false,
            spreadsheet_revision_ids: [],
            thumbnail,
        };
        const id = await this.orm.call(this.resModel, "copy", [this.resId], {
            default: defaultValues,
        });
        this._openSpreadsheet(id);
    }

    /**
     * @private
     */
    async _leaveSpreadsheet() {
        this.model.leaveSession();
        this.model.off("update", this);
        if (!this.isReadonly) {
            return this.onSpreadsheetLeft(this.getSaveData());
        }
    }

    async _onSpreadSheetNameChanged(detail) {
        const { name } = detail;
        this.state.spreadsheetName = name;
        this.env.config.setDisplayName(this.state.spreadsheetName);
    }

    async createNewSpreadsheet() {
        throw new Error("not implemented by children");
    }

    async onSpreadsheetLeft({ thumbnail, data }) {
        if (this.accessToken) {
            return;
        }
        await this.orm.write(
            this.resModel,
            [this.resId],
            this.onSpreadsheetLeftUpdateVals({ thumbnail, data })
        );
    }

    onSpreadsheetLeftUpdateVals({ data, thumbnail }) {
        return { thumbnail };
    }

    /**
     * @returns {Promise<SpreadsheetRecord>}
     */
    async _fetchData() {
        return this.orm.call(this.resModel, "join_spreadsheet_session", [
            this.resId,
            this.shareId,
            this.accessToken,
        ]);
    }

    /**
     * @protected
     */
    _notifyCreation() {
        this.notifications.add(this.notificationMessage, {
            type: "info",
            sticky: false,
        });
    }

    /**
     * Open a spreadsheet
     * @private
     */
    _openSpreadsheet(spreadsheetId) {
        this._notifyCreation();
        this.actionService.doAction(
            {
                type: "ir.actions.client",
                tag: this.props.action.tag,
                params: { spreadsheet_id: spreadsheetId },
            },
            { clear_breadcrumbs: true }
        );
    }

    /**
     * Reload the spreadsheet if an unexpected revision id is triggered.
     */
    onUnexpectedRevisionId() {
        this.actionService.doAction("reload_context");
    }

    /**
     * Load currencies from database
     */
    async loadCurrencies() {
        const odooCurrencies = await this.orm.searchRead(
            "res.currency", // model
            [], // domain
            ["symbol", "full_name", "position", "name", "decimal_places"], // fields
            {
                // opts
                order: "active DESC, full_name ASC",
                context: { active_test: false },
            }
        );
        return odooCurrencies.map((currency) => {
            return {
                code: currency.name,
                symbol: currency.symbol,
                position: currency.position || "after",
                name: currency.full_name || _t("Currency"),
                decimalPlaces: currency.decimal_places || 2,
            };
        });
    }

    async loadLocales() {
        return this.orm.call("res.lang", "get_locales_for_spreadsheet", []);
    }

    /**
     * Downloads the spreadsheet in xlsx format
     */
    async download() {
        this.ui.block();
        try {
            await this.actionService.doAction({
                type: "ir.actions.client",
                tag: "action_download_spreadsheet",
                params: {
                    name: this.state.spreadsheetName,
                    xlsxData: this.model.exportXLSX(),
                },
            });
        } finally {
            this.ui.unblock();
        }
    }

    /**
     * Downloads the spreadsheet in json format
     */
    async downloadAsJson() {
        this.ui.block();
        try {
            const data = JSON.stringify(this.model.exportData());
            await downloadFile(
                data,
                `${this.state.spreadsheetName}.osheet.json`,
                "application/json"
            );
        } finally {
            this.ui.unblock();
        }
    }

    /**
     * Retrieve the spreadsheet_data and the thumbnail associated to the
     * current spreadsheet
     */
    getSaveData() {
        const data = this.model.exportData();
        return {
            data,
            revisionId: data.revisionId,
            thumbnail: this.getThumbnail(),
        };
    }

    getThumbnail() {
        const dimensions = spreadsheet.SPREADSHEET_DIMENSIONS;
        const canvas = document.querySelector(".o-grid canvas:not(.o-figure-canvas)");
        const canvasResizer = document.createElement("canvas");
        const size = 750;
        canvasResizer.width = size;
        canvasResizer.height = size;
        const canvasCtx = canvasResizer.getContext("2d");
        // use only 25 first rows in thumbnail
        const sourceSize = Math.min(
            25 * dimensions.DEFAULT_CELL_HEIGHT,
            canvas.width,
            canvas.height
        );
        canvasCtx.drawImage(
            canvas,
            dimensions.HEADER_WIDTH - 1,
            dimensions.HEADER_HEIGHT - 1,
            sourceSize,
            sourceSize,
            0,
            0,
            size,
            size
        );
        return canvasResizer.toDataURL().replace("data:image/png;base64,", "");
    }
}
AbstractSpreadsheetAction.props = { ...standardActionServiceProps };
