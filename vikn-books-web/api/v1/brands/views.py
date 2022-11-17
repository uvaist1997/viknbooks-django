from brands.models import Brand, Brand_Log, Product, Activity_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.brands.serializers import BrandSerializer, BrandRestSerializer, ListSerializer
from api.v1.brands.functions import generate_serializer_errors
from rest_framework import status
from api.v1.brands.functions import get_auto_id
from main.functions import get_company, activity_log
import datetime
from django.db import transaction,IntegrityError
import os,re,sys
from api.v1.brands.tasks import runAPIforChangeDatasInDB
from celery.result import AsyncResult


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_brand(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BrandSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        BrandName = serialized.data['BrandName']
        # Notes = serialized.data['Notes']

        Action = 'A'
        BrandID = get_auto_id(Brand, BranchID, CompanyID)
        if not Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID, BrandName__iexact=BrandName).exists():

            Brand.objects.create(
                BrandID=BrandID,
                BranchID=BranchID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            Brand_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BrandID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand',
                         'Create', 'Brand created successfully.', 'Brand saved successfully.')

            data = {"BrandID": BrandID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                         'Brand', 'Create', 'Brand name already exist.', 'same name exists.')

            response_data = {
                "StatusCode": 6001,
                "message": "Brand name already exist."
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Brand', 'Create',
                     'Brand field not valid.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_brand(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BrandSerializer(data=request.data)
    instance = Brand.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID
    BrandID = instance.BrandID
    instanceBrandname = instance.BrandName

    if serialized.is_valid():
        BrandName = serialized.data['BrandName']
        Notes = serialized.data['Notes']
        Action = 'M'
        if not Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID, BrandName__iexact=BrandName).exclude(BrandName=instanceBrandname):
            instance.BrandName = BrandName
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            Brand_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BrandID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                         'Brand', 'Edit', 'Brand edited successfully.', 'Brand saved successfully.')

            data = {"BrandID": BrandID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        elif Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID, BrandName__iexact=BrandName).exists():
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand',
                         'Edit', 'Brand already exists.', 'Brand name already exist in this branch.')

            response_data = {
                "StatusCode": 6001,
                "message": "Brand name already exist in this branch"
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            instance.BrandName = BrandName
            instance.Notes = Notes
            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            Brand_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BrandID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                         'Brand', 'Edit', 'Brand edited successfully.', 'Brand saved successfully.')

            data = {"BrandID": BrandID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Brand', 'Edit',
                     'Brand edited failed.', generate_serializer_errors(serialized._errors))

        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def brands(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    from main.functions import get_location, get_device_name
    from django.contrib.gis.geoip2 import GeoIP2

    location = get_location(request)
    # device_name = get_device_name(request)
    print("###############")
    print(location)
    # print(device_name)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = Brand.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = BrandRestSerializer(instances, many=True)

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand', 'View', 'Brand list', 'The user viewed brands')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information',
                         CreatedUserID, 'Brand', 'View', 'Brand list', 'brand not found')
            response_data = {
                "StatusCode": 6001,
                "message": "Brands Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information',
                     CreatedUserID, 'Brand', 'View', 'Brand list', 'brand not valid')
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def brand(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Brand.objects.filter(pk=pk).exists():
        instance = Brand.objects.get(pk=pk)
        serialized = BrandRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                     'Brand', 'View', 'Brand Single Page', 'User viewed a Brand')
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Brand Not Fount!"
        }

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Brand', 'View', 'Brand Single Page', 'Brand not Found!')

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_brand(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if pk == "1":
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Brand',
                     'Delete', 'Brand Deleted failed', 'Tried to Delete Default Brand!')
        response_data = {
            "StatusCode": 6001,
            "message": "You Can't Delete this Brand!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if Brand.objects.filter(pk=pk).exists():
            instance = Brand.objects.get(pk=pk)
        if instance:
            BranchID = instance.BranchID
            BrandID = instance.BrandID
            BrandName = instance.BrandName
            Notes = instance.Notes
            Action = "D"

            if not Product.objects.filter(BranchID=BranchID, BrandID=BrandID, CompanyID=CompanyID).exists():

                instance.delete()

                Brand_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=BrandID,
                    BrandName=BrandName,
                    Notes=Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    CompanyID=CompanyID
                )
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand',
                             'Delete', 'Brand Deleted Successfully', 'Brand Deleted Successfully')

                response_data = {
                    "StatusCode": 6000,
                    "message": "Brand Deleted Successfully!"
                }
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Brand', 'Delete',
                             'Brand Deleted Failed', 'Brand Deleted Failed,Product has Created with this Brand')
                response_data = {
                    "StatusCode": 6001,
                    "message": "You can't Delete this Brand,Product exist with this Brand!!"
                }
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                         'Brand', 'Delete', 'Brand Deleted Failed', 'Brand Not Found!')
            response_data = {
                "StatusCode": 6001,
                "message": "Brand Not Found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def runAPIforChangeDatasInDBView(request):
    try:
        with transaction.atomic():
            task = runAPIforChangeDatasInDB.delay()
            task_id = task.id
            # request , company, log_type, user, source, action, message, description
            
            response_data = {
                "StatusCode": 6000,
                "task_id": task_id,
                "message": "Qury Run Successfully!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("======================exception test")
        print(exc_type, fname, exc_tb.tb_lineno)
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }
        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_progress(request, task_id):
    result = AsyncResult(task_id)
    response_data = {
        'state': result.state,
        'details': result.info,
        'task_id': task_id,
    }
    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def torunqryforBugFix(request):

    from brands import models as table
    from api.v1.sales.functions import get_auto_stockPostid
    from api.v1.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v1.accountLedgers.functions import get_auto_LedgerPostid
    from django.db.models import Q, Sum, F

    CompanyID = "8900c397-2a72-45ee-98f0-d76b7e977e7e"
    CompanyID = table.CompanySettings.objects.get(id=CompanyID)

    productids = table.Product.objects.filter(CompanyID=CompanyID).values_list('ProductID',flat=True)
    error_ids = []
    for i in productids:
        if not table.PriceList.objects.filter(CompanyID=CompanyID,ProductID=i).exists():
            error_ids.append(i)
            
    
    # for i in companies:
    #     CompanyID = i
    #     BranchID = 1
    #     if i.Edition == "Soft Edition":
    #         i.Edition =     "Lite"
    #     elif i.Edition == "Light Edition":
    #         i.Edition =     "Essential"
    #     elif i.Edition == "Basic Edition":
    #         i.Edition =     "Standard"
    #     elif i.Edition == "Standard Edition":
    #         i.Edition =     "Professional"
    #     elif i.Edition == "Enterprise Edition":
    #         i.Edition =     "Advanced"
    #     i.save()


        # companies = table.CompanySettings.objects.filter(id=)
        # for c in companies:
        #     CompanyID = c
        #     BranchID = 1

        #     if table.Parties.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        #         sales_instances = table.SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            

    print("--------------------------------------success")
    response_data = {
        "StatusCode": 6000,
        "message": "success",
        "error_ids": error_ids
    }

    return Response(response_data, status=status.HTTP_200_OK)