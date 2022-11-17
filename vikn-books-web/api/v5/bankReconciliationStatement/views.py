
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.v5.bankReconciliationStatement import serializers
from rest_framework import status
from main.functions import get_company
from brands import models


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def bank_payment_and_receipt(request):
    CompanyID = request.data['CompanyID']
    CreatedUserID = request.data['CreatedUserID']
    BranchID = request.data['BranchID']
    closing_date = request.data['closing_date']
    print(closing_date)
    CompanyID = get_company(CompanyID)

    if models.LedgerPosting.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Date__lte=closing_date).exists():
        instance = models.LedgerPosting.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, VoucherType__in=["BP", "BR"], Date__lte=closing_date)
        serialized = serializers.BankPaymentReceiptSerializer(
            instance, many=True, context={
                "request": request, "CompanyID": CompanyID})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Brands Not Found in this BranchID!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
