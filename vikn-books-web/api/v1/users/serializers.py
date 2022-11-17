from rest_framework import serializers
from brands.models import UserTable, UserType, AccountLedger, Warehouse, TransactionTypes, GeneralSettings, CompanySettings, Customer,Country, State, Activity_Log
from users.models import DatabaseStore, CompanyEmployee, CompanyFinancialYear
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator


class UserTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserTable
        fields = ('id','BranchID','UserName','Password','EmployeeID','UserTypeID','IsActive','CreatedUserID','CreatedDate')


class UserTableRestSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    class Meta:
        model = UserTable
        fields = ('id','CreatedUserID','CreatedDate','Action','customer_name')

    def get_customer_name(self, instance):
        CompanyID = self.context.get("CompanyID")
        customer_name = ""
        if UserTable.objects.filter(CompanyID=CompanyID,id=instance.id).exists():
            customer_instance = UserTable.objects.get(CompanyID=CompanyID,id=instance.id)
            customer_name = customer_instance.customer.user.username
        return customer_name
        


class UserTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserType
        fields = ('id','UserTypeName','BranchID','Notes','CreatedUserID','CreatedDate')


class UserTypeRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserType
        fields = ('id','ID','UserTypeName','BranchID','Notes','CreatedUserID','CreatedDate')


class CreateCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = DatabaseStore
        fields = ('CompanyName','Address1','Address2','Address3','city','state','country','postalcode','phone','mobile','email','website','currency','fractionalunit','vatnumber','gstnumber','tax1','tax2','tax3',)

class CreateEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyEmployee
        fields = ('FirstName', 'LastName', 'DesignationID', 'DepartmentID', 'Gender', 'Email',)


class CreateFinancialYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyFinancialYear
        fields = ('FromDate', 'ToDate', 'Notes',)


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
    class Meta:
        model = Customer
        fields = ('DateOfBirth','Country','Phone','State','City','Address','photo')


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
    # StateName = serializers.SerializerMethodField()
    company_type = serializers.SerializerMethodField()

    class Meta:
        model = CompanySettings
        fields = ('CompanyName','id','company_type','ExpiryDate')

    # def get_CountryName(self, instances):
    #     CountryName = instances.Country.Country_Name
    #     return CountryName


    def get_company_type(self, instances):
        company_type = 'personal'
        return company_type.title()


    # def get_StateName(self, instances):
    #     StateName = instances.State.Name
    #     return StateName

class CompaniesSerializer(serializers.ModelSerializer):
    # CountryName = serializers.SerializerMethodField()
    # StateName = serializers.SerializerMethodField()
    CompanyName = serializers.SerializerMethodField()
    company_type = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = UserTable
        fields = ('CompanyName','id','company_type','ExpiryDate')

    # def get_CountryName(self, instances):
    #     CountryName = instances.Country.Country_Name
    #     return CountryName


    def get_CompanyName(self, instances):
        if UserTable.objects.get(pk=instances.pk).CompanyID.CompanyName:
            CompanyName = UserTable.objects.get(pk=instances.pk).CompanyID.CompanyName
            return CompanyName
        else:
            return ""

    def get_id(self, instances):
        if UserTable.objects.get(pk=instances.pk).CompanyID.pk:
            id = UserTable.objects.get(pk=instances.pk).CompanyID.pk
            return str(id)
        else:
            return ""

    def get_company_type(self, instances):
        company_type = 'member'
        return company_type.title()


    def get_ExpiryDate(self, instances):
        if UserTable.objects.get(pk=instances.pk).ExpiryDate:
            ExpiryDate = UserTable.objects.get(pk=instances.pk).ExpiryDate
            return ExpiryDate
        else:
            return ""


    # def get_StateName(self, instances):
    #     StateName = instances.State.Name
    #     return StateName

class AccountLedgerSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountLedger
        fields = ('LedgerName','LedgerID')

class WarehouseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warehouse
        fields = ('WarehouseName','WarehouseID')

class TransactionTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransactionTypes
        fields = ('Name','TransactionTypesID')

class UserTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserType
        fields = ('UserTypeName','id')


class GeneralSettingsSerializer(serializers.Serializer):
    QtyDecimalPoint = serializers.CharField(max_length=100)
    PriceDecimalPoint = serializers.CharField(max_length=100)
    PreDateTransaction = serializers.CharField(max_length=100)
    PostDateTransaction = serializers.CharField(max_length=100)
    RoundingFigure = serializers.CharField(max_length=100)
    VAT = serializers.CharField(max_length=100)
    GST = serializers.CharField(max_length=100)
    Tax1 = serializers.CharField(max_length=100)
    Tax2 = serializers.CharField(max_length=100)
    Tax3 = serializers.CharField(max_length=100)
    Additional_Discount = serializers.CharField(max_length=100)
    Bill_Discount = serializers.CharField(max_length=100)
    # Business_Type = serializers.CharField(max_length=100)
    Negative_Stock_Show = serializers.CharField(max_length=100)
    Increment_Qty_In_POS = serializers.CharField(max_length=100)
    Kitchen_Print = serializers.CharField(max_length=100)
    Order_Print = serializers.CharField(max_length=100)
    Print_After_Save_Active = serializers.CharField(max_length=100)
    Free_Quantity_In_Sales = serializers.CharField(max_length=100)
    Free_Quantity_In_Purchase = serializers.CharField(max_length=100)
    Show_Sales_Type = serializers.CharField(max_length=100)
    Show_Purchase_Type = serializers.CharField(max_length=100)
    Purchase_GST_Type = serializers.CharField(max_length=100)
    Sales_GST_Type = serializers.CharField(max_length=100)
    Sales_VAT_Type = serializers.CharField(max_length=100)
    Purchase_VAT_Type = serializers.CharField(max_length=100)
    MultiUnit = serializers.BooleanField()
    PriceCategory = serializers.BooleanField()
    InclusiveRateSales = serializers.BooleanField()
    InclusiveRatePurchase = serializers.BooleanField()
    SalesPriceUpdate = serializers.BooleanField()
    AllowCashReceiptMoreSaleAmt = serializers.BooleanField()
    AllowAdvanceReceiptinSales = serializers.BooleanField()
    ReferenceBillNo = serializers.BooleanField()
    BlockSalesPrice = serializers.BooleanField()


class GeneralSettingsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralSettings
        fields = ('SettingsType')


# class CustomersSerializer(serializers.ModelSerializer):
#     CustomerName = serializers.SerializerMethodField()

#     class Meta:
#         model = Customer
#         fields = ('CustomerName')

#     def get_CustomerName(self, instances):
#         # customer_instances = instances.Country.Country_Name
#         for customer_instance in instances:
#             CustomerName = customer_instance.user.username
#         # if Country.objects.filter(id=CountryID).exists():
#         #     CustomerName = Country.objects.get(id=CountryID).Country_Name
#         # else:
#         #     CustomerName = ""
#         return CustomerName

class CustomersSerializer(serializers.ModelSerializer):
    CustomerName = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ('id','CustomerName',)

    def get_CustomerName(self, instance):
        CustomerName = instance.user.username
        return CustomerName


class UserTypeSerializer(serializers.ModelSerializer):
    # UserTypeName = serializers.SerializerMethodField()

    class Meta:
        model = UserType
        fields = ('id','UserTypeName',)

    # def get_UserTypeName(self, instance):
    #     UserTypeName = instance.user.username
    #     return UserTypeName

class ActivityLogSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.CompanyName', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Activity_Log
        fields = ('id','company_name','log_type','date','time','username','device_name','location','source','action','message','description',)


class CustomTokenSerializer(serializers.Serializer):
    token = serializers.CharField()