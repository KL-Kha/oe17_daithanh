# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductDesignTag(models.Model):
    _name = 'product.design.tag'
    _description = 'Product Design Tag'

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Name", required=True)
