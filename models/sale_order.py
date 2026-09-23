from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_loyalty_years = fields.Integer(string='Customer Loyalty Years', default=0)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.depends('product_uom_qty','discount','price_unit','order_id.customer_loyalty_years')
    def _compute_amount(self):
        for line in self:
            if line.order_id.customer_loyalty_years > 2 and line.product_uom_qty > 50:
                line.discount = 15.0
            else:
                line.discount = line.discount or 0.0
        super(SaleOrderLine,self)._compute_amount()
    
    @api.onchange('product_uom_qty')
    def _onchange_quantity_pricing(self):
        for line in self:
            if line.order_id.customer_loyalty_years > 2 and line.product_uom_qty > 50:
                line.discount = 15.0
            else:
                line.discount = 0.0