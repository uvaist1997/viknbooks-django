from brands.models import Warehouse, Warehouse_Log, SalesMaster, PurchaseMaster,StockPosting, UserTable
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.warehouses.serializers import WarehouseSerializer, WarehouseRestSerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.warehouses.functions import generate_serializer_errors
from rest_framework import status
from api.v1.warehouses.functions import get_auto_id
import datetime
from main.functions import get_company, activity_log



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_warehouse(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = WarehouseSerializer(data=request.data)

    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        WarehouseName = serialized.data['WarehouseName']
        Notes = serialized.data['Notes']

        Action = "A"

        WarehouseID = get_auto_id(Warehouse,BranchID,CompanyID)
        if not Warehouse.objects.filter(CompanyID=CompanyID,BranchID=BranchID,WarehouseName__iexact=WarehouseName):

            # serialized.save(UnitID=UnitID,CreatedDate=today,ModifiedDate=today)
            Warehouse.objects.create(
                WarehouseID=WarehouseID,
                BranchID=BranchID,
                WarehouseName=WarehouseName,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID
                )

            Warehouse_Log.objects.create(
                BranchID=BranchID,
                TransactionID=WarehouseID,
                WarehouseName=WarehouseName,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID
                )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Warehouse', 'Create', 'Warehouse created successfully.', 'Warehouse saved successfully.')

            data = {"WarehouseID" : WarehouseID}
            data.update(serialized.data)
            response_data = {
                "StatusCode" : 6000,
                "data" : data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse', 'Create', 'Warehouse created Failed.', 'WareHouse Name Already Exist')
            response_data = {
            "StatusCode" : 6001,
            "message" : "Warehouse name already exists."
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Warehouse', 'Create', 'Warehouse created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_warehouse(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = WarehouseSerializer(data=request.data)
    instance = Warehouse.objects.get(CompanyID=CompanyID,pk=pk)
    
    BranchID = instance.BranchID
    WarehouseID = instance.WarehouseID
    instanceWarehouseName = instance.WarehouseName
    
    if serialized.is_valid():

        WarehouseName = serialized.data['WarehouseName']
        Notes = serialized.data['Notes']

        Action = "M"

        if not Warehouse.objects.filter(CompanyID=CompanyID,BranchID=BranchID,WarehouseName__iexact=WarehouseName).exclude(WarehouseName=instanceWarehouseName):
            instance.WarehouseName = WarehouseName
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            Warehouse_Log.objects.create(
                BranchID=BranchID,
                TransactionID=WarehouseID,
                WarehouseName=WarehouseName,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID
                )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Warehouse', 'Edit', 'Warehouse Updated Successfully.', 'Warehouse Updated Successfully.')

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse', 'Edit', 'Warehouse Updated Failed.', 'Warehouse Name Already exist with this Branch')
            if Warehouse.objects.filter(CompanyID=CompanyID,BranchID=BranchID,WarehouseName__iexact=WarehouseName):
                response_data = {
                    "StatusCode" : 6001,
                    "message" : "Warehouse Name Already exist with this Branch"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.WarehouseName = WarehouseName
                instance.Notes = Notes
                instance.Action = Action
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = today
                instance.save()

                Warehouse_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=WarehouseID,
                    WarehouseName=WarehouseName,
                    Notes=Notes,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID
                    )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Warehouse', 'Edit', 'Warehouse Updated Successfully.', 'Warehouse Updated Successfully')

                response_data = {
                    "StatusCode" : 6000,
                    "data" : serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)



    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Warehouse', 'Edit', 'Warehouse Updated Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def warehouses(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)
    DefaultAccountForUser = None
    Cash_Account = None
    Bank_Account = None
    Sales_Account = None
    if UserTable.objects.filter(CompanyID=CompanyID,customer__user__pk=CreatedUserID).exists():
        DefaultAccountForUser = UserTable.objects.get(CompanyID=CompanyID,customer__user__pk=CreatedUserID).DefaultAccountForUser
        Cash_Account = UserTable.objects.get(CompanyID=CompanyID,customer__user__pk=CreatedUserID).Cash_Account
        Bank_Account = UserTable.objects.get(CompanyID=CompanyID,customer__user__pk=CreatedUserID).Bank_Account
        Sales_Account = UserTable.objects.get(CompanyID=CompanyID,customer__user__pk=CreatedUserID).Sales_Account
        
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Warehouse.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            instances = Warehouse.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            serialized = WarehouseRestSerializer(instances,many=True)
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Warehouse', 'List', 'Warehouse List Viewed Successfully', "Warehouse List Viewed Successfully")
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data,
                "DefaultAccountForUser" : DefaultAccountForUser,
                "Cash_Account" : Cash_Account,
                "Bank_Account" : Bank_Account,
                "Sales_Account" : Sales_Account,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse', 'List', 'Warehouse List Viewed Failed', "Warehouse Not Found in this Branch")
            response_data = {
            "StatusCode" : 6001,
            "message" : "Warehouse Not Found in this Branch!"
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
def warehouse(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    instance = None

    if Warehouse.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = Warehouse.objects.get(CompanyID=CompanyID,pk=pk)
        serialized = WarehouseRestSerializer(instance)

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse', 'View', 'Warehouse Single Viewed Successfully', "Warehouse Single Viewed Successfully")
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse', 'View', 'Warehouse Single Viewed Failed', "Warehouse Not Found in this Branch")
        response_data = {
            "StatusCode" : 6001,
            "message" : "Ware House Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_warehouse(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    purchaseMaster_exist = None
    salesMaster_exist = None
    stockPostings_exist = None
    if pk == "1":
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse', 'Delete', 'Warehouse Deleted Failed', "User Tried to Delete Default Warehouse!")
        response_data = {
                "StatusCode" : 6001,
                "message" : "You Can't Delete this WareHouse!!!"
            }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if Warehouse.objects.filter(CompanyID=CompanyID,pk=pk).exists():
            instance = Warehouse.objects.get(CompanyID=CompanyID,pk=pk)
        if instance:
            BranchID = instance.BranchID
            WarehouseID = instance.WarehouseID
            WarehouseName = instance.WarehouseName
            Notes = instance.Notes
            Action = "D"

            purchaseMaster_exist = PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,WarehouseID=WarehouseID).exists()
            salesMaster_exist = SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,WarehouseID=WarehouseID).exists()
            stockPostings_exist = StockPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID,WareHouseID=WarehouseID).exists()

            if not purchaseMaster_exist and not salesMaster_exist and not stockPostings_exist:
                instance.delete()

                Warehouse_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=WarehouseID,
                    WarehouseName=WarehouseName,
                    Notes=Notes,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID
                    )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Warehouse', 'Delete', 'Warehouse Deleted Successfully', "Warehouse Deleted Successfully")
                response_data = {
                    "StatusCode" : 6000,
                    "title" : "Success",
                    "message" : "WareHouse Deleted Successfully!"
                }
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse', 'Delete', 'Warehouse Deleted Failed', "Cant Delete this Warehouse,this WarehouseID is using somewhere")
                response_data = {
                    "StatusCode" : 6001,
                    "title" : "Failed",
                    "message" : "You Cant Delete this Warehouse,this WarehouseID is using somewhere!!"
                }
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse', 'Delete', 'Warehouse Deleted Failed', "WareHouse Not Found under this Branch")
            response_data = {
                "StatusCode" : 6001,
                "title" : "Failed",
                "message" : "WareHouse Not Found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)