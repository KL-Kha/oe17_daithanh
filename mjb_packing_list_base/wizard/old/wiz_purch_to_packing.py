# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SoToPackingList(models.TransientModel):
    _name = "wiz.purch.to.packing"
    _description = 'Wizard Puchasing Sheet to Packing'

    name = fields.Char(string="Name")
    sheet_line_ids = fields.Many2many('production.sheet.line', string="Lines")
    packing_list_id = fields.Many2one('packing.list', string="Packing list")
    sheet_id = fields.Many2one('production.sheet', string="Purchasing Sheet")
