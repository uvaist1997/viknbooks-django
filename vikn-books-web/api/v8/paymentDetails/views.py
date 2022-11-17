from brands.models import PaymentDetails, PaymentDetails_Log, PaymentDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.paymentDetails.serializers import PaymentDetailsSerializer, PaymentDetailsRestSerializer, PaymentDetailsDummySerializer
from api.v8.brands.serializers import ListSerializer
from api.v8.paymentDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v8.paymentDetails.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_paymentDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = PaymentDetailsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        PaymentMasterID = serialized.data['PaymentMasterID']
        PaymentGateway = serialized.data['PaymentGateway']
        RefferenceNo = serialized.data['RefferenceNo']
        CardNetwork = serialized.data['CardNetwork']
        PaymentStatus = serialized.data['PaymentStatus']
        DueDate = serialized.data['DueDate']
        LedgerID = serialized.data['LedgerID']
        Amount = serialized.data['Amount']
        Balance = serialized.data['Balance']
        Discount = serialized.data['Discount']
        NetAmount = serialized.data['NetAmount']
        Narration = serialized.data['Narration']
        Action = "A"

        PaymentDetailsID = get_auto_id(PaymentDetails, BranchID, DataBase)

        PaymentDetails.objects.create(
            PaymentDetailsID=PaymentDetailsID,
            BranchID=BranchID,
            Action=Action,
            PaymentMasterID=PaymentMasterID,
            PaymentGateway=PaymentGateway,
            RefferenceNo=RefferenceNo,
            CardNetwork=CardNetwork,
            PaymentStatus=PaymentStatus,
            DueDate=DueDate,
            LedgerID=LedgerID,
            Amount=Amount,
            Balance=Balance,
            Discount=Discount,
            NetAmount=NetAmount,
            Narration=Narration,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
        )

        PaymentDetails_Log.objects.create(
            TransactionID=PaymentDetailsID,
            BranchID=BranchID,
            Action=Action,
            PaymentMasterID=PaymentMasterID,
            PaymentGateway=PaymentGateway,
            RefferenceNo=RefferenceNo,
            CardNetwork=CardNetwork,
            PaymentStatus=PaymentStatus,
            DueDate=DueDate,
            LedgerID=LedgerID,
            Amount=Amount,
            Balance=Balance,
            Discount=Discount,
            NetAmount=NetAmount,
            Narration=Narration,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
        )

        data = {"PaymentDetailsID": PaymentDetailsID}
        data.update(serialized.data)
        response_data = {
            "StatusCode": 6000,
            "data": data
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
def edit_paymentDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized = PaymentDetailsSerializer(data=request.data)
    if PaymentDetails.objects.filter(pk=pk).exists():
        instance = PaymentDetails.objects.get(pk=pk)

        PaymentDetailsID = instance.PaymentDetailsID
        PaymentMasterID = instance.PaymentMasterID
        BranchID = instance.BranchID

        if serialized.is_valid():
            PaymentGateway = serialized.data['PaymentGateway']
            RefferenceNo = serialized.data['RefferenceNo']
            CardNetwork = serialized.data['CardNetwork']
            PaymentStatus = serialized.data['PaymentStatus']
            DueDate = serialized.data['DueDate']
            LedgerID = serialized.data['LedgerID']
            Amount = serialized.data['Amount']
            Balance = serialized.data['Balance']
            Discount = serialized.data['Discount']
            NetAmount = serialized.data['NetAmount']
            Narration = serialized.data['Narration']

            Action = "M"

            instance.PaymentGateway = PaymentGateway
            instance.RefferenceNo = RefferenceNo
            instance.CardNetwork = CardNetwork
            instance.PaymentStatus = PaymentStatus
            instance.DueDate = DueDate
            instance.LedgerID = LedgerID
            instance.Amount = Amount
            instance.Balance = Balance
            instance.Discount = Discount
            instance.NetAmount = NetAmount
            instance.Narration = Narration
            instance.CreatedUserID = CreatedUserID
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            PaymentDetails_Log.objects.create(
                TransactionID=PaymentDetailsID,
                BranchID=BranchID,
                Action=Action,
                PaymentMasterID=PaymentMasterID,
                PaymentGateway=PaymentGateway,
                RefferenceNo=RefferenceNo,
                CardNetwork=CardNetwork,
                PaymentStatus=PaymentStatus,
                DueDate=DueDate,
                LedgerID=LedgerID,
                Amount=Amount,
                Balance=Balance,
                Discount=Discount,
                NetAmount=NetAmount,
                Narration=Narration,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
            )

            data = {"PaymentDetailsID": PaymentDetailsID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors)
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Payment Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_paymentDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if PaymentDetails.objects.filter(BranchID=BranchID).exists():

            instances = PaymentDetails.objects.filter(BranchID=BranchID)

            serialized = PaymentDetailsRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Payment Details Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def paymentDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if PaymentDetails.objects.filter(pk=pk).exists():
        instance = PaymentDetails.objects.get(pk=pk)
        serialized = PaymentDetailsRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Payment Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_paymentDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if PaymentDetails.objects.filter(pk=pk).exists():
        instance = PaymentDetails.objects.get(pk=pk)
        PaymentDetailsID = instance.PaymentDetailsID
        BranchID = instance.BranchID
        PaymentMasterID = instance.PaymentMasterID
        PaymentGateway = instance.PaymentGateway
        RefferenceNo = instance.RefferenceNo
        CardNetwork = instance.CardNetwork
        PaymentStatus = instance.PaymentStatus
        DueDate = instance.DueDate
        LedgerID = instance.LedgerID
        Amount = instance.Amount
        Balance = instance.Balance
        Discount = instance.Discount
        NetAmount = instance.NetAmount
        Narration = instance.Narration
        Action = "D"

        instance.delete()

        PaymentDetails_Log.objects.create(
            TransactionID=PaymentDetailsID,
            BranchID=BranchID,
            Action=Action,
            PaymentMasterID=PaymentMasterID,
            PaymentGateway=PaymentGateway,
            RefferenceNo=RefferenceNo,
            CardNetwork=CardNetwork,
            PaymentStatus=PaymentStatus,
            DueDate=DueDate,
            LedgerID=LedgerID,
            Amount=Amount,
            Balance=Balance,
            Discount=Discount,
            NetAmount=NetAmount,
            Narration=Narration,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Payment Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Payment Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_paymentDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    BranchID = data['BranchID']
    PaymentMasterID = data['PaymentMasterID']
    PaymentGateway = data['PaymentGateway']
    RefferenceNo = data['RefferenceNo']
    CardNetwork = data['CardNetwork']
    PaymentStatus = data['PaymentStatus']
    DueDate = data['DueDate']
    LedgerID = data['LedgerID']
    Amount = data['Amount']
    Balance = data['Balance']
    Discount = data['Discount']
    NetAmount = data['NetAmount']
    Narration = data['Narration']

    detailID = 0

    PaymentDetailsDummy.objects.create(
        BranchID=BranchID,
        PaymentMasterID=PaymentMasterID,
        PaymentGateway=PaymentGateway,
        RefferenceNo=RefferenceNo,
        CardNetwork=CardNetwork,
        PaymentStatus=PaymentStatus,
        DueDate=DueDate,
        LedgerID=LedgerID,
        Amount=Amount,
        Balance=Balance,
        Discount=Discount,
        NetAmount=NetAmount,
        Narration=Narration,
        CreatedUserID=CreatedUserID,
        detailID=detailID,
    )

    response_data = {
        "StatusCode": 6000,
        "message": "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_DummyforEditPaymentMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = PaymentDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:

        BranchID = dummydetail['BranchID']
        PaymentMasterID = dummydetail['PaymentMasterID']
        PaymentGateway = dummydetail['PaymentGateway']
        RefferenceNo = dummydetail['RefferenceNo']
        CardNetwork = dummydetail['CardNetwork']
        PaymentStatus = dummydetail['PaymentStatus']
        DueDate = dummydetail['DueDate']
        LedgerID = dummydetail['LedgerID']
        Amount = dummydetail['Amount']
        Balance = dummydetail['Balance']
        Discount = dummydetail['Discount']
        NetAmount = dummydetail['NetAmount']
        Narration = dummydetail['Narration']

        detailID = 0

        PaymentDetailsDummy.objects.create(
            BranchID=BranchID,
            PaymentMasterID=PaymentMasterID,
            PaymentGateway=PaymentGateway,
            RefferenceNo=RefferenceNo,
            CardNetwork=CardNetwork,
            PaymentStatus=PaymentStatus,
            DueDate=DueDate,
            LedgerID=LedgerID,
            Amount=Amount,
            Balance=Balance,
            Discount=Discount,
            NetAmount=NetAmount,
            Narration=Narration,
            CreatedUserID=CreatedUserID,
            detailID=detailID,
        )

    response_data = {
        "StatusCode": 6000,
        "message": "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_paymentDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if PaymentDetailsDummy.objects.filter(BranchID=BranchID).exists():
            amount = 0
            balance = 0
            discount = 0
            netAmount = 0

            instances = PaymentDetailsDummy.objects.filter(BranchID=BranchID)

            for instance in instances:

                amount += instance.Amount
                balance += int(instance.Balance)
                discount += instance.Discount
                netAmount += instance.NetAmount

            serialized = PaymentDetailsDummySerializer(
                instances, many=True, context={"DataBase": DataBase})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "TotalAmount": amount,
                "TotalBalance": balance,
                "TotalDiscount": discount,
                "TotalNetAmount": netAmount,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "BranchID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_paymentDetailsDummy(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if PaymentDetailsDummy.objects.filter(pk=pk).exists():
        instance = PaymentDetailsDummy.objects.get(pk=pk)

        BranchID = data['BranchID']
        PaymentMasterID = data['PaymentMasterID']
        PaymentGateway = data['PaymentGateway']
        RefferenceNo = data['RefferenceNo']
        CardNetwork = data['CardNetwork']
        PaymentStatus = data['PaymentStatus']
        DueDate = data['DueDate']
        LedgerID = data['LedgerID']
        Amount = data['Amount']
        Balance = data['Balance']
        Discount = data['Discount']
        NetAmount = data['NetAmount']
        Narration = data['Narration']
        detailID = data['detailID']

        instance.BranchID = BranchID
        instance.PaymentMasterID = PaymentMasterID
        instance.PaymentGateway = PaymentGateway
        instance.RefferenceNo = RefferenceNo
        instance.CardNetwork = CardNetwork
        instance.PaymentStatus = PaymentStatus
        instance.DueDate = DueDate
        instance.LedgerID = LedgerID
        instance.Amount = Amount
        instance.Balance = Balance
        instance.Discount = Discount
        instance.NetAmount = NetAmount
        instance.Narration = Narration
        instance.CreatedUserID = CreatedUserID
        instance.detailID = detailID
        instance.save()

        response_data = {
            "StatusCode": 6000,
            "message": "Successfully updated!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Product Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_paymentDetailsDummy(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if PaymentDetailsDummy.objects.filter(pk=pk).exists():
        instance = PaymentDetailsDummy.objects.get(pk=pk)
        instance.delete()

        response_data = {
            "StatusCode": 6000,
            "message": "Product Removed Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Product Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
