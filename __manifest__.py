{
    'name': 'Smart Pricing Engine',
    'summary': 'Smart Dynamic Pricing Engine for E-commerce/Sales',
    'description': """Smart Dynamic Pricing Engine for E-commerce/Sales""",
    'author': 'Chike Chiagbaizu',
    'maintainer': 'Chike Chiagbaizu',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
    'sequence': 1,
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
}