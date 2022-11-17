# from __future__ import unicode_literals
# from django.shortcuts import render
# from django.http.response import HttpResponse, HttpResponseRedirect
# from django.conf import settings
# from django.db import connection
# from django import db
# import psycopg2
# from django.contrib.auth.decorators import login_required
# from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
# from django.core.management import call_command
# from django.urls import reverse
# from brands.functions import createdb
# import datetime
# import re
# import json


# @login_required
# def user_signup(request):
#     connection = None
#     url = reverse('brands:user_signup')
#     if request.method == 'POST':
#         connection = psycopg2.connect(
#            database="test",
#            user = "vikncodes",
#            password = "vikncodes123",
#            host = "localhost",
#            port = "5432"
#         )

#         cursor = connection.cursor()
#         customers = "SELECT email FROM  customers";
#         cursor.execute(customers)
#         db_emails = cursor.fetchall()

#         regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
#         email = request.POST.get("email")
#         firstname = request.POST.get("firstname")
#         lastname = request.POST.get("lastname")
#         country = request.POST.get("country")
#         mobilenumber = request.POST.get("mobilenumber")
#         registrationdate = str(datetime.date.today())
#         # isregistered = True
#         expirydate = request.POST.get("expirydate")
#         noofdb = request.POST.get("noofdb")
#         noofusers = request.POST.get("noofusers")
#         password = request.POST.get("password")
#         password1 = request.POST.get("password1")
#         if (re.search(regex,email)):
#             # if not email in db_emails:
#             if not (any(email in i for i in db_emails)) :
#                 if password == password1:
#                     password_reg = '^.*(?=.{8,10})(?=.*[a-zA-Z])(?=.*?[A-Z])(?=.*\d)[a-zA-Z0-9!@£$%^&*()_+={}?:~\[\]]+$'

#                     # compiling regex
#                     pat = re.compile(password_reg)

#                     # searching regex
#                     mat = re.search(pat, password)

#                     # validating conditions
#                     add_customer = "INSERT INTO customers(email, firstname, lastname, country, mobilenumber,expirydate,noofdb,noofusers,password,registrationdate) VALUES ( '"+email+"','"+firstname+"','"+lastname+"','"+country+"','"+mobilenumber+"','"+expirydate+"','"+noofdb+"','"+noofusers+"','"+password+"','"+registrationdate+"');"
#                     cursor.execute(add_customer)

#                     # res_id = cursor.fetchone()[0]
#                     # migration_db = 'default'+str(res_id)

#                     connection.commit()
#                     cursor.close()
#                     connection.close()

#                     if mat:
#                         response_data = {
#                             "status" : "true",
#                             "title" : "Successfully Submitted",
#                             "message" : "Registration Successfully Created"
#                         }
#                         return HttpResponse(json.dumps(response_data), content_type='application/javascript')
#                     else:
#                         response_data = {
#                             "status" : "false",
#                             "stable" : "true",
#                             "title" : "Form validation error",
#                             "message" : "Enter atleast 8 characters, One capital letter and any of the special characters: !@£$%^&*()_+={}?:~[]]+"
#                         }
#                         return HttpResponse(json.dumps(response_data), content_type='application/javascript')

#                 else:
#                     response_data = {
#                         "status" : "false",
#                         "stable" : "true",
#                         "title" : "Form validation error",
#                         "message" : "password doesnot match"
#                     }
#                     return HttpResponse(json.dumps(response_data), content_type='application/javascript')

#             else:
#                     response_data = {
#                         "status" : "false",
#                         "stable" : "true",
#                         "title" : "Form validation error",
#                         "message" : "E-mail already exists"
#                     }
#                     return HttpResponse(json.dumps(response_data), content_type='application/javascript')
#         else:
#             response_data = {
#                         "status" : "false",
#                         "stable" : "true",
#                         "title" : "Form validation error",
#                         "message" : "Invalid E-mail"
#                     }
#             return HttpResponse(json.dumps(response_data), content_type='application/javascript')

#     else:
#         context = {
#             "url" : url,
#             "title" : "User Login",
#             "caption" : "Home",
#         }
#         return render(request,'user_login/user_login.html',context)
#         # return render(request,'company/dashboard.html',context)


