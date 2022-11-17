from rest_framework import serializers
from brands.models import Parties, Route, AccountLedger, PriceCategory, Country, State
import datetime


class PartiesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parties
        fields = ('id', 'BranchID', 'PartyType', 'FirstName', 'LastName', 'PartyName', 'DisplayName', 'Address1', 'Address2', 'City', 'State', 'Attention', 'GST_Treatment', 'State_Code',
                  'Country', 'PostalCode', 'OfficePhone', 'WorkPhone', 'Mobile', 'WebURL', 'Email', 'IsBillwiseApplicable',
                  'CreditPeriod', 'CreditLimit', 'PriceCategoryID', 'CurrencyID', 'InterestOrNot', 'RouteID', 'VATNumber', 'GSTNumber', 'Tax1Number',
                  'Tax2Number', 'Tax3Number', 'PanNumber', 'BankName1', 'AccountName1', 'AccountNo1', 'IBANOrIFSCCode1', 'BankName2', 'AccountName2',
                  'AccountNo2', 'IBANOrIFSCCode2', 'IsActive', 'CreatedUserID', 'OpeningBalance', 'Attention_Shipping', 'Address1_Shipping',
                  'Address2_Shipping', 'State_Shipping', 'Country_Shipping', 'City_Shipping', 'PostalCode_Shipping', 'Phone_Shipping', 'CRNo',)


class PartiesRestSerializer(serializers.ModelSerializer):

    RouteName = serializers.SerializerMethodField()
    CrOrDr = serializers.SerializerMethodField()
    PriceCategoryName = serializers.SerializerMethodField()
    OpeningBalance = serializers.SerializerMethodField()
    CountryName = serializers.SerializerMethodField()
    StateName = serializers.SerializerMethodField()
    Country_ShippingName = serializers.SerializerMethodField()
    State_ShippingName = serializers.SerializerMethodField()
    CreatedDate = serializers.SerializerMethodField()
    as_on_date = serializers.SerializerMethodField()

    class Meta:
        model = Parties
        fields = ('id', 'PartyID', 'BranchID', 'PartyType', 'LedgerID', 'PartyCode', 'FirstName', 'LastName', 'PartyName', 'DisplayName', 'Address1', 'Address2', 'City', 'State', 'Attention', 'CountryName', 'StateName', 'Country_ShippingName', 'State_ShippingName',
                  'Country', 'PostalCode', 'OfficePhone', 'WorkPhone', 'Mobile', 'WebURL', 'Email', 'IsBillwiseApplicable',
                  'CreditPeriod', 'CreditLimit', 'PriceCategoryID', 'CurrencyID', 'InterestOrNot', 'RouteID', 'VATNumber', 'GSTNumber', 'Tax1Number',
                  'Tax2Number', 'Tax3Number', 'PanNumber', 'BankName1', 'AccountName1', 'AccountNo1', 'IBANOrIFSCCode1', 'BankName2', 'AccountName2',
                  'AccountNo2', 'IBANOrIFSCCode2', 'IsActive', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'Action', 'PartyImage', 'OpeningBalance', 'RouteName', 'CrOrDr', 'PriceCategoryName',
                  'Attention_Shipping', 'Address1_Shipping', 'GST_Treatment', 'State_Code',
                  'Address2_Shipping', 'State_Shipping', 'Country_Shipping', 'City_Shipping', 'PostalCode_Shipping', 'Phone_Shipping', 'CRNo', 'as_on_date')

    def get_as_on_date(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        as_on_date = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            as_on_date = AccountLedger.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).as_on_date

        return str(as_on_date)

    def get_CreatedDate(self, instances):
        CreatedDate = instances.CreatedDate.date()
        return str(CreatedDate)

    def get_OpeningBalance(self, instances):
        OpeningBalance = instances.OpeningBalance
        OpeningBalance = round(OpeningBalance, 2)

        return float(OpeningBalance)

    def get_CountryName(self, instances):
        CountryID = instances.Country
        CountryName = ""
        if CountryID:
            if Country.objects.filter(id=CountryID).exists():
                CountryName = Country.objects.get(id=CountryID).Country_Name
            else:
                CountryName = ""
        return CountryName

    def get_StateName(self, instances):
        StateID = instances.State
        StateName = ""
        if StateID:
            if State.objects.filter(id=StateID).exists():
                StateName = State.objects.get(id=StateID).Name
            else:
                StateName = ""
        return StateName

    def get_Country_ShippingName(self, instances):
        Country_Shipping = instances.Country_Shipping
        Country_ShippingName = ""
        if Country_Shipping:
            if Country.objects.filter(id=Country_Shipping).exists():
                Country_ShippingName = Country.objects.get(
                    id=Country_Shipping).Country_Name
            else:
                Country_ShippingName = ""
        return Country_ShippingName

    def get_State_ShippingName(self, instances):
        State_Shipping = instances.State_Shipping
        State_ShippingName = ""
        if State_Shipping:
            if State.objects.filter(id=State_Shipping).exists():
                State_ShippingName = State.objects.get(id=State_Shipping).Name
            else:
                State_ShippingName = ""
        return State_ShippingName

    def get_RouteName(self, instances):
        CompanyID = self.context.get("CompanyID")
        RouteID = instances.RouteID
        BranchID = instances.BranchID
        if Route.objects.filter(CompanyID=CompanyID, RouteID=RouteID, BranchID=BranchID).exists():
            route_detail = Route.objects.get(
                CompanyID=CompanyID, RouteID=RouteID, BranchID=BranchID)
            RouteName = route_detail.RouteName
        else:
            RouteName = ""
        return RouteName

    def get_CrOrDr(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID

        accountLedger_detail = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
        CrOrDr = accountLedger_detail.CrOrDr
        if CrOrDr == "Dr":
            CrOrDr = "0"
        else:
            CrOrDr = "1"
        # serialized = AccountLedgerDetailSerializer(accountLedger_details,many=True,)

        return CrOrDr

    def get_PriceCategoryName(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        PriceCategoryID = instances.PriceCategoryID
        if PriceCategory.objects.filter(CompanyID=CompanyID, PriceCategoryID=PriceCategoryID, BranchID=BranchID).exists():
            priceCategory_detail = PriceCategory.objects.get(
                CompanyID=CompanyID, PriceCategoryID=PriceCategoryID, BranchID=BranchID)
            PriceCategoryName = priceCategory_detail.PriceCategoryName
        else:
            PriceCategoryName = ""
        return PriceCategoryName


class RouteNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ('RouteName',)


class AccountLedgerDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountLedger
        fields = ('CrOrDr',)


class PriceCategoryDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceCategory
        fields = ('PriceCategoryName',)


class PartyListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()
    PartyType = serializers.CharField()
