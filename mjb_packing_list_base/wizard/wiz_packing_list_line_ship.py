# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class WizPackingListLineShip(models.TransientModel):
    _name = "wiz.packing.list.line.ship"
    _description = 'Wizard Packing List Line Ship'

    name = fields.Char(string="Name")
    quantity = fields.Float(string="Quantity")
    packing_list_line_id = fields.Many2one('packing.list.line', string="Packing List Line")
    product_tmpl_id = fields.Many2one('product.template', string="Product")
    packing_list_type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External')
    ], string="Type")
