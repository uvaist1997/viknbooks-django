from main.functions import get_current_role
from users.models import CustomerUser, DatabaseStore
from brands.functions import get_DBS
from django.shortcuts import render, get_object_or_404
import datetime


# def main_context(request):
#     current_school = get_current_school(request)
#     current_batch = get_current_batch(request)
#     today = datetime.date.today().strftime('%m/%d/%Y')

#     previous_date = datetime.date.today() - datetime.timedelta(days=31)
#     is_superuser = False
#     user_instance =None
#     staff_instance = None
    
#     if "set_user_timezone" in request.session:
#         user_session_ok = True
#         user_time_zone = request.session['set_user_timezone']
#     else:
#         user_session_ok = False
#         user_time_zone = "Asia/Kolkata"
       
#     current_theme = 'cyan-600'
#     if current_school:
#         current_theme = current_school.theme

#     if request.user.is_authenticated:
#         if SchoolAccess.objects.filter(user=request.user).exists():
#             if request.user.is_superuser:
#                 is_superuser=True
#         current_role = get_current_role(request)    
#         if current_role == "staff":
#             user_instance = Staff.objects.get(user=request.user,school=current_school)
#             staff_instance = user_instance
#         recent_notifications = Notification.objects.filter(user=request.user,is_deleted=False).order_by('-time')[:6]
#     else:
#         recent_notifications = []   

#     all_batches = Batch.objects.filter(is_deleted=False,school=current_school) 

#     active_parent = request.GET.get('active_parent')
#     active = request.GET.get('active')
        
#     return {
#         'app_title' : "EDYUZ 1.0",
#         "user_session_ok" : user_session_ok,        
#         "user_time_zone" : user_time_zone,
#         "confirm_delete_message" : "Are you sure want to delete this item. All associated data may be removed.",
#         "revoke_access_message" : "Are you sure to revoke this user's login access",
#         "confirm_school_delete_message" : "Your school will deleted permanantly. All data will lost.",
#         "confirm_delete_selected_message" : "Are you sure to delete all selected items.",
#         "confirm_read_message" : "Are you sure want to mark as read this item.",
#         "confirm_read_selected_message" : "Are you sure to mark as read all selected items.",
#         'domain' : request.META['HTTP_HOST'],
#         "school_access" : school_access(request),
#         'current_school' : current_school,
#         "current_theme" : current_theme,
#         "current_batch" : current_batch,
#         "previous_date" :previous_date,
        
#         "active_parent" : active_parent,
#         "active_menu" : active,
#         "user_instance" : user_instance,
#         "staff_instance" : staff_instance,
#         "is_superuser" : is_superuser,
#         "recent_notifications" : recent_notifications,
#         "all_batches": all_batches,
#     }
    
    

def main_context(request):
    user = request.user
    is_superuser = False
    datastore_pk = None
    username = None
    customer_instance = None
    datastore = None
    
    if user.is_authenticated:
        username = user.username
        if CustomerUser.objects.filter(user__id=user.id).exists():
            customer_instance = get_object_or_404(
                CustomerUser.objects.filter(user__id=user.id))
            db_id = customer_instance.databaseid
            if DatabaseStore.objects.filter(id=db_id).exists():
                datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
                datastore_pk = datastore.id
 
        if user.is_superuser:
            is_superuser = True
        else:
            is_superuser = False
    return {
        "is_superuser" : is_superuser,
        "username" : username,
        "datastore_pk" : datastore_pk,
    }