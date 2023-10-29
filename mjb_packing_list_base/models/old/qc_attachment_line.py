# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class QcAttachmentLine(models.Model):
    _name = 'qc.attachment.line'
    _description = 'Qc Attachment Line'

    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', string="Company")
    image_1 = fields.Binary(string="Image 1")
    image_2 = fields.Binary(string="Image 2")
    image_3 = fields.Binary(string="Image 3")
    image_4 = fields.Binary(string="Image 4")
    packing_list_id = fields.Many2one('packing.list', string="Packing List ID")
    production_sheet_id = fields.Many2one('production.sheet', string="Production Sheet ID")
    remarks = fields.Char(string="Remarks")
    report_id = fields.Many2one('iqc.report', string="Report ID")
    sequence = fields.Integer(string="Sequence")
