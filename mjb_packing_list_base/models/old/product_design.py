# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductDesign(models.Model):
    _name = 'product.design'
    _description = 'Product Design'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    active = fields.Boolean(string="Active")
    name = fields.Char(string="Name")
    cad_file = fields.Binary(string="CAD File")
    cad_file_filename = fields.Char(string="Filename for x_studio_binary_field_EBTDv")
    customer_id = fields.Many2one('res.partner', string="Customer ID")
    date = fields.Date(string="Date")
    done_date = fields.Datetime(string="Done date")
    image = fields.Binary(string="Image")
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')
    ],string="Kanban State")
    notes = fields.Text(string="Notes")
    original_order = fields.Many2one('sale.order', string="Original Order")
    parent_design = fields.Many2one('product.design', string="Parent Design")
    pattern_pcs = fields.Integer(string="Pattern Pcs")
    priority = fields.Boolean(string="High Priority")
    product_template_id = fields.Many2one('product.template', string="Product")
    revised_pcs = fields.Integer(string="Revised Pcs")
    revision = fields.Integer(string="Revision")
    sample_master = fields.Many2one('hr.employee', string="Sample Master")
    sequence = fields.Integer(string="Sequence")
    stage_id = fields.Many2one('product.design.stage', string="Stage")
    tag_ids = fields.Many2many('product.design.tag', string="Tags")
    user_id = fields.Many2one('res.users', string="Responsible")
    iqc_report_count = fields.Integer(string="Design count")
    sample_sheet_count = fields.Integer(string="Design count")
    product_design_count = fields.Integer(string="Parent Design count")
    product_template_count = fields.Integer(string="BSK Number count")
    costing_sheet_count = fields.Integer(string="Product Design ID count")
