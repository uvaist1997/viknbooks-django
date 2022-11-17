from brands.models import TransactionTypes, TransactionTypes_Log, MasterType
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v7.transactionTypes.serializers import TransactionTypesSerializer, TransactionTypesRestSerializer, ListSerializerByMasterName
from api.v7.brands.serializers import ListSerializer
from api.v7.transactionTypes.functions import generate_serializer_errors
from rest_framework import status
from api.v7.transactionTypes.functions import get_auto_id
import datetime
from main.functions import get_company, activity_log
from rest_framework.permissions import AllowAny, IsAuthenticated


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_transactionType(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = TransactionTypesSerializer(data=request.data)

    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        MasterTypeID = serialized.data['MasterTypeID']
        Name = serialized.data['Name']
        Notes = serialized.data['Notes']
        IsDefault = serialized.data['IsDefault']

        Action = 'A'

        TransactionTypesID = get_auto_id(TransactionTypes, BranchID, CompanyID)

        is_nameExist = False

        NameLow = Name.lower()

        transactiontypes = TransactionTypes.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for transactiontype in transactiontypes:
            transaction_name = transactiontype.Name

            transactionName = transaction_name.lower()

            if NameLow == transactionName:
                is_nameExist = True

        if not is_nameExist:

            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            TransactionTypes.objects.create(
                TransactionTypesID=TransactionTypesID,
                BranchID=BranchID,
                MasterTypeID=MasterTypeID,
                Name=Name,
                Notes=Notes,
                IsDefault=IsDefault,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID
            )

            TransactionTypes_Log.objects.create(
                TransactionID=TransactionTypesID,
                BranchID=BranchID,
                MasterTypeID=MasterTypeID,
                Name=Name,
                Notes=Notes,
                IsDefault=IsDefault,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TransactionTypes',
                         'Create', 'TransactionTypes created successfully.', 'TransactionTypes saved successfully.')

            data = {"TransactionTypesID": TransactionTypesID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TransactionTypes',
                         'Create', 'TransactionTypes created Failed.', 'Transaction Types Name Already Exist.')
            response_data = {
                "StatusCode": 6001,
                "message": "Transaction Types Name Already Exist!!!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'TransactionTypes', 'Create',
                     'TransactionTypes created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_transactionType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = TransactionTypesSerializer(data=request.data)
    instance = TransactionTypes.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID
    TransactionTypesID = instance.TransactionTypesID
    instanceName = instance.Name

    if serialized.is_valid():

        MasterTypeID = serialized.data['MasterTypeID']
        Name = serialized.data['Name']
        Notes = serialized.data['Notes']
        IsDefault = serialized.data['IsDefault']

        Action = 'M'

        is_nameExist = False
        transaction_ok = False

        NameLow = Name.lower()

        transactiontypes = TransactionTypes.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for transactiontype in transactiontypes:
            transaction_name = transactiontype.Name

            transactionName = transaction_name.lower()

            if NameLow == transactionName:
                is_nameExist = True

            if instanceName.lower() == NameLow:

                transaction_ok = True

        if transaction_ok:

            instance.MasterTypeID = MasterTypeID
            instance.Name = Name
            instance.Notes = Notes
            instance.IsDefault = IsDefault
            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            TransactionTypes_Log.objects.create(
                TransactionID=TransactionTypesID,
                BranchID=BranchID,
                MasterTypeID=MasterTypeID,
                Name=Name,
                Notes=Notes,
                IsDefault=IsDefault,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TransactionTypes',
                         'Edit', 'TransactionTypes Updated Successfully.', "TransactionTypes Updated Successfully.")

            data = {"TransactionTypesID": TransactionTypesID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TransactionTypes', 'Edit',
                             'TransactionTypes Updated Failed.', "Transaction Types Name Already exist with this Branch")
                response_data = {
                    "StatusCode": 6001,
                    "message": "Transaction Types Name Already exist with this Branch"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.MasterTypeID = MasterTypeID
                instance.Name = Name
                instance.Notes = Notes
                instance.IsDefault = IsDefault
                instance.Action = Action
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.save()

                TransactionTypes_Log.objects.create(
                    TransactionID=TransactionTypesID,
                    BranchID=BranchID,
                    MasterTypeID=MasterTypeID,
                    Name=Name,
                    Notes=Notes,
                    IsDefault=IsDefault,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TransactionTypes',
                             'Edit', 'TransactionTypes Updated Successfully.', "TransactionTypes Updated Successfully.")

                data = {"TransactionTypesID": TransactionTypesID}
                data.update(serialized.data)
                response_data = {
                    "StatusCode": 6000,
                    "data": data
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'TransactionTypes', 'Edit',
                     'TransactionTypes Updated Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def transactionTypes(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if TransactionTypes.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

            instances = TransactionTypes.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)

            serialized = TransactionTypesRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID})
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TransactionTypes', 'List',
                         'TransactionTypes List Viewed Successfully.', "TransactionTypes List Viewed Successfully")
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TransactionTypes', 'List',
                         'TransactionTypes List Viewed Failed.', "Transaction Types Not Found in this Branch")
            response_data = {
                "StatusCode": 6001,
                "message": "Transaction Types Not Found in this Branch!"
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def transactionType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    if TransactionTypes.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = TransactionTypes.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = TransactionTypesRestSerializer(
            instance, context={"CompanyID": CompanyID})

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TransactionTypes', 'View',
                     'TransactionTypes Single Viewed Successfully.', "TransactionTypes Single Viewed Successfully.")
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Transaction Type Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_transactionType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    if TransactionTypes.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = TransactionTypes.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        TransactionTypesID = instance.TransactionTypesID
        MasterTypeID = instance.MasterTypeID
        Name = instance.Name
        Notes = instance.Notes
        IsDefault = instance.IsDefault
        Action = "D"

        instance.delete()

        TransactionTypes_Log.objects.create(
            TransactionID=TransactionTypesID,
            BranchID=BranchID,
            MasterTypeID=MasterTypeID,
            Name=Name,
            Notes=Notes,
            IsDefault=IsDefault,
            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID
        )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TransactionTypes',
                     'Delete', 'Transaction Types Deleted Successfully', "Transaction Types Deleted Successfully")

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Transaction Types Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Transaction Types Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def transactionTypesByMasterName(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializerByMasterName(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        MasterName = serialized1.data['MasterName']
        print(MasterName, 'MasterName')
        print(BranchID, 'BranchID')
        a = MasterType.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Name="VAT Type")
        print(a, 'a')
        if MasterType.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Name=MasterName).exists():

            MasterTypeinstance = MasterType.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, Name=MasterName)
            MasterTypeID = MasterTypeinstance.MasterTypeID

            if MasterTypeID == 2:
                instances = TransactionTypes.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, MasterTypeID=MasterTypeID).exclude(Name="Cash")
            else:
                instances = TransactionTypes.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, MasterTypeID=MasterTypeID)

            serialized = TransactionTypesRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "MasterName Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID or MasterName You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
