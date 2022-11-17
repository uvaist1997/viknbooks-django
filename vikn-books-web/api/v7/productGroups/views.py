from brands.models import Kitchen,ProductGroup, ProductGroup_Log, ProductCategory, Product, StockAdjustmentMaster
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v7.productGroups.serializers import ProductGroupSerializer, ProductGroupRestSerializer
from api.v7.brands.serializers import ListSerializer
from api.v7.productGroups.functions import generate_serializer_errors
from rest_framework import status
from api.v7.productGroups.functions import get_auto_id
import datetime
from main.functions import get_company, activity_log
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
from rest_framework.permissions import AllowAny, IsAuthenticated


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_productGroup(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = ProductGroupSerializer(data=request.data)

    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        GroupName = serialized.data['GroupName']
        CategoryID = serialized.data['CategoryID']
        Notes = serialized.data['Notes']
        try:
            kitchen = data['kitchen']
        except:
            kitchen = None

        Action = 'A'

        if kitchen:
            if Kitchen.objects.filter(id=kitchen).exists():
                kitchen = Kitchen.objects.get(id=kitchen)
        else:
            kitchen = None

        print("kitchen58")
        print(kitchen)

        ProductGroupID = get_auto_id(ProductGroup, BranchID, CompanyID)

        is_nameExist = False

        GroupNameLow = GroupName.lower()

        productsGroups = ProductGroup.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)

        for productsGroup in productsGroups:

            group_name = productsGroup.GroupName

            groupName = group_name.lower()

            if GroupNameLow == groupName:
                is_nameExist = True

        if not is_nameExist:

            # serialized.save(UnitID=UnitID,CreatedDate=today,ModifiedDate=today)
            ProductGroup.objects.create(
                ProductGroupID=ProductGroupID,
                BranchID=BranchID,
                GroupName=GroupName,
                CategoryID=CategoryID,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                kitchen=kitchen
            )

            ProductGroup_Log.objects.create(
                BranchID=BranchID,
                TransactionID=ProductGroupID,
                GroupName=GroupName,
                CategoryID=CategoryID,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                kitchen=kitchen
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductGroup',
                         'Create', 'ProductGroup created successfully.', 'ProductGroup saved successfully.')

            data = {"ProductGroupID": ProductGroupID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Group Name Already Exist!!!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'ProductGroup', 'Create',
                     'ProductGroup field not valid.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_productGroup(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    try:
        kitchen = data['kitchen']
    except:
        kitchen = None

    Action = 'A'

    if kitchen:
        if Kitchen.objects.filter(id=kitchen).exists():
            kitchen = Kitchen.objects.get(id=kitchen)
    else:
        kitchen = None

    today = datetime.datetime.now()
    serialized = ProductGroupSerializer(data=request.data)
    instance = ProductGroup.objects.get(CompanyID=CompanyID, pk=pk)

    BranchID = instance.BranchID
    ProductGroupID = instance.ProductGroupID
    instanceGroupName = instance.GroupName

    if serialized.is_valid():

        GroupName = serialized.data['GroupName']
        CategoryID = serialized.data['CategoryID']
        Notes = serialized.data['Notes']

        Action = 'M'

        is_nameExist = False
        group_ok = False

        GroupNameLow = GroupName.lower()

        productsGroups = ProductGroup.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)

        for productsGroup in productsGroups:

            group_name = productsGroup.GroupName

            groupName = group_name.lower()

            if GroupNameLow == groupName:
                is_nameExist = True

            if instanceGroupName.lower() == GroupNameLow:

                group_ok = True

        if group_ok:

            instance.GroupName = GroupName
            instance.CategoryID = CategoryID
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.kitchen = kitchen
            instance.save()

            ProductGroup_Log.objects.create(
                BranchID=BranchID,
                TransactionID=ProductGroupID,
                GroupName=GroupName,
                CategoryID=CategoryID,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                kitchen=kitchen
            )
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductGroup',
                         'Edit', 'ProductGroup Updated successfully.', 'ProductGroup Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Group Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.GroupName = GroupName
                instance.CategoryID = CategoryID
                instance.Notes = Notes
                instance.Action = Action
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = today
                instance.kitchen = kitchen
                instance.save()

                ProductGroup_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=ProductGroupID,
                    GroupName=GroupName,
                    CategoryID=CategoryID,
                    Notes=Notes,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    kitchen=kitchen
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductGroup',
                             'Edit', 'ProductGroup Updated successfully.', 'ProductGroup Updated successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'ProductGroup', 'Edit',
                     'ProductGroup field not valid.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def productGroups(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    try:
        CategoryID = data['CategoryID']
    except:
        CategoryID = 0

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if ProductGroup.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if page_number and items_per_page:
                instances = ProductGroup.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                if CategoryID > 0:
                    instances = instances.filter(CategoryID=CategoryID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = ProductGroup.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                if CategoryID > 0:
                    ledger_sort_pagination = ledger_sort_pagination.filter(CategoryID=CategoryID)
                count = len(ledger_sort_pagination)

            serialized = ProductGroupRestSerializer(
                ledger_sort_pagination, many=True, context={"CompanyID": CompanyID})

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductGroup',
                         'List View', 'ProductGroup List Viewd successfully.', 'ProductGroup List Viewd successfully.')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'ProductGroup',
                         'List View', 'ProductGroup List Viewd Failed.', 'Product Group Not Found in this Branch.')
            response_data = {
                "StatusCode": 6001,
                "message": "Product Group Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def productGroup(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    if ProductGroup.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = ProductGroup.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = ProductGroupRestSerializer(
            instance, context={"CompanyID": CompanyID})
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductGroup', 'View',
                     'ProductGroup Single Page Viewd successfully.', 'ProductGroup Single Page Viewd successfully.')

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'ProductGroup',
                     'View', 'ProductGroup Single Page Viewd Failed.', 'Product Group Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Product Group Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_productGroup(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    product_exist = None
    StockAdjustmentMaster_exist = None
    if pk == "1":
        response_data = {
            "StatusCode": 6001,
            "message": "You Can't Delete this ProductGroup!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if ProductGroup.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instance = ProductGroup.objects.get(CompanyID=CompanyID, pk=pk)
            BranchID = instance.BranchID
            ProductGroupID = instance.ProductGroupID
            GroupName = instance.GroupName
            CategoryID = instance.CategoryID
            Notes = instance.Notes
            kitchen = instance.kitchen
            Action = "D"

            product_exist = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID).exists()
            StockAdjustmentMaster_exist = StockAdjustmentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID).exists()

            if not product_exist and not StockAdjustmentMaster_exist:
                instance.delete()

                ProductGroup_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=ProductGroupID,
                    GroupName=GroupName,
                    CategoryID=CategoryID,
                    Notes=Notes,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    kitchen=kitchen
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductGroup',
                             'Deleted', 'ProductGroup Deleted successfully.', 'ProductGroup Deleted successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "title": "Success",
                    "message": "Product Group Deleted Successfully!"
                }
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'ProductGroup', 'Deleted',
                             'ProductGroup Deleted Failed.', 'Cant Delete this Product Group,this ProductGroupID is using somewhere.')
                response_data = {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "You Cant Delete this Product Group,this ProductGroupID is using somewhere!!"
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "title": "Failed",
                "message": "Product Group Not Found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def search_productGroups(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    param = data['param']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if ProductGroup.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = ProductGroup.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            cat_ids = []
            if ProductCategory.objects.filter(CompanyID=CompanyID, CategoryName__icontains=product_name).exists():
                cat_ins = ProductCategory.objects.filter(
                    CompanyID=CompanyID, CategoryName__icontains=product_name)
                for c in cat_ins:
                    ProductCategoryID = c.ProductCategoryID
                    cat_ids.append(ProductCategoryID)
            if length < 3:
                if param == "GroupName":
                    instances = instances.filter(
                        (Q(GroupName__icontains=product_name)))[:10]
                else:
                    instances = instances.filter(
                        (Q(CategoryID__in=cat_ids)))[:10]

            else:
                if param == "GroupName":
                    instances = instances.filter(
                        (Q(GroupName__icontains=product_name)))
                else:
                    instances = instances.filter((Q(CategoryID__in=cat_ids)))

            serialized = ProductGroupRestSerializer(instances, many=True, context={
                "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "product_name": "product_name"})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