# def user_login(request):
#     connection = None
#     if request.method == 'POST':
#         connection = psycopg2.connect(
#            database="test",
#            user = "vikncodes",
#            password = "vikncodes123",
#            host = "localhost",
#            port = "5432"
#         )
#         email = request.POST.get("email")
#         password = request.POST.get("password")
#         cursor = connection.cursor()

#         db_password = "SELECT password FROM  customers WHERE email = '"+email+"'";
#         cursor.execute(db_password)
#         db_password = cursor.fetchall()
#         try:
#             user_password = db_password[0][0]
#         except:
#             user_password = None

#         db_customer_id = "SELECT id FROM  customers WHERE email = '"+email+"'";
#         cursor.execute(db_customer_id)
#         db_customer_id = cursor.fetchall()
#         try:
#             db_customer = db_customer_id[0][0]
#         except:
#             db_customer = None


#         customers = "SELECT email FROM  customers";
#         cursor.execute(customers)
#         db_emails = cursor.fetchall()

#         cursor.close()
#         connection.close()
#         if (any(email in i for i in db_emails)) and password == user_password:

#             response_data = {
#                 "status" : "true",
#                 "title" : "Successfully Submitted",
#                 "message" : "You are successfully logged in ",
#                 "redirect" : "true",
#                 "redirect_url" : reverse('brands:create_company',kwargs={'pk':db_customer})
#             }
#         else:
#             response_data = {
#                 "status" : "false",
#                 "stable" : "true",
#                 "title" : "Form validation error",
#                 "message" : "Incorrect username or password"
#             }
#         return HttpResponse(json.dumps(response_data), content_type='application/javascript')


#     else:
#         context = {
#             "title" : "User Login",
#             "caption" : "Home",
#         }
#         return render(request,'user_login/user_login.html',context)


# # @login_required
# def create_company(request,pk):
#     connection = None
#     connection = psycopg2.connect(
#        database="test",
#        user = "vikncodes",
#        password = "vikncodes123",
#        host = "localhost",
#        port = "5432"
#     )

#     cursor = connection.cursor()

#     # db_password = "SELECT password FROM  customers WHERE email = '"+email+"'";

#     is_customerid = "SELECT customerid FROM  db_store WHERE customerid = '"+pk+"'";
#     cursor.execute(is_customerid)
#     is_customerid = cursor.fetchone()
#     is_customer = False
#     if is_customerid == None:
#         is_customer = False
#     else:
#         is_customer = True

#     company_names = "SELECT * FROM  db_store WHERE customerid = '"+pk+"'";
#     cursor.execute(company_names)
#     company_name = cursor.fetchall()
#     i=0
#     company_name_arr = []
#     company_id_arr = []
#     for company in company_name:
#         company_ids = company_name[i][0]
#         company_names = company_name[i][2]
#         company_name_arr.append(company_names)
#         company_id_arr.append(company_ids)
#         i = i + 1


#     if request.method == "POST":
#         name = request.POST.get("name")
#         companyname = request.POST.get("companyname")
#         address1 = request.POST.get("address1")
#         address2 = request.POST.get("address2")
#         address3 = request.POST.get("address3")
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         city = request.POST.get("city")
#         state = request.POST.get("state")
#         country = request.POST.get("country")
#         postalcode = request.POST.get("postalcode")
#         telephone = request.POST.get("telephone")
#         mobile = request.POST.get("mobile")
#         email = request.POST.get("email")
#         website = request.POST.get("website")
#         currency = request.POST.get("currency")
#         fractionalunit = request.POST.get("fractionalunit")
#         vatnumber = request.POST.get("vatnumber")
#         gstnumber = request.POST.get("gstnumber")
#         tax1 = request.POST.get("tax1")
#         tax2 = request.POST.get("tax2")
#         tax3 = request.POST.get("tax3")
#         createddate = str(datetime.date.today())
#         customerid = pk

#         # createdb1 = createdb(companyname,address1,telephone,createddate)

