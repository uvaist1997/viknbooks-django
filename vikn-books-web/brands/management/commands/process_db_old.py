from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.management.commands import loaddata
from django.core.management import call_command
from users.models import DatabaseStore
import psycopg2
from brands import models
import os
from os import path
from datetime import date, timedelta
import sys


BASE_DIR = "/home/vikncodes/Documents/suhaib/django/erp/src/testproject"
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
            sys.stdout = open(f"{folder}{today}.json", 'w')
            os.chmod(f"{folder}{today}.json", 0o777)
            call_command('dumpdata',exclude=['contenttypes', 'auth.permission'])
            sys.stdout = sysout
            
            old_Data = today - timedelta(days=25)

            if path.exists(f"{folder}{old_Data}.json"):
                os.remove(f"{folder}{old_Data}.json")
            else:
                pass

        except Exception as error :
            print(error)
        
        print("Process successfully completed")