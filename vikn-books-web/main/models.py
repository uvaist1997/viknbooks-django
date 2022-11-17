import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


# BOOL_CHOICES = ((1, 'Yes'), (0, 'No'))

# THEME_CHOICES = (
#     ('teal', 'Teal'), 
#     ('blue', 'Blue'),
#     ('bluegrey', 'Blue Grey'),
#     ('cyan-600', 'Cyan'),
#     ('green', 'Green'),
#     ('lightgreen', 'Light Green'),
#     ('purple-400', 'Purple'),
#     ('red-400', 'Red'),
#     ('pink-400', 'Pink'),
#     ('brown', 'Brown'),
#     ('grey-600', 'Grey'),
#     ('orange', 'Orange')
# )

# PRINT_CHOICES = (
#     ('a4', 'A4'), 
#     ('compact', 'Compact(77mm)'), 
# )


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CreatedUserID = models.BigIntegerField(blank=True,null=True)
    UpdatedUserID = models.BigIntegerField(blank=True,null=True)
    CreatedDate = models.DateTimeField(db_index=True,auto_now_add=True)    
    UpdatedDate = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True
        

# class Mode(models.Model):
#     readonly = models.BooleanField(default=False)
#     maintenance = models.BooleanField(default=False)
#     down = models.BooleanField(default=False)
    
#     class Meta:
#         db_table = 'mode'
#         verbose_name = _('mode')
#         verbose_name_plural = _('mode')
#         ordering = ('id',)
        
#     class Admin:
#         list_display = ('id', 'readonly', 'maintenance', 'down')
        
#     def __str__(self):
#         return self.id
    
 
# class SchoolAccess(models.Model):
#     user = models.ForeignKey('auth.User',null=True,on_delete=models.CASCADE)
#     school = models.ForeignKey('main.School',blank=True,on_delete=models.CASCADE)
#     group = models.ForeignKey('auth.Group',on_delete=models.CASCADE)
#     is_accepted = models.BooleanField(default=False)
#     is_default = models.BooleanField(default=False)       

#     class Meta:
#         db_table = 'school_access'
#         verbose_name = _('school_access')
#         verbose_name_plural = _('school_access')
#         ordering = ('school',)
    
#     class Admin:
#         list_dispay = ('school','group','is_accepted',)
    
#     def __str__(self):
#         return self.school.name + ' ' + self.group.name
    
       
class ThemeSettings(models.Model):
    color_scheme = models.CharField(max_length=40)

    class Meta:
        db_table = 'theme_settings'
        verbose_name = _('theme settings')
        verbose_name_plural = _('theme settings')
        ordering = ('color_scheme',)
        
    def __str__(self):
        return self.color_scheme
    
    
# class Batch(BaseModel):
#     name = models.CharField(max_length=128)
#     start_date = models.DateField(blank=True,null=True)
#     end_date = models.DateField(blank=True,null=True)   
#     is_active = models.BooleanField(default=True)
#     is_deleted = models.BooleanField(default=False)
    
#     class Meta:
#         db_table = 'students_batch'
#         verbose_name = _('batch')
#         verbose_name_plural = _('batchs')
#         ordering = ('name',)
        
#     def __str__(self):
#         return self.name

        
# class Place(BaseModel):
#     name = models.CharField(max_length=128)
   
#     is_deleted = models.BooleanField(default=False)

#     class Meta:
#         db_table = 'places_place'
#         verbose_name = _('Place')
#         verbose_name_plural = _('Places')

#     def __str__(self):
#         return self.name