#         # add_company = "INSERT INTO db_store(name, companyname, address1, address2, address3, username, password, city, state,country,postalcode,phone,mobile,email,website,currency,fractionalunit,vatnumber,gstnumber,tax1,tax2,tax3,createddate,customerid) VALUES ( '"+name+"','"+companyname+"','"+address1+"','"+address2+"','"+address3+"','"+username+"','"+password+"','"+city+"','"+state+"','"+country+"','"+postalcode+"','"+telephone+"','"+mobile+"','"+email+"','"+website+"','"+currency+"','"+fractionalunit+"','"+vatnumber+"','"+gstnumber+"','"+tax1+"','"+tax2+"','"+tax3+"','"+createddate+"','"+customerid+"');"
#         # cursor.execute(add_company)

#         # connection.commit()
#         # cursor.close()
#         # connection.close()

#         response_data = {
#             "status" : "true",
#             "title" : "Successfully Submitted",
#             "message" : "Registration Successfully Created"
#         }
#         return HttpResponse(json.dumps(response_data), content_type='application/javascript')


#     context = {
#         "title" : "User Login",
#         "caption" : "Home",
#         "is_login" : False,
#         "is_company" : True,
#         "is_customer" : is_customer,
#         "company_ids" : company_id_arr,
#         "company_names" : company_name_arr,
#         'data': zip(company_id_arr, company_name_arr),
#         "pk" : pk
#     }
#     # return render(request,'user_login/create_company.html',context)
#     if not is_customer:
#         return HttpResponseRedirect(reverse('brands:create_companies',kwargs={'pk':pk}))
#     else:
#         return render(request,'company/create_company.html',context)


# @login_required
# def create_companies(request):
#     pk = request.user.id
#     if request.method == "POST":
#         companyname = request.POST.get("companyname")
#         address1 = request.POST.get("address1")
#         address2 = request.POST.get("address2")
#         address3 = request.POST.get("address3")
#         city = request.POST.get("city")
#         state = request.POST.get("state")
#         country = request.POST.get("country")
#         postalcode = request.POST.get("postalcode")
#         telephone = request.POST.get("telephone")
#         mobile = request.POST.get("mobile")
#         email = request.POST.get("email")
#         website = request.POST.get("website")
#         currency = request.POST.get("currency")
#         fractionalunit = request.POST.get("fractionalunit")
#         vatnumber = request.POST.get("vatnumber")
#         gstnumber = request.POST.get("gstnumber")
#         tax1 = request.POST.get("tax1")
#         tax2 = request.POST.get("tax2")
#         tax3 = request.POST.get("tax3")
#         createddate = str(datetime.date.today())
#         customerid = pk

#         createdb1 = createdb(companyname,address1,address2,address3,city,state,country,postalcode,telephone,mobile,email,website,currency,fractionalunit,vatnumber,gstnumber,tax1,tax2,tax3,createddate,customerid,)

#         connection = None
#         connection = psycopg2.connect(
#            database="test",
#            user = "vikncodes",
#            password = "vikncodes123",
#            host = "localhost",
#            port = "5432"
#         )

#         cursor = connection.cursor()

#         # db_password = "SELECT password FROM  customers WHERE email = '"+email+"'";

#         db_id = "SELECT id FROM  db_store WHERE companyname = '"+companyname+"'";
#         cursor.execute(db_id)
#         db_ids = cursor.fetchall()
#         try:
#             db_id = db_ids[0][0]
#         except:
#             db_id = None


#         response_data = {
#             "status" : "true",
#             "title" : "Successfully Submitted",
#             "message" : "Registration Successfully Created",
#             "redirect" : "true",
#             "redirect_url" : reverse('brands:create_db_user',kwargs={'pk':db_id, 'created_user_id':pk})
#         }
#         return HttpResponse(json.dumps(response_data), content_type='application/javascript')

#     else:
#         context = {
#             "title" : "User Login",
#             "caption" : "Home",
#             "is_login" : False,
#             "is_company" : True,
#             # "pk" : db_company
#         }
#         return render(request,'company/create_companies.html',context)


