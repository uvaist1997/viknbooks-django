from rest_framework import serializers
from brands.models import CompanySettings, FinancialYear, Country, State, BusinessType


class CompanySettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanySettings
        fields = ('id', 'Action', 'CompanyName', 'Address1', 'Address2', 'Address3', 'City', 'State', 'Country', 'PostalCode',
                  'Phone', 'Mobile', 'Website', 'VATNumber', 'GSTNumber', 'Tax1', 'Tax2', 'Tax3', 'CRNumber', "CINNumber", 'Description', "is_vat", "is_gst")


class CompanySettingsInitialSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanySettings
        fields = ('id', 'Action', 'CompanyName', 'State', 'Country',
                  'GSTNumber', 'VATNumber', 'business_type', 'is_vat', 'is_gst')


class FinancialYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = FinancialYear
        fields = ('id', 'FromDate', 'ToDate', 'IsClosed', 'CreatedUserID')


class CompanySettingsRestSerializer(serializers.ModelSerializer):
    Address1 = serializers.SerializerMethodField()
    Address2 = serializers.SerializerMethodField()
    Address3 = serializers.SerializerMethodField()
    City = serializers.SerializerMethodField()
    PostalCode = serializers.SerializerMethodField()
    Phone = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    Email = serializers.SerializerMethodField()
    Website = serializers.SerializerMethodField()
    UpdatedDate = serializers.SerializerMethodField()
    VATNumber = serializers.SerializerMethodField()
    Tax1 = serializers.SerializerMethodField()
    Tax2 = serializers.SerializerMethodField()
    Tax3 = serializers.SerializerMethodField()
    CRNumber = serializers.SerializerMethodField()
    CINNumber = serializers.SerializerMethodField()
    Description = serializers.SerializerMethodField()
    CountryName = serializers.SerializerMethodField()
    StateName = serializers.SerializerMethodField()
    BusinessTypeName = serializers.SerializerMethodField()

    class Meta:
        model = CompanySettings
        fields = (
            'id',
            'Action',
            'CompanyName',
            'CompanyLogo',
            'Address1',
            'Address2',
            'Address3',
            'City',
            'State',
            'Country',
            'PostalCode',
            "business_type",
            'Phone',
            'Mobile',
            'Email',
            'Website',
            'CreatedDate',
            'UpdatedDate',
            'CreatedUserID',
            'VATNumber',
            'GSTNumber',
            'Tax1',
            'Tax2',
            'Tax3',
            "CRNumber",
            "CINNumber",
            "Description",
            "CountryName",
            "StateName",
            "BusinessTypeName",
            "is_vat",
            "is_gst"
        )

    def get_Address1(self, instance):
        Address1 = instance.Address1
        if not Address1:
            Address1 = ""

        return Address1

    def get_Address2(self, instance):
        Address2 = instance.Address2
        if not Address2:
            Address2 = ""

        return Address2

    def get_Address3(self, instance):
        Address3 = instance.Address3
        if not Address3:
            Address3 = ""

        return Address3

    def get_City(self, instance):
        City = instance.City
        if not City:
            City = ""

    def get_Address1(self, instances):
        Address1 = ""
        if instances.Address1:
            Address1 = instances.Address1

        return Address1

    def get_Address2(self, instances):
        Address2 = ""
        if instances.Address2:
            Address2 = instances.Address2

        return Address2

    def get_Address3(self, instances):
        Address3 = ""
        if instances.Address3:
            Address3 = instances.Address3

        return Address3

    def get_City(self, instances):
        City = ""
        if instances.City:
            City = instances.City

        return City

    def get_PostalCode(self, instances):
        PostalCode = ""
        if instances.PostalCode:
            PostalCode = instances.PostalCode

        return PostalCode

    def get_Phone(self, instances):
        Phone = ""
        if instances.Phone:
            Phone = instances.Phone

        return str(Phone)

    def get_Mobile(self, instances):
        Mobile = ""
        if instances.Mobile:
            Mobile = instances.Mobile

        return str(Mobile)

    def get_Website(self, instances):
        Website = ""
        if instances.Website:
            Website = instances.Website

        return Website

    def get_UpdatedDate(self, instances):
        UpdatedDate = ""
        if instances.UpdatedDate:
            UpdatedDate = instances.UpdatedDate

        return UpdatedDate

    def get_VATNumber(self, instances):
        VATNumber = ""
        if instances.VATNumber:
            VATNumber = instances.VATNumber

        return VATNumber

    def get_Tax1(self, instances):
        Tax1 = ""
        if instances.Tax1:
            Tax1 = instances.Tax1

        return Tax1

    def get_Tax2(self, instances):
        Tax2 = ""
        if instances.Tax2:
            Tax2 = instances.Tax2

        return Tax2

    def get_Tax3(self, instances):
        Tax3 = ""
        if instances.Tax3:
            Tax3 = instances.Tax3

        return Tax3

    def get_CRNumber(self, instances):
        CRNumber = ""
        if instances.CRNumber:
            CRNumber = instances.CRNumber

        return CRNumber

    def get_CINNumber(self, instances):
        CINNumber = ""
        if instances.CINNumber:
            CINNumber = instances.CINNumber

        return CINNumber

    def get_Description(self, instances):
        Description = ""
        if instances.Description:
            Description = instances.Description

        return Description

    def get_Email(self, instances):
        Email = ""
        if instances.Email:
            Email = instances.Email

        return Email

    def get_CountryName(self, instances):
        CountryName = ""
        if instances.Country:
            CountryName = instances.Country.Country_Name

        return CountryName

    def get_StateName(self, instances):
        StateName = ""
        if instances.State:
            StateName = instances.State.Name

        return StateName

    def get_BusinessTypeName(self, instances):
        BusinessTypeName = ""
        if instances.business_type:
            BusinessTypeName = instances.business_type.Name

        return BusinessTypeName
