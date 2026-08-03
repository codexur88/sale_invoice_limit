# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Invoice Limit',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Cap the maximum amount that can be invoiced on a sales order, with a visual slider control.',
    'description': """
Sale Order Invoice Limit
=========================

Restrict how much of a sales order can be invoiced, and enforce it at the
right moment in the workflow.

Why use this module?
---------------------
By default, Odoo lets a sales order be invoiced up to its full total at any
time. In many businesses (partial deliveries, staged payments, credit
control, franchise/dealer terms, etc.) you need a hard ceiling: an order
worth 3,000 should only ever be invoiced up to 1,500, for example, until
the limit is raised or removed on purpose.

Key features
-------------
* **Invoice Limit field** on the sales order, with a live "Amount Invoiced"
  and "Amount Remaining to Invoice" readout.
* **Visual drag slider widget** to set the limit quickly, with tick marks
  scaled to the order total, instead of typing a raw number.
* **Smart enforcement point**: creating a draft invoice is never blocked
  (so users can always open a draft and adjust line amounts). The limit is
  enforced when the invoice is *posted/confirmed* - if posting would push
  the order over its limit, Odoo raises a clear, actionable error and the
  invoice stays in Draft so the amount can be corrected.
* **Grouped-invoice aware**: if a single invoice covers several sales
  orders, only the portion of that invoice belonging to each order is
  checked against that order's own limit.
* **Credit notes are accounted for**: posted credit notes reduce the
  invoiced amount, freeing up room under the limit again.
* Leave the limit at 0 for unrestricted invoicing (default behavior,
  fully backward compatible).

How it works
-------------
1. Open a sales order and go to the *Invoice Limit* tab.
2. Drag the slider (or type a value) to set the maximum invoiceable amount.
3. Invoice as usual. If a posted invoice would exceed the remaining limit,
   Odoo blocks the *post* action with a message showing the limit, what has
   already been invoiced, and the maximum still allowed - the invoice stays
   editable in Draft so you can bring the amount back within range.

Compatible with Odoo 18 Community and Enterprise, Odoo.sh and self-hosted
deployments.
    """,
    'author': 'Codexui',
    'website': '',
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_invoice_limit/static/src/js/invoice_limit_slider.js',
            'sale_invoice_limit/static/src/xml/invoice_limit_slider.xml',
            'sale_invoice_limit/static/src/scss/invoice_limit_slider.scss',
            'static/description/banner.png'
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'price': 149.0,
    'currency': 'EUR',
}
