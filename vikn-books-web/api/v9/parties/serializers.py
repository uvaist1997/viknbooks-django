from main.functions import converted_float
from rest_framework import serializers
from brands.models import PartyBankDetails, UserAdrress, Parties, Route, AccountLedger, PriceCategory, Country, State
import datetime


class PartiesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parties
        fields = ('id', 'BranchID', 'PartyType', 'FirstName', 'LastName', 'PartyName', 'DisplayName', 'Address1', 'Address2', 'City', 'State', 'Attention', 'GST_Treatment', 'State_Code',
                  'Country', 'PostalCode', 'OfficePhone', 'WorkPhone', 'Mobile', 'WebURL', 'Email', 'IsBillwiseApplicable', 'PlaceOfSupply', 'VAT_Treatment',
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
    BankDetails = serializers.SerializerMethodField()
    AccountLedgerpk = serializers.SerializerMethodField()
    PhoneNumber = serializers.SerializerMethodField()

    class Meta:
        model = Parties
        fields = ('id','AccountLedgerpk', 'PartyID', 'BranchID', 'PartyType', 'LedgerID', 'PartyCode', 'FirstName', 'LastName', 'PartyName', 'DisplayName', 'Address1', 'Address2', 'City', 'State', 'Attention', 'CountryName', 'StateName', 'Country_ShippingName', 'State_ShippingName',
                  'Country', 'PostalCode', 'OfficePhone', 'WorkPhone', 'Mobile', 'WebURL', 'Email', 'IsBillwiseApplicable',
                  'CreditPeriod', 'CreditLimit', 'PriceCategoryID', 'CurrencyID', 'InterestOrNot', 'RouteID', 'VATNumber', 'GSTNumber', 'Tax1Number',
                  'Tax2Number', 'Tax3Number', 'PanNumber', 'BankName1', 'AccountName1', 'AccountNo1', 'IBANOrIFSCCode1', 'BankName2', 'AccountName2',
                  'AccountNo2', 'IBANOrIFSCCode2', 'IsActive', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'Action', 'PartyImage', 'OpeningBalance', 'RouteName', 'CrOrDr', 'PriceCategoryName',
                  'Attention_Shipping', 'Address1_Shipping', 'GST_Treatment', 'VAT_Treatment', 'State_Code', 'PlaceOfSupply', 'BankDetails',
                  'Address2_Shipping', 'State_Shipping', 'Country_Shipping', 'City_Shipping', 'PostalCode_Shipping', 'Phone_Shipping', 'CRNo', 'as_on_date',
                  'District', 'AdditionalNo', 'District_shipping', 'AdditionalNo_shipping', 'PhoneNumber')

    def get_PhoneNumber(self, instances):
        PhoneNumber = instances.WorkPhone
        if not PhoneNumber:
            PhoneNumber = ""
        return PhoneNumber

    def get_BankDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        data = []
        if PartyBankDetails.objects.filter(CompanyID=CompanyID, Branch__BranchID=BranchID, Party=instances).exists():
            BankDetails = PartyBankDetails.objects.filter(
                CompanyID=CompanyID, Branch__BranchID=BranchID, Party=instances)
            serialized = PartyBankDetailsSerializer(BankDetails, many=True,)
            data = serialized.data
        return data

    def get_as_on_date(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        print(">>>>>>>>>>>>>>>>>----------???")
        print(LedgerID)
        as_on_date = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            as_on_date = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID).as_on_date

        return str(as_on_date)

    def get_CreatedDate(self, instances):
        CreatedDate = instances.CreatedDate.date()
        return str(CreatedDate)

    def get_OpeningBalance(self, instances):
        OpeningBalance = instances.OpeningBalance
        OpeningBalance = round(OpeningBalance, 2)

        return converted_float(OpeningBalance)

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
        print(LedgerID,"LEDGERIDOPP")
        print(CompanyID,"CompanyID")
        accountLedger_detail = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID)
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

    def get_AccountLedgerpk(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        print(">>>>>>>>>>>>>>>>>----------???")
        print(LedgerID)
        AccountLedgerpk = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            AccountLedgerpk = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID).id

        return str(AccountLedgerpk)

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


class UserAdrressSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAdrress
        fields = '__all__'


class PartyBankDetailsSerializer(serializers.ModelSerializer):
    detailID = serializers.SerializerMethodField()

    class Meta:
        model = PartyBankDetails
        fields = ('id', 'CompanyID', 'Branch', 'Party', 'BankName1',
                  'AccountName1', 'AccountNo1', 'IBANOrIFSCCode1', 'detailID')

    def get_detailID(self, instances):
        detailID = 0
        return detailID


class PartyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parties
        fields = ('PartyImage',)