# # @login_required
# def create_db_user(request, pk, created_user_id):
#     connection = None
#     connection = psycopg2.connect(
#        database="test",
#        user = "vikncodes",
#        password = "vikncodes123",
#        host = "localhost",
#        port = "5432"
#     )
#     cursor = connection.cursor()
#     db_id = "SELECT databaseid FROM  users WHERE databaseid = '"+pk+"'";
#     cursor.execute(db_id)
#     db_ids = cursor.fetchall()
#     try:
#         db_id = db_ids[0][0]
#     except:
#         db_id = None

#     try:
#         db_id = db_ids[0][0]
#     except:
#         db_id = None

#     if request.method == 'POST':


#         branchid = str(1)
#         usertypeid = str(1)
#         action = "A"
#         username = request.POST.get("name")
#         password = request.POST.get("password")
#         password1 = request.POST.get("password1")
#         employeeid = str(1)
#         cash_account = request.POST.get("cash_account")
#         bank_account = request.POST.get("bank_account")
#         warehouse = request.POST.get("warehouse")
#         sales_account = request.POST.get("sales_account")
#         sales_return_account = request.POST.get("sales_return_account")
#         purchase_account = request.POST.get("purchase_account")
#         purchase_return_account = request.POST.get("purchase_return_account")
#         sales_gst_type = request.POST.get("sales_gst_type")
#         purchase_gst_type = request.POST.get("purchase_gst_type")
#         vat_type = request.POST.get("vat_type")
#         isactive = str(True)
#         createduserid = created_user_id
#         expirydate = request.POST.get("expirydate")
#         createddate = str(datetime.date.today())
#         databaseid = pk
#         if password == password1:
#             password_reg = '^.*(?=.{8,10})(?=.*[a-zA-Z])(?=.*?[A-Z])(?=.*\d)[a-zA-Z0-9!@£$%^&*()_+={}?:~\[\]]+$'

#             # compiling regex
#             pat = re.compile(password_reg)

#             # searching regex
#             mat = re.search(pat, password)

#             # validating conditions

#             # res_id = cursor.fetchone()[0]
#             # migration_db = 'default'+str(res_id)


#             if mat:
#                 add_db_user = "INSERT INTO customer_users(branchid, usertypeid, action, username, password, employeeid, cash_account, bank_account, warehouse, sales_account, sales_return_account, purchase_account, purchase_return_account, sales_gst_type, purchase_gst_type, vat_type, isactive, createduserid, expirydate, createddate) VALUES ( '"+branchid+"','"+usertypeid+"','"+action+"','"+username+"','"+password+"','"+employeeid+"','"+cash_account+"','"+bank_account+"','"+warehouse+"','"+sales_account+"','"+sales_return_account+"','"+purchase_account+"','"+purchase_return_account+"','"+sales_gst_type+"','"+purchase_gst_type+"','"+vat_type+"','"+isactive+"','"+createduserid+"','"+expirydate+"','"+createddate+"');"
#                 cursor.execute(add_db_user)
#                 add_user = "INSERT INTO users(username, password, databaseid, createddate) VALUES ( '"+username+"','"+password+"','"+databaseid+"','"+createddate+"');"
#                 cursor.execute(add_user)
#                 connection.commit()
#                 cursor.close()
#                 connection.close()
#                 response_data = {
#                     "status" : "true",
#                     "title" : "Successfully Submitted",
#                     "message" : "Registration Successfully Created",
#                     "redirect" : "true",
#                     "redirect_url" : reverse('brands:login_db_user')
#                 }
#                 return HttpResponse(json.dumps(response_data), content_type='application/javascript')
#             else:
#                 response_data = {
#                     "status" : "false",
#                     "stable" : "true",
#                     "title" : "Form validation error",
#                     "message" : "Enter atleast 8 characters, One capital letter and any of the special characters: !@£$%^&*()_+={}?:~[]]+"
#                 }
#                 return HttpResponse(json.dumps(response_data), content_type='application/javascript')

#         else:
#             response_data = {
#                 "status" : "false",
#                 "stable" : "true",
#                 "title" : "Form validation error",
#                 "message" : "password doesnot match"
#             }
#             return HttpResponse(json.dumps(response_data), content_type='application/javascript')


