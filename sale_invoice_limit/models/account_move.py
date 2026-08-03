# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for move in self:
            if move.move_type != 'out_invoice':
                continue

            # Sales orders related to this invoice (an invoice can cover
            # more than one order when using grouped invoicing).
            orders = move.invoice_line_ids.sale_line_ids.order_id
            orders_with_limit = orders.filtered('invoice_limit_amount')

            for order in orders_with_limit:
                # Amount already posted for this order, excluding this move
                # itself (which is not posted yet).
                already_invoiced = sum(
                    inv.amount_total for inv in order.invoice_ids
                    if inv.state == 'posted'
                    and inv.move_type == 'out_invoice'
                    and inv.id != move.id
                )
                credited = sum(
                    inv.amount_total for inv in order.invoice_ids
                    if inv.state == 'posted' and inv.move_type == 'out_refund'
                )
                already_invoiced -= credited

                # Portion of this specific invoice that belongs to this
                # order (relevant for grouped invoices covering several
                # orders at once).
                move_amount_for_order = sum(
                    line.price_total for line in move.invoice_line_ids
                    if order in line.sale_line_ids.order_id
                )

                total_after_this = already_invoiced + move_amount_for_order
                if total_after_this > order.invoice_limit_amount + 0.01:
                    excess = total_after_this - order.invoice_limit_amount
                    remaining_allowed = max(
                        order.invoice_limit_amount - already_invoiced, 0
                    )
                    raise UserError(_(
                        'Invoice %(move)s cannot be posted: its amount '
                        '(%(amount).2f) exceeds the invoice limit set on '
                        'sales order %(order)s by %(excess).2f.\n\n'
                        'Invoice limit: %(limit).2f\n'
                        'Already invoiced: %(already).2f\n'
                        'Maximum allowed for this invoice: %(remaining).2f\n\n'
                        'Go back to the invoice (still in Draft) and reduce '
                        'the line amounts/quantities so the total stays '
                        'within the allowed limit, then post it again.'
                    ) % {
                        'move': move.name or _('New'),
                        'amount': move_amount_for_order,
                        'order': order.name,
                        'excess': excess,
                        'limit': order.invoice_limit_amount,
                        'already': already_invoiced,
                        'remaining': remaining_allowed,
                    })

        return super(AccountMove, self).action_post()
