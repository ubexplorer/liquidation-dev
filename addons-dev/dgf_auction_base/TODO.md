Підготовка:
- видалити контакт з id=5519
- зіставити статуси лотів з статусами аукціонів (можливо зробити це програмно через послідовність в різних xml-файлах)
- запустити стартовий крон
- оновити всі аукціони

- оновити Аукціон не відбувся (договорів = 1678, до оновлення)


Рефакторинг:
+ скопіювати моделі та перегляди до "dgf_auction_sale"
+ залишити в "dgf_auction_sale" базові поля, решту - в "dgf_auction_sale"
+ в модулі аукціонів з продажу наслідувати перегляди в режимі "primary"
+ не використовувати "res_config_settings" для нумерації лотів, в "res_config_settings" визначати спільлні налаштування для усіх категорій аукціонів, та за категоріями в окремих розділах сторінки налаштувань
+ перемістити "res_config_settings" до "dgf_auction_base". в категорійних модулях доповнювати базовий "res_config_settings"
+ значення стану аукціону в "data"
+ прибрати верхній рівень табів у формі аукціону
+ довідник методів аукціону (або selection)
+ оновити механізми синхронізації статусів аукціону та лоту
+ встановити залежність "dgf_auction_base" від модулю 'agreement'
+ додати на форму договору посилання на аукціон та лот
+ визначення банку на договорі з аукціону:
- змапити stage_id договору зі значенням status
- перенести до dgf_auction_base/dgf_procedure заглушки базових методів. Якщо тип аукцоіну generic - USerError 'Not implemented'
- додати до лоту m2m поле класифікації items
- додати модель items, звязати з лотом
; agreement
for record in records:
  partner_id = record.procedure_id.partner_id
  company_id = partner_id.company_ids
  write_values = {'company_id': company_id.id}
  record.write(write_values)
  # record.message_post(body="write_values: {}".format(write_values))
- додати правило запису для договорів
- переробити усі правила запису в Аукціонах, Активах, Документах за прикладом договорів

- реалізувати спосіб оновлення статусу лоту (при створенні та оновленні аукціону) за хронологічно останнім аукціоном:
  # на лоті
  for record in records:
    auction_ids = record.auction_ids
    last_id = max(d.id for d in auction_ids)
    last_auction = env['dgf.procedure'].browse(last_id)
    last_date = last_auction.date_modified
    lot_stage_id = last_auction.stage_id.lot_stage_id.id
    write_values = {'stage_id_date': last_date, 'stage_id': lot_stage_id}
    record.write(write_values)

- додати до лоту посилання на:
  - успішний аукціон m2o
  - ціну продажу
  - покупця

- обовязковість полів визначати в XML на формі
- додати поле "Куратор" на банк, на аукціон
- замінити модель 'dgf_procedure_contract' в модулях "dgf_auction_base" та "dgf_auction_sale"на розширення модулю 'agreement'

- в методах АРІ передбачити передавання "category_id" ланцюжками



Після видалення перед повторним завантаженням аукціонів:
  - "delete from mail_followers where res_model in ('dgf.procedure.lot', 'dgf.procedure', 'dgf.procedure.contract')"
  - "delete from mail_message where model in ('dgf.procedure.lot', 'dgf.procedure', 'procedure.contract')"

lot-sequence:
SL-%(year)s%(month)s%(day)s-

Аукціони:
- створити типи аукціонів (продаж, оренда)
- створити методи:
  - отримання аукціонів за організатором
  - отримання аукціонів за датою модифікації
  - вставка/оновлення аукціонів
  - регулярне оновлення незавершених аукціонів
- створити перегляди:

Лоти:
- створити типи лотів (продаж, оренда), на яких визначити послідовності для нумерації
- створити методи:
  - отримання аукціонів за організатором
  - отримання аукціонів за датою модифікації
  - вставка/оновлення аукціонів
  - регулярне оновлення незавершених аукціонів
- створити перегляди:

report_py3o & web_responsive updated

- models/py3o_report (fix file conversion on Windows):
   if user_installation:
    pass
    # cmd.append("-env:UserInstallation=file:%s" % user_installation)
- controllers/main (fix fix mimetype):
  if not filename.endswith(filetype):
    filename = "{}.{}".format(filename, filetype)
  content_type = "application/vnd.oasis.opendocument.text"
  # content_type = mimetypes.guess_type("x." + filetype)[0]