/** @odoo-module **/

import { KnowledgeSidebarRow } from '@knowledge/components/sidebar/sidebar_row';

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { loadBundle } from "@web/core/assets";

patch(KnowledgeSidebarRow.prototype, {
    async exportToPdf() { 
        var action = await this.orm.call(this.props.record.resModel, 'get_pdf', [this.props.article.id], {});
        
        var linkElements = document.head.getElementsByTagName('link');
        
        var cssFiles = Array.from(linkElements).filter(function(link) {
            return link.rel === 'stylesheet' && link.href.endsWith('.css');
        });
        var srchead = document.createElement('div');
        
        if (cssFiles.length > 1) {
            cssFiles.forEach(function(link) {
                var individualLink = document.createElement('link');
                individualLink.type = 'text/css';
                individualLink.rel = 'stylesheet';
                individualLink.href = link.href;

                srchead.appendChild(individualLink);
            });
        }
        
        var iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        var srcheadHTML = srchead.outerHTML;
        iframe.srcdoc = '<html><head>' + srcheadHTML + '<title>Print</title></head><body>' + action + '</body></html>';
        document.body.appendChild(iframe);
        
        setTimeout(async function() {
            await loadBundle("knowledge.assets_knowledge_print");
            iframe.contentWindow.print();
        
            document.body.removeChild(iframe);
        }, 500);
        
    },

    async callActionReport() {
        // Function implementation for callToAction
        console.log('callActionReport');
        var action = await this.orm.call(this.props.record.resModel, 'get_action_report', [this.props.article.id], {});
    }
});