from brands.models import UserTable, UserType, Customer, User_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.userTable.serializers import UserTableSerializer, UserTableSerializerRestSerializer, ListSerializer
from api.v9.userTable.functions import generate_serializer_errors
from rest_framework import status
from api.v9.brands.functions import get_auto_id
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_user_table(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    Cash_Account = data['Cash_Account']
    Bank_Account = data['Bank_Account']
    Sales_Account = data['Sales_Account']
    Sales_Return_Account = data['Sales_Return_Account']
    Purchase_Account = data['Purchase_Account']
    Purchase_Return_Account = data['Purchase_Return_Account']
    is_web = data['is_web']
    is_mobile = data['is_mobile']
    is_pos = data['is_pos']
    BranchID = data['branch']
    today = datetime.datetime.now()
    NoOfUsers = int(CompanyID.NoOfUsers)
    usertable_count = UserTable.objects.filter(CompanyID=CompanyID).count()
    serialized = UserTableSerializer(data=request.data)
    if serialized.is_valid():
        UserTypeID = serialized.data['UserType']
        UserTypeID = UserType.objects.get(pk=UserTypeID)
        DefaultAccountForUser = serialized.data['DefaultAccountForUser']
        customer = serialized.data['customer']
        customer = Customer.objects.get(pk=customer)
        ExpiryDate = serialized.data['ExpiryDate']

        Action = 'A'
        if usertable_count < NoOfUsers:
            if UserTable.objects.filter(CompanyID=CompanyID, customer=customer).exists():
                UserTable.objects.filter(CompanyID=CompanyID, customer=customer).update(
                    UpdatedDate=today,
                    UserType=UserTypeID,
                    ExpiryDate=ExpiryDate,
                    DefaultAccountForUser=DefaultAccountForUser,
                    Cash_Account=Cash_Account,
                    Bank_Account=Bank_Account,
                    Sales_Account=Sales_Account,
                    Sales_Return_Account=Sales_Return_Account,
                    Purchase_Account=Purchase_Account,
                    Purchase_Return_Account=Purchase_Return_Account,
                    Action='M',
                    is_web=is_web,
                    is_mobile=is_mobile,
                    is_pos=is_pos,
                    BranchID=BranchID
                )
                User_Log.objects.create(
                    UpdatedDate=today,
                    UserType=UserTypeID,
                    ExpiryDate=ExpiryDate,
                    DefaultAccountForUser=DefaultAccountForUser,
                    Cash_Account=Cash_Account,
                    Bank_Account=Bank_Account,
                    Sales_Account=Sales_Account,
                    Sales_Return_Account=Sales_Return_Account,
                    Purchase_Account=Purchase_Account,
                    Purchase_Return_Account=Purchase_Return_Account,
                    Action='M',
                    is_web=is_web,
                    is_mobile=is_mobile,
                    is_pos=is_pos,
                    BranchID=BranchID
                )
            else:
                user_table = UserTable.objects.create(
                    CompanyID=CompanyID,
                    UserType=UserTypeID,
                    DefaultAccountForUser=DefaultAccountForUser,
                    CreatedUserID=CreatedUserID,
                    customer=customer,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Cash_Account=Cash_Account,
                    Bank_Account=Bank_Account,
                    Sales_Account=Sales_Account,
                    Sales_Return_Account=Sales_Return_Account,
                    Purchase_Account=Purchase_Account,
                    Purchase_Return_Account=Purchase_Return_Account,
                    JoinedDate=today.date(),
                    ExpiryDate=ExpiryDate,
                    Action=Action,
                    is_web=is_web,
                    is_mobile=is_mobile,
                    is_pos=is_pos,
                    BranchID=BranchID
                )

                User_Log.objects.create(
                    TransactionID=user_table.id,
                    CompanyID=CompanyID,
                    UserType=UserTypeID,
                    DefaultAccountForUser=DefaultAccountForUser,
                    CreatedUserID=CreatedUserID,
                    customer=customer,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Cash_Account=Cash_Account,
                    Bank_Account=Bank_Account,
                    Sales_Account=Sales_Account,
                    Sales_Return_Account=Sales_Return_Account,
                    Purchase_Account=Purchase_Account,
                    Purchase_Return_Account=Purchase_Return_Account,
                    JoinedDate=today.date(),
                    ExpiryDate=ExpiryDate,
                    Action=Action,
                    is_web=is_web,
                    is_mobile=is_mobile,
                    is_pos=is_pos,
                    BranchID=BranchID
                )

            response_data = {
                "StatusCode": 6000,
                "message": "User added successfully",
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "title": "Please contact administrator.",
                "message": "Saudi Arabia : +966 53 313 4959,\n India : +91 95775 00400"
            }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_user_table(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    Cash_Account = data['Cash_Account']
    Bank_Account = data['Bank_Account']
    Sales_Account = data['Sales_Account']
    Sales_Return_Account = data['Sales_Return_Account']
    Purchase_Account = data['Purchase_Account']
    Purchase_Return_Account = data['Purchase_Return_Account']
    today = datetime.datetime.now()
    serialized = UserTableSerializer(data=request.data)
    if serialized.is_valid():

        UserTypeID = serialized.data['UserType']
        UserTypeID = UserType.objects.get(pk=UserTypeID)
        DefaultAccountForUser = serialized.data['DefaultAccountForUser']
        customer = serialized.data['customer']
        customer = Customer.objects.get(pk=customer)
        ExpiryDate = serialized.data['ExpiryDate']

        Action = 'A'
        if UserTable.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            UserTable.objects.filter(CompanyID=CompanyID, pk=pk).update(
                UpdatedDate=today,
                UserType=UserTypeID,
                ExpiryDate=ExpiryDate,
                DefaultAccountForUser=DefaultAccountForUser,
                Cash_Account=Cash_Account,
                Bank_Account=Bank_Account,
                Sales_Account=Sales_Account,
                Sales_Return_Account=Sales_Return_Account,
                Purchase_Account=Purchase_Account,
                Purchase_Return_Account=Purchase_Return_Account,
                Action='M',
            )
            User_Log.objects.create(
                UpdatedDate=today,
                UserType=UserTypeID,
                ExpiryDate=ExpiryDate,
                DefaultAccountForUser=DefaultAccountForUser,
                Cash_Account=Cash_Account,
                Bank_Account=Bank_Account,
                Sales_Account=Sales_Account,
                Sales_Return_Account=Sales_Return_Account,
                Purchase_Account=Purchase_Account,
                Purchase_Return_Account=Purchase_Return_Account,
                Action='M',
            )
        else:
            user_table = UserTable.objects.create(
                CompanyID=CompanyID,
                UserType=UserTypeID,
                DefaultAccountForUser=DefaultAccountForUser,
                CreatedUserID=CreatedUserID,
                customer=customer,
                CreatedDate=today,
                UpdatedDate=today,
                Cash_Account=Cash_Account,
                Bank_Account=Bank_Account,
                Sales_Account=Sales_Account,
                Sales_Return_Account=Sales_Return_Account,
                Purchase_Account=Purchase_Account,
                Purchase_Return_Account=Purchase_Return_Account,
                JoinedDate=today,
                ExpiryDate=ExpiryDate,
                Action=Action,
            )

            User_Log.objects.create(
                TransactionID=user_table.id,
                CompanyID=CompanyID,
                UserType=UserTypeID,
                DefaultAccountForUser=DefaultAccountForUser,
                CreatedUserID=CreatedUserID,
                customer=customer,
                CreatedDate=today,
                UpdatedDate=today,
                Cash_Account=Cash_Account,
                Bank_Account=Bank_Account,
                Sales_Account=Sales_Account,
                Sales_Return_Account=Sales_Return_Account,
                Purchase_Account=Purchase_Account,
                Purchase_Return_Account=Purchase_Return_Account,
                JoinedDate=today,
                ExpiryDate=ExpiryDate,
                Action=Action,
            )

        response_data = {
            "StatusCode": 6000,
            "message": "User added successfully",
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_tables(request):
    data = request.data
    CompanyID = data['CompanyID']
    BranchID = data['BranchID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serializer = ListSerializer(data=request.data)
    # NoOfUsers = int(CompanyID.NoOfUsers)
    # usertable_count = UserTable.objects.filter(CompanyID=CompanyID).count()
    # if usertable_count > NoOfUsers:
    #     corrent_user = usertable_count - NoOfUsers
    #     last_user_table_instance = UserTable.objects.filter(CompanyID=CompanyID)[corrent_user:]
    #     UserTable.objects.exclude(pk__in=last_user_table_instance).delete()
    if serializer.is_valid():
        if UserTable.objects.filter(CompanyID=CompanyID).exists():
            instances = UserTable.objects.filter(CompanyID=CompanyID)
            serialized = UserTableSerializerRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID, "BranchID": BranchID})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "User Table Not Found"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_table(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if UserTable.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = UserTable.objects.get(pk=pk)
    if instance:
        serialized = UserTableSerializerRestSerializer(
            instance, context={"CompanyID": CompanyID})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "User Table Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_user_table(request, pk):
    today = datetime.datetime.now()
    data = request.data
    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    instances = None
    print(selecte_ids, ">>>>>>>>>>>>>>>>346")
    if selecte_ids:
        if UserTable.objects.filter(pk__in=selecte_ids).exists():
            instances = UserTable.objects.filter(
                pk__in=selecte_ids)
    else:
        if UserTable.objects.filter(pk=pk).exists():
            instances = UserTable.objects.filter(pk=pk)

    if instances:
        for instance in instances:
            # instance = UserTable.objects.get(pk=pk)
            UserType = instance.UserType
            ExpiryDate = instance.ExpiryDate
            DefaultAccountForUser = instance.DefaultAccountForUser
            Cash_Account = instance.Cash_Account
            Bank_Account = instance.Bank_Account
            Sales_Account = instance.Sales_Account
            Sales_Return_Account = instance.Sales_Return_Account
            Purchase_Account = instance.Purchase_Account
            Purchase_Return_Account = instance.Purchase_Return_Account
            Action = "D"
            instance.delete()
            User_Log.objects.create(
                UpdatedDate=today,
                UserType=UserType,
                ExpiryDate=ExpiryDate,
                DefaultAccountForUser=DefaultAccountForUser,
                Cash_Account=Cash_Account,
                Bank_Account=Bank_Account,
                Sales_Account=Sales_Account,
                Sales_Return_Account=Sales_Return_Account,
                Purchase_Account=Purchase_Account,
                Purchase_Return_Account=Purchase_Return_Account,
                Action=Action,
            )

        response_data = {
            "StatusCode": 6000,
            "message": "User Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "User not Found!"
        }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def leave_user_table(request, pk):
    today = datetime.datetime.now()
    user_id = request.data['user_id']
    instance = UserTable.objects.get(CompanyID__pk=pk, customer__user=user_id)
    UserType = instance.UserType
    ExpiryDate = instance.ExpiryDate
    DefaultAccountForUser = instance.DefaultAccountForUser
    Cash_Account = instance.Cash_Account
    Bank_Account = instance.Bank_Account
    Sales_Account = instance.Sales_Account
    Sales_Return_Account = instance.Sales_Return_Account
    Purchase_Account = instance.Purchase_Account
    Purchase_Return_Account = instance.Purchase_Return_Account
    Action = "D"
    instance.delete()
    User_Log.objects.create(
        UpdatedDate=today,
        UserType=UserType,
        ExpiryDate=ExpiryDate,
        DefaultAccountForUser=DefaultAccountForUser,
        Cash_Account=Cash_Account,
        Bank_Account=Bank_Account,
        Sales_Account=Sales_Account,
        Sales_Return_Account=Sales_Return_Account,
        Purchase_Account=Purchase_Account,
        Purchase_Return_Account=Purchase_Return_Account,
        Action=Action,
    )

    response_data = {
        "StatusCode": 6000,
        "message": "User Deleted Successfully!"
    }
    return Response(response_data, status=status.HTTP_200_OK)
