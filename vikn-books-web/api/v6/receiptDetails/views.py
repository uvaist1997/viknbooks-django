from brands.models import ReceiptDetails, ReceiptDetails_Log, ReceiptDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v6.receiptDetails.serializers import ReceiptDetailsSerializer, ReceiptDetailsRestSerializer, ReceiptDetailsDummySerializer
from api.v6.brands.serializers import ListSerializer
from api.v6.receiptDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v6.receiptDetails.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_receiptDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = ReceiptDetailsSerializer(data=request.data)
    if serialized.is_valid():

        PaymentGateway = receiptDetail['PaymentGateway']
        BranchID = receiptDetail['BranchID']
        ReceiptMasterID = receiptDetail['ReceiptMasterID']
        VoucherType = receiptDetail['VoucherType']
        RefferenceNo = receiptDetail['RefferenceNo']
        CardNetwork = receiptDetail['CardNetwork']
        PaymentStatus = receiptDetail['PaymentStatus']
        LedgerID = receiptDetail['LedgerID']
        DueDate = receiptDetail['DueDate']
        Amount = receiptDetail['Amount']
        Discount = receiptDetail['Discount']
        NetAmount = receiptDetail['NetAmount']
        Balance = receiptDetail['Balance']
        Narration = receiptDetail['Narration']

        Action = "A"

        ReceiptDetailID = get_auto_id(ReceiptDetails, BranchID)

        ReceiptDetails.objects.create(
            ReceiptDetailID=ReceiptDetailID,
            BranchID=BranchID,
            Action=Action,
            ReceiptMasterID=ReceiptMasterID,
            VoucherType=VoucherType,
            PaymentGateway=PaymentGateway,
            RefferenceNo=RefferenceNo,
            CardNetwork=CardNetwork,
            PaymentStatus=PaymentStatus,
            LedgerID=LedgerID,
            DueDate=DueDate,
            Amount=Amount,
            Discount=Discount,
            NetAmount=NetAmount,
            Balance=Balance,
            Narration=Narration,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
        )

        ReceiptDetails_Log.objects.create(
            TransactionID=ReceiptDetailID,
            BranchID=BranchID,
            Action=Action,
            ReceiptMasterID=ReceiptMasterID,
            VoucherType=VoucherType,
            PaymentGateway=PaymentGateway,
            RefferenceNo=RefferenceNo,
            CardNetwork=CardNetwork,
            PaymentStatus=PaymentStatus,
            LedgerID=LedgerID,
            DueDate=DueDate,
            Amount=Amount,
            Discount=Discount,
            NetAmount=NetAmount,
            Balance=Balance,
            Narration=Narration,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
        )

        data = {"ReceiptDetailID": ReceiptDetailID}
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
def edit_receiptDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized = ReceiptDetailsSerializer(data=request.data)
    instance = None
    if ReceiptDetails.objects.filter(pk=pk).exists():
        instance = ReceiptDetails.objects.get(pk=pk)

        ReceiptDetailID = instance.ReceiptDetailID
        BranchID = instance.BranchID

        if serialized.is_valid():
            ReceiptMasterID = serialized.data['ReceiptMasterID']
            OldVoucherMasterID = serialized.data['OldVoucherMasterID']
            LedgerID = serialized.data['LedgerID']
            Date = serialized.data['Date']
            Amount = serialized.data['Amount']
            Discount = serialized.data['Discount']
            Narration = serialized.data['Narration']

            Action = "M"

            instance.ReceiptDetailID = ReceiptDetailID
            instance.BranchID = BranchID
            instance.Action = Action
            instance.ReceiptMasterID = ReceiptMasterID
            instance.VoucherType = VoucherType
            instance.PaymentGateway = PaymentGateway
            instance.RefferenceNo = RefferenceNo
            instance.CardNetwork = CardNetwork
            instance.PaymentStatus = PaymentStatus
            instance.LedgerID = LedgerID
            instance.DueDate = DueDate
            instance.Amount = Amount
            instance.Discount = Discount
            instance.NetAmount = NetAmount
            instance.Balance = Balance
            instance.Narration = Narration
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            ReceiptDetails_Log.objects.create(
                TransactionID=ReceiptDetailID,
                BranchID=BranchID,
                Action=Action,
                ReceiptMasterID=ReceiptMasterID,
                VoucherType=VoucherType,
                PaymentGateway=PaymentGateway,
                RefferenceNo=RefferenceNo,
                CardNetwork=CardNetwork,
                PaymentStatus=PaymentStatus,
                LedgerID=LedgerID,
                DueDate=DueDate,
                Amount=Amount,
                Discount=Discount,
                NetAmount=NetAmount,
                Balance=Balance,
                Narration=Narration,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
            )

            data = {"ReceiptDetailID": ReceiptDetailID}
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
            "message": "Receipt Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_receiptDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if ReceiptDetails.objects.filter(BranchID=BranchID).exists():

            instances = ReceiptDetails.objects.filter(BranchID=BranchID)

            serialized = ReceiptDetailsRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Receipt Details Not Found in this BranchID!"
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
def receiptDetail(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if ReceiptDetails.objects.filter(pk=pk).exists():
        instance = ReceiptDetails.objects.get(pk=pk)
        serialized = ReceiptDetailsRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Receipt Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_receiptDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if ReceiptDetails.objects.filter(pk=pk).exists():
        instance = ReceiptDetails.objects.get(pk=pk)
        ReceiptDetailID = instance.ReceiptDetailID
        BranchID = instance.BranchID
        ReceiptMasterID = instance.ReceiptMasterID
        VoucherType = instance.VoucherType
        PaymentGateway = instance.PaymentGateway
        RefferenceNo = instance.RefferenceNo
        CardNetwork = instance.CardNetwork
        PaymentStatus = instance.PaymentStatus
        LedgerID = instance.LedgerID
        DueDate = instance.DueDate
        Amount = instance.Amount
        Discount = instance.Discount
        NetAmount = instance.NetAmount
        Balance = instance.Balance
        Narration = instance.Narration

        Action = "D"

        instance.delete()

        ReceiptDetails_Log.objects.create(
            TransactionID=ReceiptDetailID,
            BranchID=BranchID,
            Action=Action,
            ReceiptMasterID=ReceiptMasterID,
            VoucherType=VoucherType,
            PaymentGateway=PaymentGateway,
            RefferenceNo=RefferenceNo,
            CardNetwork=CardNetwork,
            PaymentStatus=PaymentStatus,
            LedgerID=LedgerID,
            DueDate=DueDate,
            Amount=Amount,
            Discount=Discount,
            NetAmount=NetAmount,
            Balance=Balance,
            Narration=Narration,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Receipt Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Receipt Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_receiptDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    PaymentGateway = data['PaymentGateway']
    BranchID = data['BranchID']
    ReceiptMasterID = data['ReceiptMasterID']
    RefferenceNo = data['RefferenceNo']
    CardNetwork = data['CardNetwork']
    PaymentStatus = data['PaymentStatus']
    LedgerID = data['LedgerID']
    DueDate = data['DueDate']
    Amount = data['Amount']
    Discount = data['Discount']
    NetAmount = data['NetAmount']
    Balance = data['Balance']
    Narration = data['Narration']

    detailID = 0

    ReceiptDetailsDummy.objects.create(
        BranchID=BranchID,
        ReceiptMasterID=ReceiptMasterID,
        PaymentGateway=PaymentGateway,
        RefferenceNo=RefferenceNo,
        CardNetwork=CardNetwork,
        PaymentStatus=PaymentStatus,
        LedgerID=LedgerID,
        DueDate=DueDate,
        Amount=Amount,
        Discount=Discount,
        NetAmount=NetAmount,
        Balance=Balance,
        Narration=Narration,
        CreatedUserID=CreatedUserID,
    )

    response_data = {
        "StatusCode": 6000,
        "message": "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_DummyforEditReceiptMaster(request):

    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = ReceiptDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:

        PaymentGateway = dummydetail['PaymentGateway']
        BranchID = dummydetail['BranchID']
        ReceiptMasterID = dummydetail['ReceiptMasterID']
        RefferenceNo = dummydetail['RefferenceNo']
        CardNetwork = dummydetail['CardNetwork']
        PaymentStatus = dummydetail['PaymentStatus']
        LedgerID = dummydetail['LedgerID']
        DueDate = dummydetail['DueDate']
        Amount = dummydetail['Amount']
        Discount = dummydetail['Discount']
        NetAmount = dummydetail['NetAmount']
        Balance = dummydetail['Balance']
        Narration = dummydetail['Narration']

        detailID = 0

        ReceiptDetailsDummy.objects.create(
            BranchID=BranchID,
            ReceiptMasterID=ReceiptMasterID,
            PaymentGateway=PaymentGateway,
            RefferenceNo=RefferenceNo,
            CardNetwork=CardNetwork,
            PaymentStatus=PaymentStatus,
            LedgerID=LedgerID,
            DueDate=DueDate,
            Amount=Amount,
            Discount=Discount,
            NetAmount=NetAmount,
            Balance=Balance,
            Narration=Narration,
            CreatedUserID=CreatedUserID,
        )

    response_data = {
        "StatusCode": 6000,
        "message": "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_receiptDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if ReceiptDetailsDummy.objects.filter(BranchID=BranchID).exists():

            amount = 0
            balance = 0
            discount = 0
            netAmount = 0

            instances = ReceiptDetailsDummy.objects.filter(BranchID=BranchID)

            for instance in instances:

                amount += instance.Amount
                balance += int(instance.Balance)
                discount += instance.Discount
                netAmount += instance.NetAmount

            serialized = ReceiptDetailsDummySerializer(
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
def edit_receiptDetailsDummy(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if ReceiptDetailsDummy.objects.filter(pk=pk).exists():

        instance = ReceiptDetailsDummy.objects.get(pk=pk)

        PaymentGateway = data['PaymentGateway']
        BranchID = data['BranchID']
        ReceiptMasterID = data['ReceiptMasterID']
        RefferenceNo = data['RefferenceNo']
        CardNetwork = data['CardNetwork']
        PaymentStatus = data['PaymentStatus']
        LedgerID = data['LedgerID']
        DueDate = data['DueDate']
        Amount = data['Amount']
        Discount = data['Discount']
        NetAmount = data['NetAmount']
        Balance = data['Balance']
        Narration = data['Narration']
        detailID = data['detailID']

        instance.PaymentGateway = PaymentGateway
        instance.BranchID = BranchID
        instance.ReceiptMasterID = ReceiptMasterID
        instance.RefferenceNo = RefferenceNo
        instance.CardNetwork = CardNetwork
        instance.PaymentStatus = PaymentStatus
        instance.LedgerID = LedgerID
        instance.DueDate = DueDate
        instance.Amount = Amount
        instance.Discount = Discount
        instance.NetAmount = NetAmount
        instance.Balance = Balance
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
def delete_receiptDetailsDummy(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if ReceiptDetailsDummy.objects.filter(pk=pk).exists():
        instance = ReceiptDetailsDummy.objects.get(pk=pk)
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
