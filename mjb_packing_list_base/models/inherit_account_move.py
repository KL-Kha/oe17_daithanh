from odoo import models, fields

class PackingListInheritAccount(models.Model):
    _inherit = 'account.move'

    packing_list_id = fields.Many2one('packing.list', string='Packing List')
    studio_tracking_number = fields.Char(string="Tracking Number")
    studio_customer_po_numbers_1 = fields.Char(string="Customer PO Number(s)")

    

class PackingListInhegitAcountLine(models.Model):
    _inherit = 'account.move.line'

    analytic_account_id = fields.Many2one('account.analytic.account',string="	Analytic Account")
