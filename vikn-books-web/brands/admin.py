from __future__ import unicode_literals
from django.contrib import admin
from brands import models as model


class EditionAdmin(admin.ModelAdmin):
	list_display= ('id','Name')
admin.site.register(model.Edition,EditionAdmin)


class CompanyAdmin(admin.ModelAdmin):
	list_display= ('id','CompanyName','Edition')
admin.site.register(model.CompanySettings,CompanyAdmin)


class ActivityLogAdmin(admin.ModelAdmin):
	list_display= ('id','log_type','date','time','user','source','message','description')
admin.site.register(model.Activity_Log,ActivityLogAdmin)


class BusinessTypeAdmin(admin.ModelAdmin):
	list_display= ('id','Name')
admin.site.register(model.BusinessType,BusinessTypeAdmin)


class VersionDetailsAdmin(admin.ModelAdmin):
    	list_display= ('id','Version','Message','is_updation','is_web','is_mobile','UpdatedDate')
admin.site.register(model.VersionDetails,VersionDetailsAdmin)