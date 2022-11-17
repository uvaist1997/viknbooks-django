from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from brands import models
from main.functions import converted_float, get_VoucherName


class BankReconciliationSerializer(serializers.ModelSerializer):
    RelativeLedgerName = serializers.SerializerMethodField()
    TransactionType = serializers.SerializerMethodField()
    Reference = serializers.SerializerMethodField()
    Debit = serializers.SerializerMethodField()
    Credit = serializers.SerializerMethodField()
    PaymentGateway = serializers.SerializerMethodField()
    IsReconciliate = serializers.SerializerMethodField()

    class Meta:
        model = models.LedgerPosting
        fields = (
            "id",
            "CompanyID",
            "Date",
            "VoucherMasterID",
            "LedgerID",
            "RelatedLedgerID",
            "RelativeLedgerName",
            "TransactionType",
            "Reference",
            "Debit",
            "Credit",
            "PaymentGateway",
            "IsReconciliate",
        )

    def get_PaymentGateway(self, instance):
        return ""

    def get_IsReconciliate(self, instance):
        return False

    def get_RelativeLedgerName(self, instance):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instance.RelatedLedgerID
        LedgerName = ""
        if models.AccountLedger.objects.filter(
            LedgerID=LedgerID, CompanyID=CompanyID
        ).exists():
            LedgerName = models.AccountLedger.objects.get(
                LedgerID=LedgerID, CompanyID=CompanyID
            ).LedgerName
        return LedgerName

    def get_TransactionType(self, instance):
        CompanyID = self.context.get("CompanyID")
        VoucherType = instance.VoucherType
        TransactionType = get_VoucherName(VoucherType)
        return TransactionType

    def get_Reference(self, instance):
        Reference = ""
        return Reference

    def get_Debit(self, instance):
        Debit = instance.Debit
        return converted_float(Debit)

    def get_Credit(self, instance):
        Credit = instance.Credit
        return converted_float(Credit)


class BankReconciliationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BankReconciliationMaster
        fields = (
            "id",
            "VoucherNo",
            "Date",
            "ClosingDate",
            "StartingDate",
            "BankName",
            "BankID",
            "ClosingBalance",
            "ClearedAmt",
            "Differences",
            "Type",
        )


class ReconciliationDetailSerializer(serializers.ModelSerializer):
    LedgerPostingUnqid = serializers.SerializerMethodField()
    RelatedLedgerID = serializers.SerializerMethodField()

    class Meta:
        model = models.BankReconciliationDetails
        fields = (
            "id",
            "Date",
            "RelativeLedgerName",
            "TransactionType",
            "ChecqueOrRefNo",
            "InstrOrDueDate",
            "BankDate",
            "Debit",
            "Credit",
            "VoucherMasterID",
            "RelatedLedgerID",
            "PaymentGateway",
            "PaymentStatus",
            "IsReconciliate",
            "LedgerPostingUnqid",
        )

    def get_LedgerPostingUnqid(self, instance):
        LedgerPostid = None
        if instance.LedgerPostid:
            LedgerPostid = instance.LedgerPostid.id
        return LedgerPostid

    def get_RelatedLedgerID(self, instance):
        RelatedLedgerID = instance.RelativeLedgerID
        return RelatedLedgerID


class BankReconciliationSingleSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = models.BankReconciliationMaster
        fields = (
            "id",
            "VoucherNo",
            "Date",
            "BankName",
            "BankID",
            "ClosingBalance",
            "ClosingDate",
            "ClearedAmt",
            "Differences",
            "Type",
            "BankStatement",
            "details",
        )

    def get_details(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BankReconciliationMasterID = instance.BankReconciliationMasterID
        BranchID = instance.BranchID
        details_data = []
        if models.BankReconciliationDetails.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            BankReconciliationMasterID=BankReconciliationMasterID,
        ).exists():
            detail_instances = models.BankReconciliationDetails.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                BankReconciliationMasterID=BankReconciliationMasterID,
            )
            serialized = ReconciliationDetailSerializer(
                detail_instances,
                many=True,
                context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
            )
            details_data = serialized.data
        return details_data


class BankReconciliationReportSerializer(serializers.ModelSerializer):
    RelativeLedgerName = serializers.SerializerMethodField()
    TransactionType = serializers.SerializerMethodField()
    Reference = serializers.SerializerMethodField()
    Debit = serializers.SerializerMethodField()
    Credit = serializers.SerializerMethodField()
    PaymentGateway = serializers.SerializerMethodField()
    IsReconciliate = serializers.SerializerMethodField()

    class Meta:
        model = models.LedgerPosting
        fields = (
            "id",
            "CompanyID",
            "Date",
            "VoucherMasterID",
            "LedgerID",
            "RelatedLedgerID",
            "RelativeLedgerName",
            "TransactionType",
            "Reference",
            "Debit",
            "Credit",
            "PaymentGateway",
            "IsReconciliate",
        )

    def get_PaymentGateway(self, instance):
        return ""

    def get_IsReconciliate(self, instance):
        return False

    def get_RelativeLedgerName(self, instance):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instance.RelatedLedgerID
        LedgerName = ""
        if models.AccountLedger.objects.filter(
            LedgerID=LedgerID, CompanyID=CompanyID
        ).exists():
            LedgerName = models.AccountLedger.objects.get(
                LedgerID=LedgerID, CompanyID=CompanyID
            ).LedgerName
        return LedgerName

    def get_TransactionType(self, instance):
        CompanyID = self.context.get("CompanyID")
        VoucherType = instance.VoucherType
        TransactionType = get_VoucherName(VoucherType)
        return TransactionType

    def get_Reference(self, instance):
        Reference = ""
        return Reference

    def get_Debit(self, instance):
        Debit = instance.Debit
        return float(Debit)

    def get_Credit(self, instance):
        Credit = instance.Credit
        return float(Credit)
