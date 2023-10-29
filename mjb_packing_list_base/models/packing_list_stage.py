# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PackingListStage(models.Model):
    _name = 'packing.list.stage'
    _description = 'Packing List Stages'

    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Char(string="Stage Name", required=True)
    is_new = fields.Boolean(string="New")
    is_packing = fields.Boolean(string="Packing")
    is_loading = fields.Boolean(string="Loading")
    is_review = fields.Boolean(string="Review")
    is_delivery = fields.Boolean(string="Need Delivery")
    is_invoice = fields.Boolean(string="Need Invoice")
    is_closed = fields.Boolean(string="Closed")

class PackingListStageDefault(models.Model):
    _name = 'packing.list.stage.default'
    _description = 'Default Packing List Stages'

    @api.model
    def _create_default_stages(self):
        stages = [
            {'name': 'New', 'is_new': True},
            {'name': 'Packing', 'is_packing': False},
            {'name': 'Loading', 'is_loading': False},
            {'name': 'Review', 'is_review': False},
            {'name': 'Delivered', 'is_delivery': False},
            {'name': 'Invoiced', 'is_invoice': False},
            {'name': 'Cancelled', 'is_closed': False},
        ]
        for stage in stages:
            stage_exist = self.env['packing.list.stage'].search([('name', '=', stage['name'])])
            if not stage_exist:
                self.env['packing.list.stage'].create(stage)

    def init(self):
        self._create_default_stages()

