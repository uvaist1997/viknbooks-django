import json
import os
import datetime
import pytz
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string
from brands.models import Brand, Branch, Brand_Log, Branch_Log, AccountLedger, AccountGroup, AccountLedger_Log, LedgerPosting, LedgerPosting_Log,\
 Parties, Parties_Log, PurchaseOrderMaster, SalesOrderMaster, Employee, Bank, Bank_Log, Flavours, Flavours_Log, Kitchen, Kitchen_Log, Product, Product_Log,\
 PurchaseDetails, SalesDetails, SalesOrderDetails,StockPosting, Route, Route_Log, Warehouse, Warehouse_Log, PurchaseMaster, SalesMaster,\
 ProductGroup,ProductGroup_Log, TaxCategory, TaxCategory_Log,PriceList, PriceList_Log, SalesMaster, SalesOrderDetails, StockPosting, Route, Route_Log,\
 POSHoldDetails,PurchaseMaster,PurchaseOrderDetails,PurchaseReturnMaster,SalesReturnMaster , StockAdjustmentMaster, PriceCategory, ProductCategory_Log, ProductCategory,PurchaseMaster_Log,\
 PurchaseDetails_Log,StockPosting_Log,StockRate,StockTrans,TransactionTypes,UserTable,GeneralSettings
from inventories.forms import BrandForm, FlavoursForm, KitchenForm, ProductForm, ProductGroupForm, TaxCategoryForm, PriceListForm, RouteForm, ProductCategoryForm,WarehouseForm,\
PurchaseMasterForm, PurchaseDetailsForm
from inventories.functions import generate_form_errors, get_auto_id, get_auto_Branchid, get_auto_LedgerID,get_auto_ProductGroupID,get_auto_TaxID,get_auto_ProductCategoryID,get_auto_ProductGroupID,get_auto_TaxID
from api.v1.accountLedgers.functions import get_LedgerCode, get_auto_LedgerPostid, get_auto_idfor_party
from django.forms.models import inlineformset_factory, formset_factory
from django.forms.widgets import TextInput, Select
from api.v1.banks.functions import get_auto_Bankid
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from users.models import DatabaseStore, CustomerUser
from main.functions import get_DataBase
import datetime



@login_required
def create_brand(request):
    DataBase = get_DataBase(request)
    
    today = datetime.date.today()
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            BrandName = data.BrandName

            is_nameExist = False
            BrandNameLow = BrandName.lower()
            brands = Brand.objects.using(DataBase).filter(BranchID=1)

            for brand in brands:
                brand_name = brand.BrandName
                brandName = brand_name.lower()

                if BrandNameLow == brandName:
                    is_nameExist = True

            if not is_nameExist:
                data.CreatedDate = today
                data.Action = "A"
                data.BranchID = 1
                data.CreatedUserID = 1
                data.BrandID = get_auto_id(Brand,data.BranchID)
                Brand_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=data.BrandID,
                    BrandName=data.BrandName,
                    Notes=data.Notes,
                    CreatedDate=today,
                    CreatedUserID=1,
                    Action=data.Action,
                    )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Brand Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:brands')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Brand Already Exist")),
                    "message" : str(_("Brand Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:create_brand')
                }
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = BrandForm()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "create Brand",
            "form" : form
        }
        return render(request,"inventories/masters/create_brand.html",context)


@login_required
def view_brand(request,pk):
    import os
    os.system('ls')
    DataBase = get_DataBase(request)
    instance = Brand.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
    }
    return render(request,"inventories/masters/brand.html",context)


@login_required
def brands(request):
    DataBase = get_DataBase(request)
    instances = Brand.objects.using(DataBase).all()
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Brand',
    }
    return render(request,"inventories/masters/brands.html",context)


@login_required
def edit_brand(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()
    instance = Brand.objects.using(DataBase).get(pk=pk)
    instanceBrandName = instance.BrandName
    BrandID = instance.BrandID
    if request.method == 'POST':
        form = BrandForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            BrandName = data.BrandName
            is_nameExist = False
            brand_ok = False

            BrandNameLow = BrandName.lower()

            brands = Brand.objects.using(DataBase).filter(BranchID=1)

            for brand in brands:
                brand_name = brand.BrandName

                brandName = brand_name.lower()

                if BrandNameLow == brandName:
                    is_nameExist = True

                if instanceBrandName.lower() == BrandNameLow:
                    brand_ok = True
            if brand_ok:
                data.CreatedDate = today
                data.Action = "M"
                data.BranchID = 1
                data.CreatedUserID = 1
                Brand_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=BrandID,
                    BrandName=data.BrandName,
                    Notes=data.Notes,
                    CreatedDate=today,
                    CreatedUserID=1,
                    Action=data.Action,
                    )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Brand Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:view_brand',kwargs={'pk':instance.pk})
                }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("Brand Already Exist")),
                        "message" : str(_("Brand Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('inventories:edit_brand')
                    }
                else:
                    data.CreatedDate = today
                    data.Action = "M"
                    data.BranchID = 1
                    data.CreatedUserID = 1
                    data.BrandID = get_auto_id(Brand,data.BranchID)
                    Brand_Log.objects.using(DataBase).create(
                        BranchID=data.BranchID,
                        TransactionID=data.BrandID,
                        BrandName=data.BrandName,
                        Notes=data.Notes,
                        CreatedDate=today,
                        CreatedUserID=1,
                        Action=data.Action,
                        )
                    data.save(using=DataBase)

                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("Branch Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('inventories:view_brand',kwargs={'pk':instance.pk})
                    }
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = BrandForm(instance=instance)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Edit Brand",
            "form" : form
        }
        return render(request,"inventories/masters/create_brand.html",context)


