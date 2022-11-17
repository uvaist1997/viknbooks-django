from rest_framework import serializers
from brands.models import AccountLedger, AccountGroup, LedgerPosting, Parties, Country, State


class AccountLedgerSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountLedger
        fields = ('id','BranchID','LedgerName','AccountGroupUnder','OpeningBalance','CrOrDr','Notes','IsActive','IsDefault',)


class AccountLedgerRestSerializer(serializers.ModelSerializer):

    AccountGroupName = serializers.SerializerMethodField()
    OpeningBalance = serializers.SerializerMethodField()
    CrOrDr = serializers.SerializerMethodField()

    class Meta:
        model = AccountLedger
        fields = ('id','LedgerID','BranchID','LedgerName','LedgerCode','AccountGroupUnder','AccountGroupName','OpeningBalance','CrOrDr','Notes','IsActive','IsDefault','CreatedDate','UpdatedDate','CreatedUserID','Action')


    def get_OpeningBalance(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        OpeningBalance = instances.OpeningBalance

        OpeningBalance = round(OpeningBalance,PriceRounding)

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
        AccountGroups = AccountGroup.objects.get(AccountGroupID=AccountGroupUnder,CompanyID=CompanyID)

        AccountGroupName = AccountGroups.AccountGroupName

        return str(AccountGroupName)



class LedgerReportSerializer(serializers.ModelSerializer):

    Amount = serializers.SerializerMethodField()

    class Meta:
        model = AccountLedger
        fields = ('LedgerID','BranchID','LedgerName','LedgerCode','Amount',)


    def get_Amount(self, instances):

        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        Debit = 0
        Credit = 0
        Amount = 0

        if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID,CompanyID=CompanyID).exists():

            ledgerpost_instances = LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID,CompanyID=CompanyID)


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

    class Meta:
        model = AccountLedger
        fields = ('id','LedgerID','BranchID','LedgerName','LedgerCode','AccountGroupUnder','CustomerLedgerBalance','AccountGroupName','DisplayName','Address','City','State','Country','PostalCode','OpeningBalance','CustomerBalance','CrOrDr','Notes','IsActive','IsDefault','CreatedDate','UpdatedDate','CreatedUserID','Action')


    def get_OpeningBalance(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        OpeningBalance = instances.OpeningBalance

        OpeningBalance = round(OpeningBalance,PriceRounding)

        return str(OpeningBalance)


    def get_CustomerBalance(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        OpeningBalance = instances.OpeningBalance
        CrOrDr = instances.CrOrDr
        if CrOrDr == 'Cr':
            OpeningBalance = float(OpeningBalance) * -1

        OpeningBalance = round(OpeningBalance,PriceRounding)

        return str(OpeningBalance)


    def get_CustomerLedgerBalance(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        Balance = 0
        if LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID).exists():
            ledger_instances = LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID)
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
            if Parties.objects.filter(LedgerID=LedgerID,CompanyID=CompanyID).exists():
                Address = Parties.objects.filter(LedgerID=LedgerID,CompanyID=CompanyID).first().Address1

        return Address


    def get_City(self, instances):
        CompanyID = self.context.get("CompanyID")
        AccountGroupUnder = instances.AccountGroupUnder
        City = ""
        if AccountGroupUnder == 10 or AccountGroupUnder == 29:
            LedgerID = instances.LedgerID
            if Parties.objects.filter(LedgerID=LedgerID,CompanyID=CompanyID).exists():
                City = Parties.objects.filter(LedgerID=LedgerID,CompanyID=CompanyID).first().City

        return City


    def get_State(self, instances):
        CompanyID = self.context.get("CompanyID")
        AccountGroupUnder = instances.AccountGroupUnder
        State_Name = ""
        if AccountGroupUnder == 10 or AccountGroupUnder == 29:
            LedgerID = instances.LedgerID
            if Parties.objects.filter(LedgerID=LedgerID,CompanyID=CompanyID).exists():
                if Parties.objects.get(LedgerID=LedgerID,CompanyID=CompanyID).State:
                    pk = Parties.objects.filter(LedgerID=LedgerID,CompanyID=CompanyID).first().State
                    if State.objects.filter(pk=pk).exists():
                        State_Name = State.objects.get(pk=pk).Name

        return State_Name


    def get_Country(self, instances):
        CompanyID = self.context.get("CompanyID")
        AccountGroupUnder = instances.AccountGroupUnder
        Country_Name = ""
        if AccountGroupUnder == 10 or AccountGroupUnder == 29:
            LedgerID = instances.LedgerID
            if Parties.objects.filter(LedgerID=LedgerID,CompanyID=CompanyID).exists():
                if Parties.objects.get(LedgerID=LedgerID,CompanyID=CompanyID).Country:
                    pk = Parties.objects.filter(LedgerID=LedgerID,CompanyID=CompanyID).first().Country
                    if Country.objects.filter(pk=pk).exists():
                        Country_Name = Country.objects.get(pk=pk).Country_Name

        return Country_Name
        

    def get_PostalCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        AccountGroupUnder = instances.AccountGroupUnder
        PostalCode = ""
        if AccountGroupUnder == 10 or AccountGroupUnder == 29:
            LedgerID = instances.LedgerID
            if Parties.objects.filter(LedgerID=LedgerID,CompanyID=CompanyID).exists():
                PostalCode = Parties.objects.filter(LedgerID=LedgerID,CompanyID=CompanyID).first().PostalCode

        return PostalCode


    def get_AccountGroupName(self, instances):
        CompanyID = self.context.get("CompanyID")

        AccountGroupUnder = instances.AccountGroupUnder

        AccountGroups = AccountGroup.objects.get(AccountGroupID=AccountGroupUnder,CompanyID=CompanyID)

        AccountGroupName = AccountGroups.AccountGroupName

        return str(AccountGroupName)


    def get_DisplayName(self, instances):
        CompanyID = self.context.get("CompanyID")

        BranchID = instances.BranchID
        DisplayName = ""

        groupUnder = [10,29]

        if (instances.AccountGroupUnder in groupUnder):
            LedgerID = instances.LedgerID

            if Parties.objects.filter(LedgerID=LedgerID,BranchID=BranchID,CompanyID=CompanyID).exists():
                party = Parties.objects.get(LedgerID=LedgerID,BranchID=BranchID,CompanyID=CompanyID)
                DisplayName = party.DisplayName
        return DisplayName



class ListSerializerforPayment(serializers.Serializer):

    BranchID = serializers.IntegerField()
    AccountGroupUnder = serializers.IntegerField()

