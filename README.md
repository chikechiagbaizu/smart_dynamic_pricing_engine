# sale_dynamic_pricing

An Odoo module that automatically applies a 15% discount to sales order lines when a loyal customer orders in bulk.

I built this as an early Odoo project to learn model inheritance, computed fields, and view extension. It is small on purpose: one rule, one extra field, one set of tests.

## What it does

Sales reps in a wholesale business often give discounts to long-standing customers who buy in volume. Doing that by hand is slow and easy to get wrong, so this module does it on the quotation.

| Condition | Result |
|---|---|
| Customer loyalty is more than 2 years **and** line quantity is more than 50 | Discount is set to 15% |
| Otherwise, when totals are recomputed | The existing discount is kept |
| Otherwise, when the quantity is edited in the form | The discount is reset to 0 |

Example: a customer with 3 loyalty years orders 60 units at 10.00. The line total is 510.00 instead of 600.00, with no manual input. If the rep lowers the quantity to 40, the discount drops back to 0 and the total returns to 400.00.

## What's in it

- A `customer_loyalty_years` integer field (default 0) added to `sale.order` and shown on the quotation form, right after the customer. It is entered by hand.
- Discount logic on `sale.order.line`, evaluated whenever quantity, price, discount, or the order's loyalty value changes.
- An `@api.onchange` handler on quantity so the discount updates in the form while the user is typing, before saving.
- Two regression tests using `TransactionCase` (see [Tests](#tests)).

No core Odoo files are modified. Everything uses `_inherit` and view inheritance.

## Structure

```text
sale_dynamic_pricing/
├── __manifest__.py              
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── sale_order.py            
│   └── sale_order_line.py    
├── tests/
│   ├── __init__.py
│   └── test_dynamic_pricing.py
└── views/
    └── sale_order_views.xml  
```

## How it works

The new field on the order:

```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_loyalty_years = fields.Integer(string='Customer Loyalty Years', default=0)
```

The discount rule on the order line. `_compute_amount` sets the discount if the customer qualifies, then calls `super()` so Odoo's normal subtotal and tax calculation still runs. The onchange applies the same rule live in the form:

```python
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'order_id.customer_loyalty_years')
    def _compute_amount(self):
        for line in self:
            if line.order_id.customer_loyalty_years > 2 and line.product_uom_qty > 50:
                line.discount = 15.0
            else:
                line.discount = line.discount or 0.0
        super(SaleOrderLine, self)._compute_amount()

    @api.onchange('product_uom_qty')
    def _onchange_quantity_pricing(self):
        for line in self:
            if line.order_id.customer_loyalty_years > 2 and line.product_uom_qty > 50:
                line.discount = 15.0
            else:
                line.discount = 0.0
```

Every branch assigns a value to `discount`, which avoids errors on unsaved lines (`NewId` records) while a quotation is still being edited.

The loyalty field is added to the form with an XPath:

```xml
<xpath expr="//field[@name='partner_id']" position="after">
    <field name="customer_loyalty_years"/>
</xpath>
```

## Installation

1. Copy `sale_dynamic_pricing/` into a directory on your `addons_path`.
2. Restart Odoo and update the apps list (Apps, then Update Apps List).
3. Install **sale_dynamic_pricing**, or from the command line:

```bash
odoo-bin -c /etc/odoo.conf -d your_database -i sale_dynamic_pricing
```

## Tests

Run them against a throwaway database, not one with real data:

```bash
odoo-bin -c /etc/odoo.conf -d your_test_database -i sale_dynamic_pricing --test-enable --stop-after-init
```

`tests/test_dynamic_pricing.py` creates a customer and a product (list price 100.0) in `setUpClass`, then checks two cases. Each test creates a quotation and one order line, calls `_compute_amount()` on the line, and asserts the discount:

| Test | Loyalty years | Quantity | Expected discount |
|---|---|---|---|
| `test_01_standard_pricing_no_discount` | 1 | 60 | 0% (loyalty too low) |
| `test_02_wholesale_bulk_discount_applied` | 5 | 55 | 15% (both conditions met) |

**Not covered yet:**

- The boundary values (exactly 2 years, exactly 50 units).
- A qualifying customer with a quantity that is too low.
- The `@api.onchange` handler, including the reset-to-0 behaviour.
- Changing the loyalty years after the line already exists.
- The resulting line subtotal and order total (only the discount is asserted).
- Manual discounts being kept, overwritten, or reset.

## Usage

1. Go to Sales, then Quotations, and create a quotation.
2. Pick a customer and set **Customer Loyalty Years**.
3. Add a product line with a quantity over 50.
4. The discount on that line becomes 15% and the totals update.

## Limitations

- **Hardcoded rule.** The 2 years, 50 units, and 15% values are written in the code. Changing them means editing Python.
- **Loyalty is entered by hand.** It is a plain integer on the order, not calculated from the customer's order history, so it can be wrong or forgotten. It also has to be set on every quotation.
- **No manual override on qualifying lines.** Because `discount` is in the `@api.depends` list, typing a different discount on a qualifying line triggers a recompute that sets it back to 15%.
- **Quantity edits wipe manual discounts.** The onchange resets the discount to 0 when a line doesn't qualify, so a hand-entered discount is lost if the quantity changes afterward. The compute method behaves differently (it keeps the existing value), so the two code paths are inconsistent.
- **Duplicated logic.** The same condition appears in both the compute method and the onchange.
- **Discount set inside `_compute_amount`.** This works, but computing the discount inside the amount calculation is not the cleanest approach. A separate compute method for `discount` would be better. In recent Odoo versions `discount` on order lines is already a computed field, so this may behave differently there.
- **Thin test coverage.** Only two cases are tested and only the discount field is checked, not the totals or the onchange path.
- Tested against one Odoo version only (fill in the version you used).

## Possible improvements

- Move the thresholds and percentage into settings.
- Calculate loyalty years from the customer's first confirmed order.
- Compute the discount in one place (a dedicated compute method) and remove the duplicate onchange.
- Add tests for the boundaries, the onchange, and the line and order totals.
- Support tiers (for example 5%, 10%, 15%).
- Allow users in a specific group to override the automatic discount.

## License

LGPL-3 (change this if your manifest says otherwise).