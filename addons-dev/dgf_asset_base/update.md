## Оновлення модуля dgf_asset_base
- trancate cascade table dgf_asset_sale_import
- delete from ir_model where model in ('dgf.asset.sale.transaction', 'dgf.asset.sale.import')

- DROP TABLE public.dgf_asset_sale_transaction;
- DROP TABLE public.dgf_asset_sale_import;



