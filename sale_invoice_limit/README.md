# Sale Order Invoice Limit

Cap the maximum amount that can be invoiced on a sales order, enforced at
the right moment in the workflow, with a visual drag-slider control.

**Odoo version:** 18.0
**License:** LGPL-3
**Author:** Eng. Yasir Habeeb

## Why

By default, a sales order in Odoo can be invoiced up to its full total at
any time. Many businesses need a hard ceiling instead - staged payments,
partial deliveries, credit control, dealer/franchise terms, and so on. An
order worth 3,000 should only be invoiceable up to 1,500, for example,
until someone deliberately raises or removes that limit.

## Features

- **Invoice Limit** field on the sales order (`sale.order`), plus two
  read-only computed fields: **Amount Invoiced** and **Amount Remaining to
  Invoice**.
- **Drag slider widget** (custom OWL component) to set the limit visually,
  with tick marks that scale to the order's total. Dragging is fully local
  to the browser while in progress (no ORM writes mid-drag), so it stays
  smooth even on slower connections; the value is only written to the
  record on release.
- **Enforcement at post time, not at draft time.** Creating a draft
  invoice is never blocked, so a user can always open the draft and adjust
  line quantities/amounts. The limit is checked when the invoice is
  **posted/confirmed** - if posting would exceed the order's remaining
  limit, Odoo raises a clear error and the invoice stays in Draft.
- **Grouped invoicing aware.** If one invoice covers several sales orders,
  only the portion of that invoice attributable to each order is checked
  against that order's own limit.
- **Credit notes reduce the invoiced total**, freeing up room under the
  limit again once posted.
- Limit defaults to `0` (no restriction) - fully backward compatible with
  existing orders and workflows.

## Installation

1. Copy the `sale_invoice_limit` folder into your Odoo `addons` path (or
   push it to your Odoo.sh repository).
2. Update the apps list and install **Sale Order Invoice Limit** from the
   Apps menu.
3. Hard-refresh the browser (Ctrl+Shift+R) after install/upgrade so the
   new JS/SCSS assets load.

## Usage

1. Open a sales order and go to the **Invoice Limit** tab.
2. Drag the slider (or type a value) to set the maximum invoiceable
   amount. Leave it at `0` for unrestricted invoicing.
3. Invoice as usual. If posting an invoice would exceed the remaining
   limit, Odoo blocks the post action with a message showing:
   - the limit set on the order,
   - the amount already invoiced,
   - the maximum still allowed for that specific invoice.

   The invoice remains editable in Draft so the amount can be brought back
   within range before posting again.

## Technical notes

- `models/sale_order.py` adds `invoice_limit_amount`, `amount_invoiced`,
  and `amount_invoice_remaining` to `sale.order`, and overrides
  `_create_invoices` to block only when an order has already fully used
  its limit (nothing left to invoice).
- `models/account_move.py` overrides `action_post` on `account.move` to
  perform the actual limit check, computed per sales order to support
  grouped invoices.
- `static/src/js/invoice_limit_slider.js` registers a custom field widget
  (`invoice_limit_slider`) usable on any monetary/float/integer field via
  `widget="invoice_limit_slider"` and the `max_field` option.

## Compatibility

Odoo 18 Community and Enterprise, Odoo.sh and self-hosted deployments.

## Support

For issues or feature requests, please open a ticket on the repository's
issue tracker.
