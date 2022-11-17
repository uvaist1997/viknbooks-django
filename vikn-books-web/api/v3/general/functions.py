from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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

