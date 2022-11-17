from rest_framework import serializers
from collections import OrderedDict
from brands.models import LedgerPosting, AccountLedger, AccountGroup, StockRate, Product


def check_exists(AccountGroupUnder, value, CompanyID):
    if not AccountGroupUnder == 0:
        if AccountGroup.objects.filter(CompanyID=CompanyID, AccountGroupID=AccountGroupUnder).exists():
            group_instance = AccountGroup.objects.get(
                CompanyID=CompanyID, AccountGroupID=AccountGroupUnder)
            AccountGroupUnder = group_instance.AccountGroupUnder
            if AccountGroupUnder == value:
                return True
            else:
                return check_exists(AccountGroupUnder, value, CompanyID)
        else:
            return False
    else:
        return False


def check_groupforProfitandLoss(AccountGroupUnder, CompanyID):
    if not AccountGroupUnder == 0:
        if AccountGroup.objects.filter(CompanyID=CompanyID, AccountGroupID=AccountGroupUnder).exists():
            group_instance = AccountGroup.objects.get(
                CompanyID=CompanyID, AccountGroupID=AccountGroupUnder)
            AccountGroupUnder = group_instance.AccountGroupUnder
            AccountGroupName = group_instance.AccountGroupName
            if AccountGroupName == "Direct Expenses":
                return AccountGroupName
            elif AccountGroupName == "Indirect Expenses":
                return AccountGroupName
            elif AccountGroupName == "Direct Income":
                return AccountGroupName
            elif AccountGroupName == "Indirect Income":
                return AccountGroupName
            else:
                return check_groupforProfitandLoss(AccountGroupUnder, CompanyID)
        else:
            return False
    else:
        return False


def check_groupforBalanceSheet(AccountGroupUnder, CompanyID):
    if not AccountGroupUnder == 0:
        if AccountGroup.objects.filter(CompanyID=CompanyID, AccountGroupID=AccountGroupUnder).exists():
            group_instance = AccountGroup.objects.get(
                CompanyID=CompanyID, AccountGroupID=AccountGroupUnder)
            AccountGroupUnder = group_instance.AccountGroupUnder
            AccountGroupName = group_instance.AccountGroupName

            if AccountGroupName == "Assets":
                return AccountGroupName
            elif AccountGroupName == "Liabilitis":
                return AccountGroupName
            else:
                return check_groupforBalanceSheet(AccountGroupUnder, CompanyID)
        else:
            return False
    else:
        return False


class LedgerPostingSerializer(serializers.ModelSerializer):

    class Meta:
        model = LedgerPosting
        fields = ('id', 'BranchID', 'Date', 'VoucherMasterID', 'VoucherType', 'LedgerID',
                  'Debit', 'Credit', 'CreatedDate', 'IsActive', 'InvoiceNo', 'VoucherNo', 'CreatedUserID')


class LedgerPostingRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = LedgerPosting
        fields = ('id', 'LedgerPostingID', 'BranchID', 'Date', 'VoucherMasterID', 'VoucherType', 'LedgerID',
                  'Debit', 'Credit', 'CreatedDate', 'Action', 'IsActive', 'InvoiceNo', 'VoucherNo', 'CreatedUserID')


class TrialBalanceSerializer(serializers.ModelSerializer):

    Debit = serializers.SerializerMethodField()
    Credit = serializers.SerializerMethodField()
    VoucherType = serializers.SerializerMethodField()

    class Meta:
        model = AccountLedger
        fields = ('LedgerID', 'LedgerName', 'Debit', 'Credit', 'VoucherType')

    def get_Debit(self, account_ledger):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = account_ledger.LedgerID
        Debit = 0
        Credit = 0
        TotalDebit = 0
        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID)

            for ledgerpost_instance in ledgerpost_instances:

                Debit += float(ledgerpost_instance.Debit)
                Credit += float(ledgerpost_instance.Credit)

        Tot = float(Debit) - float(Credit)
        if float(Tot) > 0:
            TotalDebit = Tot

        return float(round(abs(TotalDebit), PriceRounding))

    def get_Credit(self, account_ledger):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = account_ledger.LedgerID
        Debit = 0
        Credit = 0
        TotalCredit = 0

        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID)

            for ledgerpost_instance in ledgerpost_instances:

                Debit += float(ledgerpost_instance.Debit)
                Credit += float(ledgerpost_instance.Credit)

        Tot = float(Debit) - float(Credit)
        if float(Tot) < 0:
            TotalCredit = Tot

        return float(round(abs(TotalCredit), PriceRounding))


    def get_VoucherType(self, account_ledger):
        CompanyID = self.context.get("CompanyID")
        LedgerID = account_ledger.LedgerID
        VoucherType = None

        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID)

            for ledgerpost_instance in ledgerpost_instances:

                VoucherType = ledgerpost_instance.VoucherType

            return VoucherType