#     else:
#         if db_id == None:
#             context = {
#                 "title" : "User Login",
#                 "caption" : "Home",
#             }
#             return render(request,'company/create_db_user.html',context)
#         else:
#             return HttpResponseRedirect(reverse('brands:login_db_user'))


# def login_db_user(request):
#     connection = None
#     if request.method == 'POST':
#         connection = psycopg2.connect(
#            database="test",
#            user = "vikncodes",
#            password = "vikncodes123",
#            host = "localhost",
#            port = "5432"
#         )
#         cursor = connection.cursor()

#         username = request.POST.get("name")
#         password = request.POST.get("password")
#         password1 = request.POST.get("password1")

#         db_password = "SELECT password FROM  users WHERE username = '"+username+"'";
#         cursor.execute(db_password)
#         db_password = cursor.fetchall()
#         user_password = db_password[0][0]

#         customers = "SELECT email FROM  customers";
#         cursor.execute(customers)
#         db_emails = cursor.fetchall()

#         cursor.close()
#         connection.close()
#         if password == user_password:

#             response_data = {
#                 "status" : "true",
#                 "title" : "Successfully Submitted",
#                 "message" : "You are successfully logged in ",
#                 "redirect" : "true",
#                 "redirect_url" : reverse('brands:dashboard')
#             }
#         else:
#             response_data = {
#                 "status" : "false",
#                 "stable" : "true",
#                 "title" : "Form validation error",
#                 "message" : "Incorrect username or password"
#             }
#         return HttpResponse(json.dumps(response_data), content_type='application/javascript')

#     else:
#         context = {
#             "title" : "User Login",
#             "caption" : "Home",
#         }
#         return render(request,'company/login_db_user.html',context)


# # def customer_user_signup(request):
#     connection = None
#     if request.method == 'POST':
#         connection = psycopg2.connect(
#            database="test",
#            user = "vikncodes",
#            password = "vikncodes123",
#            host = "localhost",
#            port = "5432"
#         )
#         cursor = connection.cursor()

#         branchid = request.POST.get("branchid")
#         usertypeid = request.POST.get("usertypeid")
#         action = "A"
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         employeeid = request.POST.get("employeeid")
#         cash_account = request.POST.get("cash_account")
#         bank_account = request.POST.get("bank_account")
#         warehouse = request.POST.get("warehouse")
#         sales_account = request.POST.get("sales_account")
#         sales_return_account = request.POST.get("sales_return_account")
#         purchase_account = request.POST.get("purchase_account")
#         purchase_return_account  = request.POST.get("purchase_return_account")
#         sales_gst_type = request.POST.get("sales_gst_type")
#         purchase_gst_type = request.POST.get("purchase_gst_type")
#         vat_type = request.POST.get("vat_type")
#         isactive = str(True)
#         createduserid = request.POST.get("createduserid")
#         expirydate = request.POST.get("expirydate")
#         createddate = str(datetime.date.today())

#         add_customer = "INSERT INTO customer_users(branchid, usertypeid, action, username, password,employeeid,cash_account,bank_account,warehouse,sales_account,sales_return_account,purchase_account,purchase_return_account,sales_gst_type,purchase_gst_type,vat_type,isactive,createduserid,createddate,expirydate) VALUES ( '"+branchid+"','"+usertypeid+"','"+action+"','"+username+"','"+password+"','"+employeeid+"','"+cash_account+"','"+bank_account+"','"+warehouse+"','"+sales_account+"','"+sales_return_account+"','"+purchase_account+"','"+purchase_return_account+"','"+sales_gst_type+"','"+purchase_gst_type+"','"+vat_type+"','"+isactive+"','"+createduserid+"','"+createddate+"','"+expirydate+"');"
#         cursor.execute(add_customer)

#         # res_id = cursor.fetchone()[0]
#         # migration_db = 'default'+str(res_id)

#         connection.commit()
#         cursor.close()
#         connection.close()

#         response_data = {
#             "status" : "true",
#             "title" : "Successfully Submitted",
#             "message" : "Registration Successfully Created"
#         }
#         return HttpResponse(json.dumps(response_data), content_type='application/javascript')

#     else:
#         context = {
#             "title" : "User Login",
#             "caption" : "Home",
#         }
#         return render(request,'user_login/customer_user_signup.html',context)