@login_required
def delete_brand(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()    
    instance = Brand.objects.using(DataBase).get(pk=pk)
    if pk == "1":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this brand")),
            "message" : str(_("Can't delete this brand! this is default brand!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        instance.delete()
        Brand_Log.objects.using(DataBase).create(
            BranchID=instance.BranchID,
            TransactionID=instance.BrandID,
            BrandName=instance.BrandName,
            Notes=instance.Notes,
            CreatedDate=today,
            CreatedUserID=1,
            Action="D",
            )
        
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Brand Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('inventories:brands')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')



@login_required
def create_flavour(request):
    from api.v1.flavours.functions import get_auto_id_flavour

    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    database = datastore.DatabaseName

    today = datetime.date.today()
    if request.method == 'POST':
        form = FlavoursForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.Action = "A"
            data.BranchID = 1
            data.FlavourID = get_auto_id_flavour(Flavours,data.BranchID)
            Flavours_Log.objects.using(DataBase).create(
                FlavourName=data.FlavourName,
                TransactionID=data.FlavourID,
                BranchID=data.BranchID,
                BgColor=data.BgColor,
                IsActive=data.IsActive,
                Action = data.Action
                )
            settings.DATABASES['default']['NAME'] = database
            data.save()

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Created")),
                "message" : str(_("Flavours Created Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:flavours')
            }
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = FlavoursForm()
        context = {
            "title" : "create Flavour",
            "form" : form
        }
        return render(request,"inventories/masters/create_flavour.html",context)


@login_required
def flavours(request):
    DataBase = get_DataBase(request)
    instances = Flavours.objects.using(DataBase).all()
    context = {
        'instances' : instances,
        'title' : 'Flavours'
    }
    return render(request,"inventories/masters/flavours.html",context)


@login_required
def view_flavour(request,pk):
    DataBase = get_DataBase(request)
    instance = Flavours.objects.using(DataBase).get(pk=pk)
    context = {
        'instance' : instance,
        'title' : 'Flavour'
    }
    return render(request,"inventories/masters/flavour.html",context)


@login_required
def edit_flavour(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()
    instance = Flavours.objects.using(DataBase).get(pk=pk)
    if request.method == 'POST':
        form = FlavoursForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.Action = "M"
            Flavours_Log.objects.using(DataBase).create(
                FlavourName=data.FlavourName,
                TransactionID=instance.FlavourID,
                BranchID=instance.BranchID,
                BgColor=data.BgColor,
                IsActive=data.IsActive,
                Action = data.Action
                )
            data.save(using=DataBase)

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Updated")),
                "message" : str(_("Flavour Updated Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:view_flavour',kwargs={'pk':instance.pk})
            }
            
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = FlavoursForm(instance=instance)
        context = {
            "title" : "Edit Flavour",
            "form" : form
        }
        return render(request,"inventories/masters/create_flavour.html",context)


@login_required
def delete_flavour(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()    
    instance = Flavours.objects.using(DataBase).get(pk=pk)

    if pk == "1":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this Flavour")),
            "message" : str(_("Can't delete this Flavour! this is default Flavour!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        Flavours_Log.objects.using(DataBase).create(
            FlavourName=instance.FlavourName,
            TransactionID=instance.FlavourID,
            BranchID=instance.BranchID,
            BgColor=instance.BgColor,
            IsActive=instance.IsActive,
            Action = instance.Action
            )
        instance.delete()
        
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Flavour Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('inventories:flavours')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
# flavours ends



@login_required
def create_kitchen(request):
    DataBase = get_DataBase(request)
    from api.v1.kitchen.functions import get_auto_id
    today = datetime.date.today()
    if request.method == 'POST':
        form = KitchenForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.Action = "A"
            data.BranchID = 1
            data.CreatedDate = today
            data.UpdatedDate = today
            data.CreatedUserID = 1
            data.KitchenID = get_auto_id(Kitchen,data.BranchID)
            Kitchen_Log.objects.using(DataBase).create(
                TransactionID=data.KitchenID,
                BranchID=data.BranchID,
                KitchenName=data.KitchenName,
                PrinterName=data.PrinterName,
                IsActive=data.IsActive,
                UpdatedDate=data.UpdatedDate,
                Notes=data.Notes,
                Action = data.Action
                )
            data.save(using=DataBase)

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Created")),
                "message" : str(_("Kitchen Created Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:kitchens')
            }
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = KitchenForm()
        context = {
            "title" : "Create Kitchen",
            "form" : form
        }
        return render(request,"inventories/masters/create_kitchen.html",context)


@login_required
def kitchens(request):
    DataBase = get_DataBase(request)
    instances = Kitchen.objects.using(DataBase).all()
    context = {
        'instances' : instances,
        'title' : 'Kitchens'
    }
    return render(request,"inventories/masters/kitchens.html",context)


@login_required
def view_kitchen(request,pk):
    DataBase = get_DataBase(request)
    instance = Kitchen.objects.using(DataBase).get(pk=pk)
    context = {
        'instance' : instance,
        'title' : 'Kitchen'
    }
    return render(request,"inventories/masters/kitchen.html",context)


@login_required
def edit_kitchen(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()
    instance = Kitchen.objects.using(DataBase).get(pk=pk)
    if request.method == 'POST':
        form = KitchenForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.Action = "M"
            Kitchen_Log.objects.using(DataBase).create(
                TransactionID=instance.KitchenID,
                BranchID=instance.BranchID,
                KitchenName=data.KitchenName,
                PrinterName=data.PrinterName,
                IsActive=data.IsActive,
                Notes=data.Notes,
                Action = data.Action
                )
            data.save(using=DataBase)

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Updated")),
                "message" : str(_("Kitchen Updated Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:view_kitchen',kwargs={'pk':instance.pk})
            }
            
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = KitchenForm(instance=instance)
        context = {
            "title" : "Edit Kitchen",
            "form" : form
        }
        return render(request,"inventories/masters/create_kitchen.html",context)


@login_required
def delete_kitchen(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()    
    instance = Kitchen.objects.using(DataBase).get(pk=pk)

    if pk == "1":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this Kitchen")),
            "message" : str(_("Can't delete this Kitchen! this is default Kitchen!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        Kitchen_Log.objects.using(DataBase).create(
            TransactionID=instance.KitchenID,
            BranchID=instance.BranchID,
            KitchenName=instance.KitchenName,
            PrinterName=instance.PrinterName,
            IsActive=instance.IsActive,
            Notes=instance.Notes,
            Action = "D"
            )
        instance.delete()
        
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Kitchen Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('inventories:kitchens')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')


# kitchen ends


@login_required
def create_route(request):
    from api.v1.routes.functions import get_auto_id


    DataBase = get_DataBase(request)

    today = datetime.date.today()
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.Action = "A"
            data.BranchID = 1
            data.RouteID = get_auto_id(Route, data.BranchID, DataBase)
            data.UpdatedDate = today
            data.CreatedUserID = request.user.id
            Route_Log.objects.using(DataBase).create(
                TransactionID=data.RouteID,
                BranchID=data.BranchID,
                RouteName=data.RouteName,
                Notes=data.Notes,
                CreatedUserID=data.CreatedUserID,
                CreatedDate=data.CreatedDate,
                UpdatedDate=data.UpdatedDate,
                Action=data.Action,
                )
            data.save(using=DataBase)

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Created")),
                "message" : str(_("Route Created Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:routes')
            }
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = RouteForm()
        context = {
            "title" : "Create Route",
            "form" : form
        }
        return render(request,"inventories/masters/create_route.html",context)


@login_required
def routes(request):
    DataBase = get_DataBase(request)
    instances = Route.objects.using(DataBase).all()
    context = {
        'instances' : instances,
        'title' : 'Routes'
    }
    return render(request,"inventories/masters/routes.html",context)


@login_required
def view_route(request,pk):
    DataBase = get_DataBase(request)

    instance = Route.objects.using(DataBase).get(pk=pk)
    context = {
        'instance' : instance,
        'title' : 'Route'
    }
    return render(request,"inventories/masters/route.html",context)


@login_required
def edit_route(request,pk):
    DataBase = get_DataBase(request)

    today = datetime.date.today()
    instance = Route.objects.using(DataBase).get(pk=pk)
    if request.method == 'POST':
        form = RouteForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.Action = "M"
            data.CreatedUserID = request.user.id
            data.UpdatedDate = today
            Route_Log.objects.using(DataBase).create(
                TransactionID=data.RouteID,
                BranchID=data.BranchID,
                RouteName=data.RouteName,
                Notes=data.Notes,
                CreatedUserID=data.CreatedUserID,
                CreatedDate=data.CreatedDate,
                UpdatedDate=data.UpdatedDate,
                Action=data.Action,
                )
            data.save(using=DataBase)

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Updated")),
                "message" : str(_("Route Updated Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:view_route',kwargs={'pk':instance.pk})
            }
            
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = RouteForm(instance=instance)
        context = {
            "title" : "Edit Route",
            "form" : form
        }
        return render(request,"inventories/masters/create_route.html",context)


@login_required
def delete_route(request,pk):
    DataBase = get_DataBase(request)
    
    today = datetime.date.today()    
    instance = Route.objects.using(DataBase).get(pk=pk)

    if pk == "1":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this Route")),
            "message" : str(_("Can't delete this Route! this is default Route!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        Route_Log.objects.using(DataBase).create(
            TransactionID=instance.RouteID,
            BranchID=instance.BranchID,
            RouteName=instance.RouteName,
            Notes=instance.Notes,
            CreatedUserID=instance.CreatedUserID,
            CreatedDate=instance.CreatedDate,
            UpdatedDate=today,
            Action='D',
            )
        instance.delete()
        
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Route Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('inventories:routes')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
# route ends


@login_required
def create_product(request):
    from api.v1.products.functions import get_auto_id, get_auto_priceListid, get_ProductCode, get_auto_AutoBarcode
    DataBase = get_DataBase(request)

    PriceListFormset = formset_factory(PriceListForm)
    today = datetime.date.today()
    BranchID = 1
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        pricelist_formset = PriceListFormset(request.POST,prefix='pricelist_formset')

        vat = request.POST.get('vat')
        gst = request.POST.get('gst')
        tax1 = request.POST.get('tax1')
        tax3 = request.POST.get('tax2')
        tax3 = request.POST.get('tax3')

        if form.is_valid() and pricelist_formset.is_valid(): 
            data = form.save(commit=False)
            BranchID = 1
            data.ProductID = get_auto_id(Product,BranchID,DataBase)
            data.ProductCode = get_ProductCode(Product, BranchID,DataBase)
            data.BranchID = BranchID
            data.Action = 'A'
            data.VatID = vat
            data.GST = gst
            data.Tax1 = tax1
            data.Tax2 = tax3
            data.Tax3 = tax3
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today

            is_nameExist = False

            ProductNameLow = data.ProductName.lower()

            products = Product.objects.using(DataBase).filter(BranchID=BranchID)

            for product in products:
                product_name = product.ProductName

                productName = product_name.lower()

                if ProductNameLow == productName:
                    is_nameExist = True

            if not is_nameExist:

                Product_Log.objects.using(DataBase).create(
                    TransactionID = data.ProductID,
                    BranchID = data.BranchID,
                    ProductCode = data.ProductCode,
                    ProductName = data.ProductName,
                    DisplayName = data.DisplayName,
                    Description = data.Description,
                    ProductGroupID = data.ProductGroupID,
                    BrandID = data.BrandID,
                    InventoryType = data.InventoryType,
                    VatID = data.VatID,
                    StockMinimum = data.StockMinimum,
                    StockReOrder = data.StockReOrder,
                    StockMaximum = data.StockMaximum,
                    MarginPercent = data.MarginPercent,
                    ProductImage = data.ProductImage,
                    Active = data.Active,
                    IsWeighingScale = data.IsWeighingScale,
                    IsRawMaterial = data.IsRawMaterial,
                    IsFinishedProduct = data.IsFinishedProduct,
                    IsSales = data.IsSales,
                    IsPurchase = data.IsPurchase,
                    WeighingCalcType = data.WeighingCalcType,
                    PLUNo = data.PLUNo,
                    IsFavourite = data.IsFavourite,
                    CreatedDate = data.CreatedDate,
                    UpdatedDate = data.UpdatedDate,
                    CreatedUserID = data.CreatedUserID,
                    GST = data.GST,
                    Tax1 = data.Tax1,
                    Tax2 = data.Tax2,
                    Tax3 = data.Tax3,
                    Action = data.Action,
                    )
                data.save(using=DataBase)
                

                count=0
                for f in pricelist_formset:
                    AutoBarcode = get_auto_AutoBarcode(PriceList,BranchID,DataBase)
                    PriceListID = get_auto_priceListid(PriceList,BranchID,DataBase)
                    UnitName = f.cleaned_data['UnitName']
                    DefaultUnit = False
                    SalesPrice = f.cleaned_data['SalesPrice']
                    PurchasePrice = f.cleaned_data['PurchasePrice']
                    MultiFactor = f.cleaned_data['MultiFactor']
                    Barcode = f.cleaned_data['Barcode']
                    SalesPrice1 = f.cleaned_data['SalesPrice1']
                    SalesPrice2 = f.cleaned_data['SalesPrice2']
                    SalesPrice3 = f.cleaned_data['SalesPrice3']
                    UnitInSales = f.cleaned_data['UnitInSales']
                    UnitInPurchase = f.cleaned_data['UnitInPurchase']
                    UnitInReports = f.cleaned_data['UnitInReports']
                    MRP = f.cleaned_data['MRP']
                    PriceList.objects.using(DataBase).create(
                        PriceListID=PriceListID,
                        BranchID=BranchID,
                        ProductID=data.ProductID,
                        product = data,
                        UnitName=UnitName,
                        SalesPrice=SalesPrice,
                        PurchasePrice=PurchasePrice,
                        MultiFactor=MultiFactor,
                        Barcode=Barcode,
                        AutoBarcode=AutoBarcode,
                        SalesPrice1=SalesPrice1,
                        SalesPrice2=SalesPrice2,
                        SalesPrice3=SalesPrice3,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=data.Action,
                        DefaultUnit=DefaultUnit,
                        UnitInSales=UnitInSales,
                        UnitInPurchase=UnitInPurchase,
                        UnitInReports=UnitInReports,
                        CreatedUserID=request.user.id,
                        MRP=MRP,
                        )

                    if count == 0:
                        PriceList.objects.using(DataBase).filter(DefaultUnit=False, product=data).update(DefaultUnit=True)
                        count += 1
                    PriceList_Log.objects.using(DataBase).create(
                        TransactionID=PriceListID,
                        BranchID=BranchID,
                        ProductID=data.ProductID,
                        UnitName=UnitName,
                        SalesPrice=SalesPrice,
                        PurchasePrice=PurchasePrice,
                        MultiFactor=MultiFactor,
                        Barcode=Barcode,
                        AutoBarcode=AutoBarcode,
                        SalesPrice1=SalesPrice1,
                        SalesPrice2=SalesPrice2,
                        SalesPrice3=SalesPrice3,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=data.Action,
                        DefaultUnit=DefaultUnit,
                        UnitInSales=UnitInSales,
                        UnitInPurchase=UnitInPurchase,
                        UnitInReports=UnitInReports,
                        CreatedUserID=request.user.id,
                        MRP=MRP,
                        )

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Product Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:products')
                }
            else:
                message = generate_form_errors(form,formset=False)
                response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Name Already Exist")),
                    "message" : str("Product Name Already Exist in this Branch!!!")
                }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        else:
            # message = generate_form_errors(form,formset=False)
            message = generate_form_errors(pricelist_formset,formset=True)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = ProductForm()
        pricelist_formset = PriceListFormset(prefix='pricelist_formset')
        # tax_category = TaxCategory.objects.using(DataBase).all()
        product_groups = ProductGroup.objects.using(DataBase).all()
        brands = Brand.objects.using(DataBase).all()

        if TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="VAT").exists():
            vat_instances = TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="VAT")
        else:
            vat_instances = TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="None")

        if TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="GST").exists():
            gst_instances = TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="GST")
        else:
            gst_instances = TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="None")

        if TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="Tax1").exists():
            tax1_instances = TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="Tax1")
        else:
            tax1_instances = TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="None")

        if TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="Tax2").exists():
            tax2_instances = TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="Tax2")
        else:
            tax2_instances = TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="None")

        if TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="Tax3").exists():
            tax3_instances = TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="Tax3")
        else:
            tax3_instances = TaxCategory.objects.using(DataBase).filter(BranchID=BranchID,TaxType="None")

        is_VAT = False
        is_GST = False
        is_TAX1 = False
        is_TAX2 = False
        is_TAX3 = False

        if GeneralSettings.objects.using(DataBase).filter(SettingsType='VAT',SettingsValue=True).exists():
            is_VAT = True
        if GeneralSettings.objects.using(DataBase).filter(SettingsType='GST',SettingsValue=True).exists():
            is_GST = True
        if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX1',SettingsValue=True).exists():
            is_TAX1 = True
        if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX2',SettingsValue=True).exists():
            is_TAX2 = True
        if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX3',SettingsValue=True).exists():
            is_TAX3 = True

        context = {
            "title" : "Create Product",
            "form" : form,
            "pricelist_formset" : pricelist_formset,
            "vat_instances" : vat_instances,
            "gst_instances" : gst_instances,
            "tax1_instances" : tax1_instances,
            "tax2_instances" : tax2_instances,
            "tax3_instances" : tax3_instances,
            "product_groups" : product_groups,
            "brands" : brands,

            "is_VAT" : is_VAT,
            "is_GST" : is_GST,
            "is_TAX1" : is_TAX1,
            "is_TAX2" : is_TAX2,
            "is_TAX3" : is_TAX3,
            "is_need_formset" : True
        }
        return render(request,"inventories/masters/create_product.html",context)


@login_required
def products(request):
    DataBase = get_DataBase(request)

    BranchID = 1
    instances = Product.objects.using(DataBase).filter(BranchID=BranchID)

    context = {
        'instances' : instances,
        'title' : 'Products'
    }
    return render(request,"inventories/masters/products.html",context)  


@login_required
def product(request,pk):
    DataBase = get_DataBase(request)

    instance = Product.objects.using(DataBase).get(pk=pk)
    price_lists = PriceList.objects.using(DataBase).filter(ProductID=instance.ProductID).reverse()
    context = {
        'instance' : instance,
        'price_lists' : price_lists,
        'title' : 'Product'
    }
    return render(request,"inventories/masters/product.html",context)


@login_required
def edit_product(request,pk):    
    from api.v1.products.functions import get_auto_id, get_auto_priceListid, get_ProductCode, get_auto_AutoBarcode
    
    today = datetime.date.today()
    DataBase = get_DataBase(request)


    instance = get_object_or_404(Product.objects.using(DataBase).filter(pk=pk))
    
    if PriceList.objects.using(DataBase).filter(product=instance).exists():
        extra = 0
    else:
        extra = 1
        
    PriceListFormset = inlineformset_factory(
            Product, 
            PriceList,
            can_delete=True,
            form=PriceListForm,
            extra=extra,
            widgets = {
            "UnitName": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
            "DefaultUnit": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
            "SalesPrice": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
            "PurchasePrice": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
            "MultiFactor": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
            "Barcode": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
            "SalesPrice1": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
            "SalesPrice2": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
            "SalesPrice3": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
            "UnitInSales": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
            "UnitInPurchase": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
            "UnitInReports": TextInput(attrs = { "class": "required form-control","placeholder" : "Description",}),    
        }
        )

    if request.method == 'POST':
            
        form = ProductForm(request.POST,instance=instance)
        vat = request.POST.get('vat')
        gst = request.POST.get('gst')
        tax1 = request.POST.get('tax1')
        tax3 = request.POST.get('tax2')
        tax3 = request.POST.get('tax3')
        
        if form.is_valid():  
            
            data = form.save(commit=False)
            BranchID = 1
            data.ProductID = get_auto_id(Product,BranchID,DataBase)
            data.ProductCode = get_ProductCode(Product, BranchID,DataBase)
            data.BranchID = BranchID
            data.Action = 'A'
            data.VatID = vat
            data.GST = gst
            data.Tax1 = tax1
            data.Tax2 = tax3
            data.Tax3 = tax3
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today

            is_nameExist = False

            ProductNameLow = data.ProductName.lower()

            products = Product.objects.using(DataBase).filter(BranchID=BranchID)

            for product in products:
                product_name = product.ProductName

                productName = product_name.lower()

                if ProductNameLow == productName:
                    is_nameExist = True

            if not is_nameExist:

                Product_Log.objects.using(DataBase).create(
                    TransactionID = data.ProductID,
                    BranchID = data.BranchID,
                    ProductCode = data.ProductCode,
                    ProductName = data.ProductName,
                    DisplayName = data.DisplayName,
                    Description = data.Description,
                    ProductGroupID = data.ProductGroupID,
                    BrandID = data.BrandID,
                    InventoryType = data.InventoryType,
                    VatID = data.VatID,
                    StockMinimum = data.StockMinimum,
                    StockReOrder = data.StockReOrder,
                    StockMaximum = data.StockMaximum,
                    MarginPercent = data.MarginPercent,
                    ProductImage = data.ProductImage,
                    Active = data.Active,
                    IsWeighingScale = data.IsWeighingScale,
                    IsRawMaterial = data.IsRawMaterial,
                    IsFinishedProduct = data.IsFinishedProduct,
                    IsSales = data.IsSales,
                    IsPurchase = data.IsPurchase,
                    WeighingCalcType = data.WeighingCalcType,
                    PLUNo = data.PLUNo,
                    IsFavourite = data.IsFavourite,
                    CreatedDate = data.CreatedDate,
                    UpdatedDate = data.UpdatedDate,
                    CreatedUserID = data.CreatedUserID,
                    GST = data.GST,
                    Tax1 = data.Tax1,
                    Tax2 = data.Tax2,
                    Tax3 = data.Tax3,
                    Action = data.Action,
                    )
                data.save(using=DataBase)

                PriceListID = get_auto_priceListid(PriceList,BranchID,DataBase)
                AutoBarcode = get_auto_AutoBarcode(PriceList,BranchID,DataBase)
                pricelist_items = pricelist_formset.save(commit=False)
                for item in pricelist_items:
                    UnitName = f.cleaned_data['UnitName']
                    DefaultUnit = f.cleaned_data['DefaultUnit']
                    SalesPrice = f.cleaned_data['SalesPrice']
                    PurchasePrice = f.cleaned_data['PurchasePrice']
                    MultiFactor = f.cleaned_data['MultiFactor']
                    Barcode = f.cleaned_data['Barcode']
                    SalesPrice1 = f.cleaned_data['SalesPrice1']
                    SalesPrice2 = f.cleaned_data['SalesPrice2']
                    SalesPrice3 = f.cleaned_data['SalesPrice3']
                    UnitInSales = f.cleaned_data['UnitInSales']
                    UnitInPurchase = f.cleaned_data['UnitInPurchase']
                    UnitInReports = f.cleaned_data['UnitInReports']

                    PriceList.objects.using(DataBase).create(
                        PriceListID=PriceListID,
                        BranchID=BranchID,
                        ProductID=data.ProductID,
                        Product=data,
                        UnitName=UnitName,
                        SalesPrice=SalesPrice,
                        PurchasePrice=PurchasePrice,
                        MultiFactor=MultiFactor,
                        Barcode=Barcode,
                        AutoBarcode=AutoBarcode,
                        SalesPrice1=SalesPrice1,
                        SalesPrice2=SalesPrice2,
                        SalesPrice3=SalesPrice3,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=data.Action,
                        DefaultUnit=DefaultUnit,
                        UnitInSales=UnitInSales,
                        UnitInPurchase=UnitInPurchase,
                        UnitInReports=UnitInReports,
                        CreatedUserID=request.user.id,
                        )

                    PriceList_Log.objects.using(DataBase).create(
                        TransactionID=PriceListID,
                        BranchID=BranchID,
                        ProductID=data.ProductID,
                        Product=data,
                        UnitName=UnitName,
                        SalesPrice=SalesPrice,
                        PurchasePrice=PurchasePrice,
                        MultiFactor=MultiFactor,
                        Barcode=Barcode,
                        AutoBarcode=AutoBarcode,
                        SalesPrice1=SalesPrice1,
                        SalesPrice2=SalesPrice2,
                        SalesPrice3=SalesPrice3,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=data.Action,
                        DefaultUnit=DefaultUnit,
                        UnitInSales=UnitInSales,
                        UnitInPurchase=UnitInPurchase,
                        UnitInReports=UnitInReports,
                        CreatedUserID=request.user.id,
                        )
                    item.save()

                for obj in pricelist_formset.deleted_objects:
                    obj.delete()
            
                response_data = {
                    "status" : "true",
                    "title" : "Successfully Updated",
                    "message" : "Customer Successfully Updated.",
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:product',kwargs={'pk':instance.pk})
                }   
            else:
                message = generate_form_errors(form,formset=True)
                response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Name Already Exist")),
                    "message" : str("Product Name Already Exist in thi Branch!!!")
                }
        else:
            message = generate_form_errors(form,formset=True) 
            message = generate_form_errors(pricelist_formset,formset=True)     
                    
            response_data = {
                "status" : "false",
                "stable" : "true",
                "title" : "Form validation error",
                "message" : message
            }  
            
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    else: 
        form = ProductForm(instance=instance)
        pricelist_formset = PriceListFormset(prefix='pricelist_formset', instance=instance)

        context = {
            "form" : form,
            "title" : "Edit Product : " + instance.ProductName,
            "instance" : instance,
            "pricelist_formset" : pricelist_formset,
            "redirect" : True,
            "is_need_formset" : True

        }
    return render(request,"inventories/masters/create_product.html",context)



