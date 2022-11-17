from rest_framework import serializers
from brands.models import AccountLedger, AccountGroup, LedgerPosting, Parties, Country, State
from django.db.models import Q, Prefetch, Sum


class AccountLedgerSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountLedger
        fields = ('id', 'BranchID', 'LedgerName', 'AccountGroupUnder',
                  'OpeningBalance', 'CrOrDr', 'Notes', 'IsActive', 'IsDefault',)


class AccountLedgerRestSerializer(serializers.ModelSerializer):

    AccountGroupName = serializers.SerializerMethodField()
    OpeningBalance = serializers.SerializerMethodField()
    CrOrDr = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    GSTNumber = serializers.SerializerMethodField()


    class Meta:
        model = AccountLedger
        fields = ('id', 'LedgerID','Mobile','GSTNumber', 'BranchID', 'LedgerName', 'LedgerCode', 'AccountGroupUnder', 'AccountGroupName', 'OpeningBalance',
                  'CrOrDr', 'Notes', 'IsActive', 'IsDefault', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'Action', 'as_on_date')

    def get_OpeningBalance(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        OpeningBalance = instances.OpeningBalance

        OpeningBalance = round(OpeningBalance, PriceRounding)

        return float(OpeningBalance)

    def get_CrOrDr(self, instances):

        CrOrDr = instances.CrOrDr
        if CrOrDr == "Cr":
            CrOrDr = "Credit"
        else:
            CrOrDr = "Debit"

        return str(CrOrDr)

    def get_AccountGroupName(self, instances):

        CompanyID = self.context.get("CompanyID")

        AccountGroupUnder = instances.AccountGroupUnder
        AccountGroups = AccountGroup.objects.get(
            AccountGroupID=AccountGroupUnder, CompanyID=CompanyID)

        AccountGroupName = AccountGroups.AccountGroupName

        return str(AccountGroupName)

    def get_Mobile(self, instances):

        CompanyID = self.context.get("CompanyID")
        Mobile = ""
        if Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            Mobile = Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).Mobile

        return str(Mobile)

    def get_GSTNumber(self, instances):

        CompanyID = self.context.get("CompanyID")
        GSTNumber = ""
        if Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            GSTNumber = Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).GSTNumber

        return str(GSTNumber)


class LedgerReportSerializer(serializers.ModelSerializer):

    Amount = serializers.SerializerMethodField()

    class Meta:
        model = AccountLedger
        fields = ('LedgerID', 'BranchID', 'LedgerName',
                  'LedgerCode', 'Amount',)

    def get_Amount(self, instances):

        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        Debit = 0
        Credit = 0
        Amount = 0

        if LedgerPosting.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(
                LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)

            for ledgerpost_instance in ledgerpost_instances:

                Debit += ledgerpost_instance.Debit
                Credit += ledgerpost_instance.Credit

                Amount = Debit - Credit

            return Amount


