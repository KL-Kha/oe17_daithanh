# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, SUPERUSER_ID
from odoo.exceptions import UserError
from . import models
from . import controllers


def post_init(env):
    companies = env['res.company'].search([('chart_template', '=', 'br')])
    for company in companies:
        Template = env['account.chart.template'].with_company(company)
        for xml_id, tax_data in Template._get_br_avatax_account_tax().items():
            tax = Template.ref(xml_id, raise_if_not_found=False)
            if tax and 'l10n_br_avatax_code' in tax_data:
                tax.l10n_br_avatax_code = tax_data['l10n_br_avatax_code']

        Template._load_data({'account.fiscal.position': Template._get_br_avatax_fiscal_position()})
