# -*- coding: utf-8 -*-
{
    'name': 'MJB - Knowledge Export Child PDF',
    'version': '17.0.1',
    'author': "Majorbird",
    'website': "majorbird.cn",
    'category': 'Productivity',
    'depends': [
        'base',
        'knowledge',
        'web',
        'web_editor',
        'web_unsplash',
    ],
    'data': [
        'data/ir_actions_server.xml',
    ],
    'qweb': [],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
    'assets': {
        'web.assets_backend': [
            'mjb_knowledge_export_pdf/static/src/**/*',
            'mjb_knowledge_export_pdf/static/src/scss/knowledge_views_custom.scss',
        ],
    },
}
