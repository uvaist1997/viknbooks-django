from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from brands.models import (
    AccountLedger,
    Activity_Log,
    CompanySettings,
    Country,
    Customer,
    GeneralSettings,
    SoftwareVersion,
    State,
    TransactionTypes,
    UserTable,
    UserType,
    Warehouse,
)
from main.functions import get_companyDataPerc
from users.models import CompanyEmployee, CompanyFinancialYear, DatabaseStore


class UserTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTable
        fields = (
            "id",
            "BranchID",
            "UserName",
            "Password",
            "EmployeeID",
            "UserTypeID",
            "IsActive",
            "CreatedUserID",
            "CreatedDate",
        )


class UserTableRestSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    UserID = serializers.SerializerMethodField()

    class Meta:
        model = UserTable
        fields = (
            "id",
            "CreatedUserID",
            "CreatedDate",
            "Action",
            "customer_name",
            "name",
            "UserID",
        )

    def get_UserID(self, instance):
        CompanyID = self.context.get("CompanyID")
        UserID = ""
        if UserTable.objects.filter(CompanyID=CompanyID, id=instance.id).exists():
            customer_instance = UserTable.objects.get(
                CompanyID=CompanyID, id=instance.id
            )
            UserID = customer_instance.customer.user.id
        return UserID

    def get_customer_name(self, instance):
        CompanyID = self.context.get("CompanyID")
        customer_name = ""
        if UserTable.objects.filter(CompanyID=CompanyID, id=instance.id).exists():
            customer_instance = UserTable.objects.get(
                CompanyID=CompanyID, id=instance.id
            )
            customer_name = customer_instance.customer.user.username
        return customer_name

    def get_name(self, instance):
        CompanyID = self.context.get("CompanyID")
        customer_name = ""
        if UserTable.objects.filter(CompanyID=CompanyID, id=instance.id).exists():
            customer_instance = UserTable.objects.get(
                CompanyID=CompanyID, id=instance.id
            )
            customer_name = customer_instance.customer.user.username
        return customer_name


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = (
            "id",
            "UserTypeName",
            "BranchID",
            "Notes",
            "CreatedUserID",
            "CreatedDate",
        )


class UserTypeRestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = (
            "id",
            "ID",
            "UserTypeName",
            "BranchID",
            "Notes",
            "CreatedUserID",
            "CreatedDate",
        )


class CreateCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseStore
        fields = (
            "CompanyName",
            "Address1",
            "Address2",
            "Address3",
            "city",
            "state",
            "country",
            "postalcode",
            "phone",
            "mobile",
            "email",
            "website",
            "currency",
            "fractionalunit",
            "vatnumber",
            "gstnumber",
            "tax1",
            "tax2",
            "tax3",
        )


class CreateEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyEmployee
        fields = (
            "FirstName",
            "LastName",
            "DesignationID",
            "DepartmentID",
            "Gender",
            "Email",
        )


class CreateFinancialYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyFinancialYear
        fields = (
            "FromDate",
            "ToDate",
            "Notes",
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=100)


class SignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    username = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=50)
    password1 = serializers.CharField(max_length=100)
    password2 = serializers.CharField(max_length=100)


class UserViewSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    username = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=50)


class UpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    # DateOfBirth = serializers.CharField(max_length=50)
    # Country = serializers.CharField(max_length=50)
    # Phone = serializers.CharField(max_length=50)
    # State = serializers.CharField(max_length=50)
    # City = serializers.CharField(max_length=50)
    # Address = serializers.CharField(max_length=50)


class CustomerUserViewSerializer(serializers.ModelSerializer):
    CountryName = serializers.SerializerMethodField()
    StateName = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = (
            "DateOfBirth",
            "Country",
            "Phone",
            "State",
            "City",
            "Address",
            "photo",
            "CountryName",
            "StateName",
        )

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


