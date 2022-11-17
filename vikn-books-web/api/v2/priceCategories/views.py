from brands.models import PriceCategory, PriceCategory_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.priceCategories.serializers import PriceCategorySerializer, PriceCategoryRestSerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.priceCategories.functions import generate_serializer_errors
from rest_framework import status
from api.v2.priceCategories.functions import get_auto_id
import datetime
from main.functions import get_company, activity_log


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_priceCategory(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = PriceCategorySerializer(data=request.data)

    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        PriceCategoryName = serialized.data['PriceCategoryName']
        ColumnName = serialized.data['ColumnName']
        IsActive = serialized.data['IsActive']
        Notes = serialized.data['Notes']

        Action = 'A'
        PriceCategoryID = get_auto_id(PriceCategory,BranchID,CompanyID)

        is_nameExist = False

        PriceCategoryNameLow = PriceCategoryName.lower()

        categories = PriceCategory.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

        for category in categories:

            category_name = category.PriceCategoryName

            categoryName = category_name.lower()

            if PriceCategoryNameLow == categoryName:
                is_nameExist = True

        if not is_nameExist:

            # serialized.save(UnitID=UnitID,CreatedDate=today,ModifiedDate=today)
            PriceCategory.objects.create(
                PriceCategoryID=PriceCategoryID,
                BranchID=BranchID,
                PriceCategoryName=PriceCategoryName,
                ColumnName=ColumnName,
                IsActive=IsActive,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

            PriceCategory_Log.objects.create(
                BranchID=BranchID,
                TransactionID=PriceCategoryID,
                PriceCategoryName=PriceCategoryName,
                ColumnName=ColumnName,
                IsActive=IsActive,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PriceCategory', 'Create', 'PriceCategory created successfully.', 'PriceCategory saved successfully.')

            data = {"PriceCategoryID" : PriceCategoryID}
            data.update(serialized.data)
            response_data = {
                "StatusCode" : 6000,
                "data" : data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PriceCategory', 'Create', 'PriceCategory created Failed.', 'Price Category Name Already Exist!')

            response_data = {
            "StatusCode" : 6001,
            "message" : "Price Category Name Already Exist!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'PriceCategory', 'Create', 'PriceCategory created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_priceCategory(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = PriceCategorySerializer(data=request.data)
    instance = PriceCategory.objects.get(CompanyID=CompanyID,pk=pk)
    
    BranchID = instance.BranchID
    PriceCategoryID = instance.PriceCategoryID
    instancePriceCategoryName = instance.PriceCategoryName
    
    if serialized.is_valid():

        PriceCategoryName = serialized.data['PriceCategoryName']
        ColumnName = serialized.data['ColumnName']
        IsActive = serialized.data['IsActive']
        Notes = serialized.data['Notes']

        Action = 'M'

        is_nameExist = False
        category_ok = False

        PriceCategoryNameLow = PriceCategoryName.lower()

        categories = PriceCategory.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

        for category in categories:

            category_name = category.PriceCategoryName

            categoryName = category_name.lower()

            if PriceCategoryNameLow == categoryName:
                is_nameExist = True

            if instancePriceCategoryName.lower() == PriceCategoryNameLow:

                category_ok = True

        if  category_ok:

            instance.PriceCategoryName = PriceCategoryName
            instance.ColumnName = ColumnName
            instance.IsActive = IsActive
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            PriceCategory_Log.objects.create(
                BranchID=BranchID,
                TransactionID=PriceCategoryID,
                PriceCategoryName=PriceCategoryName,
                ColumnName=ColumnName,
                IsActive=IsActive,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:


            if is_nameExist:

                response_data = {
                    "StatusCode" : 6001,
                    "message" : "Price Category Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.PriceCategoryName = PriceCategoryName
                instance.ColumnName = ColumnName
                instance.Notes = Notes
                instance.Action = Action
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = UpdatedDate
                instance.save()

                PriceCategory_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=PriceCategoryID,
                    PriceCategoryName=PriceCategoryName,
                    ColumnName=ColumnName,
                    IsActive=IsActive,
                    Notes=Notes,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )
                
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PriceCategory', 'Edit', 'PriceCategory Update successfully.', 'PriceCategory UpdatedDate successfully.')
                response_data = {
                    "StatusCode" : 6000,
                    "data" : serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'PriceCategory', 'Edit', 'PriceCategory field not valid.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def priceCategories(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']    
        if PriceCategory.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            instances = PriceCategory.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            serialized = PriceCategoryRestSerializer(instances,many=True)

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PriceCategory', 'List View', 'PriceCategory List Viewd Successfully', 'PriceCategory List Viewd Successfully')

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PriceCategory', 'List View', 'PriceCategory List Viewd Failed', 'Price Category Not Found under this Branch')

            response_data = {
            "StatusCode" : 6001,
            "message" : "Price Category Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def priceCategory(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    if PriceCategory.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = PriceCategory.objects.get(CompanyID=CompanyID,pk=pk)
        serialized = PriceCategoryRestSerializer(instance)

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PriceCategory', 'View', 'PriceCategory Single Page Viewd Successfully', 'PriceCategory Single Page Viewd Successfully')
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PriceCategory', 'View', 'PriceCategory Single Page Viewd Failed', 'Price Category Not Found')
        response_data = {
            "StatusCode" : 6001,
            "message" : "Price Category Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_priceCategory(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if PriceCategory.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = PriceCategory.objects.get(CompanyID=CompanyID,pk=pk)
    if instance:
        BranchID = instance.BranchID
        PriceCategoryID = instance.PriceCategoryID
        PriceCategoryName = instance.PriceCategoryName
        ColumnName = instance.ColumnName
        IsActive = instance.IsActive
        Notes = instance.Notes
        Action = "D"

        instance.delete()

        PriceCategory_Log.objects.create(
            BranchID=BranchID,
            TransactionID=PriceCategoryID,
            PriceCategoryName=PriceCategoryName,
            ColumnName=ColumnName,
            IsActive=IsActive,
            Notes=Notes,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PriceCategory', 'Delete', 'PriceCategory Deleted Successfully', 'Price Category Deleted Successfully')

        response_data = {
            "StatusCode" : 6000,
            "title" : "Success",
            "message" : "Price Category Deleted Successfully!"
        }
    else:
         #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PriceCategory', 'Delete', 'PriceCategory Deleted Failed', 'Price Category Not Found')
        response_data = {
            "StatusCode" : 6001,
            "title" : "Failed",
            "message" : "Price Category Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)