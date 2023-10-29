# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime

class PackingList(models.Model):
    _name = 'packing.list'
    _description = 'Packing List'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char(string="Name")
    title = fields.Char(string="Title", default="Packing List")
    bl_number = fields.Char(string="BL Number")
    packing_instructions_filename = fields.Char(string="Filename for x_studio_binary_field_KO2cR")
    order_number = fields.Char(string="Order Number")
    shipping_marks = fields.Char(string="Shipping Marks")
    vessel = fields.Char(string="Vessel")
    invoice_number = fields.Char(string="Invoice Number")
    container_number = fields.Char(string="Container number")
    goods_origin = fields.Char(string="Goods origin")
    container_information = fields.Char(string="Container information")
    bl_file_filename = fields.Char(string="Filename for x_studio_binary_field_G4X8M") #save file

    packing_instructions = fields.Binary(string="Packing Instructions")
    bl_file = fields.Binary(string="BL File")

    stock_picking_ids = fields.Many2many('stock.picking', string='Related Stock Pickings')
    account_move_ids = fields.Many2many('account.move', string='Related Account Moves')
    packing_list_id__account_move_count = fields.Integer(string="Account Move count", compute='_compute_account_move_count')
    packing_list_id__stock_picking_count = fields.Integer(string="Stock Picking count", compute='_compute_packing_list_id')
    packing_list_id__mjb_packing_list_line_count = fields.Integer(string="Picking List Line count", compute='_compute_packing_list_line_count')
    packing_list_id__sales_order_count = fields.Integer(string="Sales Order count", compute='_compute_sales_order_count')
    sequence = fields.Integer(string="Sequence", default=lambda self: self.env['ir.sequence'].next_by_code('sequence'))
    report_count = fields.Integer(string="Packing List count")

    total_cbm = fields.Float(string="Total Cbm")
    total_nw = fields.Float(string="Total Net Weight")
    total_gw = fields.Float(string="Total Gross Weight")
    number_cartons = fields.Float(string="Total Carton Quantity	")
    total_quantity = fields.Float(string="Total Quantity")
    total_amount = fields.Float(string="Total Amount")
    total_pallet_quantity = fields.Float(string="Total Pallet Quantity")

    invoice_date = fields.Date(string="Invoice Date")
    date_arrival = fields.Date(string="Date Arrival")
    date_loading = fields.Date(string="Date Loading")
    date_departure = fields.Date(string="Date Departure")
    
    priority = fields.Boolean(string="High Priority")
    active = fields.Boolean(string="Active", default=True)
    
    shipping_type = fields.Selection([
        ('ocean', 'Ocean'),
        ('air', 'Air'),
        ('land', 'Land')
    ], string="Shipping Type")
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')
    ], string="Kanban State")
    packing_list_type = fields.Selection([
        ('customer', 'Customer'),
        ('internal', 'Internal Material'),
        ('external', 'External Material')
    ],
        string="Packing List Type")
    
    payment_terms_id = fields.Many2one('account.payment.term', string="Payment Terms")
    incoterm = fields.Many2one('account.incoterms', string="Incoterm")
    responsible = fields.Many2one('res.users', string="Responsible")
    consignee = fields.Many2one('res.partner', string="Consignee")
    forwarder = fields.Many2one('res.partner', string="Forwarder")
    port_from_id = fields.Many2one('shipping.destination', string="Port From")
    port_to_id = fields.Many2one('shipping.destination', string="Port To")
    delivery_address = fields.Many2one('res.partner',string="Delivery Address")
    manufacturer_id = fields.Many2one('res.partner', string="Manufacturer")
    customer = fields.Many2one('res.partner', string="Customer")
    shipper = fields.Many2one('res.partner', string="Shipper")

    x_forwarder_id = fields.Many2one('res.partner',string="Forwarder")
    
    stage_lock = fields.Boolean(string="Stage Lock",default=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company.id)

    
    # attachments_ids = fields.One2many('qc.attachment.line', 'packing_list_id', string="AttachmentsS")
    line_real_ids = fields.One2many('packing.list.line', 'packing_list_id', string="Shipped Lines")
    line_ids = fields.One2many('packing.list.line', 'packing_list_id', string="Lines")

    orders = fields.Many2many('sale.order', string="Orders")

    actual_freight_cost = fields.Float(string="Actual Freight Cost")
    freight_invoiced_customer = fields.Float(string="Freight Invoiced to Customer")
    freight_prepaid = fields.Boolean(string="Freight Prepaid")
    studio_inventory_site = fields.Char(string="Inventory Site")
    studio_vendor_pl = fields.Char(string="Vendor PL")
    studio_vendor_po_no = fields.Char(string="Vendor PO No")
    tracking = fields.Char(string="Tracking")
    tradelink_udr = fields.Char(string="Tradelink UDR")
    ship_status = fields.Char(string="Ship Status")
    loading_ref = fields.Char(string="Loading Ref")
    ref = fields.Char(string="Ref", compute='_compute_ref')
    estimated_freight_cost = fields.Float(string='Estimated Freight Cost')
    declare  = fields.Boolean(string="Declare Y/N")
    local_charges  = fields.Boolean(string="Local Charges")
    mate_receipt  = fields.Boolean(string="Mate Receipt")
    notes = fields.Text(string="Notes")
    
    code_prefix = fields.Char(default='Packing/')

    stage_id = fields.Many2one('packing.list.stage', string="Stage", default=lambda self: self.env['packing.list.stage'].search([('name','=','New')], limit=1),track_visibility="always")
    stage_id_lock = fields.Many2one('packing.list.stage', string="Stage", default=lambda self: self.env['packing.list.stage'].search([('name','=','New')], limit=1))
    code = fields.Char(compute='_compute_code', store=True)

    is_move_back_allowed = fields.Boolean(compute='_compute_is_move_back_allowed', store=False)
    is_cancel_allowed = fields.Boolean(compute='_compute_is_cancel_allowed', store=False)
    is_packing_allowed = fields.Boolean(compute='_compute_is_packing_allowed', store=False)
    is_loading_allowed = fields.Boolean(compute='_compute_is_loading_allowed', store=False)
    is_review_allowed = fields.Boolean(compute='_compute_is_review_allowed', store=False)
    is_delivered_allowed = fields.Boolean(compute='_compute_is_delivered_allowed', store=False)

    @api.depends('code_prefix', 'sequence')
    def _compute_code(self):
        for record in self:
            record.code = f"{record.code_prefix}{record.sequence:04d}"

    @api.depends('orders')
    def _compute_ref(self):
        for record in self:
            res = record.orders.mapped("studio_customer_po_number")
            record.ref = ",".join([str(r) for r in res])

    @api.depends('stock_picking_ids')
    def _compute_packing_list_id(self):
        results = self.env['stock.picking'].read_group([('packing_list_id', 'in', self.ids)], ['packing_list_id'], ['packing_list_id'])
        dic = {}
        for x in results: dic[x['packing_list_id'][0]] = x['packing_list_id_count']
        for record in self: record['packing_list_id__stock_picking_count'] = dic.get(record.id, 0)

    @api.depends('account_move_ids')
    def _compute_account_move_count(self):
        results = self.env['account.move'].read_group([('packing_list_id', 'in', self.ids)], ['packing_list_id'], ['packing_list_id'])
        dic = {}
        for x in results: dic[x['packing_list_id'][0]] = x['packing_list_id_count']
        for record in self: record['packing_list_id__account_move_count'] = dic.get(record.id, 0)

    @api.depends('line_ids')
    def _compute_packing_list_line_count(self):
        for record in self:
            record.packing_list_id__mjb_packing_list_line_count = len(record.line_ids)
    
    @api.depends('orders')
    def _compute_sales_order_count(self):
        for record in self:
            order_count = self.env['sale.order'].search_count([('id', 'in', self.orders.ids)])
            record.packing_list_id__sales_order_count = order_count


    def add_to_pl(self):
        if self:
            if not self.customer:
                raise ValidationError(_("You must select a customer first"))
            action ={
                'view_type':'form',
                'view_mode': 'form',
                'res_model' : 'add.to.packing.list.wizard',
                'view_id': self.env.ref('mjb_packing_list_base.add_to_packing_list_wizard_form_view').id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'nodestroy': True,
                'context': {
                    'default_partner_id': self.customer.id,
                    'default_order_id': self.orders.id,
                    'default_target_packing_list': self.id,
                }
            }
            # Call the action_update_pl() function after the action is returned
            result = self.action_update_pl()
            return action

        
    def pl_display_so(self):
        return {
            'name': 'Sales Orders',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.orders.id)],
        }

    def packing_list_id__stock_picking(self):
        return {
            'name': 'Deliveries',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'domain': [('packing_list_id', '=', self.id)],
        }

    def packing_list_id__account_move(self):
        return {
            'name': 'Invoices',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': [('packing_list_id', '=', self.id)],
        }

    def packing_list_id__mjb_packing_list_line(self):
        return {
            'name': 'Packing List Line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'packing.list.line',
            'type': 'ir.actions.act_window',
            'domain': [('packing_list_id', '=', self.id)],
        }
    
    @api.depends('stage_id')
    def _compute_is_move_back_allowed(self):
        for record in self:
            stage_name = record.stage_id.name
            record.is_move_back_allowed = stage_name not in ['New']
    
    @api.depends('stage_id')
    def _compute_is_packing_allowed(self):
        for record in self:
            stage_name = record.stage_id.name
            record.is_packing_allowed = stage_name not in ['Packing']
    
    @api.depends('stage_id')
    def _compute_is_loading_allowed(self):
        for record in self:
            stage_name = record.stage_id.name
            record.is_loading_allowed = stage_name not in ['Loading']

    @api.depends('stage_id')
    def _compute_is_review_allowed(self):
        for record in self:
            stage_name = record.stage_id.name
            record.is_review_allowed = stage_name not in ['Review']
    
    @api.depends('stage_id')
    def _compute_is_delivered_allowed(self):
        for record in self:
            stage_name = record.stage_id.name
            record.is_delivered_allowed = stage_name not in ['Delivered']
        
    @api.depends('stage_id')
    def _compute_is_cancel_allowed(self):
        for record in self:
            stage_name = record.stage_id.name
            record.is_cancel_allowed = stage_name not in ['Cancelled']

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        self.stage_id_lock = self.stage_id

    def move_back(self):
        for record in self:
            previous_stages = self.env['packing.list.stage'].search([('id', '<', record.stage_id.id)], order='id DESC')
            if previous_stages:
                record.stage_id = previous_stages[0]
                record.stage_id_lock = previous_stages[0]

    def move_forward(self):
        for record in self:
            previous_stages = self.env['packing.list.stage'].search([('id', '>', record.stage_id.id)], order='id ASC')
            if previous_stages:
                record.stage_id = previous_stages[0]
                record.stage_id_lock = previous_stages[0]
                
            if record.stage_id.name == "Loading":
                record.date_loading = datetime.date.today()


    def button_cancel(self):
        for record in self:
            record.stage_id = self.env['packing.list.stage'].search([('name','=','Cancelled')], limit=1)
            record.stage_id_lock = record.stage_id

    def setName(self,sheet):
        others= sheet.env['packing.list'].search([
            ('code','=',sheet.name),
            ('id','!=',sheet.id)
        ],limit=1)
        v = {}
        if not sheet['code'] or (sheet['code'] == 'New') or (sheet['code'] == '') or len(others) > 0:
            v['code'] = self.env['ir.sequence'].sudo().next_by_code('scp.packing.list')
        v['name'] = "[" + str(sheet.code) + "] "+  str(sheet.title or "")
        return v

    def action_update_pl(self):
        for sheet in self:
            vr = {}
            vr.update(self.setName(sheet))

            # Set payment terms
            if not sheet.payment_terms_id:
                if sheet.customer.property_payment_term_id:
                    vr.update({
                        "payment_terms_id": sheet.customer.property_payment_term_id.id
                    })
            
            # Totals
            totalQty = sum(sheet.line_ids.mapped("quantity"))
            totalNetWeight = sum(sheet.line_ids.mapped("total_net_weight"))
            totalGrossWeight = sum(sheet.line_ids.mapped("total_gross_weight"))
            totalCtnQty = sum(sheet.line_ids.mapped("carton_quantity"))
            totalCbm = sum(sheet.line_ids.mapped("total_cbm"))
            totalAmount = sum(sheet.line_ids.mapped("total_amount"))
            totalPalletQty = sum(sheet.line_ids.mapped("pallet_qty"))

            vr['total_nw'] = totalNetWeight
            vr['total_gw'] = totalGrossWeight
            vr['number_cartons'] = totalCtnQty
            vr['total_quantity'] = totalQty
            vr['total_cbm'] = totalCbm
            vr['total_amount'] = totalAmount
            vr['total_pallet_quantity'] = totalPalletQty

            sheet.write(vr)

    def action_update_pl_line_title(self):
        for packingList in self:
            if packingList.line_ids:
                for line in packingList.line_ids:
                    line.write({
                        'title': packingList.title
                    })
