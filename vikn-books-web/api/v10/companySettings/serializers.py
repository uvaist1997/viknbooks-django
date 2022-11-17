from rest_framework import serializers

from brands.models import (
    Branch,
    BusinessType,
    CompanySettings,
    Country,
    Edition,
    FinancialYear,
    State,
    UserTable,
)
from django.contrib.auth.models import Group, User


class CompanySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySettings
        fields = (
            "id",
            "Action",
            "CompanyName",
            "Address1",
            "Address2",
            "Address3",
            "City",
            "State",
            "Country",
            "PostalCode",
            "Phone",
            "Mobile",
            "Website",
            "VATNumber",
            "GSTNumber",
            "LUTNumber",
            "Tax1",
            "Tax2",
            "Tax3",
            "CRNumber",
            "CINNumber",
            "Description",
            "is_vat",
            "is_gst",
            "RegistrationType",
            "IsBranch",
            "NoOfBrances",
            "EnableZatca"
        )


class CompanySettingsInitialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySettings
        fields = (
            "id",
            "Action",
            "CompanyName",
            "State",
            "Country",
            "GSTNumber",
            "LUTNumber",
            "VATNumber",
            "business_type",
            "is_vat",
            "is_gst",
            "Edition",
            "Email",
            "Phone",
            "Address1",
            "Address2",
            "City",
            "PostalCode",
            "IsBranch",
            "NoOfBrances",
            "EnableZatca",
        )


class FinancialYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialYear
        fields = ("id", "FromDate", "ToDate", "IsClosed")


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
    CountryCode = serializers.SerializerMethodField()
    StateName = serializers.SerializerMethodField()
    BusinessTypeName = serializers.SerializerMethodField()
    BranchName = serializers.SerializerMethodField()
    BranchID = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = CompanySettings
        fields = (
            "id",
            "Action",
            "CompanyName",
            "CompanyLogo",
            "Address1",
            "Address2",
            "Address3",
            "City",
            "State",
            "Country",
            "PostalCode",
            "business_type",
            "Phone",
            "Mobile",
            "Email",
            "Website",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "VATNumber",
            "GSTNumber",
            "LUTNumber",
            "Tax1",
            "Tax2",
            "Tax3",
            "CRNumber",
            "CINNumber",
            "Description",
            "CountryName",
            "CountryCode",
            "StateName",
            "BusinessTypeName",
            "is_vat",
            "is_gst",
            "Edition",
            "RegistrationType",
            "IsBranch",
            "NoOfBrances",
            "BranchName",
            "BranchID",
            "CompanyID",
            "username",
            "EnableZatca"
        )

    def get_username(self, instance):
        CreatedUserID = instance.CreatedUserID
        username = ""
        if CreatedUserID:
            username = User.objects.get(pk=CreatedUserID).username
        return username

    def get_CompanyID(self, instance):
        CompanyID = instance.id
        return CompanyID

    def get_BranchName(self, instance):
        CompanyID = instance.id
        request = self.context.get("request")
        try:
            userId = request.user.id
        except:
            userId = self.context.get("CreatedUserID")
        BranchName = ""

        if UserTable.objects.filter(customer__user=userId, CompanyID=CompanyID, Active=True):
            BranchID = UserTable.objects.get(
                customer__user=userId, CompanyID=CompanyID, Active=True
            ).BranchID
            BranchName = "Primary Branch"
            if Branch.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
                BranchName = Branch.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID
                ).BranchName

        return BranchName

    def get_BranchID(self, instance):
        CompanyID = instance.id
        try:
            request = self.context.get("request")
            userId = request.user.id
        except:
            userId = None
        BranchName = ""
        BranchID = 1
        print(CompanyID,"///////////////////////////",userId)
        if UserTable.objects.filter(customer__user=userId, CompanyID=CompanyID, Active=True):
            BranchID = UserTable.objects.get(
                customer__user=userId, CompanyID=CompanyID, Active=True
            ).BranchID

        return BranchID

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

    def get_CountryCode(self, instances):
        CountryCode = ""
        if instances.Country:
            CountryCode = instances.Country.CountryCode

        return CountryCode

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


class QRCompanySettingsRestSerializer(serializers.ModelSerializer):
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
            "id",
            "Action",
            "CompanyName",
            "CompanyLogo",
            "Address1",
            "Address2",
            "Address3",
            "City",
            "State",
            "Country",
            "PostalCode",
            "business_type",
            "Phone",
            "Mobile",
            "Email",
            "Website",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "VATNumber",
            "GSTNumber",
            "Tax1",
            "Tax2",
            "Tax3",
            "CRNumber",
            "CINNumber",
            "Description",
            "CountryName",
            "StateName",
            "BusinessTypeName",
            "is_vat",
            "is_gst",
            "EnableZatca"
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


class EditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edition
        fields = ("id", "Name")


class CompanySettingsPrintRestSerializer(serializers.ModelSerializer):
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
    GSTNumber = serializers.SerializerMethodField()
    VATNumber = serializers.SerializerMethodField()
    Tax1 = serializers.SerializerMethodField()
    Tax2 = serializers.SerializerMethodField()
    Tax3 = serializers.SerializerMethodField()
    CRNumber = serializers.SerializerMethodField()
    CINNumber = serializers.SerializerMethodField()
    Description = serializers.SerializerMethodField()
    CountryName = serializers.SerializerMethodField()
    CountryCode = serializers.SerializerMethodField()
    StateName = serializers.SerializerMethodField()
    BusinessTypeName = serializers.SerializerMethodField()

    class Meta:
        model = CompanySettings
        fields = (
            "id",
            "Action",
            "CompanyName",
            "CompanyLogo",
            "Address1",
            "Address2",
            "Address3",
            "City",
            "State",
            "Country",
            "PostalCode",
            "business_type",
            "Phone",
            "Mobile",
            "Email",
            "Website",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "VATNumber",
            "GSTNumber",
            "LUTNumber",
            "Tax1",
            "Tax2",
            "Tax3",
            "CRNumber",
            "CINNumber",
            "Description",
            "CountryName",
            "CountryCode",
            "StateName",
            "BusinessTypeName",
            "is_vat",
            "is_gst",
            "Edition",
            "RegistrationType",
            "IsBranch",
            "NoOfBrances",
            "EnableZatca"
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

    def get_GSTNumber(self, instances):
        GSTNumber = ""
        if instances.GSTNumber:
            GSTNumber = instances.GSTNumber
        print(GSTNumber,'GSTNumber')
        return GSTNumber

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

    def get_CountryCode(self, instances):
        CountryCode = ""
        if instances.Country:
            CountryCode = instances.Country.CountryCode

        return CountryCode

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


class CompanyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySettings
        fields = ("CompanyLogo",)
