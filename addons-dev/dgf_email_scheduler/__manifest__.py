
{
    'name': 'DGF Email Scheduler',
    'version': '14.0',
    'author': 'PPTS [India] Pvt.Ltd',
    'category': 'Liquidation/General',
    'license': 'LGPL-3',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base', 'mail'],
    'description': """
    This module will generate emails based on the selected templates.""",
    'data': [
        'security/ir.model.access.csv',
        'data/email_reminder_cron.xml',
        'views/email_scheduler_view.xml',
        'views/email_scheduler_menu.xml',
    ],
    'images': [''],
    'installable': True,
    'auto_install': False,
    'application': False,
}
