# Project 3: Smart Dynamic Pricing Engine for Sales 📈💸

An enterprise-grade wholesale bulk pricing matrix and automated discount engine that extends the core Odoo Sales ecosystem.

## 📋 Business Case & Problem Statement
Wholesale business distribution models require dynamic pricing adaptations based on customer historical accounts and real-time transaction volumes. Manually tracking and applying percentage adjustments creates intense administrative lag, spikes ordering input mistakes, and complicates product list structures unnecessarily.

**The Solution:** This application inherits directly from Odoo’s foundational Sales core apps (`sale.order` and `sale.order.line`). It hooks an automated discount calculation mechanism directly into the base computation matrix. When an eligible high-loyalty wholesale customer purchases in high volume, the system automatically writes a 15% pricing reduction directly to the transaction layer—recalculating document subtotals on the fly without user intervention.

---

## 🛠️ Key Technical Implementations
* **Advanced Core ORM Class Inheritance:** Safely extended foundational enterprise database columns (`sale.order` and `sale.order.line`) using standard model inheritance structures (`_inherit`) without modifying the original base code files.
* **Pipeline Computation Interceptions:** Overrode the core subtotal calculation engine (`_compute_amount`), intercepting the execution thread to safely evaluate business rule matrices before passing final financial values back up to the native ledger using explicit `super()` wrappers.
* **Proactive State Fallback Caching:** Engineered rigorous conditional branch loops that enforce value allocations under every logical outcome path—preventing transactional cache invalidation breaks and `NewId` evaluation failures.
* **Real-Time Client-Side Reactive Updates:** Developed active front-end screen triggers using `@api.onchange` mappings to track quantity alterations live, instantaneously wiping or applying discount structures right on the salesperson's viewport matrix.

---

## 🗂️ Module Directory Structure
```text
sale_dynamic_pricing/
├── __manifest__.py                  # Module descriptor declaring 'sale' as a core dependency
├── __init__.py                      # Python package initializers
├── models/
│   ├── __init__.py
│   ├── sale_order.py                # Core sale.order extension properties
│   └── sale_order_line.py           # Computation overrides and onchange triggers
├── tests/
│   ├── __init__.py
│   └── test_dynamic_pricing.py      # Automated TransactionCase regression suites
└── views/
    └── sale_order_views.xml         # XPath inheritance layout rules mapping fields to UI
```

---

## 🔩 Technical Specifications & Code Snippets

### Core Business Logic Computation Overrides (Python)
```python
@api.depends('product_uom_qty', 'discount', 'price_unit', 'order_id.customer_loyalty_years')
def _compute_amount(self):
    for line in self:
        if line.order_id and line.order_id.customer_loyalty_years > 2 and line.product_uom_qty > 50:
            line.discount = 15.0
        else:
            line.discount = line.discount or 0.0
    super(SaleOrderLine, self)._compute_amount()
```

### UI Presentation Layer Injections (XML XPath)
```xml
<record id="view_order_form_inherit_loyalty_pricing" model="ir.ui.view">
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='partner_id']" position="after">
            <field name="customer_loyalty_years"/>
        </xpath>
    </field>
</record>
```

---

## 🚀 Deployment & Installation Checklist
1. Export the module repository code to your target deployment `custom_addons` directories.
2. Verify that your `__manifest__.py` file declares `['sale']` inside its installation context `depends` array to allow correct extension class matching.
3. Refresh the application registries via *Apps -> Update Apps List*.
4. Initialize the package (`sale_dynamic_pricing`). Execute your automated unit tests via terminal command flags to verify database mapping safety:
```bash
odoo-bin -c /etc/odoo.conf -d your_database -i sale_dynamic_pricing --test-enable
```