class ListSerializerforTrialBalance(serializers.Serializer):

    BranchID = serializers.IntegerField()
    ToDate = serializers.DateField()


# class LedgerReportAllSerializer(serializers.ModelSerializer):

#     LedgerName = serializers.SerializerMethodField()

#     class Meta:
#         model = LedgerPosting
#         fields = ('LedgerID','LedgerName','Debit','Credit')


#     def get_LedgerName(self, instance):
#         LedgerID = instance.LedgerID
#         BranchID = instance.BranchID
#         if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID).exists():
#             AccountLedgerInstances = AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID)
#             for instance in AccountLedgerInstances:
#                 LedgerName = instance.LedgerName
#             return LedgerName
#         else:
#             return ""

class LedgerReportAllSerializer(serializers.ModelSerializer):
    Debit = serializers.SerializerMethodField()
    Credit = serializers.SerializerMethodField()

    class Meta:
        model = AccountLedger
        fields = ('LedgerID', 'LedgerName', 'Debit', 'Credit')

    def get_Debit(self, account_ledger):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = account_ledger.LedgerID
        BranchID = account_ledger.BranchID

        print("#===####################====#########")
        print(PriceRounding)

        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
            Debit = 0
            for ledgerpost_instance in ledgerpost_instances:

                Debit += ledgerpost_instance.Debit

            return float(round(Debit, PriceRounding))

    def get_Credit(self, account_ledger):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = account_ledger.LedgerID
        BranchID = account_ledger.BranchID

        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

            Credit = 0
            for ledgerpost_instance in ledgerpost_instances:

                Credit += ledgerpost_instance.Credit

            return float(round(Credit, PriceRounding))


class LedgerReportLedgerWiseSerializer(serializers.ModelSerializer):

    LedgerName = serializers.SerializerMethodField()
    VoucherType = serializers.SerializerMethodField()

    class Meta:
        model = LedgerPosting
        fields = ('LedgerPostingID', 'LedgerID', 'LedgerName',
                  'VoucherType', 'VoucherNo', 'Date', 'Debit', 'Credit')

    def get_LedgerName(self, instance):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            AccountLedgerInstances = AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
            for instance in AccountLedgerInstances:
                LedgerName = instance.LedgerName
            return LedgerName
        else:
            return ""

    def get_VoucherType(self, instance):

        if instance.VoucherType == 'JL':
            VoucherType = 'Journal'
        elif instance.VoucherType == 'SI':
            VoucherType = 'Sales Invoice'
        elif instance.VoucherType == 'PI':
            VoucherType = 'Purchase Invoice'
        elif instance.VoucherType == 'SR':
            VoucherType = 'Sales Return'
        elif instance.VoucherType == 'PR':
            VoucherType = 'Purchase Return'
        elif instance.VoucherType == 'SO':
            VoucherType = 'Sales Order'
        elif instance.VoucherType == 'PO':
            VoucherType = 'Purchase Order'
        elif instance.VoucherType == 'CP':
            VoucherType = 'Cash Payment'
        elif instance.VoucherType == 'BP':
            VoucherType = 'Bank Payment'
        elif instance.VoucherType == 'CR':
            VoucherType = 'Cash Receipt'
        elif instance.VoucherType == 'BR':
            VoucherType = 'Bank Receipt'
        elif instance.VoucherType == 'LOB':
            VoucherType = 'Ledger Opening Balance'

        return VoucherType


class LedgerReportGroupSerializer(serializers.ModelSerializer):

    LedgerName = serializers.SerializerMethodField()
    GroupUnder = serializers.SerializerMethodField()

    class Meta:
        model = LedgerPosting
        fields = ('LedgerID', 'LedgerName', 'Debit', 'Credit', 'GroupUnder')

    def get_LedgerName(self, instance):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            AccountLedgerInstances = AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
            for instance in AccountLedgerInstances:
                LedgerName = instance.LedgerName
            return LedgerName
        else:
            return ""

    # def get_GroupUnder(self, instance):
    #     value = self.context.get("value")
    #     CompanyID = self.context.get("CompanyID")
    #     LedgerID = instance.LedgerID
    #     BranchID = instance.BranchID
    #     instance = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID)
    #     AccountGroupUnder = instance.AccountGroupUnder
    #     check = check_exists(AccountGroupUnder,value,CompanyID)
    #     if check:
    #         return True
    #     else:
    #         return False

    def get_GroupUnder(self, instance):
        value = self.context.get("value")
        CompanyID = self.context.get("CompanyID")
        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        instance = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
        AccountGroupUnder = instance.AccountGroupUnder
        # check = check_exists(AccountGroupUnder,value,CompanyID)
        if value == AccountGroupUnder:
            return True
        else:
            return False


