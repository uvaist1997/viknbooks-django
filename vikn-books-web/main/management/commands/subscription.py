from django.shortcuts import render, get_object_or_404
from django.core.management.base import BaseCommand, CommandError
from main.functions import get_settings, add_subscription
from families.models import Family, Subscription
import datetime

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        settings = get_settings()
        families = Family.objects.filter(is_deleted=False)
        today = datetime.date.today()

        for family in families:
            add_subscription(family,today)

            