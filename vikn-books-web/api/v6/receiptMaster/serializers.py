from rest_framework import serializers
from brands.models import ReceiptMaster


class ReceiptMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReceiptMaster
        fields = ('id','BranchID','VoucherNo','InvoiceNo','SuffixPrefixID','ReceiptNo','ReferenceNo',
        	'LedgerID','EmployeeID',
        	'FinancialYearID','Date','TotalAmount','Notes','IsActive','CreatedDate','CreatedUserID')


class ReceiptMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReceiptMaster
        fields = ('id','ReceiptMasterID','BranchID','Action','VoucherNo','InvoiceNo','SuffixPrefixID','ReceiptNo',
        	'ReferenceNo','LedgerID','EmployeeID',
        	'FinancialYearID','Date','TotalAmount','Notes','IsActive','CreatedDate','CreatedUserID')
