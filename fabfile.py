from cuisine import *
from fabric.api import *
from fabric.context_managers import *
from fabric.utils import puts
from fabric.colors import red, green


GIT_REPO = 'https://github.com/bobuss/py-imageable.git'
env.user = 'ubuntu'
env.key_filename = 'insset-key.pem'

def app_user(command):
    '''
    This helper method runs the given command as the webapp user.
    '''
    sudo(command, user='redacted_webapp')


def production():
    puts(red('Using PRODUCTION settings'))
    env.hosts = ['ec2-54-211-208-206.compute-1.amazonaws.com']


def setup_packages():
    puts(green('Installing Ubuntu packages'))
    sudo('apt-get update')
    package_ensure('nginx')
    package_ensure('supervisor')
    package_ensure('git-core')

    package_ensure('python-pip')
    package_ensure('python-imaging')


def setup_users():
    puts(green('Creating Ubuntu users'))

    user_ensure('redacted_webapp')




def configure_nginx():
    puts(green('Configuring Nginx web server'))

    config_template = text_strip_margin('''
    |
    |server {
    |   listen 80
    |
    |   access_log /srv/redacted-webapp/logs/nginx_access.log;
    |
    |   location /static/ {
    |       alias /srv/redacted-webapp/src/media/;
    |       autoindex on;
    |   }
    |
    |   location /media/ {
    |       alias /srv/redacted-webapp/shortcuts/admin_media/;
    |   }
    |
    |   location / {
    |       proxy_pass http://127.0.0.1:5000/;
    |       proxy_redirect off;
    |       proxy_set_header Host $host;
    |       proxy_set_header   X-Real-IP        $remote_addr;
    |       proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
    |   }
    |
    |}
    |
    ''')

    file_write('/etc/nginx/sites-available/redacted.conf', config_template)

    if not dir_exists('/srv/redacted-webapp/shortcuts/admin_media'):
        run('ln -s /usr/local/lib/python2.6/dist-packages/django/contrib/admin/media /srv/redacted-webapp/shortcuts/admin_media')

    if file_exists('/etc/nginx/sites-enabled/default'):
        sudo('rm /etc/nginx/sites-enabled/default')

    if not file_exists('/etc/nginx/sites-enabled/redacted.conf'):
        sudo('ln -s /etc/nginx/sites-available/redacted.conf /etc/nginx/sites-enabled/redacted.conf')

    sudo('service nginx reload')




def configure_supervisor():
    puts(green('Configuring the supervisor process'))

    runner_script = text_strip_margin('''
    |#!/bin/bash
    |
    |cd /srv/redacted-webapp/src
    |exec gunicorn_django --bind=127.0.0.1:9001
    |
    ''')

    file_write('/srv/redacted-webapp/bin/runserver', runner_script, mode='a+rx')

    supervisor_conf = text_strip_margin('''
    |
    |[program:redacted-webapp]
    |command=/srv/redacted-webapp/bin/runserver
    |user=redacted_webapp
    |
    ''')

    file_write('/etc/supervisor/conf.d/redacted.conf', supervisor_conf)


def setup_folders():
    puts(green('Setting up on-disk folders'))

    dir_ensure('/srv/redacted-webapp', owner='redacted_webapp', group='redacted_webapp')
    dir_ensure('/srv/redacted-webapp/src/media', owner='redacted_webapp', group='redacted_webapp')
    dir_ensure('/srv/redacted-webapp/shortcuts', owner='redacted_webapp', group='redacted_webapp')
    dir_ensure('/srv/redacted-webapp/logs', owner='www-data', group='www-data')
    dir_ensure('/srv/redacted-webapp/bin', owner='www-data', group='www-data')


def clone_from_github():

    puts(green('Fetching latest code from GitHub'))

    with cd('/srv/redacted-webapp/'):

        if dir_exists('/srv/redacted-webapp/src'):
            with cd('/srv/redacted-webapp/src'):
                app_user('git checkout -- .')
                app_user('git pull')
        else:
            app_user('git clone %s src' % GIT_REPO)

    with cd('/srv/redacted-webapp/src'):

        puts(green('Installing app dependencies'))

        run('pip install -r requirements.txt')




def restart_web_server():
    puts(green('Reloading the supervisor process'))

    sudo('supervisorctl reload')


def deploy():
    puts(green('Starting deployment'))
    setup_packages()
    setup_users()
    setup_folders()
    configure_nginx()
    configure_supervisor()
    clone_from_github()
    restart_web_server()