@login_required
def delete_product(request,pk):
    DataBase = get_DataBase(request)


    today = datetime.date.today()
    product_instance = None
    priceLists_instance = None
    purchaseDetails_exist = None
    purchaseOrderDetails_exist = None
    salesDetails_exist = None
    salesOrderDetails_exist = None
    stockPostings_exist = None

    if Product.objects.using(DataBase).filter(pk=pk).exists():
        product_instance = Product.objects.using(DataBase).get(pk=pk)
        ProductID = product_instance.ProductID
        BranchID = product_instance.BranchID  

    if product_instance:
        ProductCode = product_instance.ProductCode
        ProductName = product_instance.ProductName
        DisplayName = product_instance.DisplayName
        Description = product_instance.Description
        ProductGroupID = product_instance.ProductGroupID
        BrandID = product_instance.BrandID
        InventoryType = product_instance.InventoryType
        VatID = product_instance.VatID
        StockMinimum = product_instance.StockMinimum
        StockReOrder = product_instance.StockReOrder
        StockMaximum = product_instance.StockMaximum
        MarginPercent = product_instance.MarginPercent
        ProductImage = product_instance.ProductImage
        Active = product_instance.Active
        IsRawMaterial = product_instance.IsRawMaterial
        IsFinishedProduct = product_instance.IsFinishedProduct
        IsSales = product_instance.IsSales
        IsPurchase = product_instance.IsPurchase
        IsWeighingScale = product_instance.IsWeighingScale
        WeighingCalcType = product_instance.WeighingCalcType
        PLUNo = product_instance.PLUNo
        GST = product_instance.GST
        Tax1 = product_instance.Tax1
        Tax2 = product_instance.Tax2
        Tax3 = product_instance.Tax3
        IsFavourite = product_instance.IsFavourite

        Action = "D"

        purchaseDetails_exist = PurchaseDetails.objects.using(DataBase).filter(BranchID=BranchID,ProductID=ProductID).exists()
        purchaseOrderDetails_exist = PurchaseOrderDetails.objects.using(DataBase).filter(BranchID=BranchID,ProductID=ProductID).exists()
        salesDetails_exist = SalesDetails.objects.using(DataBase).filter(BranchID=BranchID,ProductID=ProductID).exists()
        salesOrderDetails_exist = SalesOrderDetails.objects.using(DataBase).filter(BranchID=BranchID,ProductID=ProductID).exists()
        stockPostings_exist = StockPosting.objects.using(DataBase).filter(BranchID=BranchID,ProductID=ProductID).exists()

        if not purchaseDetails_exist and not purchaseOrderDetails_exist and not salesDetails_exist and not salesOrderDetails_exist and not stockPostings_exist:
            
            product_instance.delete()

            Product_Log.objects.using(DataBase).create(
                TransactionID=ProductID,
                BranchID=BranchID,
                ProductCode=ProductCode,
                ProductName=ProductName,
                DisplayName=DisplayName,
                Description=Description,
                ProductGroupID=ProductGroupID,
                BrandID=BrandID,
                InventoryType=InventoryType,
                VatID=VatID,
                StockMinimum=StockMinimum,
                StockReOrder=StockReOrder,
                StockMaximum=StockMaximum,
                MarginPercent=MarginPercent,
                ProductImage=ProductImage,
                Active=Active,
                IsWeighingScale=IsWeighingScale,
                IsRawMaterial=IsRawMaterial,
                IsFinishedProduct=IsFinishedProduct,
                IsSales=IsSales,
                IsPurchase=IsPurchase,
                WeighingCalcType=WeighingCalcType,
                PLUNo=PLUNo,
                IsFavourite=IsFavourite,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=request.user.id,
                GST=GST,
                Tax1=Tax1,
                Tax2=Tax2,
                Tax3=Tax3,
                Action=Action,
                )

            priceLists_instances = PriceList.objects.using(DataBase).filter(ProductID=ProductID,BranchID=BranchID)

            for priceLists_instance in priceLists_instances:

                PriceListID = priceLists_instance.PriceListID
                BranchID = priceLists_instance.BranchID
                ProductID = priceLists_instance.ProductID
                product = priceLists_instance.product
                UnitName = priceLists_instance.UnitName
                SalesPrice = priceLists_instance.SalesPrice
                PurchasePrice = priceLists_instance.PurchasePrice
                MultiFactor = priceLists_instance.MultiFactor
                Barcode = priceLists_instance.Barcode
                AutoBarcode = priceLists_instance.AutoBarcode
                SalesPrice1 = priceLists_instance.SalesPrice1
                SalesPrice2 = priceLists_instance.SalesPrice2
                SalesPrice3 = priceLists_instance.SalesPrice3
                DefaultUnit = priceLists_instance.DefaultUnit
                UnitInSales = priceLists_instance.UnitInSales
                UnitInPurchase = priceLists_instance.UnitInPurchase
                UnitInReports = priceLists_instance.UnitInReports

                priceLists_instance.delete()

                PriceList_Log.objects.using(DataBase).create(
                    TransactionID=PriceListID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    product=product,
                    UnitName=UnitName,
                    SalesPrice=SalesPrice,
                    PurchasePrice=PurchasePrice,
                    MultiFactor=MultiFactor,
                    Barcode=Barcode,
                    AutoBarcode=AutoBarcode,
                    SalesPrice1=SalesPrice1,
                    SalesPrice2=SalesPrice2,
                    SalesPrice3=SalesPrice3,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    DefaultUnit=DefaultUnit,
                    UnitInSales=UnitInSales,
                    UnitInPurchase=UnitInPurchase,
                    UnitInReports=UnitInReports,
                    CreatedUserID=CreatedUserID,
                    )

    response_data = {
        "status" : "true",
        "title" : str(_("Successfully Deleted")),
        "message" : str(_("Product Deleted Successfully.")),
        "redirect" : "true",
        "redirect_url" : reverse('inventories:products')
    }
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def create_productGroup(request):
    DataBase = get_DataBase(request)
    today = datetime.date.today()

    if request.method == 'POST':
        form = ProductGroupForm(request.POST)
        category = request.POST.get('category')

        if form.is_valid(): 
            data = form.save(commit=False)

            is_nameExist = False
            GroupNameLow = data.GroupName.lower()
            groups = ProductGroup.objects.using(DataBase).filter(BranchID=1)

            for group in groups:
                group_name = group.GroupName
                GroupName = group_name.lower()

                if GroupNameLow == GroupName:
                    is_nameExist = True

            if not is_nameExist:
                data.BranchID = 1
                data.CreatedDate = today
                data.UpdatedDate=today
                data.Action = "A"
                data.CategoryID = category
                data.CreatedUserID = user.id
                data.ProductGroupID = get_auto_ProductGroupID(ProductGroup,DataBase,data.BranchID)

                ProductGroup_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=data.ProductGroupID,
                    GroupName=data.GroupName,
                    CategoryID=data.CategoryID,
                    Notes=data.Notes,
                    Action=data.Action,
                    CreatedUserID=user.id,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )

                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Product Groups Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:productGroups')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Product Group Already Exist")),
                    "message" : str(_("Product Group Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:create_productGroup')
                }
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = ProductGroupForm()
        category_instances = None
        if ProductCategory.objects.using(DataBase).filter(BranchID=1).exists():
            category_instances = ProductCategory.objects.using(DataBase).filter(BranchID=1)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create productGroup",
            "form" : form,
            "category_instances" : category_instances,
        }
        return render(request,"inventories/masters/create_productGroup.html",context)


@login_required
def productGroups(request):
    DataBase = get_DataBase(request)

    instances = ProductGroup.objects.using(DataBase).filter(BranchID=1)
    query = request.GET.get("q")
    if query:
        instances = instances.filter(Q(GroupName__icontains=query))
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Product Groups',
        "DataBase" : DataBase
    }
    return render(request,"inventories/masters/productGroups.html",context)



@login_required
def view_productGroup(request,pk):
    DataBase = get_DataBase(request)

    instance = ProductGroup.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'ProductGroup',
        "DataBase" : DataBase
    }
    return render(request,"inventories/masters/productGroup.html",context)