# def dashboard(request):
#     context = {
#         "title" : "dashboard"
#     }
#     return render(request,"company/dashboard.html",context)


# @login_required
# def create_formsetTest(request):

#     from brands.models import Brand, Branch, Brand_Log, Branch_Log, AccountLedger, AccountGroup, AccountLedger_Log, LedgerPosting, LedgerPosting_Log,\
#      Parties, Parties_Log, PurchaseOrderMaster, SalesOrderMaster, Employee, Bank, Bank_Log, Flavours, Flavours_Log, Kitchen, Kitchen_Log, Product, Product_Log,\
#      PurchaseDetails, SalesDetails, SalesOrderDetails,StockPosting, Route, Route_Log, Warehouse, Warehouse_Log, PurchaseMaster, SalesMaster,\
#      ProductGroup,ProductGroup_Log, TaxCategory, TaxCategory_Log,PriceList, PriceList_Log, SalesMaster, SalesOrderDetails, StockPosting, Route, Route_Log,\
#      POSHoldDetails,PurchaseMaster,PurchaseOrderDetails,PurchaseReturnMaster,SalesReturnMaster , StockAdjustmentMaster, PriceCategory, ProductCategory_Log, ProductCategory,PurchaseMaster_Log,\
#      PurchaseDetails_Log,StockPosting_Log,StockRate,StockTrans,TransactionTypes,UserTable,GeneralSettings,TestFormModel,TestFormSetModel
#     from brands.forms import TestFormModelForm, TestFormSetModelForm
#     from django.forms.models import inlineformset_factory, formset_factory
#     from django.utils.translation import gettext_lazy as _

#     TestFormSetModelFormset = formset_factory(TestFormSetModelForm)
#     today = datetime.date.today()
#     if request.method == 'POST':
#         form = TestFormModelForm(request.POST,request.FILES)
#         pricelist_formset = TestFormSetModelFormset(request.POST,prefix='pricelist_formset')
#         if form.is_valid() and pricelist_formset.is_valid():
#             data = form.save(commit=False)
#             BranchID = 1
#             data.ProductID = 1
#             data.ProductCode = "a1"
#             data.BranchID = BranchID
#             data.Action = 'A'
#             data.CreatedUserID = request.user.id
#             data.CreatedDate = today
#             data.UpdatedDate = today

#             data.save()

#             for f in pricelist_formset:
#                 AutoBarcode = 1
#                 PriceListID = 1
#                 UnitName = f.cleaned_data['UnitName']
#                 DefaultUnit = False
#                 SalesPrice = f.cleaned_data['SalesPrice']
#                 PurchasePrice = f.cleaned_data['PurchasePrice']
#                 MultiFactor = f.cleaned_data['MultiFactor']
#                 Barcode = f.cleaned_data['Barcode']
#                 SalesPrice1 = f.cleaned_data['SalesPrice1']
#                 SalesPrice2 = f.cleaned_data['SalesPrice2']
#                 SalesPrice3 = f.cleaned_data['SalesPrice3']
#                 UnitInSales = f.cleaned_data['UnitInSales']
#                 UnitInPurchase = f.cleaned_data['UnitInPurchase']
#                 UnitInReports = f.cleaned_data['UnitInReports']
#                 MRP = f.cleaned_data['MRP']
#                 TestFormSetModel.objects.create(
#                     PriceListID=PriceListID,
#                     BranchID=BranchID,
#                     ProductID=data.ProductID,
#                     product = data,
#                     UnitName=UnitName,
#                     SalesPrice=SalesPrice,
#                     PurchasePrice=PurchasePrice,
#                     MultiFactor=MultiFactor,
#                     Barcode=Barcode,
#                     AutoBarcode=AutoBarcode,
#                     SalesPrice1=SalesPrice1,
#                     SalesPrice2=SalesPrice2,
#                     SalesPrice3=SalesPrice3,
#                     CreatedDate=today,
#                     UpdatedDate=today,
#                     Action=data.Action,
#                     DefaultUnit=DefaultUnit,
#                     UnitInSales=UnitInSales,
#                     UnitInPurchase=UnitInPurchase,
#                     UnitInReports=UnitInReports,
#                     CreatedUserID=request.user.id,
#                     MRP=MRP,
#                     )

