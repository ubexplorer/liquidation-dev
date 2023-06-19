## Stage environment
### Restore DB from backup
- rename existing DB
- edit *.conf "list_db=True" ?
- restart service:  `sudo systemctl restart odoo` ?
- restore backup to the new DB woth the same name
- stop service:  `sudo systemctl stop odoo`
- run Odoo from another user (`odoo`):
```
sudo -H -u odoo bash -c '/usr/bin/python3 /usr/bin/odoo --config /etc/odoo/odoo.conf --logfile None --database liquidation --update all'
```
[OR]
```
sudo su - odoo -s /bin/bash && /usr/bin/python3 /usr/bin/odoo --config /etc/odoo/odoo.conf --database liquidation --update all --logfile None
```

- edit *.conf "list_db=False"
- start service:  `sudo systemctl start odoo`

### Configure modules
- install, then uninstall "Gmail*"
- uninstall:
    - google_account
    - iap_alternative_provider
    - server_environment
    - dgf_enforcement?
- copy modules:
    - dgf_currency_rate_nbu
    - dgf_enforcement
    - dgf_bankr_monitoring (later. after changes be made)
    - dgf_iap_provider
    - dgf_iap_vkursi
    - dgf_iap_vkursi_contacts
- install:
    - dgf_iap_provider
    - dgf_iap_vkursi
    - dgf_iap_vkursi_contacts
    - dgf_currency_rate_nbu
    - dgf_enforcement
- update:
    - dgf_bankr_monitoring (later. after changes be made)


## Prod environment