from brands.models import ProductCategory, ProductCategory_Log, ProductGroup
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.productCategories.serializers import ProductCategorySerializer, ProductCategoryRestSerializer
from api.v3.brands.serializers import ListSerializer
from api.v3.productCategories.functions import generate_serializer_errors
from rest_framework import status
from api.v3.productCategories.functions import get_auto_id
import datetime
from main.functions import get_company, activity_log


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
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if ProductCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            instances = ProductCategory.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            serialized = ProductCategoryRestSerializer(instances, many=True)

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ProductCategory', 'List View',
                         'ProductCategory List Viewed successfully.', 'ProductCategory List Viewed successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
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
    instance = None
    if pk == "1":
        response_data = {
            "StatusCode": 6001,
            "message": "You Can't Delete this ProductCategory!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if ProductCategory.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instance = ProductCategory.objects.get(CompanyID=CompanyID, pk=pk)
        if instance:
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
