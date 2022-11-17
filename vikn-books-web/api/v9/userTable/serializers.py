from rest_framework import serializers
from brands.models import Branch, UserTable, Customer, UserType, AccountLedger
from rest_framework.fields import CurrentUserDefault


class UserTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserTable
        fields = ('UserType', 'DefaultAccountForUser',
                  'customer', 'ExpiryDate',)


class UserTableSerializerRestSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    user_type_name = serializers.SerializerMethodField()
    cash_account_name = serializers.SerializerMethodField()
    bank_account_name = serializers.SerializerMethodField()
    sales_account_name = serializers.SerializerMethodField()
    sales_return_account_name = serializers.SerializerMethodField()
    purchase_account_name = serializers.SerializerMethodField()
    purchase_return_account_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = UserTable
        fields = ('id', 'CompanyID', 'UserType', 'user_type_name', 'Action', 'DefaultAccountForUser',
                  'CreatedUserID', 'customer', 'customer_name', 'CreatedDate', 'UpdatedDate', 'Cash_Account', 'Bank_Account',
                  'Sales_Account', 'Sales_Return_Account', 'Purchase_Account', 'Purchase_Return_Account', 'JoinedDate', 'ExpiryDate',
                  'LeaveDate', 'cash_account_name', 'bank_account_name', 'sales_account_name', 'sales_return_account_name',
                  'purchase_account_name', 'purchase_return_account_name', 'email', 'BranchID', 'is_web', 'is_mobile', 'is_pos',
                  'show_all_warehouse','DefaultWarehouse')

    def get_email(self, instance):
        CompanyID = self.context.get("CompanyID")
        email = Customer.objects.get(pk=instance.customer.pk).user.email
        return email

    def get_customer_name(self, instance):
        CompanyID = self.context.get("CompanyID")
        customer_name = Customer.objects.get(
            pk=instance.customer.pk).user.username
        return customer_name

    def get_user_type_name(self, instance):
        CompanyID = self.context.get("CompanyID")
        user_type_name = "Owner"
        if instance.UserType:
            user_type_name = UserType.objects.get(
                pk=instance.UserType.pk).UserTypeName
        return user_type_name

    def get_cash_account_name(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = self.context.get("BranchID")
        if AccountLedger.objects.filter(LedgerID=instance.Cash_Account, CompanyID=CompanyID).exists():
            cash_account_name = AccountLedger.objects.get(
                LedgerID=instance.Cash_Account, CompanyID=CompanyID).LedgerName
            return cash_account_name
        else:
            return "Not Found"

    def get_bank_account_name(self, instance):
        CompanyID = self.context.get("CompanyID")
        if AccountLedger.objects.filter(LedgerID=instance.Bank_Account, CompanyID=CompanyID).exists():
            bank_account_name = AccountLedger.objects.get(
                LedgerID=instance.Bank_Account, CompanyID=CompanyID).LedgerName
            return bank_account_name
        else:
            return "Not Found"

    def get_sales_account_name(self, instance):
        CompanyID = self.context.get("CompanyID")
        print(CompanyID)
        print(instance.Sales_Account, 55)
        if AccountLedger.objects.filter(LedgerID=instance.Sales_Account, CompanyID=CompanyID).exists():
            sales_account_name = AccountLedger.objects.get(
                LedgerID=instance.Sales_Account, CompanyID=CompanyID).LedgerName
            return sales_account_name
        else:
            return "Not Found"

    def get_sales_return_account_name(self, instance):
        CompanyID = self.context.get("CompanyID")
        if AccountLedger.objects.filter(LedgerID=instance.Sales_Return_Account, CompanyID=CompanyID).exists():
            sales_return_account_name = AccountLedger.objects.get(
                LedgerID=instance.Sales_Return_Account, CompanyID=CompanyID).LedgerName
            return sales_return_account_name
        else:
            return "Not Found"

    def get_purchase_account_name(self, instance):
        CompanyID = self.context.get("CompanyID")
        if AccountLedger.objects.filter(LedgerID=instance.Purchase_Account, CompanyID=CompanyID).exists():
            purchase_account_name = AccountLedger.objects.get(
                LedgerID=instance.Purchase_Account, CompanyID=CompanyID).LedgerName
            return purchase_account_name
        else:
            return "Not Found"

    def get_purchase_return_account_name(self, instance):
        CompanyID = self.context.get("CompanyID")
        if AccountLedger.objects.filter(LedgerID=instance.Purchase_Return_Account, CompanyID=CompanyID).exists():
            purchase_return_account_name = AccountLedger.objects.get(
                LedgerID=instance.Purchase_Return_Account, CompanyID=CompanyID).LedgerName
            return purchase_return_account_name
        else:
            return "Not Found"


class ListSerializer(serializers.Serializer):

    CompanyID = serializers.CharField()
    CreatedUserID = serializers.CharField()