@login_required
def edit_productGroup(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()
    instance = ProductGroup.objects.using(DataBase).get(pk=pk)
    ProductGroupID = instance.ProductGroupID
    instanceGroupName = instance.GroupName
    BranchID = instance.BranchID

    if request.method == 'POST':
        form = ProductGroupForm(request.POST,instance=instance)
        category = request.POST.get('category')
        if form.is_valid(): 
            data = form.save(commit=False)
            GroupName = data.GroupName
            is_nameExist = False
            ledger_ok = False

            is_nameExist = False
            GroupNameLow = data.GroupName.lower()
            groups = ProductGroup.objects.using(DataBase).all()

            for group in groups:
                group_name = group.GroupName
                GroupName = group_name.lower()

                if GroupNameLow == GroupName:
                    is_nameExist = True

                if instanceGroupName.lower() == GroupNameLow:
                    ledger_ok = True

            if ledger_ok:
                data.UpdatedDate=today
                data.Action = "M"
                data.CategoryID = category
                data.CreatedUserID = user.id

                ProductGroup_Log.objects.using(DataBase).create(
                    BranchID=BranchID,
                    TransactionID=ProductGroupID,
                    GroupName=data.GroupName,
                    CategoryID=data.CategoryID,
                    Notes=data.Notes,
                    Action=data.Action,
                    CreatedUserID=user.id,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )

                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Updated")),
                    "message" : str(_("Product Groups Updated Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:productGroups')
                }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("Product Group Already Exist")),
                        "message" : str(_("Product Group Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('inventories:edit_productGroup',kwargs={"pk":instance.pk}),
                    }
                else:
                    data.UpdatedDate=today
                    data.Action = "M"
                    data.CreatedUserID = user.id

                    ProductGroup_Log.objects.using(DataBase).create(
                        BranchID=BranchID,
                        TransactionID=ProductGroupID,
                        GroupName=data.GroupName,
                        CategoryID=data.CategoryID,
                        Notes=data.Notes,
                        Action=data.Action,
                        CreatedUserID=user.id,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    data.save(using=DataBase)

                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("Product Groups Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('inventories:productGroups')
                    }
                return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = ProductGroupForm(instance=instance)
        category_instances = None
        if ProductCategory.objects.using(DataBase).filter(BranchID=1).exists():
            category_instances = ProductCategory.objects.using(DataBase).filter(BranchID=1)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,
            "is_edit" : True,

            "title" : "Edit productGroup",
            "category_instances" : category_instances,
            "form" : form,
            "instance" : instance,
            "DataBase" : DataBase
        }
        return render(request,"inventories/masters/create_productGroup.html",context)


@login_required
def delete_productGroup(request,pk):
    DataBase = get_DataBase(request)

    product_exist = None
    StockAdjustmentMaster_exist = None

    today = datetime.date.today()

    if pk == "1":
        response_data = {
            "status" : "false",
            "title" : str(_("Can't be Deleted")),
            "message" : str(_("This ProductGroup Can't Be Deleted Successfully!!this is a Default ProductGroup.")),
            "redirect" : "true",
            "redirect_url" : reverse('inventories:productGroups')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        instance = ProductGroup.objects.using(DataBase).get(pk=pk)

        product_exist = Product.objects.using(DataBase).filter(BranchID=instance.BranchID,ProductGroupID=instance.ProductGroupID).exists()
        StockAdjustmentMaster_exist = StockAdjustmentMaster.objects.using(DataBase).filter(BranchID=instance.BranchID,ProductGroupID=instance.ProductGroupID).exists()

        if not product_exist and not StockAdjustmentMaster_exist:
            ProductGroup_Log.objects.using(DataBase).create(
                BranchID=instance.BranchID,
                TransactionID=instance.ProductGroupID,
                GroupName=instance.GroupName,
                CategoryID=instance.CategoryID,
                Notes=instance.Notes,
                Action=instance.Action,
                CreatedUserID=user.id,
                CreatedDate=today,
                UpdatedDate=today,
                )
            instance.delete()
            
            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Deleted")),
                "message" : str(_("Product Group Deleted Successfully.")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:productGroups')
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')

        else:
            response_data = {
                "status" : "false",
                "title" : str(_("Can't be Deleted")),
                "message" : str(_("You Cant Delete this ProductGroup,this ProductGroup is already using somewhere!!")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:productGroups')
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def create_taxCategory(request):
    DataBase = get_DataBase(request)
    today = datetime.date.today()
    user = request.user

    if request.method == 'POST':
        form = TaxCategoryForm(request.POST)

        if form.is_valid(): 
            data = form.save(commit=False)

            is_nameExist = False
            TaxNameLow = data.TaxName.lower()
            taxCats = TaxCategory.objects.using(DataBase).filter(BranchID=1)

            for taxCat in taxCats:
                tax_name = taxCat.TaxName
                TaxName = tax_name.lower()

                if TaxNameLow == TaxName:
                    is_nameExist = True

            if not is_nameExist:
                data.BranchID = 1
                data.CreatedDate = today
                data.UpdatedDate=today
                data.Action = "A"
                data.CreatedUserID = user.id
                data.TaxID = get_auto_TaxID(TaxCategory,DataBase,data.BranchID)

                TaxCategory_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=data.TaxID,
                    TaxName=data.TaxName,
                    TaxType=data.TaxType,
                    PurchaseTax=data.PurchaseTax,
                    SalesTax=data.SalesTax,
                    Inclusive=data.Inclusive,
                    Action=data.Action,
                    CreatedUserID=user.id,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("TaxCategory Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:taxCategories')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Tax Already Exist")),
                    "message" : str(_("Tax Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:create_taxCategory')
                }
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = TaxCategoryForm()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create Tax",
            "form" : form,
        }
        return render(request,"inventories/masters/create_taxCategory.html",context)


@login_required
def taxCategories(request):
    DataBase = get_DataBase(request)

    instances = TaxCategory.objects.using(DataBase).filter(BranchID=1)
    query = request.GET.get("q")
    if query:
        instances = instances.filter(Q(TaxName__icontains=query))
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Tax Categories'
    }
    return render(request,"inventories/masters/taxCategories.html",context)


@login_required
def view_taxCategory(request,pk):
    DataBase = get_DataBase(request)

    instance = TaxCategory.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'TaxCategory'
    }
    return render(request,"inventories/masters/taxCategory.html",context)


@login_required
def edit_taxCategory(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()
    user = request.user

    instance = TaxCategory.objects.using(DataBase).get(pk=pk)
    TaxID = instance.TaxID
    BranchID = instance.BranchID
    instanceTaxName = instance.TaxName

    if request.method == 'POST':
        form = TaxCategoryForm(request.POST,instance=instance)

        if form.is_valid(): 
            data = form.save(commit=False)

            is_nameExist = False
            TaxNameLow = data.TaxName.lower()
            taxCats = TaxCategory.objects.using(DataBase).filter(BranchID=1)

            for taxCat in taxCats:
                tax_name = taxCat.TaxName
                TaxName = tax_name.lower()

                if TaxNameLow == TaxName:
                    is_nameExist = True

                if instanceTaxName.lower() == TaxNameLow:
                    tax_ok = True

            if tax_ok:
                data.UpdatedDate=today
                data.Action = "M"
                data.CreatedUserID = user.id
   

                TaxCategory_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=data.TaxID,
                    TaxName=data.TaxName,
                    TaxType=data.TaxType,
                    PurchaseTax=data.PurchaseTax,
                    SalesTax=data.SalesTax,
                    Inclusive=data.Inclusive,
                    Action=data.Action,
                    CreatedUserID=user.id,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Updated")),
                    "message" : str(_("TaxCategory Updated Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:taxCategories')
                }
            else:
                if is_nameExist:
                    rresponse_data = {
                        "status" : "false",
                        "title" : str(_("TaxCategory Already Exist")),
                        "message" : str(_("TaxCategory Name is Already exist with in the Branch")),
                        "redirect" : "true",
                        "redirect_url" : reverse("inventories:edit_taxCategory",kwargs={"pk":instance.pk}),
                    }
                else:
                    data.UpdatedDate=today
                    data.Action = "M"
                    data.CreatedUserID = user.id

                    TaxCategory_Log.objects.using(DataBase).create(
                        BranchID=BranchID,
                        TransactionID=TaxID,
                        TaxName=data.TaxName,
                        TaxType=data.TaxType,
                        PurchaseTax=data.PurchaseTax,
                        SalesTax=data.SalesTax,
                        Inclusive=data.Inclusive,
                        Action=data.Action,
                        CreatedUserID=user.id,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )
                    data.save(using=DataBase)

                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("TaxCategory Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('inventories:taxCategories')
                    }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
                
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = TaxCategoryForm(instance=instance)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create TaxCategory",
            "form" : form,
        }
        return render(request,"inventories/masters/create_taxCategory.html",context)


@login_required
def delete_taxCategory(request,pk):
    DataBase = get_DataBase(request)

    posholdDetails_exist = None
    purchaseDetails_exist = None
    purchaseOrderDetails_exist = None
    purchaseReturnDetails_exist = None
    salesDetails_exist = None
    salesOrderDetails_exist = None
    salesReturnDetails_exist = None

    today = datetime.date.today()  
    if pk == "1":
        response_data = {
            "status" : "false",
            "title" : str(_("Can't be Deleted")),
            "message" : str(_("This TaxCategory Can't Be Deleted Successfully!!this is a Default TaxCategory.")),
            "redirect" : "true",
            "redirect_url" : reverse('inventories:taxCategories')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:

        instance = TaxCategory.objects.using(DataBase).get(pk=pk)

        posholdDetails_exist = POSHoldDetails.objects.using(DataBase).filter(BranchID=instance.BranchID,TaxID=instance.TaxID).exists()
        purchaseDetails_exist = PurchaseMaster.objects.using(DataBase).filter(BranchID=instance.BranchID,TaxID=instance.TaxID).exists()
        purchaseOrderDetails_exist = PurchaseOrderDetails.objects.using(DataBase).filter(BranchID=instance.BranchID,TaxID=instance.TaxID).exists()
        purchaseReturnDetails_exist = PurchaseReturnMaster.objects.using(DataBase).filter(BranchID=instance.BranchID,TaxID=instance.TaxID).exists()
        salesDetails_exist = SalesMaster.objects.using(DataBase).filter(BranchID=instance.BranchID,TaxID=instance.TaxID).exists()
        salesOrderDetails_exist = SalesOrderDetails.objects.using(DataBase).filter(BranchID=instance.BranchID,TaxID=instance.TaxID).exists()
        salesReturnDetails_exist = SalesReturnMaster.objects.using(DataBase).filter(BranchID=instance.BranchID,TaxID=instance.TaxID).exists()

        if not posholdDetails_exist and not purchaseDetails_exist and not purchaseOrderDetails_exist and not purchaseReturnDetails_exist and not salesDetails_exist and not salesOrderDetails_exist and not salesReturnDetails_exist:
            TaxCategory_Log.objects.using(DataBase).create(
                BranchID=instance.BranchID,
                TransactionID=instance.TaxID,
                TaxName=instance.TaxName,
                TaxType=instance.TaxType,
                PurchaseTax=instance.PurchaseTax,
                SalesTax=instance.SalesTax,
                Inclusive=instance.Inclusive,
                Action=instance.Action,
                CreatedUserID=user.id,
                CreatedDate=today,
                UpdatedDate=today,
                )
            instance.delete()
        
            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Deleted")),
                "message" : str(_("TaxCategory Deleted Successfully.")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:taxCategories')
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        else:
            response_data = {
                "status" : "false",
                "title" : str(_("Can't be Deleted")),
                "message" : str(_("You Cant Delete this TaxCategory,this Tax is already using somewhere!!")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:taxCategories')
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def priceCategories(request):
    DataBase = get_DataBase(request)

    instances = PriceCategory.objects.using(DataBase).filter(BranchID=1)
    query = request.GET.get("q")
    if query:
        instances = instances.filter(Q(PriceCategoryName__icontains=query))
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Price Categories'
    }
    return render(request,"inventories/masters/priceCategories.html",context)


@login_required
def view_priceCategory(request,pk):
    DataBase = get_DataBase(request)

    instance = PriceCategory.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'Price Category'
    }
    return render(request,"inventories/masters/priceCategory.html",context)


@login_required
def create_productCategory(request):
    DataBase = get_DataBase(request)
    today = datetime.date.today()

    if request.method == 'POST':
        form = ProductCategoryForm(request.POST)

        if form.is_valid(): 
            data = form.save(commit=False)

            is_nameExist = False
            CategoryNameLow = data.CategoryName.lower()
            proCats = ProductCategory.objects.using(DataBase).filter(BranchID=1)

            for proCat in proCats:
                pro_name = proCat.CategoryName
                CategoryName = pro_name.lower()

                if CategoryNameLow == CategoryName:
                    is_nameExist = True

            if not is_nameExist:
                data.BranchID = 1
                data.CreatedDate = today
                data.UpdatedDate=today
                data.Action = "A"
                data.CreatedUserID = user.id
                data.ProductCategoryID = get_auto_ProductCategoryID(ProductCategory,DataBase,data.BranchID)

                ProductCategory_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=data.ProductCategoryID,
                    CategoryName=data.CategoryName,
                    Notes=data.Notes,
                    Action=data.Action,
                    CreatedUserID= user.id,
                    CreatedDate=today,
                    UpdatedDate=today,

                    )
           
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("ProductCategory Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:productCategories')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Product Category Already Exist")),
                    "message" : str(_("Product Category Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:create_productCategory')
                }
                   
            

            return HttpResponse(json.dumps(response_data), content_type='application/javascript')


        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = ProductCategoryForm()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create ProductCategory",
            "form" : form,
        }
        return render(request,"inventories/masters/create_productCategory.html",context)


@login_required
def productCategories(request):

    DataBase = get_DataBase(request)


    instances = ProductCategory.objects.using(DataBase).filter(BranchID=1)
    query = request.GET.get("q")
    if query:
        instances = instances.filter(Q(CategoryName__icontains=query))
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Product Categories'
    }
    return render(request,"inventories/masters/productCategories.html",context)


@login_required
def view_productCategory(request,pk):
    DataBase = get_DataBase(request)

    instance = ProductCategory.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'Product Category'
    }
    return render(request,"inventories/masters/productCategory.html",context)


@login_required
def edit_productCategory(request,pk):

    DataBase = get_DataBase(request)
    today = datetime.date.today()

    instance = ProductCategory.objects.using(DataBase).get(pk=pk)
    ProductCategoryID = instance.ProductCategoryID
    BranchID = instance.BranchID
    instanceCategoryName = instance.CategoryName

    if request.method == 'POST':
        form = ProductCategoryForm(request.POST,instance=instance)

        if form.is_valid(): 
            data = form.save(commit=False)
            CategoryName = data.CategoryName

            is_nameExist = False
            cat_ok = False

            is_nameExist = False
            CategoryNameLow = data.CategoryName.lower()
            categories = ProductCategory.objects.using(DataBase).filter(BranchID=BranchID)

            for category in categories:
                cat_name = category.CategoryName
                CategoryName = cat_name.lower()

                if CategoryNameLow == CategoryName:
                    is_nameExist = True

                if instanceCategoryName.lower() == CategoryNameLow:
                    cat_ok = True

            if cat_ok:
                data.UpdatedDate=today
                data.Action = "M"
                data.CreatedUserID = user.id

                ProductCategory_Log.objects.using(DataBase).create(
                    BranchID=BranchID,
                    TransactionID=ProductCategoryID,
                    CategoryName=data.CategoryName,
                    Notes=data.Notes,
                    Action=data.Action,
                    CreatedUserID=user.id,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )


                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Updated")),
                    "message" : str(_("ProductCategory Updated Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:productCategories')
                    }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("ProductCategory Already Exist")),
                        "message" : str(_("ProductCategory Name is Already exist with in the Branch")),
                        "redirect" : "true",
                        "redirect_url" : reverse("inventories:edit_productCategory",kwargs={"pk":instance.pk}),
                    }
                else:
                    data.UpdatedDate=today
                    data.Action = "M"
                    data.CreatedUserID = user.id

                    ProductCategory_Log.objects.using(DataBase).create(
                        BranchID=BranchID,
                        TransactionID=ProductCategoryID,
                        CategoryName=data.CategoryName,
                        Notes=data.Notes,
                        Action=data.Action,
                        CreatedUserID=user.id,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )
                    data.save(using=DataBase)

                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("ProductCategory Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('inventories:productCategories')
                    }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')   

        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = ProductCategoryForm(instance=instance)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create ProductCategory",
            "form" : form,
        }
        return render(request,"inventories/masters/create_productCategory.html",context)