class LedgerReportSerializer(serializers.ModelSerializer):

    Debit = serializers.SerializerMethodField()
    Credit = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()

    class Meta:
        model = AccountLedger
        fields = ('LedgerID', 'LedgerName', 'Debit', 'Credit', 'Balance')

    def get_Debit(self, account_ledger):
        CompanyID = self.context.get("CompanyID")
        LedgerID = account_ledger.LedgerID
        Debit = 0

        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID)

            for ledgerpost_instance in ledgerpost_instances:

                Debit += ledgerpost_instance.Debit

            return Debit

    def get_Credit(self, account_ledger):
        CompanyID = self.context.get("CompanyID")
        LedgerID = account_ledger.LedgerID
        Credit = 0

        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID)

            for ledgerpost_instance in ledgerpost_instances:

                Credit += ledgerpost_instance.Credit

            return Credit

    def get_Balance(self, account_ledger):
        CompanyID = self.context.get("CompanyID")
        LedgerID = account_ledger.LedgerID
        Balance = 0

        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID)

            for ledgerpost_instance in ledgerpost_instances:

                Balance += ledgerpost_instance.Balance

            return Balance


class ListSerializerforLedgerReport(serializers.Serializer):

    BranchID = serializers.IntegerField()
    FromDate = serializers.DateField()
    ToDate = serializers.DateField()
    ID = serializers.IntegerField()
    value = serializers.IntegerField()


class ListSerializerforProfitAndLoss(serializers.Serializer):

    BranchID = serializers.IntegerField()
    FromDate = serializers.DateField()
    ToDate = serializers.DateField()


class ProfitAndLossSerializer(serializers.ModelSerializer):

    Balance = serializers.SerializerMethodField()
    # TotalBalance = serializers.SerializerMethodField()
    GroupUnder = serializers.SerializerMethodField()

    class Meta:
        model = AccountLedger
        fields = ('LedgerID', 'LedgerName', 'Balance', 'GroupUnder')

    def get_Balance(self, account_ledger):
        CompanyID = self.context.get("CompanyID")
        LedgerID = account_ledger.LedgerID
        Debit = 0
        Credit = 0

        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID)

            for ledgerpost_instance in ledgerpost_instances:

                Debit += ledgerpost_instance.Debit
                Credit += ledgerpost_instance.Credit

                Balance = Debit - Credit

            return float(Balance)

    def get_GroupUnder(self, instance):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        instance = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
        if instance:
            AccountGroupUnder = instance.AccountGroupUnder
            check = check_groupforProfitandLoss(AccountGroupUnder, CompanyID)
            if check:
                return check
            else:
                return False
        else:
            return ""


class BalanceSheetSerializer(serializers.ModelSerializer):

    Balance = serializers.SerializerMethodField()
    # TotalBalance = serializers.SerializerMethodField()
    GroupUnder = serializers.SerializerMethodField()

    class Meta:
        model = AccountLedger
        fields = ('LedgerID', 'LedgerName', 'Balance', 'GroupUnder')

    def get_Balance(self, account_ledger):
        CompanyID = self.context.get("CompanyID")
        LedgerID = account_ledger.LedgerID
        Debit = 0
        Credit = 0
        Balance = 0
        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID)

            for ledgerpost_instance in ledgerpost_instances:

                Debit += ledgerpost_instance.Debit
                Credit += ledgerpost_instance.Credit

            Balance = Debit - Credit

        return float(Balance)

    def get_GroupUnder(self, instance):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        instance = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
        AccountGroupUnder = instance.AccountGroupUnder

        check = check_groupforBalanceSheet(AccountGroupUnder, CompanyID)
        if check:
            return check
        else:
            return False


class StockReportSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    Cost = serializers.SerializerMethodField()

    class Meta:
        model = StockRate
        fields = ('id', 'StockRateID', 'BranchID', 'BatchID', 'PurchasePrice', 'SalesPrice',
                  'Qty', 'Cost', 'ProductID', 'ProductName', 'WareHouseID', 'Date', 'PriceListID', 'CreatedDate', 'CreatedUserID')

    def get_ProductName(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():
            ProductInstances = Product.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
            for instance in ProductInstances:
                ProductName = instance.ProductName
            return ProductName
        else:
            return ""

    def get_PurchasePrice(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        PurchasePrice = instances.PurchasePrice

        PurchasePrice = round(PurchasePrice, PriceRounding)

        return str(PurchasePrice)

    def get_SalesPrice(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        SalesPrice = instances.SalesPrice

        SalesPrice = round(SalesPrice, PriceRounding)

        return str(SalesPrice)

    def get_Qty(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        Qty = instances.Qty

        print("###################")
        print(Qty)

        Qty = round(Qty, PriceRounding)

        return str(Qty)

    def get_Cost(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        Cost = instances.Cost

        Cost = round(Cost, PriceRounding)

        return str(Cost)
