from rest_framework import serializers
from brands import models
from rest_framework.fields import CurrentUserDefault


class BankPaymentReceiptSerializer(serializers.ModelSerializer):
    LedgerName = serializers.SerializerMethodField()
    DueDate = serializers.SerializerMethodField()
    RefferenceNo = serializers.SerializerMethodField()

    class Meta:
        model = models.LedgerPosting
        fields = ("id", "CompanyID", "LedgerPostingID", "BranchID", "Action", "Date", "VoucherNo", "VoucherMasterID",
                  "VoucherDetailID", "VoucherType", "LedgerID", "LedgerName", "Debit", "Credit", "CreatedDate", "UpdatedDate", "CreatedUserID", "IsActive", "DueDate", "RefferenceNo")

    def get_LedgerName(self, instance):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        if models.AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
            LedgerName = models.AccountLedger.objects.get(
                LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).LedgerName
            return LedgerName
        else:
            return ""

    def get_DueDate(self, instance):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        VoucherDetailID = instance.VoucherDetailID
        VoucherType = instance.VoucherType
        VoucherMasterID = instance.VoucherMasterID
        if VoucherType == "BP":
            if models.PaymentDetails.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PaymentMasterID=VoucherMasterID, PaymentDetailsID=VoucherDetailID).exists():
                DueDate = models.PaymentDetails.objects.get(
                    LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PaymentMasterID=VoucherMasterID, PaymentDetailsID=VoucherDetailID).DueDate
                return DueDate
            else:
                return ""
        if VoucherType == "BR":
            if models.ReceiptDetails.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, ReceiptMasterID=VoucherMasterID, ReceiptDetailID=VoucherDetailID).exists():
                DueDate = models.ReceiptDetails.objects.get(
                    LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, ReceiptMasterID=VoucherMasterID, ReceiptDetailID=VoucherDetailID).DueDate
                return DueDate
            else:
                return ""

    def get_RefferenceNo(self, instance):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        VoucherDetailID = instance.VoucherDetailID
        VoucherType = instance.VoucherType
        VoucherMasterID = instance.VoucherMasterID
        if VoucherType == "BP":
            if models.PaymentDetails.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PaymentMasterID=VoucherMasterID, PaymentDetailsID=VoucherDetailID).exists():
                RefferenceNo = models.PaymentDetails.objects.get(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID,
                                                                 PaymentMasterID=VoucherMasterID, PaymentDetailsID=VoucherDetailID).RefferenceNo
                return RefferenceNo
            else:
                return ""
        if VoucherType == "BR":
            if models.ReceiptDetails.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, ReceiptMasterID=VoucherMasterID, ReceiptDetailID=VoucherDetailID).exists():
                RefferenceNo = models.ReceiptDetails.objects.get(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID,
                                                                 ReceiptMasterID=VoucherMasterID, ReceiptDetailID=VoucherDetailID).RefferenceNo
                return RefferenceNo
            else:
                return ""