@login_required
def delete_productCategory(request,pk):

    DataBase = get_DataBase(request)

    today = datetime.date.today()  
    if pk == "1":
        response_data = {
            "status" : "false",
            "title" : str(_("Can't be Deleted")),
            "message" : str(_("This Product Category Can't Be Deleted!!this is a Default TaxCategory.")),
            "redirect" : "true",
            "redirect_url" : reverse('inventories:productCategories')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        instance = ProductCategory.objects.using(DataBase).get(pk=pk)
        if not ProductGroup.objects.using(DataBase).filter(CategoryID=instance.ProductCategoryID,BranchID=instance.BranchID).exists():
            ProductCategory_Log.objects.using(DataBase).create(
                BranchID=instance.BranchID,
                TransactionID=instance.ProductCategoryID,
                CategoryName=instance.CategoryName,
                Notes=instance.Notes,
                Action="D",
                CreatedUserID=user.id,
                CreatedDate=today,
                UpdatedDate=today,
                )
            instance.delete()
        
            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Deleted")),
                "message" : str(_("ProductCategory Deleted Successfully.")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:productCategories')
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        else:
            response_data = {
                "status" : "false",
                "title" : str(_("Can't be Deleted")),
                "message" : str(_("You Cant Delete this ProductCategory,this Category is already using somewhere!!")),
                "redirect" : "true",
                "redirect_url" : reverse('inventories:productCategories')
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
@login_required
def create_warehouse(request):
    from api.v1.warehouses.functions import get_auto_id


    DataBase = get_DataBase(request)

    today = datetime.date.today()
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.Action = "A"
            data.BranchID = 1
            data.WarehouseID = get_auto_id(Warehouse, data.BranchID, DataBase)
            data.UpdatedDate = today
            data.CreatedUserID = request.user.id

            is_nameExist = False

            WarehouseNameLow = data.WarehouseName.lower()

            warehouses = Warehouse.objects.using(DataBase).filter(BranchID=data.BranchID)

            for warehouse in warehouses:
                warehouse_name = warehouse.WarehouseName

                warehouseName = warehouse_name.lower()

                if WarehouseNameLow == warehouseName:
                    is_nameExist = True

            if not is_nameExist:

                Warehouse_Log.objects.using(DataBase).create(
                    TransactionID=data.WarehouseID,
                    BranchID=data.BranchID,
                    WarehouseName=data.WarehouseName,
                    Notes=data.Notes,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    Action=data.Action,
                    )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Warehouse Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:warehouses')
                }
            else:
                if is_nameExist:
                    response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Warehouse Name Already exist")),
                    "message" : str("Warehouse Name Already exist with this Branch ID")
                }

            return HttpResponse(json.dumps(response_data), content_type='application/javascript')


        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = WarehouseForm()
        context = {
            "title" : "Create Warehouse",
            "form" : form
        }
        return render(request,"inventories/masters/create_warehouse.html",context)


@login_required
def warehouses(request):
    DataBase = get_DataBase(request)
    instances = Warehouse.objects.using(DataBase).all()
    context = {
        'instances' : instances,
        'title' : 'Warehouses'
    }
    return render(request,"inventories/masters/warehouses.html",context)


@login_required
def view_warehouse(request,pk):
    DataBase = get_DataBase(request)

    instance = Warehouse.objects.using(DataBase).get(pk=pk)
    context = {
        'instance' : instance,
        'title' : 'Warehouse'
    }
    return render(request,"inventories/masters/warehouse.html",context)


@login_required
def edit_warehouse(request,pk):
    DataBase = get_DataBase(request)

    today = datetime.date.today()
    instance = Warehouse.objects.using(DataBase).get(pk=pk)
    if request.method == 'POST':
        form = WarehouseForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.Action = "M"
            data.CreatedUserID = request.user.id
            data.UpdatedDate = today

            is_nameExist = False
            warehose_ok = False

            WarehouseNameLow = data.WarehouseName.lower()

            warehouses = Warehouse.objects.using(DataBase).filter(BranchID=data.BranchID)

            for warehouse in warehouses:
                warehouse_name = warehouse.WarehouseName

                warehouseName = warehouse_name.lower()

                if WarehouseNameLow == warehouseName:
                    is_nameExist = True

                if instance.WarehouseName.lower() == WarehouseNameLow:

                    warehose_ok = True


            if  warehose_ok:
                Warehouse_Log.objects.using(DataBase).create(
                    TransactionID=data.WarehouseID,
                    BranchID=data.BranchID,
                    WarehouseName=data.WarehouseName,
                    Notes=data.Notes,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    Action=data.Action,
                    )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Updated")),
                    "message" : str(_("Warehouse Updated Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:view_warehouse',kwargs={'pk':instance.pk})
                }
            else:
                if is_nameExist:
                    response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Warehouse Name Already exist")),
                    "message" : str("Warehouse Name Already exist with this Branch ID")
                }

            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
            
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = WarehouseForm(instance=instance)
        context = {
            "title" : "Edit Warehouse",
            "form" : form
        }
        return render(request,"inventories/masters/create_warehouse.html",context)


@login_required
def delete_warehouse(request,pk):
    DataBase = get_DataBase(request)
    
    today = datetime.date.today()    
    instance = Warehouse.objects.using(DataBase).get(pk=pk)

    if pk == "1":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this Warehouse")),
            "message" : str(_("Can't delete this Warehouse! this is default Warehouse!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        if Warehouse.objects.using(DataBase).filter(pk=pk).exists():
            instance = Warehouse.objects.using(DataBase).get(pk=pk)
        if instance:
            BranchID = instance.BranchID
            WarehouseID = instance.WarehouseID
            WarehouseName = instance.WarehouseName
            Notes = instance.Notes
            Action = "D"

            purchaseMaster_exist = PurchaseMaster.objects.using(DataBase).filter(BranchID=BranchID,WarehouseID=WarehouseID).exists()
            salesMaster_exist = SalesMaster.objects.using(DataBase).filter(BranchID=BranchID,WarehouseID=WarehouseID).exists()
            stockPostings_exist = StockPosting.objects.using(DataBase).filter(BranchID=BranchID,WareHouseID=WarehouseID).exists()

            if not purchaseMaster_exist and not salesMaster_exist and not stockPostings_exist:
                instance.delete()

                Warehouse_Log.objects.using(DataBase).create(
                    BranchID=BranchID,
                    TransactionID=WarehouseID,
                    WarehouseName=WarehouseName,
                    Notes=Notes,
                    Action=Action,
                    CreatedUserID=request.user.id,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Warehouse Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('inventories:warehouses')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
# Warehouse ends


@login_required
def create_purchaseInvoice(request):
    from api.v1.sales.functions import get_auto_stockPostid 
    from api.v1.purchases.functions import get_auto_id, get_auto_idMaster, get_auto_StockRateID, get_auto_StockTransID
    from accounts.functions import generateVoucherNo

    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase
    VoucherType = "PI"

    BranchID = 1
    VoucherNo = generateVoucherNo(VoucherType, BranchID, DataBase)

    PurchaseDetailsFormset = formset_factory(PurchaseDetailsForm)
    user_instance = get_object_or_404(UserTable.objects.using(DataBase).filter(UserName=user))
    
    today = datetime.date.today()
    if request.method == 'POST':

        PurchaseAccount = request.POST.get('purchaseAccount')
        LedgerID = request.POST.get('ledger')
        TaxID = request.POST.get('taxType')
        WarehouseID = request.POST.get('wareHouse')

        taxType_Instance = get_object_or_404(TransactionTypes.objects.using(DataBase).filter(BranchID=BranchID,TransactionTypesID=TaxID))

        form = PurchaseMasterForm(request.POST)
        purchaseDetails_formset = PurchaseDetailsFormset(request.POST,prefix='purchaseDetails_formset')
        if form.is_valid() and purchaseDetails_formset.is_valid(): 
            data = form.save(commit=False)
            
            data.PurchaseMasterID = get_auto_idMaster(PurchaseMaster,BranchID,DataBase)
            data.BranchID = BranchID
            data.EmployeeID = user_instance.EmployeeID
            data.FinacialYearID = 1
            data.Action = 'A'
            data.PurchaseAccount = PurchaseAccount
            data.LedgerID = LedgerID
            data.TransactionTypeID = TaxID
            data.WarehouseID = WarehouseID
            data.AdditionalCost = 0
            data.PriceCategoryID = 1
            data.TaxType = taxType_Instance.Name
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today

            is_voucherExist = False
            VoucherNoLow = data.VoucherNo.lower()
            insts = PurchaseMaster.objects.using(DataBase).filter(BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True
       
            if not is_voucherExist:
                data.save(using=DataBase)

                PurchaseMaster_Log.objects.using(DataBase).create(
                    TransactionID=data.PurchaseMasterID,
                    BranchID=data.BranchID,
                    Action=data.Action,
                    VoucherNo=data.VoucherNo,
                    RefferenceBillNo=data.RefferenceBillNo,
                    Date=data.Date,
                    VenderInvoiceDate=data.VenderInvoiceDate,
                    CreditPeriod=data.CreditPeriod,
                    LedgerID=data.LedgerID,
                    PriceCategoryID=data.PriceCategoryID,
                    EmployeeID=data.EmployeeID,
                    PurchaseAccount=data.PurchaseAccount,
                    CustomerName=data.CustomerName,
                    Address1=data.Address1,
                    Address2=data.Address2,
                    Address3=data.Address3,
                    Notes=data.Notes,
                    FinacialYearID=data.FinacialYearID,
                    TotalGrossAmt=data.TotalGrossAmt,
                    TotalTax=data.TotalTax,
                    NetTotal=data.NetTotal,
                    AddlDiscPercent=data.AddlDiscPercent,
                    AddlDiscAmt=data.AddlDiscAmt,
                    AdditionalCost=data.AdditionalCost,
                    TotalDiscount=data.TotalDiscount,
                    GrandTotal=data.GrandTotal,
                    RoundOff=data.RoundOff,
                    TransactionTypeID=data.TransactionTypeID,
                    WarehouseID=data.WarehouseID,
                    IsActive=data.IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=data.CreatedUserID,
                    TaxID=data.TaxID,
                    TaxType=data.TaxType,
                    VATAmount=data.VATAmount,
                    SGSTAmount=data.SGSTAmount,
                    CGSTAmount=data.CGSTAmount,
                    IGSTAmount=data.IGSTAmount,
                    TAX1Amount=data.TAX1Amount,
                    TAX2Amount=data.TAX2Amount,
                    TAX3Amount=data.TAX3Amount,
                    BillDiscPercent=data.BillDiscPercent,
                    BillDiscAmt=data.BillDiscAmt,
                    Balance=data.Balance
                    )

                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                LedgerPosting.objects.using(DataBase).create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=data.VoucherNo,
                    LedgerID=data.PurchaseAccount,
                    Debit=data.TotalGrossAmt,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=user.id,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )

                LedgerPosting_Log.objects.using(DataBase).create(
                    TransactionID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=data.VoucherNo,
                    LedgerID=data.PurchaseAccount,
                    Debit=data.TotalGrossAmt,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=user.id,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )

                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                LedgerPosting.objects.using(DataBase).create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=data.VoucherNo,
                    LedgerID=data.LedgerID,
                    Credit=data.GrandTotal,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=user.id,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )

                LedgerPosting_Log.objects.using(DataBase).create(
                    TransactionID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=data.VoucherNo,
                    LedgerID=data.LedgerID,
                    Credit=data.GrandTotal,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=user.id,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )

                if float(data.TotalTax) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerID = "55"

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Debit=data.TotalTax,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=user.id,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Debit=data.TotalTax,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=user.id,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                if float(data.TotalDiscount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerID = "74"

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Credit=data.TotalDiscount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=user.id,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Credit=data.TotalDiscount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=user.id,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                if float(data.RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerID = "78"

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Debit=data.RoundOff,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=user.id,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Debit=data.RoundOff,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=user.id,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                if float(data.RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    RoundOff = abs(float(data.RoundOff))

                    LedgerID = "78"

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Credit=RoundOff,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=user.id,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Credit=RoundOff,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=user.id,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

        

                
                # AutoBarcode = get_auto_AutoBarcode(PriceList,BranchID,DataBase)

                for f in purchaseDetails_formset:
                    Qty = f.cleaned_data['Qty']
                    FreeQty = f.cleaned_data['FreeQty']
                    UnitPrice = f.cleaned_data['UnitPrice']
                    RateWithTax = f.cleaned_data['RateWithTax']
                    CostPerItem = f.cleaned_data['CostPerItem']
                    PriceListID = f.cleaned_data['PriceListID']
                    DiscountPerc = f.cleaned_data['DiscountPerc']
                    DiscountAmount = f.cleaned_data['DiscountAmount']
                    AddlDiscPerc = f.cleaned_data['AddlDiscPerc']
                    AddlDiscAmt = f.cleaned_data['AddlDiscAmt']
                    GrossAmount = f.cleaned_data['GrossAmount']
                    TaxableAmount = f.cleaned_data['TaxableAmount']
                    VATPerc = f.cleaned_data['VATPerc']
                    VATAmount = f.cleaned_data['VATAmount']
                    SGSTPerc = f.cleaned_data['SGSTPerc']
                    SGSTAmount = f.cleaned_data['SGSTAmount']
                    CGSTPerc = f.cleaned_data['CGSTPerc']
                    CGSTAmount = f.cleaned_data['CGSTAmount']
                    IGSTPerc = f.cleaned_data['IGSTPerc']
                    IGSTAmount = f.cleaned_data['IGSTAmount']
                    NetAmount = f.cleaned_data['NetAmount']
                    TAX1Perc = f.cleaned_data['TAX1Perc']
                    TAX1Amount = f.cleaned_data['TAX1Amount']
                    TAX2Perc = f.cleaned_data['TAX2Perc']
                    TAX2Amount = f.cleaned_data['TAX2Amount']
                    TAX3Perc = f.cleaned_data['TAX3Perc']
                    TAX3Amount = f.cleaned_data['TAX3Amount']
                    ProductID = f.cleaned_data['ProductID']

                    # UnitPrice = request.POST.get('unitAmount')
                    # PriceListID = request.POST.get('PriceListID')

                    PurchaseDetailsID = get_auto_id(PurchaseDetails,BranchID,DataBase)
                    PurchaseDetails.objects.using(DataBase).create(
                        PurchaseDetailsID=PurchaseDetailsID,
                        BranchID=BranchID,
                        Action=data.Action,
                        PurchaseMasterID=data.PurchaseMasterID,
                        purchase_master=data,
                        ProductID=ProductID,
                        Qty=Qty,
                        FreeQty=FreeQty,
                        UnitPrice=UnitPrice,
                        RateWithTax=RateWithTax,
                        CostPerItem=CostPerItem,
                        PriceListID=PriceListID,
                        DiscountPerc=DiscountPerc,
                        DiscountAmount=DiscountAmount,
                        AddlDiscPerc=AddlDiscPerc,
                        AddlDiscAmt=AddlDiscAmt,
                        GrossAmount=GrossAmount,
                        TaxableAmount=TaxableAmount,
                        VATPerc=VATPerc,
                        VATAmount=VATAmount,
                        SGSTPerc=SGSTPerc,
                        SGSTAmount=SGSTAmount,
                        CGSTPerc=CGSTPerc,
                        CGSTAmount=CGSTAmount,
                        IGSTPerc=IGSTPerc,
                        IGSTAmount=IGSTAmount,
                        NetAmount=NetAmount,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=user.id,
                        TAX1Perc=TAX1Perc,
                        TAX1Amount=TAX1Amount,
                        TAX2Perc=TAX2Perc,
                        TAX2Amount=TAX2Amount,
                        TAX3Perc=TAX3Perc,
                        TAX3Amount=TAX3Amount,
                        )

                    PurchaseDetails_Log.objects.using(DataBase).create(
                        TransactionID=PurchaseDetailsID,
                        BranchID=BranchID,
                        Action=data.Action,
                        PurchaseMasterID=data.PurchaseMasterID,
                        ProductID=ProductID,
                        Qty=Qty,
                        FreeQty=FreeQty,
                        UnitPrice=UnitPrice,
                        RateWithTax=RateWithTax,
                        CostPerItem=CostPerItem,
                        PriceListID=PriceListID,
                        DiscountPerc=DiscountPerc,
                        DiscountAmount=DiscountAmount,
                        AddlDiscPerc=AddlDiscPerc,
                        AddlDiscAmt=AddlDiscAmt,
                        GrossAmount=GrossAmount,
                        TaxableAmount=TaxableAmount,
                        VATPerc=VATPerc,
                        VATAmount=VATAmount,
                        SGSTPerc=SGSTPerc,
                        SGSTAmount=SGSTAmount,
                        CGSTPerc=CGSTPerc,
                        CGSTAmount=CGSTAmount,
                        IGSTPerc=IGSTPerc,
                        IGSTAmount=IGSTAmount,
                        NetAmount=NetAmount,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=user.id,
                        TAX1Perc=TAX1Perc,
                        TAX1Amount=TAX1Amount,
                        TAX2Perc=TAX2Perc,
                        TAX2Amount=TAX2Amount,
                        TAX3Perc=TAX3Perc,
                        TAX3Amount=TAX3Amount,
                        )

                    StockPostingID = get_auto_stockPostid(StockPosting,BranchID,DataBase)
                    BatchID = 1
                    StockPosting.objects.using(DataBase).create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=data.Action,
                        Date=data.Date,
                        VoucherMasterID=data.PurchaseMasterID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
                        WareHouseID=data.WarehouseID,
                        QtyIn=Qty,
                        Rate=CostPerItem,
                        PriceListID=PriceListID,
                        IsActive=data.IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=user.id
                        )

                    StockPosting_Log.objects.using(DataBase).create(
                        TransactionID=StockPostingID,
                        BranchID=BranchID,
                        Action=data.Action,
                        Date=data.Date,
                        VoucherMasterID=data.PurchaseMasterID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
                        WareHouseID=data.WarehouseID,
                        QtyIn=Qty,
                        Rate=CostPerItem,
                        PriceListID=PriceListID,
                        IsActive=data.IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=user.id
                        )

                    priceList = PriceList.objects.using(DataBase).get(ProductID=ProductID,DefaultUnit=True,BranchID=BranchID)

                    PriceListID = priceList.PriceListID
                    MultiFactor = priceList.MultiFactor

                    PurchasePrice = priceList.PurchasePrice
                    SalesPrice = priceList.SalesPrice

                    qty = float(FreeQty) + float(Qty)

                    Qty = float(MultiFactor) * float(qty)
                    Cost = float(CostPerItem) /  float(MultiFactor)

                    Qy = round(Qty,4)
                    Qty = str(Qy)

                    Ct = round(Cost,4)
                    Cost = str(Ct)

                    stockRateInstance = None

                    if StockRate.objects.using(DataBase).filter(BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=data.WarehouseID,PriceListID=PriceListID).exists():
                        stockRateInstance = StockRate.objects.using(DataBase).get(BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=data.WarehouseID,PriceListID=PriceListID)
                        
                        StockRateID = stockRateInstance.StockRateID
                        stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
                        stockRateInstance.save()

                        StockTransID = get_auto_StockTransID(StockTrans,BranchID,DataBase)
                        StockTrans.objects.using(DataBase).create(
                            StockTransID=StockTransID,
                            BranchID=BranchID,
                            VoucherType=VoucherType,
                            StockRateID=StockRateID,
                            DetailID=PurchaseDetailsID,
                            MasterID=data.PurchaseMasterID,
                            Qty=Qty,
                            IsActive=data.IsActive
                            )
                    else:
                        StockRateID = get_auto_StockRateID(StockRate,BranchID,DataBase)
                        StockRate.objects.using(DataBase).create(
                            StockRateID=StockRateID,
                            BranchID=BranchID,
                            BatchID=BatchID,
                            PurchasePrice=PurchasePrice,
                            SalesPrice=SalesPrice,
                            Qty=Qty,
                            Cost=Cost,
                            ProductID=ProductID,
                            WareHouseID=data.WarehouseID,
                            Date=data.Date,
                            PriceListID=PriceListID,
                            CreatedUserID=user.id,
                            CreatedDate=today,
                            UpdatedDate=today,
                            )

                        StockTransID = get_auto_StockTransID(StockTrans,BranchID,DataBase)
                        StockTrans.objects.using(DataBase).create(
                            StockTransID=StockTransID,
                            BranchID=BranchID,
                            VoucherType=VoucherType,
                            StockRateID=StockRateID,
                            DetailID=PurchaseDetailsID,
                            MasterID=data.PurchaseMasterID,
                            Qty=Qty,
                            IsActive=data.IsActive
                            )

                

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Purchase Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('inventories:purchaseInvoices')
                }
            else:
                message = generate_form_errors(form,formset=False)
                response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("VoucherNo already exist!")),
                    "message" : str("VoucherNo Already Exist in this Branch!!!")
                }

        else:
            # message = generate_form_errors(form,formset=False)
            message = generate_form_errors(purchaseDetails_formset,formset=True)
            # print(form.errors)
            print(purchaseDetails_formset.errors)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        user = user.id
        BranchID = 1
        ledger_instances = None
        priceCategory_instances = None
        if AccountLedger.objects.using(DataBase).filter(BranchID=BranchID,AccountGroupUnder__in=[8,9,10,29]).exists():
            ledger_instances = AccountLedger.objects.using(DataBase).filter(BranchID=BranchID,AccountGroupUnder__in=[8,9,10,29])
        ledger_instances = None
        if PriceCategory.objects.using(DataBase).filter(BranchID=BranchID).exists():
            priceCategory_instances = PriceCategory.objects.using(DataBase).filter(BranchID=BranchID)

        product_datas = Product.objects.using(DataBase).filter(BranchID=1)
        ledger_datas = AccountLedger.objects.using(DataBase).filter(BranchID=BranchID,AccountGroupUnder__in=[8,9,10,29])
        purchaseAccount_datas = AccountLedger.objects.using(DataBase).filter(BranchID=BranchID,AccountGroupUnder=48)
        wareHouse_datas = Warehouse.objects.using(DataBase).filter(BranchID=BranchID)

        form = PurchaseMasterForm(initial={'VoucherNo' : VoucherNo })
        purchaseDetails_formset = PurchaseDetailsFormset(prefix='purchaseDetails_formset')
        
        is_VAT = False
        is_GST = False
        is_TAX1 = False
        is_TAX2 = False
        is_TAX3 = False

        if GeneralSettings.objects.using(DataBase).filter(SettingsType='VAT',SettingsValue=True).exists():
            is_VAT = True
        if GeneralSettings.objects.using(DataBase).filter(SettingsType='GST',SettingsValue=True).exists():
            is_GST = True
        if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX1',SettingsValue=True).exists():
            is_TAX1 = True
        if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX2',SettingsValue=True).exists():
            is_TAX2 = True
        if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX3',SettingsValue=True).exists():
            is_TAX3 = True

        taxType_datas = None
        if is_VAT:
            taxType_datas = TransactionTypes.objects.using(DataBase).filter(BranchID=BranchID,MasterTypeID=8)
        if is_GST:
            taxType_datas = TransactionTypes.objects.using(DataBase).filter(BranchID=BranchID,MasterTypeID=7)

        context = {
            "title" : "Create Purchase Invoice",
            "form" : form,
            "ledger_instances" : ledger_instances,
            "priceCategory_instances" : priceCategory_instances,
            "purchaseDetails_formset" : purchaseDetails_formset,
            "product_datas" : product_datas,
            "ledger_datas" : ledger_datas,
            "wareHouse_datas" : wareHouse_datas,
            "taxType_datas" : taxType_datas,
            "purchaseAccount_datas" : purchaseAccount_datas,
            "is_VAT" : is_VAT,
            "is_GST" : is_GST,
            "is_TAX1" : is_TAX1,
            "is_TAX2" : is_TAX2,
            "is_TAX3" : is_TAX3,
            "is_need_formset" : True
        }
        return render(request,"inventories/masters/create_purchaseInvoice.html",context)



@login_required
def purchaseInvoices(request):
    DataBase = get_DataBase(request)
    BranchID = 1
    instances = PurchaseMaster.objects.using(DataBase).filter(BranchID=BranchID)
    context = {
        'instances' : instances,
        'title' : 'Purchase Invoices'
    }
    return render(request,"inventories/masters/purchaseInvoices.html",context)



def get_unitPrice(request):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase

    test_arr = []
    product_id = request.GET.get('product_id')

    BranchID = 1

    if Product.objects.using(DataBase).filter(ProductID=product_id,BranchID=BranchID).exists():
        product_instance = get_object_or_404(Product.objects.using(DataBase).filter(ProductID=product_id,BranchID=BranchID))
        TaxID1 = product_instance.Tax1
        TaxID2 = product_instance.Tax2
        TaxID3 = product_instance.Tax3
        GST = product_instance.GST
        VatID = product_instance.VatID
        BranchID = product_instance.BranchID

        Tax1_PurchaseTax = 0
        Tax2_PurchaseTax = 0
        Tax3_PurchaseTax = 0
        GST_PurchaseTax = 0
        Vat_PurchaseTax = 0

        if TaxCategory.objects.using(DataBase).filter(TaxID=TaxID1,BranchID=BranchID).exists():
            tax = TaxCategory.objects.using(DataBase).get(TaxID=TaxID1,BranchID=BranchID)
            PurchaseTax = tax.PurchaseTax
            Tax1_PurchaseTax = round(PurchaseTax,2)

        if TaxCategory.objects.using(DataBase).filter(TaxID=TaxID2,BranchID=BranchID).exists():
            tax = TaxCategory.objects.using(DataBase).get(TaxID=TaxID2,BranchID=BranchID)
            PurchaseTax = tax.PurchaseTax
            Tax2_PurchaseTax = round(PurchaseTax,2)

        if TaxCategory.objects.using(DataBase).filter(TaxID=TaxID3,BranchID=BranchID).exists():
            tax = TaxCategory.objects.using(DataBase).get(TaxID=TaxID3,BranchID=BranchID)
            PurchaseTax = tax.PurchaseTax
            Tax3_PurchaseTax = round(PurchaseTax,2)

        if TaxCategory.objects.using(DataBase).filter(TaxID=GST,BranchID=BranchID).exists():
            tax = TaxCategory.objects.using(DataBase).get(TaxID=GST,BranchID=BranchID)
            PurchaseTax = tax.PurchaseTax
            GST_PurchaseTax = round(PurchaseTax,2)

        if TaxCategory.objects.using(DataBase).filter(TaxID=VatID,BranchID=BranchID).exists():
            tax = TaxCategory.objects.using(DataBase).get(TaxID=VatID,BranchID=BranchID)
            PurchaseTax = tax.PurchaseTax
            Vat_PurchaseTax = round(PurchaseTax,2)
   
        if PriceList.objects.using(DataBase).filter(ProductID=product_id,BranchID=BranchID).exists():
            priceList = PriceList.objects.using(DataBase).filter(ProductID=product_id,BranchID=1)
     
            for p in priceList:
                test_dic = {
                 'PurchasePrice' : float(p.PurchasePrice),
                 'UnitName' : p.UnitName,
                 "PriceListID" : p.PriceListID,
                }
                test_arr. append(test_dic)
            
            response_data = {
                "status" : "true",
                "test_arr" : test_arr,
                "Tax1_PurchaseTax" : float(Tax1_PurchaseTax),
                "Tax2_PurchaseTax" : float(Tax2_PurchaseTax),
                "Tax3_PurchaseTax" : float(Tax3_PurchaseTax),
                "GST_PurchaseTax" : float(GST_PurchaseTax),
                "Vat_PurchaseTax" : float(Vat_PurchaseTax),
            }
        else:
            response_data = {
                "status" : "false",
                "message" : "PriceList is not exists."
            }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        response_data = {
            "status" : "false",
            "message" : "Product is not exists."
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')



def get_amount(request):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase

    PriceListID = request.GET.get('PriceListID')
 
    if PriceList.objects.using(DataBase).filter(PriceListID=PriceListID,BranchID=1).exists():
        priceList = get_object_or_404(PriceList.objects.using(DataBase).filter(PriceListID=PriceListID,BranchID=1))
 
        response_data = {
            "status" : "true",
            "PurchasePrice" : float(priceList.PurchasePrice),
        }
    else:
        response_data = {
            "status" : "false",
            "message" : "PriceList is not exists."
        }
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')




@login_required
def edit_purchaseInvoice(request,pk):
    from api.v1.sales.functions import get_auto_stockPostid 
    from api.v1.purchases.functions import get_auto_id, get_auto_idMaster, get_auto_StockRateID, get_auto_StockTransID
    from accounts.functions import generateVoucherNo

    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase
    VoucherType = "PI"

    instance = get_object_or_404(PurchaseMaster.objects.using(DataBase).filter(pk=pk))
    item_qryset = PurchaseDetails.objects.using(DataBase).filter(purchase_master=instance)

    
    PurchaseMasterID = instance.PurchaseMasterID
    VoucherNo = instance.VoucherNo
    BranchID = instance.BranchID

    
    user_instance = get_object_or_404(UserTable.objects.using(DataBase).filter(UserName=user))
    today = datetime.date.today()

    Action = "M"

    # if request.method == 'POST':

    #     response_data = {
    #         "status" : "true",
    #     }
    #     return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    # else:

    user = user.id
    BranchID = 1
    ledger_instances = None
    priceCategory_instances = None
    if AccountLedger.objects.using(DataBase).filter(BranchID=BranchID,AccountGroupUnder__in=[8,9,10,29]).exists():
        ledger_instances = AccountLedger.objects.using(DataBase).filter(BranchID=BranchID,AccountGroupUnder__in=[8,9,10,29])
    ledger_instances = None
    if PriceCategory.objects.using(DataBase).filter(BranchID=BranchID).exists():
        priceCategory_instances = PriceCategory.objects.using(DataBase).filter(BranchID=BranchID)

    product_datas = Product.objects.using(DataBase).filter(BranchID=1)
    ledger_datas = AccountLedger.objects.using(DataBase).filter(BranchID=BranchID,AccountGroupUnder__in=[8,9,10,29])
    purchaseAccount_datas = AccountLedger.objects.using(DataBase).filter(BranchID=BranchID,AccountGroupUnder=48)
    wareHouse_datas = Warehouse.objects.using(DataBase).filter(BranchID=BranchID)

    form = PurchaseMasterForm(instance=instance)

    is_VAT = False
    is_GST = False
    is_TAX1 = False
    is_TAX2 = False
    is_TAX3 = False

    if GeneralSettings.objects.using(DataBase).filter(SettingsType='VAT',SettingsValue=True).exists():
        is_VAT = True
    if GeneralSettings.objects.using(DataBase).filter(SettingsType='GST',SettingsValue=True).exists():
        is_GST = True
    if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX1',SettingsValue=True).exists():
        is_TAX1 = True
    if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX2',SettingsValue=True).exists():
        is_TAX2 = True
    if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX3',SettingsValue=True).exists():
        is_TAX3 = True

    if is_VAT:
        taxType_datas = TransactionTypes.objects.using(DataBase).filter(BranchID=BranchID,MasterTypeID=8)
    if is_GST:
        taxType_datas = TransactionTypes.objects.using(DataBase).filter(BranchID=BranchID,MasterTypeID=7)

    context = {
        "title" : "Create Purchase Invoice",
        "form" : form,
        "ledger_instances" : ledger_instances,
        "priceCategory_instances" : priceCategory_instances,
        "product_datas" : product_datas,
        "ledger_datas" : ledger_datas,
        "wareHouse_datas" : wareHouse_datas,
        "taxType_datas" : taxType_datas,
        "purchaseAccount_datas" : purchaseAccount_datas,
        "is_VAT" : is_VAT,
        "is_GST" : is_GST,
        "is_TAX1" : is_TAX1,
        "is_TAX2" : is_TAX2,
        "is_TAX3" : is_TAX3,
        "item_qryset" : item_qryset,
        "instance" : instance,
        "DataBase" : DataBase,

        "is_edit" : True,
        "is_need_formset" : False
    }
    return render(request,"duplyformset.html",context)



def get_purchaseDetails(request):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase

    instanceID = request.GET.get('id')

    instance = get_object_or_404(PurchaseMaster.objects.using(DataBase).filter(id=instanceID))

    BranchID = 1
    test_arr = []
    ProductID = 0
    UnitPrice = 0
    Qty = 0
    NetAmount = 0

    is_VAT = False
    is_GST = False
    is_TAX1 = False
    is_TAX2 = False
    is_TAX3 = False

    if GeneralSettings.objects.using(DataBase).filter(SettingsType='VAT',SettingsValue=True).exists():
        is_VAT = True
    if GeneralSettings.objects.using(DataBase).filter(SettingsType='GST',SettingsValue=True).exists():
        is_GST = True
    if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX1',SettingsValue=True).exists():
        is_TAX1 = True
    if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX2',SettingsValue=True).exists():
        is_TAX2 = True
    if GeneralSettings.objects.using(DataBase).filter(SettingsType='TAX3',SettingsValue=True).exists():
        is_TAX3 = True

    if is_VAT:
        taxType_datas = TransactionTypes.objects.using(DataBase).filter(BranchID=BranchID,MasterTypeID=8)
    if is_GST:
        taxType_datas = TransactionTypes.objects.using(DataBase).filter(BranchID=BranchID,MasterTypeID=7)

    if PurchaseDetails.objects.using(DataBase).filter(purchase_master=instance).exists():
        purchaseDetails = PurchaseDetails.objects.using(DataBase).filter(purchase_master=instance)
        
        for p in purchaseDetails:
            product_instance = get_object_or_404(Product.objects.using(DataBase).filter(ProductID=p.ProductID,BranchID=BranchID))
            product_name = product_instance.ProductName

            TAX1Perc = p.TAX1Perc
            if TAX1Perc == None:
                TAX1Perc = 0

            TAX1Amount = p.TAX1Amount
            if TAX1Amount == None:
                TAX1Amount = 0

            TAX2Perc = p.TAX2Perc
            if TAX2Perc == None:
                TAX2Perc = 0

            TAX2Amount = p.TAX2Amount
            if TAX2Amount == None:
                TAX2Amount = 0

            TAX3Perc = p.TAX3Perc
            if TAX3Perc == None:
                TAX3Perc = 0

            TAX3Amount = p.TAX3Amount
            if TAX3Amount == None:
                TAX3Amount = 0

            VATPerc = p.VATPerc
            if VATPerc == None:
                VATPerc = 0

            VATAmount = p.VATAmount
            if VATAmount == None:
                VATAmount = 0

            SGSTPerc = p.SGSTPerc
            if SGSTPerc == None:
                SGSTPerc = 0

            SGSTAmount = p.SGSTAmount
            if SGSTAmount == None:
                SGSTAmount = 0

            CGSTPerc = p.CGSTPerc
            if CGSTPerc == None:
                CGSTPerc = 0

            CGSTAmount = p.CGSTAmount
            if CGSTAmount == None:
                CGSTAmount = 0

            IGSTPerc = p.IGSTPerc
            if IGSTPerc == None:
                IGSTPerc = 0

            IGSTAmount = p.IGSTAmount
            if IGSTAmount == None:
                IGSTAmount = 0


            TotalTax = (TAX1Amount + TAX2Amount + TAX3Amount + VATAmount + SGSTAmount + CGSTAmount + IGSTAmount)

            test_dic = {
            # 'defltOption' : product_name,
             'UnitPrice' : float(p.UnitPrice),
             'Qty' : float(p.Qty),
             "FreeQty" : float(p.FreeQty),
             "RateWithTax" : float(p.RateWithTax),
             "CostPerItem" : float(p.CostPerItem),
             "DiscountPerc" : float(p.DiscountPerc),
             "DiscountAmount" : float(p.DiscountAmount),
             "AddlDiscPerc" : float(p.AddlDiscPerc),
             "AddlDiscAmt" : float(p.AddlDiscAmt),
             "TaxableAmount" : float(p.TaxableAmount),
             "VATPerc" : float(VATPerc),
             "VATAmount" : float(VATAmount),
             "SGSTPerc" : float(SGSTPerc),
             "SGSTAmount" : float(SGSTAmount),
             "CGSTPerc" : float(CGSTPerc),
             "CGSTAmount" : float(CGSTAmount),
             "IGSTPerc" : float(IGSTPerc),
             "IGSTAmount" : float(IGSTAmount),
             "NetAmount" : float(p.NetAmount),
             "GrossAmount" : float(p.GrossAmount),
             "TAX1Perc" : float(TAX1Perc),
             "TAX1Amount" : float(TAX1Amount),
             "TAX2Perc" : float(TAX2Perc),
             "TAX2Amount" : float(TAX2Amount),
             "TAX3Perc" : float(TAX3Perc),
             "TAX3Amount" : float(TAX3Amount),
             "TotalTax" : float(TotalTax),
             'pppp' : p.ProductID,
             'PriceListID' : p.PriceListID,
             'PurchaseDetailUniqID' : p.id,
             "ProductName" : product_name,
            }
            test_arr.append(test_dic)

            
        response_data = {
            "status" : "true",
            "test_arr" : test_arr,
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        response_data = {
            "status" : "false",
            "message" : "Product is not exists."
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')


from django.views.decorators.csrf import csrf_protect
@csrf_protect
def post_purchaseEdited(request):

    from api.v1.purchases.functions import get_auto_id, get_auto_idMaster, get_auto_StockRateID, get_auto_StockTransID
    from api.v1.sales.functions import get_auto_stockPostid 

    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase
    today = datetime.date.today()

    Action = "M"
    CreatedUserID = user.id

    BatchID = 1

    user_instance = get_object_or_404(UserTable.objects.using(DataBase).filter(UserName=user))
   
    masterArray = json.loads(request.POST.get('masterArray'))

    for i in masterArray:

        pk = i['masterID']
        RefferenceBillNo = i['RefferenceBillNo']
        date = i['date']
        VenderInvoiceDate = i['VenderInvoiceDate']
        CreditPeriod = i['CreditPeriod']
        LedgerID = i['LedgerID']
        tax_type = i['tax_type']
        tax_id = i['tax_id']
        purchaseAccount = i['purchaseAccount']
        wareHouse = i['wareHouse']
        voucherNo = i['voucherNo']
        customerName = i['customerName']
        address1 = i['address1']
        address2 = i['address2']
        address3 = i['address3']
        notes = i['notes']
        TotalGrossAmt = i['TotalGrossAmt']
        AddlDiscAmt = i['AddlDiscAmt']
        AddlDiscPercent = i['AddlDiscPercent']
        TotalTax = i['TotalTax']
        NetTotal = i['NetTotal']
        TotalDiscount = i['TotalDiscount']
        GrandTotal = i['GrandTotal']
        RoundOff = i['RoundOff']
        SGSTAmount = i['SGSTAmount']
        CGSTAmount = i['CGSTAmount']
        IGSTAmount = i['IGSTAmount']
        TAX1Amount = i['TAX1Amount']
        TAX2Amount = i['TAX2Amount']
        TAX3Amount = i['TAX3Amount']
        VATAmount = i['VATAmount']
        BillDiscPercent = i['BillDiscPercent']
        BillDiscAmt = i['BillDiscAmt']
        Balance = i['Balance']
        IsActive = i['IsActive']


    purchaseMaster_instance = PurchaseMaster.objects.using(DataBase).get(pk=pk)
    PurchaseMasterID = purchaseMaster_instance.PurchaseMasterID
    BranchID = purchaseMaster_instance.BranchID
    VoucherNo = purchaseMaster_instance.VoucherNo
    PriceCategoryID = purchaseMaster_instance.PriceCategoryID
    FinacialYearID = purchaseMaster_instance.FinacialYearID
    AdditionalCost = purchaseMaster_instance.AdditionalCost

    purchaseMaster_instance.RefferenceBillNo = RefferenceBillNo
    purchaseMaster_instance.Date = date
    purchaseMaster_instance.VenderInvoiceDate = VenderInvoiceDate
    purchaseMaster_instance.CreditPeriod = CreditPeriod
    purchaseMaster_instance.LedgerID = LedgerID
    purchaseMaster_instance.EmployeeID = user_instance.EmployeeID
    purchaseMaster_instance.PurchaseAccount = purchaseAccount
    purchaseMaster_instance.CustomerName = customerName
    purchaseMaster_instance.Address1 = address1
    purchaseMaster_instance.Address2 = address2
    purchaseMaster_instance.Address3 = address3
    purchaseMaster_instance.Notes = notes
    purchaseMaster_instance.TotalGrossAmt = TotalGrossAmt
    purchaseMaster_instance.TotalTax = TotalTax
    purchaseMaster_instance.NetTotal = NetTotal
    purchaseMaster_instance.AddlDiscPercent = AddlDiscPercent
    purchaseMaster_instance.AddlDiscAmt = AddlDiscAmt
    purchaseMaster_instance.TotalDiscount = TotalDiscount
    purchaseMaster_instance.GrandTotal = GrandTotal
    purchaseMaster_instance.RoundOff = RoundOff
    purchaseMaster_instance.TransactionTypeID = tax_id
    purchaseMaster_instance.WarehouseID = wareHouse
    purchaseMaster_instance.IsActive = IsActive
    purchaseMaster_instance.Action = Action
    purchaseMaster_instance.UpdatedDate = today
    purchaseMaster_instance.CreatedUserID = CreatedUserID
    purchaseMaster_instance.TaxID = tax_id
    purchaseMaster_instance.TaxType = tax_type
    purchaseMaster_instance.VATAmount = VATAmount
    purchaseMaster_instance.SGSTAmount = SGSTAmount
    purchaseMaster_instance.CGSTAmount = CGSTAmount
    purchaseMaster_instance.IGSTAmount = IGSTAmount
    purchaseMaster_instance.TAX1Amount = TAX1Amount
    purchaseMaster_instance.TAX2Amount = TAX2Amount
    purchaseMaster_instance.TAX3Amount = TAX3Amount
    purchaseMaster_instance.BillDiscPercent = BillDiscPercent
    purchaseMaster_instance.BillDiscAmt = BillDiscAmt
    purchaseMaster_instance.Balance = Balance

    purchaseMaster_instance.save()


    PurchaseMaster_Log.objects.using(DataBase).create(
        TransactionID=PurchaseMasterID,
        BranchID=BranchID,
        Action=Action,
        VoucherNo=VoucherNo,
        RefferenceBillNo=RefferenceBillNo,
        Date=date,
        VenderInvoiceDate=VenderInvoiceDate,
        CreditPeriod=CreditPeriod,
        LedgerID=LedgerID,
        PriceCategoryID=PriceCategoryID,
        EmployeeID=user_instance.EmployeeID,
        PurchaseAccount=purchaseAccount,
        CustomerName=customerName,
        Address1=address1,
        Address2=address2,
        Address3=address3,
        Notes=notes,
        FinacialYearID=FinacialYearID,
        TotalGrossAmt=TotalGrossAmt,
        TotalTax=TotalTax,
        NetTotal=NetTotal,
        AddlDiscPercent=AddlDiscPercent,
        AddlDiscAmt=AddlDiscAmt,
        AdditionalCost=AdditionalCost,
        TotalDiscount=TotalDiscount,
        GrandTotal=GrandTotal,
        RoundOff=RoundOff,
        TransactionTypeID=tax_id,
        WarehouseID=wareHouse,
        IsActive=IsActive,
        CreatedDate=today,
        UpdatedDate=today,
        CreatedUserID=CreatedUserID,
        TaxID=tax_id,
        TaxType=tax_type,
        VATAmount=VATAmount,
        SGSTAmount=SGSTAmount,
        CGSTAmount=CGSTAmount,
        IGSTAmount=IGSTAmount,
        TAX1Amount=TAX1Amount,
        TAX2Amount=TAX2Amount,
        TAX3Amount=TAX3Amount,
        BillDiscPercent=BillDiscPercent,
        BillDiscAmt=BillDiscAmt,
        Balance=Balance,
        )

    

    if LedgerPosting.objects.using(DataBase).filter(VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():

        ledgerPostInstances = LedgerPosting.objects.using(DataBase).filter(VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")
        
        for ledgerPostInstance in ledgerPostInstances:
            
            ledgerPostInstance.delete()

    if StockPosting.objects.using(DataBase).filter( VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():

        stockPostingInstances = StockPosting.objects.using(DataBase).filter( VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")
        
        for stockPostingInstance in stockPostingInstances:
    
            stockPostingInstance.delete()


    VoucherType = "PI"

    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

    LedgerPosting.objects.using(DataBase).create(
        LedgerPostingID=LedgerPostingID,
        BranchID=BranchID,
        Date=date,
        VoucherMasterID=PurchaseMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=purchaseAccount,
        Debit=TotalGrossAmt,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        )

    LedgerPosting_Log.objects.using(DataBase).create(
        TransactionID=LedgerPostingID,
        BranchID=BranchID,
        Date=date,
        VoucherMasterID=PurchaseMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=purchaseAccount,
        Debit=TotalGrossAmt,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        )

    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

    LedgerPosting.objects.using(DataBase).create(
        LedgerPostingID=LedgerPostingID,
        BranchID=BranchID,
        Date=date,
        VoucherMasterID=PurchaseMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=LedgerID,
        Credit=GrandTotal,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        )

    LedgerPosting_Log.objects.using(DataBase).create(
        TransactionID=LedgerPostingID,
        BranchID=BranchID,
        Date=date,
        VoucherMasterID=PurchaseMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=LedgerID,
        Credit=GrandTotal,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        )

    if float(TotalTax) > 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

        LedgerID = "55"

        LedgerPosting.objects.using(DataBase).create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=TotalTax,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            )

        LedgerPosting_Log.objects.using(DataBase).create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=TotalTax,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            )

    if float(TotalDiscount) > 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

        LedgerID = "74"

        LedgerPosting.objects.using(DataBase).create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=TotalDiscount,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            )

        LedgerPosting_Log.objects.using(DataBase).create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=TotalDiscount,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            )

    if float(RoundOff) > 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

        LedgerID = "78"

        LedgerPosting.objects.using(DataBase).create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=RoundOff,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            )

        LedgerPosting_Log.objects.using(DataBase).create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=RoundOff,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            )

    if float(RoundOff) < 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

        RoundOff = abs(float(RoundOff))

        LedgerID = "78"

        LedgerPosting.objects.using(DataBase).create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=RoundOff,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            )

        LedgerPosting_Log.objects.using(DataBase).create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=RoundOff,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            )


    formArray = json.loads(request.POST.get('formArray'))

    detail_ids = []

    for f in formArray:
        pk = f['PurchaseDetailUniqID']
        ProductID = f['product_id']
        Qty = f['Qty']
        FreeQty = f['FreeQty']
        UnitPrice = f['unitAmount']
        RateWithTax = f['RateWithTax']
        CostPerItem = f['CostPerItem']
        PriceListID = f['PriceListID']
        DiscountPerc = f['DiscountPerc']
        DiscountAmount = f['DiscountAmount']
        AddlDiscPerc = f['AddlDiscPerc']
        AddlDiscAmt = f['AddlDiscAmt']
        GrossAmount = f['GrossAmount']
        TaxableAmount = f['TaxableAmount']
        VATPerc = f['VATPerc']
        VATAmount = f['VATAmount']
        SGSTPerc = f['SGSTPerc']
        SGSTAmount = f['SGSTAmount']
        CGSTPerc = f['CGSTPerc']
        CGSTAmount = f['CGSTAmount']
        IGSTPerc = f['IGSTPerc']
        IGSTAmount = f['IGSTAmount']
        NetAmount = f['NetAmount']
        TAX1Perc = f['TAX1Perc']
        TAX1Amount = f['TAX1Amount']
        TAX2Perc = f['TAX2Perc']
        TAX2Amount = f['TAX2Amount']
        TAX3Perc = f['TAX3Perc']
        TAX3Amount = f['TAX3Amount']


        print("###########################")
        print(pk)
        StockPostingID = get_auto_stockPostid(StockPosting,BranchID,DataBase)

        if int(pk) > 0:
            detail_ids.append(pk)
            purchaseDetail_instance = PurchaseDetails.objects.using(DataBase).get(pk=pk)
            PurchaseDetailsID = purchaseDetail_instance.PurchaseDetailsID
            purchaseDetail_instance.ProductID = ProductID
            purchaseDetail_instance.Qty = Qty
            purchaseDetail_instance.FreeQty = FreeQty
            purchaseDetail_instance.UnitPrice = UnitPrice
            purchaseDetail_instance.RateWithTax = RateWithTax
            purchaseDetail_instance.CostPerItem = CostPerItem
            purchaseDetail_instance.PriceListID = PriceListID
            purchaseDetail_instance.DiscountPerc = DiscountPerc
            purchaseDetail_instance.DiscountAmount = DiscountAmount
            purchaseDetail_instance.AddlDiscPerc = AddlDiscPerc
            purchaseDetail_instance.AddlDiscAmt = AddlDiscAmt
            purchaseDetail_instance.GrossAmount = GrossAmount
            purchaseDetail_instance.TaxableAmount = TaxableAmount
            purchaseDetail_instance.VATPerc = VATPerc
            purchaseDetail_instance.VATAmount = VATAmount
            purchaseDetail_instance.SGSTPerc = SGSTPerc
            purchaseDetail_instance.SGSTAmount = SGSTAmount
            purchaseDetail_instance.CGSTPerc = CGSTPerc
            purchaseDetail_instance.CGSTAmount = CGSTAmount
            purchaseDetail_instance.IGSTPerc = IGSTPerc
            purchaseDetail_instance.IGSTAmount = IGSTAmount
            purchaseDetail_instance.NetAmount = NetAmount
            purchaseDetail_instance.Action = Action
            purchaseDetail_instance.UpdatedDate = today
            purchaseDetail_instance.CreatedUserID = CreatedUserID
            purchaseDetail_instance.TAX1Perc = TAX1Perc
            purchaseDetail_instance.TAX1Amount = TAX1Amount
            purchaseDetail_instance.TAX2Perc = TAX2Perc
            purchaseDetail_instance.TAX2Amount = TAX2Amount
            purchaseDetail_instance.TAX3Perc = TAX3Perc
            purchaseDetail_instance.TAX3Amount = TAX3Amount

            purchaseDetail_instance.save()

            PurchaseDetails_Log.objects.using(DataBase).create(
                TransactionID=PurchaseDetailsID,
                BranchID=BranchID,
                Action=Action,
                PurchaseMasterID=PurchaseMasterID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerItem=CostPerItem,
                PriceListID=PriceListID,
                DiscountPerc=DiscountPerc,
                DiscountAmount=DiscountAmount,
                AddlDiscPerc=AddlDiscPerc,
                AddlDiscAmt=AddlDiscAmt,
                GrossAmount=GrossAmount,
                TaxableAmount=TaxableAmount,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                )

            StockPosting.objects.using(DataBase).create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=wareHouse,
                QtyIn=Qty,
                Rate=CostPerItem,
                PriceListID=PriceListID,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID
                )

            StockPosting_Log.objects.using(DataBase).create(
                TransactionID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=wareHouse,
                QtyIn=Qty,
                Rate=CostPerItem,
                PriceListID=PriceListID,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID
                )

        else:
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            PurchaseDetailsID = get_auto_id(PurchaseDetails,BranchID,DataBase)
            Action = "A"
            instance = PurchaseDetails.objects.using(DataBase).create(
                PurchaseDetailsID=PurchaseDetailsID,
                BranchID=BranchID,
                purchase_master=purchaseMaster_instance,
                Action=Action,
                PurchaseMasterID=PurchaseMasterID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerItem=CostPerItem,
                PriceListID=PriceListID,
                DiscountPerc=DiscountPerc,
                DiscountAmount=DiscountAmount,
                AddlDiscPerc=AddlDiscPerc,
                AddlDiscAmt=AddlDiscAmt,
                GrossAmount=GrossAmount,
                TaxableAmount=TaxableAmount,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                )

            detail_ids.append(instance.id)

            PurchaseDetails_Log.objects.using(DataBase).create(
                TransactionID=PurchaseDetailsID,
                BranchID=BranchID,
                Action=Action,
                PurchaseMasterID=PurchaseMasterID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerItem=CostPerItem,
                PriceListID=PriceListID,
                DiscountPerc=DiscountPerc,
                DiscountAmount=DiscountAmount,
                AddlDiscPerc=AddlDiscPerc,
                AddlDiscAmt=AddlDiscAmt,
                GrossAmount=GrossAmount,
                TaxableAmount=TaxableAmount,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                )

            StockPosting.objects.using(DataBase).create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=wareHouse,
                QtyIn=Qty,
                Rate=CostPerItem,
                PriceListID=PriceListID,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID
                )

            StockPosting_Log.objects.using(DataBase).create(
                TransactionID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=wareHouse,
                QtyIn=Qty,
                Rate=CostPerItem,
                PriceListID=PriceListID,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID
                )
        

        priceList = PriceList.objects.using(DataBase).get(ProductID=ProductID,DefaultUnit=True)

        PriceListID = priceList.PriceListID
        MultiFactor = priceList.MultiFactor

        PurchasePrice = priceList.PurchasePrice
        SalesPrice = priceList.SalesPrice

        qty = float(FreeQty) + float(Qty)

        Qty = float(MultiFactor) * float(qty)
        Cost = float(CostPerItem) /  float(MultiFactor)

        Qy = round(Qty,4)
        Qty = str(Qy)


        Ct = round(Cost,4)
        Cost = str(Ct)

        if int(pk) == 0:
            if StockRate.objects.using(DataBase).filter(BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=wareHouse,PriceListID=PriceListID).exists():
                stockRateInstance = StockRate.objects.using(DataBase).get(BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=wareHouse,PriceListID=PriceListID)
                
                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
                stockRateInstance.save()

                StockTransID = get_auto_StockTransID(StockTrans,BranchID,DataBase)
                StockTrans.objects.using(DataBase).create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    DetailID=PurchaseDetailsID,
                    MasterID=PurchaseMasterID,
                    Qty=Qty,
                    IsActive=IsActive
                    )
            else:
                StockRateID = get_auto_StockRateID(StockRate,BranchID,DataBase)
                StockRate.objects.using(DataBase).create(
                    StockRateID=StockRateID,
                    BranchID=BranchID,
                    BatchID=BatchID,
                    PurchasePrice=PurchasePrice,
                    SalesPrice=SalesPrice,
                    Qty=Qty,
                    Cost=Cost,
                    ProductID=ProductID,
                    WareHouseID=wareHouse,
                    Date=date,
                    PriceListID=PriceListID,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )

                StockTransID = get_auto_StockTransID(StockTrans,BranchID,DataBase)
                StockTrans.objects.using(DataBase).create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    DetailID=PurchaseDetailsID,
                    MasterID=PurchaseMasterID,
                    Qty=Qty,
                    IsActive=IsActive
                    )

        else:

            stockTrans_instance = StockTrans.objects.using(DataBase).get(DetailID=PurchaseDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True)
            stockRateID = stockTrans_instance.StockRateID
            stockRate_instance = StockRate.objects.using(DataBase).get(StockRateID=stockRateID,BranchID=BranchID,WareHouseID=wareHouse)
            
            if float(stockTrans_instance.Qty) < float(Qty):
                deff = float(Qty) - float(stockTrans_instance.Qty)
                stockTrans_instance.Qty = float(stockTrans_instance.Qty) + float(deff)
                stockTrans_instance.save()

                stockRate_instance.Qty = float(stockRate_instance.Qty) + float(deff)
                stockRate_instance.save()

            elif float(stockTrans_instance.Qty) > float(Qty):
                deff = float(stockTrans_instance.Qty) - float(Qty)
                stockTrans_instance.Qty = float(stockTrans_instance.Qty) - float(deff)
                stockTrans_instance.save() 

                stockRate_instance.Qty = float(stockRate_instance.Qty) - float(deff)
                stockRate_instance.save()

    if detail_ids:
        print("++++++++++++++++++++++++++++++++++")
        print(detail_ids)
        if PurchaseDetails.objects.using(DataBase).exclude(pk__in=detail_ids,PurchaseMasterID=PurchaseMasterID).exists():
            deleted_details = PurchaseDetails.objects.using(DataBase).exclude(pk__in=detail_ids,PurchaseMasterID=PurchaseMasterID)
            print("-----------------------")
            print(deleted_details)
            # for deleted_detail in deleted_details:
            #     PurchaseDetailsID = deleted_detail.PurchaseDetailsID
            #     deleted_detail.delete()

            #     if StockTrans.objects.using(DataBase).filter(DetailID=PurchaseDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
                    
            #         stockTrans_instances = StockTrans.objects.using(DataBase).filter(DetailID=PurchaseDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True)
            #         for stockTrans_instance in stockTrans_instances:
            #             qty_in_stockTrans = stockTrans_instance.Qty
            #             StockRateID = stockTrans_instance.StockRateID
            #             stockTrans_instance.IsActive = False
            #             stockTrans_instance.save()

            #             stockRate_instance = get_object_or_404(StockRate.objects.using(DataBase).filter(StockRateID=StockRateID,BranchID=BranchID,WareHouseID=wareHouse))
            #             stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
            #             stockRate_instance.save()

    response_data = {
        "status" : "true",
    }
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    