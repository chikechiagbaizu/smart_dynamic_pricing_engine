from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_loyalty_years = fields.Integer(string='Customer Loyalty Years', default=0)