# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductColor(models.Model):
    _name = 'product.color'
    _description = 'Product Color'

    avatar_image = fields.Binary(string="Avatar")
    name = fields.Char(string="Name")
    name_fr = fields.Char(string="Name FR")
    name_nl = fields.Char(string="Name NL")
    code = fields.Char(string="Code")
    spartoo_color_code = fields.Char(string="Spartoo Color Code")
    type = fields.Selection([
        ('customer', 'Customer'),
        ('factory', 'Factory'),
    ], string="Type")
