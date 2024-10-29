{
    'name': 'Task type',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Liquidation/Project',
    'license': 'OPL-1',
    'version': '14.0.1.0.2',

    'depends': [
        'project',
        # 'base',
        # 'web'
    ],
    'data': [
        'report/report.xml',
        'report/templates.xml',
        'security/ir.model.access.csv',
        'views/task_view.xml',
    ],

    'installable': True,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],
}
