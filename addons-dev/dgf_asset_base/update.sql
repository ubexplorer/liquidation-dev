-- Copy DB on server
-- psql --host "localhost" --port "5432" --username "bionic" --dbname="liquidation"
-- -c "CREATE DATABASE "liquidation-stage" WITH TEMPLATE liquidation OWNER 'odoo-dev';"

-- Оновлення модуля dgf_asset_base
TRUNCATE TABLE public.dgf_asset_sale_import RESTART IDENTITY CASCADE;
DROP TABLE public.dgf_asset_sale_transaction;
DROP TABLE public.dgf_asset_sale_import;
delete from ir_model where model in ('dgf.asset.sale.transaction', 'dgf.asset.sale.import')