#             response_data = {
#                 "status" : "true",
#                 "title" : str(_("Successfully Created")),
#                 "message" : str(_("Product Created Successfully!")),
#                 "redirect" : "true",
#                 "redirect_url" : reverse('reviews:formsetTests')
#             }

#         else:
#             # message = generate_form_errors(form,formset=False)
#             message = generate_form_errors(pricelist_formset,formset=True)
#             response_data = {
#                 'status' : 'false',
#                 'stable' : 'true',
#                 'title' : str(_("Form validation error")),
#                 "message" : str(message)
#             }

#         return HttpResponse(json.dumps(response_data), content_type='application/javascript')
#     else:
#         form = TestFormModelForm()
#         pricelist_formset = TestFormSetModelFormset(prefix='pricelist_formset')
#         tax_category = TaxCategory.objects.all()
#         product_groups = ProductGroup.objects.all()
#         brands = Brand.objects.all()

#         context = {
#             "title" : "Create Product",
#             "form" : form,
#             "pricelist_formset" : pricelist_formset,
#             "tax_category" : tax_category,
#             "product_groups" : product_groups,
#             "brands" : brands,
#             "is_need_formset" : True
#         }
#         return render(request,"create_formsetTest.html",context)


# @login_required
# def formsetTests(request):
#     from brands.models import TestFormModel

#     BranchID = 1
#     instances = TestFormModel.objects.filter(BranchID=BranchID)

#     context = {
#         'instances' : instances,
#         'title' : 'Products'
#     }
#     return render(request,"formsetTests.html",context)


# @login_required
# def edit_formsetTest(request,pk):
#     from brands.models import Brand, Branch, Brand_Log, Branch_Log, AccountLedger, AccountGroup, AccountLedger_Log, LedgerPosting, LedgerPosting_Log,\
#      Parties, Parties_Log, PurchaseOrderMaster, SalesOrderMaster, Employee, Bank, Bank_Log, Flavours, Flavours_Log, Kitchen, Kitchen_Log, Product, Product_Log,\
#      PurchaseDetails, SalesDetails, SalesOrderDetails,StockPosting, Route, Route_Log, Warehouse, Warehouse_Log, PurchaseMaster, SalesMaster,\
#      ProductGroup,ProductGroup_Log, TaxCategory, TaxCategory_Log,PriceList, PriceList_Log, SalesMaster, SalesOrderDetails, StockPosting, Route, Route_Log,\
#      POSHoldDetails,PurchaseMaster,PurchaseOrderDetails,PurchaseReturnMaster,SalesReturnMaster , StockAdjustmentMaster, PriceCategory, ProductCategory_Log, ProductCategory,PurchaseMaster_Log,\
#      PurchaseDetails_Log,StockPosting_Log,StockRate,StockTrans,TransactionTypes,UserTable,GeneralSettings,TestFormModel,TestFormSetModel
#     from brands.forms import TestFormModelForm, TestFormSetModelForm
#     from django.forms.models import inlineformset_factory, formset_factory
#     from django.utils.translation import gettext_lazy as _
#     from django.shortcuts import render, get_object_or_404
#     from django.forms.widgets import TextInput, Select

#     today = datetime.date.today()


#     instance = get_object_or_404(TestFormModel.objects.filter(pk=pk))


#     if TestFormSetModel.objects.filter(product=instance).exists():
#         extra = 0
#     else:
#         extra = 1

#     TestFormSetModelFormset = inlineformset_factory(
#         TestFormModel,
#         TestFormSetModel,
#         can_delete=True,
#         form=TestFormSetModelForm,
#         extra=extra,
#         widgets = {
#             "UnitName": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#             "DefaultUnit": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#             "SalesPrice": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#             "PurchasePrice": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#             "MultiFactor": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#             "Barcode": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#             "SalesPrice1": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#             "SalesPrice2": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#             "SalesPrice3": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#             "UnitInSales": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#             "UnitInPurchase": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#             "UnitInReports": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),
#         }
#         )

#     if request.method == 'POST':

