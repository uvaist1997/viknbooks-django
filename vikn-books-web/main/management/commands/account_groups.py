from __future__ import print_function
from django.core.management import call_command
from django.shortcuts import render, get_object_or_404
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import datetime
from finance.models import AccountGroup


class Command(BaseCommand):
    
    def handle(self, *args, **options):

        user = User.objects.get(id=1)
        
        if AccountGroup.objects.filter(name='bank_account').exists():
            print ("Account Group with name Bank Account already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="asset",
                name="bank_account",
                auto_id=1,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='capital_account').exists():
            print ("Account Group with name Capital Account already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="liability",
                name="capital_account",
                auto_id=2,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='cash_in_hand').exists():
            print ("Account Group with name cash_in_hand already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="asset",
                name="cash_in_hand",
                auto_id=3,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='current_asset').exists():
            print ("Account Group with name current_asset already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="asset",
                name="current_asset",
                auto_id=4,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='current_liability').exists():
            print ("Account Group with name current_liability already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="liability",
                name="current_liability",
                auto_id=5,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='direct_expense').exists():
            print ("Account Group with name direct_expense already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="expense",
                name="direct_expense",
                auto_id=6,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='direct_income').exists():
            print ("Account Group with name direct_income already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="income",
                name="direct_income",
                auto_id=7,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='fees').exists():
            print ("Account Group with name fees already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="income",
                name="fees",
                auto_id=8,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='indirect_expense').exists():
            print ("Account Group with name indirect_expense already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="expense",
                name="indirect_expense",
                auto_id=9,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='indirect_income').exists():
            print ("Account Group with name indirect_income already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="income",
                name="indirect_income",
                auto_id=10,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='loans_and_liability').exists():
            print ("Account Group with name loans_and_liability already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="liability",
                name="loans_and_liability",
                auto_id=11,
                creator=user,
                updater=user
            )
       
        if AccountGroup.objects.filter(name='fitre_zakat_collection').exists():
            print ("Account Group with name fitre_zakat_collection already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="income",
                name="fitre_zakat_collection",
                auto_id=12,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='fitre_zakat_distribution').exists():
            print ("Account Group with name fitre_zakat_distribution already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="expense",
                name="fitre_zakat_distribution",
                auto_id=13,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='zakat_collection').exists():
            print ("Account Group with name zakat_collection already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="income",
                name="zakat_collection",
                auto_id=14,
                creator=user,
                updater=user
            )

        if AccountGroup.objects.filter(name='zakat_distribution').exists():
            print ("Account Group with name zakat_distribution already exists")
        else:
            AccountGroup.objects.create(
                is_system_generated=True,
                is_deleted=False,
                category_type="income",
                name="zakat_distribution",
                auto_id=15,
                creator=user,
                updater=user
            )

