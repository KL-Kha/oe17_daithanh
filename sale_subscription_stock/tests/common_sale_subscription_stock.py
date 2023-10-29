# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from freezegun import freeze_time

from odoo.tests import tagged
from odoo import Command, fields
from odoo.addons.sale_subscription.tests.common_sale_subscription import TestSubscriptionCommon
from odoo.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_common import ValuationReconciliationTestCommon


@tagged('-at_install', 'post_install')
class TestSubscriptionStockCommon(TestSubscriptionCommon, ValuationReconciliationTestCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        context_no_mail = {'no_reset_password': True, 'mail_create_nosubscribe': True, 'mail_create_nolog': True}
        SaleOrder = cls.env['sale.order'].with_context(context_no_mail)
        Product = cls.env['product.product'].with_context(context_no_mail)

        cls.uom_unit = cls.env.ref('uom.product_uom_unit')

        cls.recurrence_3_months = cls.env['sale.temporal.recurrence'].create({'duration': 3, 'unit': 'month'})

        # Pricing

        pricing_commands = [
            Command.create({
                'recurrence_id': cls.recurrence_month.id,
                'price': 45,
            }),
            Command.create({
                'recurrence_id': cls.recurrence_3_months.id,
                'price': 50,
            })
        ]

        cls.pricing_1month = cls.env['product.pricing'].create({
            'recurrence_id': cls.recurrence_month.id,
            'price': 45,
        })

        cls.pricing_3month = cls.env['product.pricing'].create({
            'recurrence_id': cls.recurrence_3_months.id,
            'price': 50,
        })

        # Product

        cls.sub_product_order = Product.create({
            'name': "Subscription consumable invoiced on order",
            'standard_price': 0.0,
            'type': 'consu',
            'uom_id': cls.uom_unit.id,
            'invoice_policy': 'order',
            'recurring_invoice': True,
            'product_pricing_ids': pricing_commands,
        })

        cls.sub_product_order_2 = Product.create({
            'name': "Subscription consumable invoiced on order #2",
            'standard_price': 0.0,
            'type': 'consu',
            'uom_id': cls.uom_unit.id,
            'invoice_policy': 'order',
            'recurring_invoice': True,
            'product_pricing_ids': pricing_commands,
        })

        cls.sub_product_delivery = Product.create({
            'name': "Subscription consumable invoiced on delivery",
            'standard_price': 0.0,
            'type': 'consu',
            'uom_id': cls.uom_unit.id,
            'invoice_policy': 'delivery',
            'recurring_invoice': True,
            'product_pricing_ids': pricing_commands,
        })

        cls.product_non_recurring = Product.create({
            'name': "Consumable invoiced on order",
            'standard_price': 30.0,
            'type': 'consu',
            'uom_id': cls.uom_unit.id,
            'invoice_policy': 'order',
        })

        # SO

        cls.subscription_order = SaleOrder.create({
            'name': 'Order',
            'is_subscription': True,
            'partner_id': cls.user_portal.partner_id.id,
            'recurrence_id': cls.recurrence_month.id,
            'pricelist_id': cls.company_data['default_pricelist'].id,
            'order_line': [Command.create({
                'product_id': cls.sub_product_order.id,
                'product_uom_qty': 1,
                'tax_id': [Command.clear()],
            })]
        })

        cls.subscription_delivery = SaleOrder.create({
            'name': 'Delivery',
            'is_subscription': True,
            'partner_id': cls.user_portal.partner_id.id,
            'recurrence_id': cls.recurrence_month.id,
            'pricelist_id': cls.company_data['default_pricelist'].id,
            'order_line': [Command.create({
                'product_id': cls.sub_product_delivery.id,
                'product_uom_qty': 1,
                'tax_id': [Command.clear()],
            })]
        })

        # update status
        # cls.subscription_delivery._compute_is_deferred()

        with freeze_time("2022-03-02"):
            cls.subscription_order.write({'start_date': fields.date.today(), 'next_invoice_date': False})
            cls.subscription_delivery.write({'start_date': fields.date.today(), 'next_invoice_date': False})
            cls.subscription_order.action_confirm()
            cls.subscription_delivery.action_confirm()

    def simulate_period(self, subscription, date, move_qty=False):
        with freeze_time(date):
            invoice = subscription._create_recurring_invoice()
            if invoice and invoice.state == 'draft':
                invoice.action_post()
            picking = subscription.picking_ids and subscription.picking_ids.filtered(lambda picking: picking.date.date().isoformat() == date)
            if picking:
                for move in picking.move_ids:
                    move.write({'quantity_done': move_qty or move.product_uom_qty})
                picking._action_done()
        return invoice, picking
