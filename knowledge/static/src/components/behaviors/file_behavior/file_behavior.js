/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { AbstractBehavior } from "@knowledge/components/behaviors/abstract_behavior/abstract_behavior";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { AttachToMessageMacro, UseAsAttachmentMacro } from "@knowledge/macros/file_macros";
import { useService } from "@web/core/utils/hooks";
import { getDataURLFromFile } from "@web/core/utils/urls";
import {
    encodeDataBehaviorProps,
} from "@knowledge/js/knowledge_utils";
import {
    BehaviorToolbar,
    BehaviorToolbarButton,
} from "@knowledge/components/behaviors/behavior_toolbar/behavior_toolbar";
import { downloadFile } from "@web/core/network/download";


export class FileBehavior extends AbstractBehavior {
    static components = {
        BehaviorToolbar,
        BehaviorToolbarButton,
    };
    static props = {
        ...AbstractBehavior.props,
        fileExtension: { type: String, optional: true },
        fileImage: { type: Object, optional: true },
        fileName: { type: String, optional: true },
    };
    static template = "knowledge.FileBehavior";

    setup() {
        super.setup();
        this.actionService = useService('action');
        this.dialogService = useService('dialog');
        this.rpcService = useService('rpc');
        this.uiService = useService('ui');
        this.macrosServices = {
            action: this.actionService,
            dialog: this.dialogService,
            ui: this.uiService,
        };
        this.targetRecordInfo = this.knowledgeCommandsService.getCommandsRecordInfo();

        // ensure that the fileName and extension are saved in data-behavior-props of the anchor element
        if (!this.props.anchor.dataset.behaviorProps) {
            this.props.anchor.dataset.behaviorProps = encodeDataBehaviorProps({
                fileName: this.props.fileName,
                fileExtension: this.props.fileExtension,
            });
        }
    }

    //--------------------------------------------------------------------------
    // HANDLERS
    //--------------------------------------------------------------------------

    /**
     * Callback function called when the user clicks on the "Send as Message" button.
     * The function will execute a macro that will open the last opened form view,
     * compose a new message and attach the associated file to it.
     * @param {Event} ev
     */
    async onClickAttachToMessage(ev) {
        const fileLink = this.props.anchor.querySelector('.o_knowledge_file_image > a');
        if (!fileLink || !fileLink.hasAttribute('href')) {
            return;
        }
        const dataTransfer = new DataTransfer();
        const href = fileLink.getAttribute('href');
        try {
            const response = await window.fetch(href);
            const blob = await response.blob();
            const file = new File([blob], fileLink.getAttribute('title'), {
                type: blob.type
            });
            /**
             * dataTransfer will be used to mimic a drag and drop of
             * the file in the target record chatter.
             * @see KnowledgeMacro
             */
            dataTransfer.items.add(file);
        } catch {
            return;
        }
        const macro = new AttachToMessageMacro({
            targetXmlDoc: this.targetRecordInfo.xmlDoc,
            breadcrumbs: this.targetRecordInfo.breadcrumbs,
            data: {
                dataTransfer: dataTransfer,
            },
            services: this.macrosServices,
        });
        macro.start();
    }

    /**
     * Callback function called when the user clicks on the "Download" button.
     * The function will simply open a link that will trigger the download of
     * the associated file. If the url is not valid, the function will display
     * an error message.
     * @param {Event} ev
     */
    async onClickDownload(ev) {
        const fileLink = this.props.anchor.querySelector('.o_knowledge_file_image > a');
        if (!fileLink || !fileLink.hasAttribute('href')) {
            return;
        }
        const title = fileLink.getAttribute('title');
        const href = fileLink.getAttribute('href');
        try {
            await downloadFile(href);
        } catch {
            this.dialogService.add(AlertDialog, {
                body: _t('Oops, the file %s could not be found. Please replace this file box by a new one to re-upload the file.', title),
                title: _t('Missing File'),
                confirm: () => {},
                confirmLabel: _t('Ok'),
            });
        }
    }

    /**
     * Callback function called when the user clicks on the "Use As Attachment" button.
     * The function will execute a macro that will open the last opened form view
     * and add the associated file to the attachments of the chatter.
     * @param {Event} ev
     */
    async onClickUseAsAttachment(ev) {
        const fileLink = this.props.anchor.querySelector('.o_knowledge_file_image > a');
        if (!fileLink || !fileLink.hasAttribute('href')) {
            return;
        }
        const href = fileLink.getAttribute('href');
        let attachment;
        try {
            const response = await window.fetch(href);
            const blob = await response.blob();
            const dataURL = await getDataURLFromFile(blob);
            attachment = await this.rpcService('/web_editor/attachment/add_data', {
                name: fileLink.getAttribute('title'),
                data: dataURL.split(',')[1],
                is_image: false,
                res_id: this.targetRecordInfo.resId,
                res_model: this.targetRecordInfo.resModel,
            });
        } catch {
            return;
        }
        if (!attachment) {
            return;
        }
        const macro = new UseAsAttachmentMacro({
            targetXmlDoc: this.targetRecordInfo.xmlDoc,
            breadcrumbs: this.targetRecordInfo.breadcrumbs,
            data: null,
            services: this.macrosServices,
        });
        macro.start();
    }
}
