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

BASE_DIR = "/home/vikncodes/django/viknbooks_erp/src/testproject"


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            today = date.today()
            # call_command(f"dumbdata > {today}.json", interactive=False)
            # call_command('loaddata', 'initial_datas',database=database, verbosity=0)
            folder = f"{BASE_DIR}/database_backup/"
            if not path.exists(folder):
                os.mkdir(folder)
                os.chmod(folder, 0o777)
            else:
                pass
            sysout = sys.stdout
            sys.stdout = open(f"{folder}{today}.json", "w")
            os.chmod(f"{folder}{today}.json", 0o777)
            call_command("dumpdata", exclude=["contenttypes", "auth.permission"])
            sys.stdout = sysout
            os.system(f"cd {folder} \nzip -r {folder}{today}.zip {today}.json")
            if path.exists(f"{folder}{today}.json"):
                os.remove(f"{folder}{today}.json")
            else:
                pass

            old_Data = today - timedelta(days=4)

            if path.exists(f"{folder}{old_Data}.zip"):
                os.remove(f"{folder}{old_Data}.zip")
            else:
                pass

        except Exception as error:
            print(error)

        print("Process successfully completed")
