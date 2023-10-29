# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SoToPackingList(models.TransientModel):
    _name = "so.to.packing.list.wizard"
    _description = 'Sale order to packing list wizard'

    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string="Target Packing List")
    order_id = fields.Many2one('sale.order', string="Order")
    order_line_ids = fields.Many2many('sale.order.line', string="Order Line IDs")
    target_packing_list = fields.Many2one('packing.list', string="Target Packing List")