class AccountLedgerListSerializer(serializers.ModelSerializer):

    AccountGroupName = serializers.SerializerMethodField()
    OpeningBalance = serializers.SerializerMethodField()
    CustomerBalance = serializers.SerializerMethodField()
    Address = serializers.SerializerMethodField()
    City = serializers.SerializerMethodField()
    State = serializers.SerializerMethodField()
    Country = serializers.SerializerMethodField()
    PostalCode = serializers.SerializerMethodField()
    CustomerLedgerBalance = serializers.SerializerMethodField()
    DisplayName = serializers.SerializerMethodField()
    Attention = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    GSTNumber = serializers.SerializerMethodField()
    Tax_no = serializers.SerializerMethodField()
    CRNo = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    gst_no = serializers.SerializerMethodField()
    vat_no = serializers.SerializerMethodField()


    class Meta:
        model = AccountLedger
        fields = ('id','Tax_no','CRNo','name', 'LedgerID','Mobile','GSTNumber','Balance', 'BranchID', 'LedgerName', 'LedgerCode', 'AccountGroupUnder', 'CustomerLedgerBalance', 'AccountGroupName', 'DisplayName', 'Address', 'City','Attention',
                  'State', 'Country', 'PostalCode','gst_no','vat_no', 'OpeningBalance', 'CustomerBalance', 'CrOrDr', 'Notes', 'IsActive', 'IsDefault', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'Action')

    def get_name(self, instances):
        CompanyID = self.context.get("CompanyID")
        name = instances.LedgerName
        return str(name)

    def get_gst_no(self, instances):
        CompanyID = self.context.get("CompanyID")
        gst_no = ""
        if Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            gst_no = Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).GSTNumber
        return str(gst_no)


    def get_vat_no(self, instances):
        CompanyID = self.context.get("CompanyID")
        vat_no = ""
        if Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            vat_no = Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).VATNumber
        return str(vat_no)

        
    def get_Balance(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        Balance = 0
        if LedgerPosting.objects.filter(LedgerID=instances.LedgerID,BranchID=BranchID, CompanyID=CompanyID).exists():
            ledger_ins = LedgerPosting.objects.filter(LedgerID=instances.LedgerID,BranchID=BranchID,CompanyID=CompanyID)
            ledger_Debit_Sum = ledger_ins.aggregate(Sum('Debit'))
            ledger_Credit_Sum = ledger_ins.aggregate(
                Sum('Credit'))
            ledger_Debit_Sum = ledger_Debit_Sum['Debit__sum']
            ledger_Credit_Sum = ledger_Credit_Sum['Credit__sum']
            Balance = float(ledger_Debit_Sum) - \
                float(ledger_Credit_Sum)

        return str(Balance)


    def get_Tax_no(self, instances):

        CompanyID = self.context.get("CompanyID")
        Tax_no = ""
        if Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            Tax_no = Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).VATNumber

        return str(Tax_no)

    def get_CRNo(self, instances):

        CompanyID = self.context.get("CompanyID")
        CR_no = ""
        if Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            CR_no = Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).CRNo

        return str(CR_no)

    def get_Mobile(self, instances):

        CompanyID = self.context.get("CompanyID")
        Mobile = ""
        if Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            Mobile = Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).Mobile

        return str(Mobile)

    def get_GSTNumber(self, instances):

        CompanyID = self.context.get("CompanyID")
        GSTNumber = ""
        if Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            GSTNumber = Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).GSTNumber

        return str(GSTNumber)


    def get_OpeningBalance(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        OpeningBalance = instances.OpeningBalance

        # OpeningBalance = round(OpeningBalance,PriceRounding)

        return str(OpeningBalance)

    def get_CustomerBalance(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        OpeningBalance = instances.OpeningBalance
        CrOrDr = instances.CrOrDr
        if CrOrDr == 'Cr':
            OpeningBalance = float(OpeningBalance) * -1

        # OpeningBalance = round(OpeningBalance,PriceRounding)

        return str(OpeningBalance)

    def get_CustomerLedgerBalance(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        Balance = 0
        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            ledger_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
            TotalDebit = 0
            TotalCredit = 0

            for i in ledger_instances:
                TotalDebit += float(i.Debit)
                TotalCredit += float(i.Credit)

            Balance = float(TotalDebit) - float(TotalCredit)

        return float(Balance)

    def get_Address(self, instances):
        CompanyID = self.context.get("CompanyID")
        AccountGroupUnder = instances.AccountGroupUnder
        Address = ""
        if AccountGroupUnder == 10 or AccountGroupUnder == 29:
            LedgerID = instances.LedgerID
            if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
                Address = Parties.objects.filter(
                    LedgerID=LedgerID, CompanyID=CompanyID).first().Address1

        return Address


    def get_Attention(self, instances):
        CompanyID = self.context.get("CompanyID")
        AccountGroupUnder = instances.AccountGroupUnder
        Attention = ""
        if AccountGroupUnder == 10 or AccountGroupUnder == 29:
            LedgerID = instances.LedgerID
            if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
                Attention = Parties.objects.filter(
                    LedgerID=LedgerID, CompanyID=CompanyID).first().Attention

        return Attention

    def get_City(self, instances):
        CompanyID = self.context.get("CompanyID")
        AccountGroupUnder = instances.AccountGroupUnder
        City = ""
        if AccountGroupUnder == 10 or AccountGroupUnder == 29:
            LedgerID = instances.LedgerID
            if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
                City = Parties.objects.filter(
                    LedgerID=LedgerID, CompanyID=CompanyID).first().City

        return City

    def get_State(self, instances):
        CompanyID = self.context.get("CompanyID")
        AccountGroupUnder = instances.AccountGroupUnder
        State_Name = ""
        if AccountGroupUnder == 10 or AccountGroupUnder == 29:
            LedgerID = instances.LedgerID
            if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
                if Parties.objects.get(LedgerID=LedgerID, CompanyID=CompanyID).State:
                    pk = Parties.objects.filter(
                        LedgerID=LedgerID, CompanyID=CompanyID).first().State
                    a = Parties.objects.filter(
                        LedgerID=LedgerID, CompanyID=CompanyID)
                    for i in a:
                        print(i.State,"//////////////////////UVAIS///////////////////////////")
                    if State.objects.filter(pk=pk).exists():
                        State_Name = State.objects.get(pk=pk).Name

        return State_Name

    def get_Country(self, instances):
        CompanyID = self.context.get("CompanyID")
        AccountGroupUnder = instances.AccountGroupUnder
        Country_Name = ""
        if AccountGroupUnder == 10 or AccountGroupUnder == 29:
            LedgerID = instances.LedgerID
            if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
                if Parties.objects.get(LedgerID=LedgerID, CompanyID=CompanyID).Country:
                    pk = Parties.objects.filter(
                        LedgerID=LedgerID, CompanyID=CompanyID).first().Country
                    if Country.objects.filter(pk=pk).exists():
                        Country_Name = Country.objects.get(pk=pk).Country_Name

        return Country_Name

    def get_PostalCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        AccountGroupUnder = instances.AccountGroupUnder
        PostalCode = ""
        if AccountGroupUnder == 10 or AccountGroupUnder == 29:
            LedgerID = instances.LedgerID
            if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
                PostalCode = Parties.objects.filter(
                    LedgerID=LedgerID, CompanyID=CompanyID).first().PostalCode

        return PostalCode

    def get_AccountGroupName(self, instances):
        CompanyID = self.context.get("CompanyID")

        AccountGroupUnder = instances.AccountGroupUnder

        AccountGroups = AccountGroup.objects.get(
            AccountGroupID=AccountGroupUnder, CompanyID=CompanyID)

        AccountGroupName = AccountGroups.AccountGroupName

        return str(AccountGroupName)

    def get_DisplayName(self, instances):
        CompanyID = self.context.get("CompanyID")

        BranchID = instances.BranchID
        DisplayName = ""

        groupUnder = [10, 29]

        if (instances.AccountGroupUnder in groupUnder):
            LedgerID = instances.LedgerID

            if Parties.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                party = Parties.objects.get(
                    LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                DisplayName = party.DisplayName
        return DisplayName


class ListSerializerforPayment(serializers.Serializer):

    BranchID = serializers.IntegerField()
    AccountGroupUnder = serializers.IntegerField()
