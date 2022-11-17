from brands.models import BranchSettings, ProductCategory, ProductCategory_Log, ProductGroup
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.productCategories.serializers import ProductCategorySerializer, ProductCategoryRestSerializer
from api.v9.brands.serializers import ListSerializer
from api.v9.productCategories.functions import generate_serializer_errors
from rest_framework import status
from api.v9.productCategories.functions import get_auto_id
import datetime
from main.functions import get_company, activity_log
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_productCategory(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = ProductCategorySerializer(data=request.data)

    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        CategoryName = serialized.data['CategoryName']
        Notes = serialized.data['Notes']

        Action = 'A'

        ProductCategoryID = get_auto_id(ProductCategory, BranchID, CompanyID)

        is_nameExist = False

        CategoryNameLow = CategoryName.lower()

        check_productsForAllBranches = False
        if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="productsForAllBranches").exists():
            check_productsForAllBranches = BranchSettings.objects.get(
                CompanyID=CompanyID, SettingsType="productsForAllBranches").SettingsValue

        if check_productsForAllBranches == True or check_productsForAllBranches == "True":
            categories = ProductCategory.objects.filter(
                CompanyID=CompanyID)
        else:
            categories = ProductCategory.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

        for category in categories:

            category_name = category.CategoryName

            categoryName = category_name.lower()

            if CategoryNameLow == categoryName:

                is_nameExist = True

        if not is_nameExist:

            # serialized.save(UnitID=UnitID,CreatedDate=today,ModifiedDate=today)
            ProductCategory.objects.create(
                ProductCategoryID=ProductCategoryID,
                BranchID=BranchID,
                CategoryName=CategoryName,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            ProductCategory_Log.objects.create(
                BranchID=BranchID,
                TransactionID=ProductCategoryID,
                CategoryName=CategoryName,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductCategory',
                         'Create', 'ProductCategory created successfully.', 'ProductCategory saved successfully.')

            data = {"ProductCategoryID": ProductCategoryID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "ProductCategory Name Already Exist!!!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'ProductCategory', 'Create',
                     'ProductCategory created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_productCategory(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = ProductCategorySerializer(data=request.data)

    instance = ProductCategory.objects.get(CompanyID=CompanyID, pk=pk)

    BranchID = instance.BranchID
    ProductCategoryID = instance.ProductCategoryID
    instanceCategoryName = instance.CategoryName

    if serialized.is_valid():

        CategoryName = serialized.data['CategoryName']
        Notes = serialized.data['Notes']

        Action = 'M'

        is_nameExist = False
        category_ok = False

        CategoryNameLow = CategoryName.lower()

        check_productsForAllBranches = False
        if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="productsForAllBranches").exists():
            check_productsForAllBranches = BranchSettings.objects.get(
                CompanyID=CompanyID, SettingsType="productsForAllBranches").SettingsValue

        if check_productsForAllBranches == True or check_productsForAllBranches == "True":
            categories = ProductCategory.objects.filter(
                CompanyID=CompanyID)
        else:
            categories = ProductCategory.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

        for category in categories:

            category_name = category.CategoryName

            categoryName = category_name.lower()

            if CategoryNameLow == categoryName:

                is_nameExist = True

            if instanceCategoryName.lower() == CategoryNameLow:

                category_ok = True

        if category_ok:

            instance.CategoryName = CategoryName
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            ProductCategory_Log.objects.create(
                BranchID=BranchID,
                TransactionID=ProductCategoryID,
                CategoryName=CategoryName,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Category Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.CategoryName = CategoryName
                instance.Notes = Notes
                instance.Action = Action
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = today
                instance.save()

                ProductCategory_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=ProductCategoryID,
                    CategoryName=CategoryName,
                    Notes=Notes,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductCategory',
                             'Edit', 'ProductCategory Updated successfully.', 'ProductCategory Updated successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'ProductCategory', 'Edit',
                     'ProductCategory field not valid.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def productCategories(request):
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

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        check_productsForAllBranches = False
        if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="productsForAllBranches").exists():
            check_productsForAllBranches = BranchSettings.objects.get(
                CompanyID=CompanyID, SettingsType="productsForAllBranches").SettingsValue

        if check_productsForAllBranches == True or check_productsForAllBranches == "True":
            product_category_instance = ProductCategory.objects.filter(
                CompanyID=CompanyID)
        else:
            product_category_instance = ProductCategory.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
        if product_category_instance.exists():
            if page_number and items_per_page:
                instances = product_category_instance
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = product_category_instance
                count = len(ledger_sort_pagination)

            serialized = ProductCategoryRestSerializer(
                ledger_sort_pagination, many=True)

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductCategory', 'List View',
                         'ProductCategory List Viewed successfully.', 'ProductCategory List Viewed successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'ProductCategory', 'List View',
                         'ProductCategory List Viewed Failed.', 'ProductCategory Not Found in this Branch.')

            response_data = {
                "StatusCode": 6001,
                "message": "Product Category Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def productCategory(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    if ProductCategory.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = ProductCategory.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = ProductCategoryRestSerializer(instance)

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductCategory', 'View',
                     'ProductCategory Single Page Viewed successfully.', 'ProductCategory Single Page  Viewed successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'ProductCategory',
                     'View', 'ProductCategory Single Page Viewed Failed.', 'Product Category Not Fount.')
        response_data = {
            "StatusCode": 6001,
            "message": "Product Category Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_productCategory(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []
    instances = None
    if pk == "1":
        response_data = {
            "StatusCode": 6001,
            "message": "You Can't Delete this ProductCategory!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if selecte_ids:
            if ProductCategory.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
                instances = ProductCategory.objects.filter(pk__in=selecte_ids)
        else:
            if ProductCategory.objects.filter(CompanyID=CompanyID, pk=pk).exists():
                instances = ProductCategory.objects.filter(pk=pk)

        if instances:
            for instance in instances:
                BranchID = instance.BranchID
                ProductCategoryID = instance.ProductCategoryID
                CategoryName = instance.CategoryName
                Notes = instance.Notes
                Action = "D"
                if not ProductGroup.objects.filter(CompanyID=CompanyID, CategoryID=ProductCategoryID, BranchID=BranchID).exists():

                    instance.delete()

                    ProductCategory_Log.objects.create(
                        BranchID=BranchID,
                        TransactionID=ProductCategoryID,
                        CategoryName=CategoryName,
                        Notes=Notes,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductCategory',
                                 'Delete', 'ProductCategory Deleted successfully.', 'ProductCategory Deleted successfully.')
                    response_data = {
                        "StatusCode": 6000,
                        "title": "Success",
                        "message": "Product Category Deleted Successfully!"
                    }
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'ProductCategory',
                                 'Delete', 'ProductCategory Deleted Failed.', 'Product Group exist with this Category')
                    response_data = {
                        "StatusCode": 6001,
                        "title": "Failed",
                        "message": "Product Group exist with this Category ID!!"
                    }
        else:
            response_data = {
                "StatusCode": 6001,
                "title": "Failed",
                "message": "Product Category Not Fount!"
            }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_productCategories(request):
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
        check_productsForAllBranches = False

        if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="productsForAllBranches").exists():
            check_productsForAllBranches = BranchSettings.objects.get(
                CompanyID=CompanyID, SettingsType="productsForAllBranches").SettingsValue

        if check_productsForAllBranches == True or check_productsForAllBranches == "True":
            product_category_list = ProductCategory.objects.filter(
                CompanyID=CompanyID)
        else:
            product_category_list = ProductCategory.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

        if product_category_list.exists():
            instances = product_category_list

            if length < 3:
                if param == "CategoryName":
                    instances = instances.filter(
                        (Q(CategoryName__icontains=product_name)))[:10]
            else:
                if param == "CategoryName":
                    instances = instances.filter(
                        (Q(CategoryName__icontains=product_name)))

            serialized = ProductCategoryRestSerializer(instances, many=True, context={
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_productCategory_list(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if ProductCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if length < 3:
                instances = ProductCategory.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                instances = instances.filter((Q(CategoryName__icontains=product_name)))[:10]
            else:
                instances = ProductCategory.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                instances = instances.filter((Q(CategoryName__icontains=product_name)))
            serialized = ProductCategoryRestSerializer(instances, many=True, context={
                "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "product_name": "product_name"})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
