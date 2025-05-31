{
    "name": "ФГВ: Активи лоту",
    "summary": "Модуль поєднує 'Активи' з лотами в процедурах продажу та користування.",
    "version": "14.0.1.1.0",
    "category": "Liquidation/Assets",
    "author": "DGF",
    "website": "",
    "license": "AGPL-3",
    "depends": [
        "dgf_asset_base",
        "dgf_auction_base",
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/dgf_asset_base_views.xml',
        'views/dgf_procedure_lot_views.xml',
        'views/dgf_procedure_lot_asset_views.xml',        
    ],
    "demo": [],
    "maintainers": [
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