#         form = TestFormModelForm(request.POST,instance=instance)

#         if form.is_valid():

#             data = form.save(commit=False)
#             BranchID = 1
#             data.ProductID = 1
#             data.ProductCode = "aa"
#             data.BranchID = BranchID
#             data.Action = 'M'
#             data.CreatedUserID = request.user.id
#             data.UpdatedDate = today

#             data.save()

#             PriceListID = 1
#             AutoBarcode = 1
#             pricelist_items = pricelist_formset.save(commit=False)
#             for item in pricelist_items:
#                 UnitName = f.cleaned_data['UnitName']
#                 DefaultUnit = f.cleaned_data['DefaultUnit']
#                 SalesPrice = f.cleaned_data['SalesPrice']
#                 PurchasePrice = f.cleaned_data['PurchasePrice']
#                 MultiFactor = f.cleaned_data['MultiFactor']
#                 Barcode = f.cleaned_data['Barcode']
#                 SalesPrice1 = f.cleaned_data['SalesPrice1']
#                 SalesPrice2 = f.cleaned_data['SalesPrice2']
#                 SalesPrice3 = f.cleaned_data['SalesPrice3']
#                 UnitInSales = f.cleaned_data['UnitInSales']
#                 UnitInPurchase = f.cleaned_data['UnitInPurchase']
#                 UnitInReports = f.cleaned_data['UnitInReports']

#                 PriceList.objects.using(DataBase).create(
#                     PriceListID=PriceListID,
#                     BranchID=BranchID,
#                     ProductID=data.ProductID,
#                     Product=data,
#                     UnitName=UnitName,
#                     SalesPrice=SalesPrice,
#                     PurchasePrice=PurchasePrice,
#                     MultiFactor=MultiFactor,
#                     Barcode=Barcode,
#                     AutoBarcode=AutoBarcode,
#                     SalesPrice1=SalesPrice1,
#                     SalesPrice2=SalesPrice2,
#                     SalesPrice3=SalesPrice3,
#                     CreatedDate=today,
#                     UpdatedDate=today,
#                     Action=data.Action,
#                     DefaultUnit=DefaultUnit,
#                     UnitInSales=UnitInSales,
#                     UnitInPurchase=UnitInPurchase,
#                     UnitInReports=UnitInReports,
#                     CreatedUserID=request.user.id,
#                     )

#                 item.save()

#             for obj in pricelist_formset.deleted_objects:
#                 obj.delete()

#             response_data = {
#                 "status" : "true",
#                 "title" : "Successfully Updated",
#                 "message" : "Customer Successfully Updated.",
#                 "redirect" : "true",
#                 "redirect_url" : reverse('inventories:product',kwargs={'pk':instance.pk})
#             }
#         else:
#             message = generate_form_errors(form,formset=True)
#             message = generate_form_errors(pricelist_formset,formset=True)

#             response_data = {
#                 "status" : "false",
#                 "stable" : "true",
#                 "title" : "Form validation error",
#                 "message" : message
#             }

#         return HttpResponse(json.dumps(response_data), content_type='application/javascript')

#     else:
#         form = TestFormModelForm(instance=instance)
#         pricelist_formset = TestFormSetModelFormset(prefix='pricelist_formset', instance=instance)

#         context = {
#             "form" : form,
#             "title" : "Edit Product : " + instance.ProductName,
#             "instance" : instance,
#             "pricelist_formset" : pricelist_formset,
#             "redirect" : True,
#             "is_need_formset" : True

#         }
#     return render(request,"create_formsetTest.html",context)


# from django.contrib.auth.models import User
# from django.contrib import messages
# from django.views.generic.edit import FormView
# from django.shortcuts import redirect

# from .forms import GenerateRandomUserForm
# from .tasks import create_random_user_accounts


# class GenerateRandomUserView(FormView):
#     template_name = 'core/generate_random_users.html'
#     form_class = GenerateRandomUserForm

#     def form_valid(self, form):
#         total = form.cleaned_data.get('total')
#         create_random_user_accounts.delay(total)
#         messages.success(
#             self.request, 'We are generating your random users! Wait a moment and refresh this page.')
#         return redirect('users_list')
