# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CartonType(models.Model):
    _name = 'carton.type'
    _description = 'Carton Type'

    # def _compute_cbm(self):
    #     for record in self:
    #         w = record.width or 0.0
    #         l = record.length or 0.0
    #         h = record.height or 0.0
    #         rate = 1
    #         if record.uom_id:
    #             if record.uom_id.factor > 0:
    #                 rate = 1 / record.uom_id.factor
    #         cbm = w * l * h * rate
    #         record.cbm = cbm

    active = fields.Boolean(string="Active",default=True)
    code = fields.Char(string="Code")
    name = fields.Char(string="Name")
    cbm = fields.Float(string="Qty Per Ctn")
    height = fields.Float(string="Height")
    length = fields.Float(string="Length")
    sequence = fields.Integer(string="Sequence")
    uom_id = fields.Many2one('uom.uom', string="UoM")
    weight = fields.Float(string="Weight")
    weight_uom = fields.Many2one('uom.uom', string="Weight UoM")
    width = fields.Float(string="Width")
    notes = fields.Text(string="Notes")
    partner_id = fields.Many2one('res.partner',string="Partner")
    product_id = fields.Many2one('product.template',string="Product")
    type = fields.Selection([
        ('carton', 'Carton'),
        ('pallet', 'Pallet'),
    ], string="Type")