from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.management.commands import loaddata
from django.core.management import call_command
from users.models import DatabaseStore
import psycopg2
from brands import models
import os


class Command(BaseCommand):


	def handle(self, *args, **options):
		try:
			records = DatabaseStore.objects.filter(is_process=False)
			print("hello")
			call_command("makemigrations", interactive=False)
			for row in records:
				database = 'default'+str(row.id)
				call_command("migrate", database=database, interactive=False)
				call_command('loaddata', 'initial_datas',database=database, verbosity=0)
				company = models.CompanySettings(
					CompanySettingsID=row.id,
					CompanyName=row.CompanyName,
					Address1=row.Address1,
					Address2=row.Address2,
					Address3=row.Address3,
					City = row.city,
					State = row.state,
					Country = row.country,
					PostalCode = row.postalcode,
					Phone=row.phone,
					Mobile = row.mobile,
					EmailAddress = row.email,
					Website = row.website,
					CurrencyID = row.currency,
					FractionalUnit = row.fractionalunit,
					CreatedDate=row.CreatedDate,
					db_name=database,
					TaxNumber = row.tax1,
					CreatedUserID = row.customerid,

				)
				company.save(using=database)
				companyLog = models.CompanySettings_Log(
					TransactionID=row.id,
					CompanyName=row.CompanyName,
					Address1=row.Address1,
					Address2=row.Address2,
					Address3=row.Address3,
					City = row.city,
					State = row.state,
					Country = row.country,
					PostalCode = row.postalcode,
					Phone=row.phone,
					Mobile = row.mobile,
					EmailAddress = row.email,
					Website = row.website,
					CurrencyID = row.currency,
					FractionalUnit = row.fractionalunit,
					CreatedDate=row.CreatedDate,
					db_name=database,
					TaxNumber = row.tax1,
					CreatedUserID = row.customerid,

				)
				companyLog.save(using=database)

				DatabaseStore.objects.filter(pk=row.id).update(is_process=True)

		except (Exception, psycopg2.Error) as error :
		    print ("Error while connecting to PostgreSQL", error)

		
		print("Process successfully completed")