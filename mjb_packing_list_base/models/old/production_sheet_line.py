# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductionSheetLine(models.Model):
    _name = 'production.sheet.line'
    _description = 'Production Sheet Line'

    @api.depends(
        'purchase_order_lines.qty_invoiced',
        'purchase_order_lines.order_id.state'
    )
    def _compute_billed_qty(self):
        for record in self:
            val = 0.0
            if record.purchase_order_lines:
                for l in record.purchase_order_lines:
                    if l.order_id.state != 'cancel':
                        val += l.qty_invoiced
            record.billed_qty = val

    @api.depends('unit_price', 'purchase_price')
    def _compute_price_gap(self):
        for record in self:
            gap = 0.0
            if record.unit_price and record.purchase_price:
                gap = (record.unit_price - record.purchase_price) / record.unit_price
            record.price_gap = gap

    @api.depends(
        'unit_price',
        'purchase_price'
    )
    def _compute_price_gap_value(self):
        for record in self:
            val = (record.unit_price or 0.0) - (record.purchase_price or 0.0)
            record.price_gap_value = val

    @api.depends(
        'production_quantity',
        'material_quantity'
    )
    def _compute_production_quantity_net(self):
        for record in self:
            prod_qty = (record.production_quantity or 0.0)
            if record.is_additional:
                prod_qty = 1.0
            record.production_quantity_net = prod_qty * (record.material_quantity or 0.0)

    @api.depends(
        'production_quantity',
        'material_quantity'
    )
    def _compute_production_quantity_total(self):
        for record in self:
            prod_qty = (record.production_quantity or 0.0)
            if record.is_additional:
                prod_qty = 1.0
            record.production_quantity_net = prod_qty * (record.material_quantity or 0.0)

    @api.depends(
        'purchase_order_lines.product_qty',
        'purchase_order_lines.order_id.state',
        'purchase_approved'
    )
    def _compute_purchased_qty(self):
        for record in self:
            val = 0.0
            if record.purchase_order_lines:
                for l in record.purchase_order_lines:
                    if l.order_id.state != 'cancel':
                        val += l.product_qty
            record.purchased_qty = val

    @api.depends(
        'production_quantity_total',
        'purchased_qty'
    )
    def _compute_purchased_qty_rate(self):
        for record in self:
            val = (record.purchased_qty or 0.0) / (record.production_quantity_total or 1.0)
            record.purchased_qty_rate = val

    @api.depends(
        'purchase_order_lines.qty_received',
        'purchase_order_lines.order_id.state'
    )
    def _compute_received_qty(self):
        for record in self:
            val = 0.0
            if record.purchase_order_lines:
                for l in record.purchase_order_lines:
                    if l.order_id.state != 'cancel':
                        val += l.qty_received
            record.received_qty = val

    @api.depends(
        'unit_price',
        'production_quantity_total'
    )
    def _compute_total_costing_price(self):
        for record in self:
            val = (record.production_quantity_total or 0.0) * (record.unit_price or 0.0)
            record.total_costing_price = val

    @api.depends(
        'total_purchase_price',
        'total_costing_price'
    )
    def _compute_total_price_gap_value(self):
        for record in self:
            val = (record.total_costing_price or 0.0) - (record.total_purchase_price or 0.0)
            record.total_price_gap_value = val

    @api.depends(
        'production_quantity_total',
        'purchase_price'
    )
    def _compute_total_purchase_price(self):
        for record in self:
            val = (record.production_quantity_total or 0.0) * (record.purchase_price or 0.0)
            record.total_purchase_price = val

    active = fields.Boolean(string="Active")
    material_width = fields.Float(string="Material Width")
    name = fields.Char(string="Description")
    parent_id = fields.Many2one('production.sheet.line', string="Parent Line")
    product_name = fields.Char(string="Product Name")
    billed_qty = fields.Float(string="Billed Qty", compute="_compute_billed_qty")
    children_ids = fields.One2many('production.sheet.line', 'parent_id', string="Children IDS")
    color = fields.Many2one('product.color', string="Product Color")
    color_id = fields.Many2one('product.color', string="Color")
    costing_sheet_line_id = fields.Many2one('costing.sheet.line', string="Costing Sheet Line ID")
    customer_order = fields.Char(related='order_id.client_order_ref', string="Customer Order")
    defect_rate = fields.Float(string="Defect Rate /不良率")
    design = fields.Many2one('product.design', string="Design")
    # final_product = fields.Many2one(related='production_sheet_id.product_id', string="Final Product")
    float_field_Dn2I3 = fields.Float(string="New Decimal")
    float_field_PA5eb = fields.Float(string="New Decimal")
    float_field_Uzsg5 = fields.Float(string="New Decimal")
    is_additional = fields.Boolean(string="Is Additional")
    # is_semi_finished = fields.Boolean(related='costing_sheet_line_id.is_semi_finished', string="Is Semi Finished")
    length = fields.Float(string="Length/长度")
    material_quantity = fields.Float(string="Material Quantity/材料用量")
    one2many_field_ia1r6 = fields.One2many('production.sheet.line', 'parent_id', string="New One2many")
    # order_id = fields.Many2one(related='production_sheet_id.related_order', string="Order Id")
    order_id = fields.Many2one('sale.order', string="Order Id")
    # order_quantity = fields.Float(related='production_sheet_id.quantity', string="New Related Field")
    price_gap = fields.Float(string="Price Gap", compute="_compute_price_gap")
    price_gap_value = fields.Float(string="Price Gap Value", compute="_compute_price_gap_value")
    # process_info = fields.Char(related="costing_sheet_line_id.process_info", string="Process Info")
    # process_key = fields.Char(related='costing_sheet_line_id.process_key', string="Process Key")
    product_id = fields.Many2one('product.template', string="Product")
    # production_quantity = fields.Float(related='production_sheet_id.quantity', string="Production Quantity/生产数量")
    production_quantity_net = fields.Float(string="Production Quantity Net/单 用量", compute="_compute_production_quantity_net")
    production_quantity_total = fields.Float(string="Production Quantity Total", compute="_compute_production_quantity_total")
    production_sheet_id = fields.Many2one('production.sheet', string="Production Sheet")
    purchase_approved = fields.Boolean(string="Purchase Approved")
    purchase_order_lines = fields.One2many('purchase.order.line', string="Purchase Order Lines")
    purchase_price = fields.Float(string="Purchase Price")
    purchase_price_gap = fields.Text(string="Purchase Price Gap")
    purchased_qty = fields.Float(string="Purchased Qty", compute="_compute_purchased_qty")
    purchased_qty_rate = fields.Float(string="Purchased Qty Rate", compute="_compute_purchased_qty_rate")
    quantity = fields.Float(string="Quantity/数量")
    # quantity_on_hand = fields.Float(related="product_id.qty_available", string="Quantity on hand")
    received_qty = fields.Float(string="Received Qty", compute="_compute_received_qty")
    related_customer = fields.Many2one(related='order_id.partner_id', string="Related Customer")
    remarks = fields.Char(string="Remarks")
    sales_order_line_id = fields.Many2one('sale.order.line', string="Sales Order Line ID")
    sample_sheet_line_id = fields.Many2one('sample.sheet.line', string="Sample Sheet Line ID")
    section_id = fields.Many2one('costing.sheet.line', string="Section")
    seq = fields.Char(string="Seq")
    sequence = fields.Integer(string="Sequence")
    supplier_id = fields.Many2one('res.partner', string="Supplier")
    total_costing_price = fields.Float(string="Total Costing Price", compute="_compute_total_costing_price")
    total_price_gap_value = fields.Float(string="Total Price Gap Value", compute="_compute_total_price_gap_value")
    total_purchase_price = fields.Float(string="Total Purchase Price", compute="_compute_total_purchase_price")
    type = fields.Selection([
        ('component', 'Component'),
        ('subcontract', 'Subcontract')
    ], string="Type")
    unit_price = fields.Float(string="Costing Unit Price")
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    width = fields.Float(string="Width/宽度")
