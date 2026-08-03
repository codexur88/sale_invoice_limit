# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_limit_amount = fields.Monetary(
        string='Invoice Limit',
        currency_field='currency_id',
        help='Maximum amount that is allowed to be invoiced on this order. '
             'Leave at 0 for no limit (invoicing is unrestricted).',
        copy=False,
    )
    amount_invoiced = fields.Monetary(
        string='Amount Invoiced',
        compute='_compute_invoice_limit_amounts',
        currency_field='currency_id',
        store=True,
    )
    amount_invoice_remaining = fields.Monetary(
        string='Amount Remaining to Invoice',
        compute='_compute_invoice_limit_amounts',
        currency_field='currency_id',
        store=True,
    )

    @api.depends(
        'invoice_ids', 'invoice_ids.state', 'invoice_ids.move_type',
        'invoice_ids.amount_total', 'invoice_limit_amount', 'amount_total',
    )
    def _compute_invoice_limit_amounts(self):
        for order in self:
            invoiced = sum(
                inv.amount_total for inv in order.invoice_ids
                if inv.state == 'posted' and inv.move_type == 'out_invoice'
            )
            credited = sum(
                inv.amount_total for inv in order.invoice_ids
                if inv.state == 'posted' and inv.move_type == 'out_refund'
            )
            order.amount_invoiced = invoiced - credited
            if order.invoice_limit_amount:
                order.amount_invoice_remaining = order.invoice_limit_amount - order.amount_invoiced
            else:
                order.amount_invoice_remaining = order.amount_total - order.amount_invoiced

    def _create_invoices(self, grouped=False, final=False, date=None):
        # Pre-check: block only when the order has already reached its limit,
        # since there would be nothing left to invoice.
        for order in self:
            if order.invoice_limit_amount:
                remaining = order.invoice_limit_amount - order.amount_invoiced
                if remaining <= 0.005:
                    raise UserError(_(
                        'Sales order %(name)s has reached its invoice limit '
                        '(%(limit)s). %(invoiced)s has already been invoiced '
                        'and no further invoice can be created for it. '
                        'Increase the limit on the order if needed.'
                    ) % {
                        'name': order.name,
                        'limit': order.invoice_limit_amount,
                        'invoiced': order.amount_invoiced,
                    })

        # Note: we deliberately do not block here after invoice creation.
        # Raising after super() would roll back the whole transaction and
        # prevent even the draft invoice from being created. The real limit
        # check happens when the invoice is posted/confirmed instead (see
        # account_move.py), so the user can still open the draft invoice
        # and reduce its line amounts before posting.
        moves = super(SaleOrder, self)._create_invoices(
            grouped=grouped, final=final, date=date
        )
        return moves
