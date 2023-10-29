
{
    'name': "Facebook Messenger in Odoo Website",
    'version': '17.0',
    'category': 'Marketing',
    'summary': 'Facebook Messenger. '
               'This helps your customers to contact you using Facebook Messenger.',
    'description': "Let's make it easier for your customers to contact you by"
                   "using Facebook Messenger.",
    'author': 'Cybrosys Techno Solutions',
    'depends': ['base', 'website', 'website_sale'],
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'images': ['static/description/banner.png'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/fb_chatter_templates.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
