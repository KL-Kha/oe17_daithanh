from odoo import models, fields

class PackingListInheritStock(models.Model):
    _inherit = 'stock.picking'

    packing_list_id = fields.Many2one('packing.list', string='Packing List')
