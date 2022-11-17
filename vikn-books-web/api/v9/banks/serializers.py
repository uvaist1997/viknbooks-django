from rest_framework import serializers

from brands.models import AccountLedger, Bank, Country, State


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = (
            "id",
            "BranchID",
            "LedgerCode",
            "Name",
            "LedgerName",
            "AccountNumber",
            "CrOrDr",
            "BranchCode",
            "IFSCCode",
            "MICRCode",
            "Status",
            "OpeningBalance",
            "Address",
            "City",
            "State",
            "Country",
            "PostalCode",
            "Phone",
            "Mobile",
            "Email",
            "CreatedUserID",
            "Notes",
        )


class BankRestSerializer(serializers.ModelSerializer):

    OpeningBalance = serializers.SerializerMethodField()
    CrOrDr = serializers.SerializerMethodField()
    BranchCode = serializers.SerializerMethodField()
    IFSCCode = serializers.SerializerMethodField()
    Country_name = serializers.SerializerMethodField()
    State_name = serializers.SerializerMethodField()
    as_on_date = serializers.SerializerMethodField()
    LedgerID = serializers.SerializerMethodField()

    class Meta:
        model = Bank
        fields = (
            "id",
            "BankID",
            "BranchID",
            "LedgerCode",
            "Name",
            "LedgerName",
            "AccountNumber",
            "CrOrDr",
            "BranchCode",
            "IFSCCode",
            "MICRCode",
            "Status",
            "OpeningBalance",
            "Address",
            "City",
            "State",
            "Country",
            "Country_name",
            "State_name",
            "PostalCode",
            "Phone",
            "Mobile",
            "Email",
            "CreatedUserID",
            "CreatedDate",
            "UpdatedDate",
            "Notes",
            "Action",
            "as_on_date",
            "LedgerID",
        )

    def get_as_on_date(self, instances):
        CompanyID = instances.CompanyID
        BranchID = instances.BranchID
        LedgerCode = instances.LedgerCode
        LedgerName = instances.LedgerName
        as_on_date = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerName=LedgerName
        ).exists():
            as_on_date = AccountLedger.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, LedgerName=LedgerName
            ).as_on_date
        return as_on_date

    def get_OpeningBalance(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        OpeningBalance = instances.OpeningBalance
        OpeningBalance = round(OpeningBalance, PriceRounding)

        return str(OpeningBalance)

    def get_Country_name(self, instances):
        CountryID = instances.Country
        CountryName = ""
        if CountryID:
            if Country.objects.filter(id=CountryID).exists():
                CountryName = Country.objects.get(id=CountryID).Country_Name
            else:
                CountryName = ""
        return CountryName

    def get_State_name(self, instances):
        StateID = instances.State
        StateName = ""
        if StateID:
            if State.objects.filter(id=StateID).exists():
                StateName = State.objects.get(id=StateID).Name
            else:
                StateName = ""
        return StateName

    def get_CrOrDr(self, instances):
        CrOrDr = instances.CrOrDr
        if CrOrDr == "Cr":
            CrOrDr = "Credit"
        else:
            CrOrDr = "Debit"
        return str(CrOrDr)

    def get_BranchCode(self, instances):
        BranchCode = instances.BranchCode
        if BranchCode == None:
            BranchCode = "-"
        return str(BranchCode)

    def get_IFSCCode(self, instances):
        IFSCCode = instances.IFSCCode
        if IFSCCode == None:
            IFSCCode = "-"
        return str(IFSCCode)

    def get_LedgerID(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerName = instances.LedgerName
        LedgerID = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerName=LedgerName
        ).exists():
            LedgerID = (
                AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName=LedgerName)
                .first()
                .LedgerID
            )
        return LedgerID
