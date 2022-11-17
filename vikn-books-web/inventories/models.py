from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


class TaskFormReact(models.Model):
    Date = models.DateTimeField()
    Description = models.TextField(blank=True,null=True)

    class Meta:
        db_table = 'taskFormReact'
        verbose_name = _('taskForm')
        verbose_name_plural = _('taskForm')


class TaskFormSetReact(models.Model):
    taskFormId = models.BigIntegerField(blank=True,null=True)
    projectName = models.CharField(max_length=128,blank=True,null=True,)
    task = models.CharField(max_length=128,blank=True,null=True,)
    taskNotes = models.TextField(blank=True,null=True)
    taskStatus = models.CharField(max_length=128,blank=True,null=True,)

    class Meta:
        db_table = 'taskFormSetReact'
        verbose_name = _('taskFormSet')
        verbose_name_plural = _('taskFormSet')