class UserAccountsSerializer(serializers.Serializer):
    Cash_Account = serializers.CharField(max_length=100)
    Bank_Account = serializers.CharField(max_length=100)
    warehouse = serializers.CharField(max_length=100)
    Sales_Account = serializers.CharField(max_length=100)
    Sales_Return_Account = serializers.CharField(max_length=100)
    Purchase_Account = serializers.CharField(max_length=100)
    Purchase_Return_Account = serializers.CharField(max_length=100)
    Sales_GST_Type = serializers.CharField(max_length=100)
    Purchase_GST_Type = serializers.CharField(max_length=100)
    VAT_Type = serializers.CharField(max_length=100)
    ExpiryDate = serializers.CharField(max_length=100)
    UserTypeID = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=50)
    username = serializers.CharField(max_length=100)
    password1 = serializers.CharField(max_length=100)
    password2 = serializers.CharField(max_length=100)
    CreatedUserID = serializers.CharField(max_length=100)


class MyCompaniesSerializer(serializers.ModelSerializer):
    # CountryName = serializers.SerializerMethodField()
    StateName = serializers.SerializerMethodField()
    company_type = serializers.SerializerMethodField()
    CompanyDataPerc = serializers.SerializerMethodField()
    IsPosUser = serializers.SerializerMethodField()

    class Meta:
        model = CompanySettings
        fields = (
            "CompanyName",
            "id",
            "company_type",
            "ExpiryDate",
            "Permission",
            "CompanyLogo",
            "Edition",
            "IsPosUser",
            "StateName",
            "Email",
            "CompanyDataPerc"
        )
        
    def get_IsPosUser(self, instance):
        IsPosUser = instance.IsPosUser
        if not IsPosUser:
            IsPosUser = False
        return IsPosUser

    def get_CompanyDataPerc(self, instance):
        CompanyDataPerc = get_companyDataPerc(instance)
        return CompanyDataPerc

    def get_company_type(self, instances):
        company_type = "personal"
        return company_type.title()

    def get_StateName(self, instances):
        StateName = instances.State.Name
        return StateName


class CompaniesSerializer(serializers.ModelSerializer):
    # CountryName = serializers.SerializerMethodField()
    # StateName = serializers.SerializerMethodField()
    Permission = serializers.SerializerMethodField()
    CompanyName = serializers.SerializerMethodField()
    company_type = serializers.SerializerMethodField()
    CompanyLogo = serializers.SerializerMethodField()
    Edition = serializers.SerializerMethodField()
    IsPosUser = serializers.SerializerMethodField()
    StateName = serializers.SerializerMethodField()
    Email = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyDataPerc = serializers.SerializerMethodField()

    class Meta:
        model = UserTable
        fields = (
            "CompanyName",
            "id",
            "company_type",
            "ExpiryDate",
            "Permission",
            "CompanyLogo",
            "Edition",
            "IsPosUser",
            "StateName",
            "Email",
            "CompanyDataPerc"
        )

    def get_CompanyDataPerc(self, instance):
        CompanyDataPerc = get_companyDataPerc(instance.CompanyID)
        return CompanyDataPerc
    
    
    def get_Edition(self, instances):
        if UserTable.objects.get(pk=instances.pk, Active=True).CompanyID.Edition:
            Edition = UserTable.objects.get(
                pk=instances.pk, Active=True).CompanyID.Edition
            return Edition
        else:
            return ""

    def get_IsPosUser(self, instances):
        if UserTable.objects.get(pk=instances.pk, Active=True).CompanyID.IsPosUser:
            IsPosUser = UserTable.objects.get(
                pk=instances.pk, Active=True).CompanyID.IsPosUser
            return IsPosUser
        else:
            return False

    def get_CompanyName(self, instances):
        if UserTable.objects.get(pk=instances.pk, Active=True).CompanyID.CompanyName:
            CompanyName = UserTable.objects.get(
                pk=instances.pk, Active=True).CompanyID.CompanyName
            return CompanyName
        else:
            return ""

    def get_Permission(self, instances):
        if UserTable.objects.get(pk=instances.pk, Active=True).CompanyID.Permission:
            Permission = UserTable.objects.get(
                pk=instances.pk, Active=True).CompanyID.Permission
            return Permission
        else:
            return ""

    def get_CompanyLogo(self, instances):
        if UserTable.objects.get(pk=instances.pk, Active=True).CompanyID.CompanyLogo:
            CompanyLogo = UserTable.objects.get(
                pk=instances.pk, Active=True).CompanyID.CompanyLogo
            return CompanyLogo.url
        else:
            return ""

    def get_id(self, instances):
        if UserTable.objects.get(pk=instances.pk, Active=True).CompanyID.pk:
            id = UserTable.objects.get(
                pk=instances.pk, Active=True).CompanyID.pk
            return str(id)
        else:
            return ""

    def get_company_type(self, instances):
        company_type = "member"
        return company_type.title()

    def get_ExpiryDate(self, instances):
        if UserTable.objects.get(pk=instances.pk, Active=True).ExpiryDate:
            ExpiryDate = UserTable.objects.get(
                pk=instances.pk, Active=True).ExpiryDate
            return ExpiryDate
        else:
            return ""

    def get_StateName(self, instances):
        if UserTable.objects.get(pk=instances.pk, Active=True).CompanyID.State.Name:
            StateName = UserTable.objects.get(
                pk=instances.pk, Active=True).CompanyID.State.Name
            return StateName
        else:
            return ""

    def get_Email(self, instances):
        if UserTable.objects.get(pk=instances.pk, Active=True).CompanyID.Email:
            Email = UserTable.objects.get(
                pk=instances.pk, Active=True).CompanyID.Email
            return Email
        else:
            return ""


class AccountLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountLedger
        fields = ("LedgerName", "LedgerID")


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ("WarehouseName", "WarehouseID")


class TransactionTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionTypes
        fields = ("Name", "TransactionTypesID")


class UserTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ("UserTypeName", "id", "ID")


class GeneralSettingsSerializer(serializers.Serializer):
    QtyDecimalPoint = serializers.CharField(max_length=100)
    PriceDecimalPoint = serializers.CharField(max_length=100)
    # loyalty_PointValue = serializers.CharField(max_length=100)
    PreDateTransaction = serializers.CharField(max_length=100)
    PostDateTransaction = serializers.CharField(max_length=100)
    RoundingFigure = serializers.CharField(max_length=100)
    VAT = serializers.BooleanField()
    GST = serializers.BooleanField()
    KFC = serializers.BooleanField()
    Tax1 = serializers.BooleanField()
    Tax2 = serializers.BooleanField()
    Tax3 = serializers.BooleanField()
    Additional_Discount = serializers.BooleanField()
    Bill_Discount = serializers.BooleanField()
    # Business_Type = serializers.CharField(max_length=100)
    Negative_Stock_Show = serializers.BooleanField()
    Increment_Qty_In_POS = serializers.BooleanField()
    Kitchen_Print = serializers.BooleanField()
    Order_Print = serializers.BooleanField()
    Print_After_Save_Active = serializers.BooleanField()
    # Free_Quantity_In_Sales = serializers.BooleanField()
    # Free_Quantity_In_Purchase = serializers.BooleanField()
    Show_Sales_Type = serializers.BooleanField()
    Show_Purchase_Type = serializers.BooleanField()
    Purchase_GST_Type = serializers.CharField(max_length=100)
    Sales_GST_Type = serializers.CharField(max_length=100)
    Sales_VAT_Type = serializers.CharField(max_length=100)
    Purchase_VAT_Type = serializers.CharField(max_length=100)
    MultiUnit = serializers.BooleanField()
    Loyalty_Point_Expire = serializers.BooleanField()
    is_Loyalty_SalesReturn_MinimumSalePrice = serializers.BooleanField()
    PriceCategory = serializers.BooleanField()
    InclusiveRateSales = serializers.BooleanField()
    InclusiveRatePurchase = serializers.BooleanField()
    InclusiveRateWorkOrder = serializers.BooleanField()
    SalesPriceUpdate = serializers.BooleanField()
    PurchasePriceUpdate = serializers.BooleanField()
    AllowCashReceiptMoreSaleAmt = serializers.BooleanField()
    AllowCashReceiptMorePurchaseAmt = serializers.BooleanField()
    AllowAdvanceReceiptinSales = serializers.BooleanField()
    AllowAdvanceReceiptinPurchase = serializers.BooleanField()
    AllowQtyDividerinSales = serializers.BooleanField()
    ReferenceBillNo = serializers.BooleanField()
    BlockSalesPrice = serializers.BooleanField()
    # ShowProfitinSalesRegisterReport = serializers.BooleanField()
    # ShowCustomerLastSalesPriceinSales = serializers.BooleanField()
    # ShowSupplierLastPurchasePriceinPurchase = serializers.BooleanField()
    VoucherNoAutoGenerate = serializers.BooleanField()
    ShowSettingsinSales = serializers.BooleanField()
    blockSaleByBillDisct = serializers.BooleanField()
    EnableTransilationInProduct = serializers.BooleanField()
    EnableProductBatchWise = serializers.BooleanField()
    AllowUpdateBatchPriceInSales = serializers.BooleanField()
    ShowPositiveStockInSales = serializers.BooleanField()
    ShowNegativeBatchInSales = serializers.BooleanField()
    AllowNegativeStockSales = serializers.BooleanField()
    CreateBatchForWorkOrder = serializers.BooleanField()
    ShowYearMonthCalanderInWorkOrder = serializers.BooleanField()
    ShowDiscountInSales = serializers.BooleanField()
    ShowDiscountInPurchase = serializers.BooleanField()
    ShowManDateAndExpDatePurchase = serializers.BooleanField()
    ShowSupplierInSales = serializers.BooleanField()
    ShowDueBalanceInSales = serializers.BooleanField()
    ShowDueBalanceInPurchase = serializers.BooleanField()
    ShowEmployeesInSales = serializers.BooleanField()
    Free_Quantity_In_Sales = serializers.BooleanField()
    Free_Quantity_In_Purchase = serializers.BooleanField()
    ShowCustomerInPurchase = serializers.BooleanField()
    EnableCardNetWork = serializers.BooleanField()
    EnableCardDetails = serializers.BooleanField()
    ShowSalesPriceInPurchase = serializers.BooleanField()
    ShowDiscountInPayments = serializers.BooleanField()
    ShowDiscountInReceipts = serializers.BooleanField()
    EnableLoyaltySettings = serializers.BooleanField()
    ShowSettingsinPurchase = serializers.BooleanField()
    EnableSerialNoInSales = serializers.BooleanField()
    AllowExtraSerielNos = serializers.BooleanField()
    EnableItemCodeNoInSales = serializers.BooleanField()
    # EnableCreditLimit = serializers.BooleanField()
    # EnableFaeraSettings = serializers.BooleanField()
    ShowDescriptionInSales = serializers.BooleanField()
    ShowWarrantyPeriodInProduct = serializers.BooleanField()
    EnableSalesManInSales = serializers.BooleanField()
    BlockTransactionsByDate = serializers.BooleanField()
    BatchCriteria = serializers.CharField(max_length=100)
    RoundOffPurchase = serializers.CharField(max_length=100)
    RoundOffSales = serializers.CharField(max_length=100)
    EnableShippingCharge = serializers.BooleanField()
    EnableVoucherNoUserWise = serializers.BooleanField()
    # ShowInactiveUsers = serializers.BooleanField()
    # CustomerBasedPrint = serializers.BooleanField()
    # ShowAllProductsInWorkOrder = serializers.BooleanField()
    # EnableDuplicateProductName = serializers.BooleanField()
    # show_productcode_InsearchSale = serializers.BooleanField()
    # show_stock_InsearchSale = serializers.BooleanField()
    # show_purchasePrice_InsearchSale = serializers.BooleanField()
    # show_productcode_InsearchPurchase = serializers.BooleanField()
    # show_stock_InsearchPurchase = serializers.BooleanField()
    # show_salesPrice_InsearchPurchase = serializers.BooleanField()
    # EnableWarehouse = serializers.BooleanField()
    # EnableCreditPeriod = serializers.BooleanField()
    EnableBillwise = serializers.BooleanField()
    # AllowNegativeStockInStockTransfer = serializers.BooleanField()
    # AutoIncrimentQty = serializers.BooleanField()
    # BlockSalesBelowPurchase = serializers.BooleanField()
    # ShowMaximumStockAlert = serializers.BooleanField()


class GeneralSettingsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralSettings
        fields = "SettingsType"


class CustomersSerializer(serializers.ModelSerializer):
    CustomerName = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = (
            "id",
            "CustomerName",
        )

    def get_CustomerName(self, instance):
        CustomerName = instance.user.username
        return CustomerName


class UserTypeSerializer(serializers.ModelSerializer):
    # UserTypeName = serializers.SerializerMethodField()

    class Meta:
        model = UserType
        fields = (
            "id",
            "UserTypeName",
        )


class ActivityLogSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.CompanyName", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Activity_Log
        fields = (
            "id",
            "company_name",
            "log_type",
            "date",
            "time",
            "username",
            "device_name",
            "location",
            "source",
            "action",
            "message",
            "description",
            "is_solved",
        )


class CustomTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class SoftwareVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareVersion
        fields = ("CurrentVersion", "MinimumVersion")


class UserListSerializer(serializers.ModelSerializer):
    Phone = serializers.SerializerMethodField()
    Country = serializers.SerializerMethodField()
    State = serializers.SerializerMethodField()
    No_of_organizations = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()
    Gender = serializers.SerializerMethodField()
    Language = serializers.SerializerMethodField()
    TimeZone = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "email",
            "Phone",
            "Country",
            "State",
            "No_of_organizations",
            "date_joined",
            "Gender",
            "Language",
            "TimeZone",
            "photo",
        )

    def get_photo(self, instance):
        user_id = instance.id
        CompanyID = self.context.get("CompanyID")
        request = self.context.get("request")
        photo = ""
        if Customer.objects.filter(user__pk=user_id).exists():
            instance = Customer.objects.get(user__pk=user_id)
            serialized = ImageSerializer(
                instance, context={"CompanyID": CompanyID, "request": request}
            )
        return serialized.data.get("photo")

    def get_Phone(self, instance):
        user_id = instance.id
        Phone = ""
        if Customer.objects.filter(user__pk=user_id).exists():
            instance = Customer.objects.get(user__pk=user_id)
            Phone = instance.Phone
        return Phone

    def get_Country(self, instance):
        user_id = instance.id
        country = ""
        if Customer.objects.filter(user__pk=user_id).exists():
            instance = Customer.objects.get(user__pk=user_id)
            if instance.Country:
                country = instance.Country.Country_Name
        return country

    def get_State(self, instance):
        user_id = instance.id
        state = ""
        if Customer.objects.filter(user__pk=user_id).exists():
            instance = Customer.objects.get(user__pk=user_id)
            if instance.State:
                state = instance.State.Name
        return state

    def get_Gender(self, instance):
        user_id = instance.id
        Gender = "None"
        if Customer.objects.filter(user__pk=user_id).exists():
            instance = Customer.objects.get(user__pk=user_id)
            if instance.Gender:
                Gender = instance.Gender
        return Gender

    def get_Language(self, instance):
        user_id = instance.id
        Language = "english"
        if Customer.objects.filter(user__pk=user_id).exists():
            instance = Customer.objects.get(user__pk=user_id)
            if instance.Language:
                Language = instance.Language
        return Language

    def get_TimeZone(self, instance):
        user_id = instance.id
        TimeZone = "Asia/Calcutta"
        if Customer.objects.filter(user__pk=user_id).exists():
            instance = Customer.objects.get(user__pk=user_id)
            if instance.TimeZone:
                TimeZone = instance.TimeZone
        return TimeZone

    def get_No_of_organizations(self, instance):
        user_id = instance.id
        No_of_organizations = 0
        if CompanySettings.objects.filter(owner__pk=user_id).exists():
            instance = CompanySettings.objects.filter(owner__pk=user_id)
            No_of_organizations = instance.count()
        return No_of_organizations

    def get_date_joined(self, instance):
        date_joined = instance.date_joined.date()
        return date_joined


class UsernameEmailSerializer(serializers.Serializer):
    data = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField()
    new_password2 = serializers.CharField()


class ValidateSerializer(serializers.Serializer):
    email = serializers.EmailField()


# added by suhaib
class EditProfile(serializers.Serializer):
    Name = serializers.CharField(max_length=50)
    Gender = serializers.CharField(max_length=50)
    Country = serializers.CharField(max_length=50)
    State = serializers.CharField(max_length=50)
    Language = serializers.CharField(max_length=50)
    TimeZone = serializers.CharField(max_length=100)


class EditAccountInfo(serializers.Serializer):
    email = serializers.CharField(max_length=50)
    phone = serializers.CharField(max_length=50)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=50)
    new_password = serializers.CharField(max_length=50)
    confirm_password = serializers.CharField(max_length=50)


class UsernameSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)


class UserCredentialSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)


# ends here


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("photo",)
