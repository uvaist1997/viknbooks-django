
from __future__ import print_function
from django.core.management import call_command
from django.shortcuts import render, get_object_or_404
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import datetime
from finance.models import AccountHead, AccountGroup


class Command(BaseCommand):
    
    def handle(self, *args, **options):

        user = User.objects.get(id=1)
        fees_account_group = AccountGroup.objects.get(is_system_generated=True,name="fees")
        indirect_income = AccountGroup.objects.get(is_system_generated=True,name="indirect_income")
        direct_income = AccountGroup.objects.get(is_system_generated=True,name="direct_income")
        cash_account_group = AccountGroup.objects.get(is_system_generated=True,name="cash_in_hand")
        fitre_zakat_distribution = AccountGroup.objects.get(is_system_generated=True,name="fitre_zakat_distribution")
        fitre_zakat_collection = AccountGroup.objects.get(is_system_generated=True,name="fitre_zakat_collection")
        zakat_collection = AccountGroup.objects.get(is_system_generated=True,name="zakat_collection")
        zakat_distribution = AccountGroup.objects.get(is_system_generated=True,name="zakat_distribution")

        #create initial product units
        if AccountHead.objects.filter(name='cash').exists():
            print ("Account Heads with name cash already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = cash_account_group,
                is_deleted=False,
                name="cash",
                auto_id=1,
                creator=user,
                updater=user
            )

        if AccountHead.objects.filter(name='subscription_fee').exists():
            print ("Account Heads with name subscription_fee already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = fees_account_group,
                is_deleted=False,
                name="subscription_fee",
                auto_id=2,
                creator=user,
                updater=user
            )

        if AccountHead.objects.filter(name='pending_balance').exists():
            print ("Account Heads with name pending_balance already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = fees_account_group,
                is_deleted=False,
                name="pending_balance",
                auto_id=3,
                creator=user,
                updater=user
            )

        if AccountHead.objects.filter(name='special_subscription_fee').exists():
            print ("Account Heads with name special subscription fee already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = fees_account_group,
                is_deleted=False,
                name="special_subscription_fee",
                auto_id=4,
                creator=user,
                updater=user
            )

        if AccountHead.objects.filter(name='qabar_fee').exists():
            print ("Account Heads with name qabar fee already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = indirect_income,
                is_deleted=False,
                name="qabar_fee",
                auto_id=5,
                creator=user,
                updater=user
            )

        if AccountHead.objects.filter(name='donation').exists():
            print ("Account Heads with name donation already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = indirect_income,
                is_deleted=False,
                name="donation",
                auto_id=6,
                creator=user,
                updater=user
            )
        if AccountHead.objects.filter(name='fitre_zakat_fee').exists():
            print ("Account Heads with name fitre zakat collection already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = direct_income,
                is_deleted=False,
                name="fitre_zakat_fee",
                auto_id=7,
                creator=user,
                updater=user
            )

        if AccountHead.objects.filter(name='fitre_zakat_distribution').exists():
            print ("Account Heads with name fitre zakat distribution already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = fitre_zakat_distribution,
                is_deleted=False,
                name="fitre_zakat_distribution",
                auto_id=8,
                creator=user,
                updater=user
            )

        if AccountHead.objects.filter(name='fitre_zakat_collection').exists():
            print ("Account Heads with name fitre zakat collection already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = fitre_zakat_collection,
                is_deleted=False,
                name="fitre_zakat_collection",
                auto_id=9,
                creator=user,
                updater=user
            )

        if AccountHead.objects.filter(name='zakat_fee').exists():
            print ("Account Heads with name zakat collection already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = direct_income,
                is_deleted=False,
                name="zakat_fee",
                auto_id=10,
                creator=user,
                updater=user
            )

        if AccountHead.objects.filter(name='zakat_collection').exists():
            print ("Account Heads with name zakat collection already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = zakat_collection,
                is_deleted=False,
                name="zakat_collection",
                auto_id=11,
                creator=user,
                updater=user
            )

        if AccountHead.objects.filter(name='zakat_distribution').exists():
            print ("Account Heads with name zakat distribution already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = zakat_distribution,
                is_deleted=False,
                name="zakat_distribution",
                auto_id=12,
                creator=user,
                updater=user
            )

        if AccountHead.objects.filter(name='marriage_fee').exists():
            print ("Account Heads with name marriage fee already exists")
        else:
            AccountHead.objects.create(
                is_system_generated=True,
                account_group = direct_income,
                is_deleted=False,
                name="marriage_fee",
                auto_id=13,
                creator=user,
                updater=user
            )
       
     