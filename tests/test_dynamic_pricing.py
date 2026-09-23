from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestDynamicPricingEngine(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Set up transactional baseline data records for the test execution path."""
        super(TestDynamicPricingEngine, cls).setUpClass()
        
        # 1. Create a baseline customer profile
        cls.customer = cls.env['res.partner'].create({
            'name': 'Wholesale Alpha Corp',
        })
        
        # 2. Create a standard warehouse product catalog item
        cls.product = cls.env['product.product'].create({
            'name': 'Industrial Bulk Widget',
            'lst_price': 100.0,  # Base list price valuation
        })

    def test_01_standard_pricing_no_discount(self):
        """Verify that standard profiles below the loyalty threshold receive zero wholesale discount."""
        order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'customer_loyalty_years': 1,  # Below the 2-year threshold limit
        })
        
        line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': self.product.id,
            'product_uom_qty': 60.0,     # Above the quantity criteria, but loyalty fails
            'price_unit': 100.0,
        })
        
        # Explicitly call the computational sub-total calculation layer
        line._compute_amount()
        self.assertEqual(line.discount, 0.0, "Should register 0% discount: customer loyalty matrix is too low.")

    def test_02_wholesale_bulk_discount_applied(self):
        """Verify that lines matching both parameters successfully trigger the 15% wholesale discount."""
        order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'customer_loyalty_years': 5,  # Satisfies > 2 years logic gate
        })
        
        line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': self.product.id,
            'product_uom_qty': 55.0,     # Satisfies > 50 units logic gate
            'price_unit': 100.0,
        })
        
        line._compute_amount()
        self.assertEqual(line.discount, 15.0, "Should register 15% discount: wholesale conditions met.")
