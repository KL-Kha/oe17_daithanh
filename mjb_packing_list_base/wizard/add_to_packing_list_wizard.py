# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AddToPackingListWizard(models.TransientModel):
    _name = "add.to.packing.list.wizard"
    _description = 'Wizard Add to Packing list'

    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string="Target Packing List")
    order_id = fields.Many2one('sale.order', string="Order")
    order_line_ids = fields.Many2many('sale.order.line', string="Order Line IDs", default=lambda self: self._default_order_line_ids())
    target_packing_list = fields.Many2one('packing.list', string="Target Packing List")

    @api.model
    def _default_order_line_ids(self):
        active_id = self.env.context.get('active_id')
        if len(self.order_id) > 1:
            for sale_order in order_id:
                order_line_ids = [(4, 0, sale_order.order_line.ids)]
         

    def confirm_form(self):
        if len(self.order_line_ids) == 0:
            raise ValidationError("No order line has been selected !")

        new_packing_list = False

        if not self.target_packing_list:
            new_packing_list = self.env['packing.list'].create({
                'customer': self.partner_id.id,
                'name': self.name,
                'delivery_address':self.order_line_ids.order_id[0].partner_shipping_id.id,
                "active": True
            })

            self.target_packing_list = new_packing_list
        
        target = self.target_packing_list
        
        existingOrderIds = [order.id for order in target.orders]
        if self.order_id.id not in existingOrderIds:
            target.write({
                'orders': [(4,self.order_id.id)],
                'delivery_address': [(4,self.partner_id.id)]
            })

        existingLineIds = [line.order_line_id.id for line in target.line_ids]
        toCreate = []
        for line in self.order_line_ids:
            if line.id not in existingLineIds:
                toCreate.append([0,0,{
                    'packing_list_id': target.id,
                    'order_ref': line.order_id.id,
                    'order_line_id': line.id,
                    'product_id': line.product_id.id,
                    'quantity':line.product_uom_qty,
                    'unit_price':line.price_unit,
                    'product_tmpl_id': line.product_template_id,
                }])
        
        if len(toCreate) > 0: 
            target.write({
                'line_ids': toCreate 
            })
        
        view = self.env['ir.ui.view'].search([('name', '=', 'external.packing.list.tree.view')])
        domain = [('id', '=', new_packing_list.id)] if new_packing_list else []
        return {
            'name': 'Picking List',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'packing.list',
            'type': 'ir.actions.act_window',
            'views': [(view.id, 'tree'), (False, 'form')],
            'domain': domain,
        }
