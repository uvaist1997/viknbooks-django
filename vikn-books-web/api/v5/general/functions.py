from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re


def generate_serializer_errors(args):
	message = ""
	for key, values in args.iteritems():
		error_message = ""
		for value in values:
			error_message += value + ","
		error_message = error_message[:-1]

		message += "%s : %s | " %(key,error_message)
	return message[:-3]


def get_current_role(cls):
	current_role = "user" 

	if cls.user.is_authenticated:           
		roles = list(set([x.name for x in cls.user.groups.all()]))
		if cls.user.is_superuser:
			current_role = "superuser"
		elif 'users' in roles:
				current_role = 'users'
		elif 'customer_user' in roles:
				current_role = 'customer_user'
					
	return current_role


def call_paginator_all(model_object, page_number, items_per_page):
	paginator = Paginator(model_object, items_per_page)
	content = paginator.page(page_number)
	return content


def list_pagination(list_value, items_per_page, page_no):
	paginator_object = Paginator(list_value, items_per_page)
	get_value = paginator_object.page(page_no).object_list
	return get_value

def isValidMasterCardNo(str):
 
    # Regex to check valid
    # GST (Goods and Services Tax) number
    regex = "^[0-9]{2}[A-Z]{5}[0-9]{4}"+"[A-Z]{1}[1-9A-Z]{1}"+"Z[0-9A-Z]{1}$"
     
    # Compile the ReGex
    p = re.compile(regex)
 
    # If the string is empty
    # return false
    if (str == None):
        return False
 
    # Return if the string
    # matched the ReGex
    if(re.search(p, str)):
        return True
    else:
        return False