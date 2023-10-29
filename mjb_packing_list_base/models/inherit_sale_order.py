from odoo import models, fields, api

class PackingListInheritSale(models.Model):
    _inherit = 'sale.order'

    studio_customer_po_number = fields.Char(string="Customer PO Number")
    packing_list_id = fields.Many2one('packing.list', string='Packing List')
    packing_list_ids = fields.One2many('packing.list','orders', string='List of Packing List')

    so__y_count = fields.Integer(string="Account Move count", compute='_compute_pkl_count')
    
    @api.depends('packing_list_ids')
    def _compute_pkl_count(self):
        for packing in self:
            packing.so__y_count = len(packing.packing_list_ids)
    
    def sale_order__packing_list(self):
        action = self.env.ref('mjb_packing_list_base.packing_list_action').read()[0]
        action['domain'] = [
        ('orders','=', self.id)
        ]
        return action

class PackingListInheritSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    remaining_qty = fields.Float(string='Remaining Quantity', compute='_compute_remaining_qty', store=True)

    @api.depends('product_uom_qty', 'qty_delivered', 'qty_invoiced')
    def _compute_remaining_qty(self):
        for line in self:
            qty_delivered = line.qty_delivered or 0.0
            qty_invoiced = line.qty_invoiced or 0.0
            line.remaining_qty = max(line.product_uom_qty - qty_delivered - qty_invoiced, 0.0)