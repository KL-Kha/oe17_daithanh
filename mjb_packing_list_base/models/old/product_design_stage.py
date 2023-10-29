# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductDesignStage(models.Model):
    _name = 'product.design.stage'
    _description = 'Product Design Stage'

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
