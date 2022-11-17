import os
import sys
from datetime import date, timedelta
from os import path

import psycopg2
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands import loaddata
from django.utils import timezone

from brands import models
from users.models import DatabaseStore
from subprocess import PIPE, Popen
import shlex

# BASE_DIR = "/home/vikncodes/django/viknbooks_erp/src/testproject"
BASE_DIR = "/home/vikncodes/django/viknbooks/src/testproject"



def dump_table(host, dbname, user, password, bckup_name, **kwargs):
    command = f'pg_dump --host={host} ' \
        f'--dbname={dbname} ' \
        f'--username={user} ' \
        f'--no-password ' \
        f'--file="{BASE_DIR}/database_backup/"{bckup_name} '

    proc = Popen(command, shell=True, env={
        'PGPASSWORD': password
    })
    proc.wait()


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            today = date.today()
            folder = f"{BASE_DIR}/database_backup/"
            if not path.exists(folder):
                os.mkdir(folder)
                os.chmod(folder, 0o777)
            else:
                pass
            bckup_name = str(today) + ".sql"
            dump_table('localhost', 'viknbooks',
                       'vikncodes', 'vikncodes123', bckup_name)

            if path.exists(f"{folder}{bckup_name}"):
                os.system(
                    f"""
                    cd {folder}
                    zip -r {today}.zip {today}.sql 
                    rm {today}.sql
                    """
                )

            old_Data = today - timedelta(days=4)
            if path.exists(f"{folder}{old_Data}.zip"):
                os.remove(f"{folder}{old_Data}.zip")
            else:
                pass

        except Exception as error:
            print(error)

        print("Process successfully completed")
