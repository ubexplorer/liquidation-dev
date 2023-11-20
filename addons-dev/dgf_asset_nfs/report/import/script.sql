--update dgf_document dd
--set "name" = replace (replace (dd."name", '[', ''), ']', '')
update dgf_document dd
set "name" = replace (dd."name", 'Рішення протокольне', 'Протокольне рішення')