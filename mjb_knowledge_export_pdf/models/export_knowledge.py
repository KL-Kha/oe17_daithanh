from odoo import models, fields, api, _

class KnowledgeArticle(models.Model):
    _inherit = 'knowledge.article'

    def get_sorted_child_ids(self):
        return sorted(self.child_ids, key=lambda x: x.sequence)

    def get_child_article(self):
        body_html = ""
        sorted_children = self.get_sorted_child_ids()
        for child in sorted_children:
            body_html += child.body
            if child.child_ids:
                body_html += child.get_child_article()
        return body_html

    def get_pdf(self):
        child_article = self.get_child_article()
        body_html = self.body + child_article

        return body_html

    def get_action_report(self):
        return self.env.ref('mjb_knowledge_export_pdf.x_mjb_action_export_pdf').run()