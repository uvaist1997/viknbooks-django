import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import datetime



class Contact(models.Model):
    name = models.CharField(max_length=250,blank=True,null=True)
    phone = models.CharField(max_length=250,blank=True,null=True)
    email = models.EmailField(max_length=128,blank=True,null=True)
    subject = models.TextField(max_length=250,blank=True,null=True)
    message = models.TextField(max_length=250,blank=True,null=True)
    created_date = models.DateTimeField(db_index=True,auto_now_add=True)  

    class Meta:
        db_table = 'web_contact'
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')
        ordering = ('name',)
        
    def __str__(self):
        return self.name