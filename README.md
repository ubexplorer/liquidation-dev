# Odoo project template
## Install dependencies
```bash
set PGPASSWORD='odoo' && pg_restore --username odoo --password=odoo --dbname liquidation --clean --verbose liquidation.dump
```

```bash
sudo add-apt-repository ppa:linuxuprising/libpng12 &&
sudo apt update &&
sudo apt install git python3-pip build-essential wget python3-dev python3-venv python3-wheel libxslt-dev libzip-dev libldap2-dev libsasl2-dev python3-setuptools libjpeg-dev libpng12-0 gdebi gcc libpq-dev -y
sudo apt-get install nodejs npm -y
sudo npm install -g rtlcss

wget -q -O - https://nightly.odoo.com/odoo.key | sudo gpg --dearmor -o /usr/share/keyrings/odoo-archive-keyring.gpg
echo 'deb [signed-by=/usr/share/keyrings/odoo-archive-keyring.gpg] https://nightly.odoo.com/14.0/nightly/deb/ ./' | sudo tee /etc/apt/sources.list.d/odoo.list
sudo apt-get update && sudo apt-get install odoo


sudo chown -R $USER:$USER /opt/
```

## Configure postgresql
```bash
sudo -u postgres createuser --superuser $(whoami)
psql --dbname template1 -c "alter role $(whoami) with password 'newpassword'"
```

## Configure git
```bash
git config --global user.name "SerhiiZavalko"
git config --global user.email sergey.zavalko@gmail.com
```

## Configure dev environment
### 20.0.4
```bash
python3 -m venv env
source env/bin/activate
mkdir filestore logs
git clone -b 18.0 --single-branch --depth 1 https://github.com/odoo/odoo.git src
env/bin/pip install setuptools wheel debugpy scrypt && env/bin/pip install -r src/requirements.txt
env/bin/pip install paramiko py3o.template py3o.formats
```

## Configure CPanel environment
```bash
python3 -m venv env
source env/bin/activate
mkdir src local bin filestore logs
git clone -b 16.0 --single-branch --depth 1 https://github.com/odoo/odoo.git odoo/src
env/bin/pip install setuptools wheel debugpy scrypt && env/bin/pip install -r src/odoo/requirements.txt
env/bin/pip install paramiko py3o.template py3o.formats
python\python.exe python\scripts\pip.exe install py3o.template
python\python.exe python\scripts\pip.exe install py3o.formats
python\python.exe python\scripts\pip.exe install openpyxl

python\python.exe python\scripts\pip.exe install py3o.fusion
python\python.exe python\scripts\pip.exe install service-identity
python\python.exe python\scripts\pip.exe install py3o.renderserver
python\python.exe python\scripts\pip.exe download py3o.renderserver
```



## Get config
```bash
src/odoo-bin --config odoo.conf --addons-path addons-default --data-dir filestore --save --stop-after-init
```

## Run server
```bash
bin/odoo
```



## Misc commands
### modules
```bash
python3 -c 'help("modules")'
```

### debug attach
```bash
python3 -m debugpy --listen 5678 src/odoo/odoo-bin -c odoo.conf
```

### ports
```bash
sudo ss -ltnp
```

### Ubuntu
```bash
xdg-open http://localhost:8069/web
chmod +x bin/odoo
ln -s ~/projects/learn/odoo/book/Odoo_14_Development_Cookbook.pdf ~/Desktop/OdooCookbook.pdf
```

### Odoo
```bash
src/odoo/odoo-bin scaffold scaffolded_module local-dev/
odoo-bin scaffold -h
odoo-bin scaffold -t path/to/template my_module
```
By default, Odoo has two templates in the /odoo/cli/templates directory. One is the default template, and the second is the theme template.

### errors
```log
Warn: Can't find .pfb for face 'Times-Roman'
git clone -b 15.0 --single-branch --depth 1 https://github.com/OCA/web.git odoo-web/15.0
```


D:\portable\LibreOfficePortable\App\libreoffice\program\soffice.exe --headless --convert-to 'docx' import\file.odt

soffice --headless --convert-to pdf "D:\projects\coding\odoo\project\dgf\liquidation-dev\import\file.odt" --outdir c:\temp
soffice --headless --convert-to docx "D:\projects\coding\odoo\project\dgf\liquidation-dev\import\file.odt" --outdir c:\temp
soffice --headless --convert-to docx file.odt
soffice --headless --convert-to docx file.odt -env:UserInstallation=file:C:\Users\serge\AppData\Local\Temp
soffice --headless --convert-to docx file.odt -env:UserInstallation=file:///C:/Users/serge/AppData/Local/Temp/
soffice --headless --convert-to docx file.odt -env:UserInstallation=file:C:\\Users\\serge\\AppData\\Local\\Temp\\


C:\Program Files\LibreOffice\program\


```bash
subprocess.CalledProcessError:
Command '['D:\\portable\\LibreOfficePortable\\App\\libreoffice\\program\\soffice.exe', '--headless', '--convert-to', 'docx', 'C:\\Users\\serge\\AppData\\Local\\Temp\\p3o.report.tmp.fr22ozud.ods', '-env:UserInstallation=file:C:\\Users\\serge\\AppData\\Local\\Temp\\tmpy8ot7kum']' returned non-zero exit status 1.
```
