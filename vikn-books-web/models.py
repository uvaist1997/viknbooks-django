from __future__ import unicode_literals
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from versatileimagefield.fields import VersatileImageField
from django.utils.encoding import smart_text
from main.models import BaseModel
from django.conf import settings
import uuid
from PIL import Image, ImageDraw
from io import BytesIO
import qrcode
from django.core.files.base import File
from ckeditor.fields import RichTextField


User = settings.AUTH_USER_MODEL

TAX_TYPE_CHOICES = (
    ('vat', 'VAT'),
    ('gst', 'GST'),
)

STATE_TYPE_CHOICES = (
    ('state', 'State'),
    ('union_territory', 'Union Territory'),
)


class UserType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.BigIntegerField()
    UserTypeName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    IsActive = models.BooleanField(default=False)
    BranchID = models.BigIntegerField(default=1, blank=True, null=True)

    class Meta:
        db_table = 'users_userType'
        verbose_name = _('userType')
        verbose_name_plural = _('usersType')
        unique_together = (('CompanyID', 'ID',),)
        ordering = ('-CreatedDate', 'ID')

    def __unicode__(self):
        return str(self.ID)


class UserTypeLog(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    UserTypeName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    IsActive = models.BooleanField(default=False)
    BranchID = models.BigIntegerField(default=1, blank=True, null=True)

    class Meta:
        db_table = 'users_userTypeLog'
        verbose_name = _('userTypeLog')
        verbose_name_plural = _('usersTypeLog')
        unique_together = (('CompanyID', 'ID',),)
        ordering = ('-CreatedDate', 'ID')

    def __unicode__(self):
        return str(self.ID)


class UserTable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    UserType = models.ForeignKey(
        "brands.UserType", on_delete=models.CASCADE, blank=True, null=True)
    DefaultAccountForUser = models.BooleanField(
        default=False, blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    customer = models.ForeignKey(
        "brands.Customer", on_delete=models.CASCADE, blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Cash_Account = models.BigIntegerField(blank=True, null=True, default=None)
    Bank_Account = models.BigIntegerField(blank=True, null=True, default=None)
    Sales_Account = models.BigIntegerField(blank=True, null=True, default=None)
    Sales_Return_Account = models.BigIntegerField(
        blank=True, null=True, default=None)
    Purchase_Account = models.BigIntegerField(
        blank=True, null=True, default=None)
    Purchase_Return_Account = models.BigIntegerField(
        blank=True, null=True, default=None)
    JoinedDate = models.DateField(blank=True, null=True)
    ExpiryDate = models.DateField(blank=True, null=True)
    LeaveDate = models.DateField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    is_owner = models.BooleanField(default=False, blank=True, null=True)
    is_web = models.BooleanField(default=True, blank=True, null=True)
    is_mobile = models.BooleanField(default=True, blank=True, null=True)
    is_pos = models.BooleanField(default=False, blank=True, null=True)
    BranchID = models.BigIntegerField(default=1, blank=True, null=True)
    # ID = models.BigIntegerField()
    # BranchID = models.BigIntegerField()
    # UserName  = models.CharField(max_length=128)
    # Password  = models.CharField(max_length=128)
    # EmployeeID = models.BigIntegerField()
    # IsActive = models.BooleanField(default=True)
    # Warehouse = models.BigIntegerField()
    # Sales_GST_Type = models.BigIntegerField()
    # Purchase_GST_Type = models.BigIntegerField()
    # VAT_Type = models.BigIntegerField()
    # IsLeave = models.BooleanField(default=False)

    class Meta:
        db_table = 'users_userTable'
        verbose_name = _('userTable')
        verbose_name_plural = _('usersTable')
        unique_together = (('CompanyID', 'id'),)
        ordering = ('-CreatedDate', 'id')

    def __unicode__(self):
        return str(self.ID)


class User_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TransactionID = models.CharField(max_length=128, blank=True, null=True)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    UserType = models.ForeignKey(
        "brands.UserType", on_delete=models.CASCADE, blank=True, null=True)
    DefaultAccountForUser = models.BooleanField(default=False)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    customer = models.ForeignKey(
        "brands.Customer", on_delete=models.CASCADE, blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Cash_Account = models.BigIntegerField(blank=True, null=True, default=None)
    Bank_Account = models.BigIntegerField(blank=True, null=True, default=None)
    Sales_Account = models.BigIntegerField(blank=True, null=True, default=None)
    Sales_Return_Account = models.BigIntegerField(
        blank=True, null=True, default=None)
    Purchase_Account = models.BigIntegerField(
        blank=True, null=True, default=None)
    Purchase_Return_Account = models.BigIntegerField(
        blank=True, null=True, default=None)
    JoinedDate = models.DateTimeField(blank=True, null=True)
    ExpiryDate = models.DateField(blank=True, null=True)
    LeaveDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    is_owner = models.BooleanField(default=False, blank=True, null=True)
    is_web = models.BooleanField(default=True, blank=True, null=True)
    is_mobile = models.BooleanField(default=True, blank=True, null=True)
    is_pos = models.BooleanField(default=False, blank=True, null=True)
    BranchID = models.BigIntegerField(default=1, blank=True, null=True)

    # ID = models.BigIntegerField()
    # BranchID = models.BigIntegerField()
    # UserName  = models.CharField(max_length=128)
    # Password  = models.CharField(max_length=128)
    # EmployeeID = models.BigIntegerField()
    # IsActive = models.BooleanField(default=True)
    # Warehouse = models.BigIntegerField()
    # Sales_GST_Type = models.BigIntegerField()
    # Purchase_GST_Type = models.BigIntegerField()
    # VAT_Type = models.BigIntegerField()
    # IsLeave = models.BooleanField(default=False)

    class Meta:
        db_table = 'users_userTableLog'
        verbose_name = _('userTableLog')
        verbose_name_plural = _('usersTableLog')
        ordering = ('-CreatedDate', 'id')

    def __unicode__(self):
        return str(self.id)


class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BrandID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    BrandName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'brands_brand'
        verbose_name = _('brand')
        verbose_name_plural = _('brands')
        unique_together = (('CompanyID', 'BrandID', 'BranchID'),)
        ordering = ('-CreatedDate', 'BrandID')

    class Admin:
        list_display = ('BrandID', 'BranchID', 'BrandName',
                        'Notes', 'CreatedUserID', 'UpdatedDate', 'Action',)

    def __unicode__(self):
        return str(self.BrandID)


class Brand_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    BrandName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'brandLogs_brandLog'
        verbose_name = _('brandLog')
        verbose_name_plural = _('brandLogss')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    RouteID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    RouteName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'route_route'
        verbose_name = _('route')
        verbose_name_plural = _('routes')
        unique_together = (('CompanyID', 'RouteID', 'BranchID'),)
        ordering = ('-CreatedDate', 'RouteID')

    def __unicode__(self):
        return str(self.RouteID)


class Route_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    RouteName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'routeLog_routeLog'
        verbose_name = _('routeLog')
        verbose_name_plural = _('routeLogs')
        ordering = ('ID',)

    def __unicode__(self):
        return str(self.ID)


class TaxType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    TaxTypeID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    TaxTypeName = models.CharField(max_length=128, blank=True, null=True)
    Active = models.BooleanField(default=True)

    class Meta:
        db_table = 'taxType_taxType'
        verbose_name = _('taxType')
        verbose_name_plural = _('taxTypes')
        unique_together = (('CompanyID', 'TaxTypeID', 'BranchID'),)
        ordering = ('-TaxTypeID',)

    def __unicode__(self):
        return str(self.TaxTypeID)


class TaxCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    TaxID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    TaxName = models.CharField(max_length=128, blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    PurchaseTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SalesTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Inclusive = models.BooleanField(default=False)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'taxcategory_taxcategory'
        verbose_name = _('taxcategory')
        verbose_name_plural = _('taxcategories')
        unique_together = (('CompanyID', 'TaxID', 'BranchID'),)
        ordering = ('-CreatedDate', 'TaxID')

    def __unicode__(self):
        return str(self.TaxID)


class TaxCategory_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    TaxName = models.CharField(max_length=128, blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    PurchaseTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SalesTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Inclusive = models.BooleanField(default=False)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'taxcategoryLog_taxcategoryLog'
        verbose_name = _('taxcategoryLog')
        verbose_name_plural = _('taxcategoryLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ProductCategoryID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    CategoryName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'productcategory_productcategory'
        verbose_name = _('productcategory')
        verbose_name_plural = _('productcategories')
        unique_together = (('CompanyID', 'ProductCategoryID', 'BranchID'),)
        ordering = ('-CreatedDate', 'ProductCategoryID')

    def __unicode__(self):
        return str(self.ProductCategoryID)


class ProductCategory_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    CategoryName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'productcategoryLog_productcategoryLog'
        verbose_name = _('productcategoryLog')
        verbose_name_plural = _('productcategoryLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class ProductGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ProductGroupID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    GroupName = models.CharField(max_length=128)
    CategoryID = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    kitchen = models.ForeignKey(
        "brands.Kitchen", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'productgroup_productgroup'
        verbose_name = _('productgroup')
        verbose_name_plural = _('productgroups')
        unique_together = (('CompanyID', 'ProductGroupID', 'BranchID'),)
        ordering = ('-CreatedDate', 'ProductGroupID')

    def __unicode__(self):
        return str(self.ProductGroupID)


class ProductGroup_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    GroupName = models.CharField(max_length=128)
    CategoryID = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    kitchen = models.ForeignKey(
        "brands.Kitchen", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'productgroupLog_productgroupLog'
        verbose_name = _('productgroupLog')
        verbose_name_plural = _('productgroupLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class Warehouse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    WarehouseID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    WarehouseName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'warehouse_warehouse'
        verbose_name = _('warehouse')
        verbose_name_plural = _('warehouses')
        unique_together = (('CompanyID', 'WarehouseID', 'BranchID'),)
        ordering = ('-CreatedDate', 'WarehouseID')

    def __unicode__(self):
        return str(self.WarehouseID)


class Warehouse_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    WarehouseName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'warehouseLog_warehouseLog'
        verbose_name = _('warehouseLog')
        verbose_name_plural = _('warehouseLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class PriceCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PriceCategoryID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    PriceCategoryName = models.CharField(max_length=128)
    ColumnName = models.CharField(max_length=128, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'pricecategory_pricecategory'
        verbose_name = _('pricecategory')
        verbose_name_plural = _('pricecategorys')
        unique_together = (('CompanyID', 'PriceCategoryID', 'BranchID'),)
        ordering = ('CreatedDate', 'PriceCategoryID')

    def __unicode__(self):
        return str(self.PriceCategoryID)


class PriceCategory_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    PriceCategoryName = models.CharField(max_length=128)
    ColumnName = models.CharField(max_length=128, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'pricecategoryLog_pricecategoryLog'
        verbose_name = _('pricecategoryLog')
        verbose_name_plural = _('pricecategoryLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class AccountGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    AccountGroupID = models.BigIntegerField()
    AccountGroupName = models.CharField(max_length=128)
    GroupCode = models.CharField(max_length=128, blank=True, null=True)
    AccountGroupUnder = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    IsDefault = models.BooleanField(default=False)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'accountgroup_accountgroup'
        verbose_name = _('accountgroup')
        verbose_name_plural = _('accountgroups')
        ordering = ('AccountGroupID', 'CreatedDate')

    def __unicode__(self):
        return str(self.AccountGroupID)


class AccountGroup_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    AccountGroupName = models.CharField(max_length=128)
    TransactionID = models.BigIntegerField()
    GroupCode = models.CharField(max_length=128, blank=True, null=True)
    AccountGroupUnder = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    IsDefault = models.BooleanField(default=False)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'accountgroupLog_accountgroupLog'
        verbose_name = _('accountgroupLog')
        verbose_name_plural = _('accountgroupLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class AccountLedger(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True,db_index=True)
    LedgerID = models.BigIntegerField(db_index=True)
    BranchID = models.BigIntegerField(db_index=True)
    LedgerName = models.CharField(max_length=128,db_index=True)
    LedgerCode = models.CharField(max_length=128, blank=True, null=True,db_index=True)
    AccountGroupUnder = models.BigIntegerField(blank=True, null=True,db_index=True)
    OpeningBalance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True,db_index=True)
    CrOrDr = models.CharField(max_length=128, blank=True, null=True,db_index=True)
    Notes = models.TextField(blank=True, null=True,db_index=True)
    IsActive = models.BooleanField(default=True,db_index=True)
    IsDefault = models.BooleanField(default=False)
    CreatedUserID = models.BigIntegerField(blank=True, null=True,db_index=True)
    CreatedDate = models.DateTimeField(auto_now_add=True,db_index=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True,db_index=True)
    as_on_date = models.DateField(blank=True, null=True,db_index=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A",db_index=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True,db_index=True)

    class Meta:
        db_table = 'accountLedger_accountLedger'
        verbose_name = _('accountLedger')
        verbose_name_plural = _('accountLedgers')
        unique_together = (('CompanyID', 'LedgerID', 'BranchID'),)
        ordering = ('-CreatedDate', 'LedgerID')

    def __unicode__(self):
        return str(self.LedgerID)


class AccountLedger_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    LedgerName = models.CharField(max_length=128)
    LedgerCode = models.CharField(max_length=128, blank=True, null=True)
    AccountGroupUnder = models.BigIntegerField(blank=True, null=True)
    OpeningBalance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CrOrDr = models.CharField(max_length=128, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    IsDefault = models.BooleanField(default=False)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    as_on_date = models.DateField(blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'accountLedgerLog_accountLedgerLog'
        verbose_name = _('accountLedgerLog')
        verbose_name_plural = _('accountLedgerLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    BranchName = models.CharField(max_length=128)
    DisplayName = models.CharField(max_length=128, blank=True, null=True)
    Building = models.CharField(max_length=128, blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    state = models.ForeignKey(
        "brands.State", on_delete=models.CASCADE, blank=True, null=True)
    country = models.ForeignKey(
        "brands.Country", on_delete=models.CASCADE, blank=True, null=True)
    PostalCode = models.CharField(max_length=128, blank=True, null=True)
    Phone = models.BigIntegerField(blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    is_regional_office = models.BooleanField(default=False)
    regional_office = models.ForeignKey(
        "brands.Branch", related_name='regionaloffice', on_delete=models.CASCADE, blank=True, null=True)
    VATNumber = models.CharField(max_length=128, blank=True, null=True)
    GSTNumber = models.CharField(max_length=128, blank=True, null=True)
    is_gst = models.BooleanField(default=False)
    is_vat = models.BooleanField(default=False)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    vat_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='vat_on_sales_log', on_delete=models.CASCADE, blank=True, null=True)
    vat_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='vat_on_purchase_log', on_delete=models.CASCADE, blank=True, null=True)
    vat_on_expense = models.ForeignKey(
        "brands.AccountLedger", related_name='vat_on_expense_log', on_delete=models.CASCADE, blank=True, null=True)

    central_gst_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='central_gst_on_sales_log', on_delete=models.CASCADE, blank=True, null=True)
    state_gst_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='state_gst_on_sales_log', on_delete=models.CASCADE, blank=True, null=True)
    integrated_gst_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='integrated_gst_on_sales_log', on_delete=models.CASCADE, blank=True, null=True)
    central_gst_on_expense = models.ForeignKey(
        "brands.AccountLedger", related_name='central_gst_on_expense_log', on_delete=models.CASCADE, blank=True, null=True)
    central_gst_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='central_gst_on_purchase_log', on_delete=models.CASCADE, blank=True, null=True)
    state_gst_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='state_gst_on_purchase_log', on_delete=models.CASCADE, blank=True, null=True)
    integrated_gst_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='integrated_gst_on_purchase_log', on_delete=models.CASCADE, blank=True, null=True)
    state_gst_on_payment = models.ForeignKey(
        "brands.AccountLedger", related_name='state_gst_on_payment_log', on_delete=models.CASCADE, blank=True, null=True)

    round_off_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='round_off_sales_log', on_delete=models.CASCADE, blank=True, null=True)
    discount_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='discount_on_sales_log', on_delete=models.CASCADE, blank=True, null=True)
    discount_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='discount_on_purchase_log', on_delete=models.CASCADE, blank=True, null=True)
    discount_on_payment = models.ForeignKey(
        "brands.AccountLedger", related_name='discount_on_payment_log', on_delete=models.CASCADE, blank=True, null=True)
    discount_on_receipt = models.ForeignKey(
        "brands.AccountLedger", related_name='discount_on_receipt_log', on_delete=models.CASCADE, blank=True, null=True)
    discount_on_loyalty = models.ForeignKey(
        "brands.AccountLedger", related_name='discount_on_loyalty_log', on_delete=models.CASCADE, blank=True, null=True)
    round_off_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='round_off_purchase_log', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'branch_branch'
        verbose_name = _('branch')
        verbose_name_plural = _('branchs')
        unique_together = (('CompanyID', 'BranchID'),)
        ordering = ('-CreatedDate', 'BranchID')

    def __unicode__(self):
        return str(self.BranchID)


class Branch_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchName = models.CharField(max_length=128)
    DisplayName = models.CharField(max_length=128, blank=True, null=True)
    Building = models.CharField(max_length=128, blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    state = models.ForeignKey(
        "brands.State", on_delete=models.CASCADE, blank=True, null=True)
    country = models.ForeignKey(
        "brands.Country", on_delete=models.CASCADE, blank=True, null=True)
    PostalCode = models.CharField(max_length=128, blank=True, null=True)
    Phone = models.BigIntegerField(blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    is_regional_office = models.BooleanField(default=False)
    regional_office = models.ForeignKey(
        "brands.Branch", related_name='regionaloffice_log', on_delete=models.CASCADE, blank=True, null=True)

    VATNumber = models.CharField(max_length=128, blank=True, null=True)
    GSTNumber = models.CharField(max_length=128, blank=True, null=True)
    is_gst = models.BooleanField(default=False)
    is_vat = models.BooleanField(default=False)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    vat_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='vat_on_sales', on_delete=models.CASCADE, blank=True, null=True)
    central_gst_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='central_gst_on_sales', on_delete=models.CASCADE, blank=True, null=True)
    state_gst_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='state_gst_on_sales', on_delete=models.CASCADE, blank=True, null=True)
    kerala_flood_cess = models.ForeignKey(
        "brands.AccountLedger", related_name='kerala_flood_cess', on_delete=models.CASCADE, blank=True, null=True)
    integrated_gst_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='integrated_gst_on_sales', on_delete=models.CASCADE, blank=True, null=True)
    tax1_on_service_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='tax1_on_service_sales', on_delete=models.CASCADE, blank=True, null=True)
    tax1_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='tax1_on_sales', on_delete=models.CASCADE, blank=True, null=True)
    tax2_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='tax2_on_sales', on_delete=models.CASCADE, blank=True, null=True)
    tax3_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='tax3_on_sales', on_delete=models.CASCADE, blank=True, null=True)
    round_off_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='round_off_sales', on_delete=models.CASCADE, blank=True, null=True)
    discount_on_sales = models.ForeignKey(
        "brands.AccountLedger", related_name='discount_on_sales', on_delete=models.CASCADE, blank=True, null=True)
    discount_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='discount_on_purchase', on_delete=models.CASCADE, blank=True, null=True)
    discount_on_payment = models.ForeignKey(
        "brands.AccountLedger", related_name='discount_on_payment', on_delete=models.CASCADE, blank=True, null=True)
    discount_on_receipt = models.ForeignKey(
        "brands.AccountLedger", related_name='discount_on_receipt', on_delete=models.CASCADE, blank=True, null=True)
    discount_on_loyalty = models.ForeignKey(
        "brands.AccountLedger", related_name='discount_on_loyalty', on_delete=models.CASCADE, blank=True, null=True)
    vat_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='vat_on_purchase', on_delete=models.CASCADE, blank=True, null=True)
    central_gst_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='central_gst_on_purchase', on_delete=models.CASCADE, blank=True, null=True)
    state_gst_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='state_gst_on_purchase', on_delete=models.CASCADE, blank=True, null=True)
    integrated_gst_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='integrated_gst_on_purchase', on_delete=models.CASCADE, blank=True, null=True)
    tax1_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='tax1_on_purchase', on_delete=models.CASCADE, blank=True, null=True)
    tax2_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='tax2_on_purchase', on_delete=models.CASCADE, blank=True, null=True)
    tax3_on_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='tax3_on_purchase', on_delete=models.CASCADE, blank=True, null=True)
    round_off_purchase = models.ForeignKey(
        "brands.AccountLedger", related_name='round_off_purchase', on_delete=models.CASCADE, blank=True, null=True)
    vat_on_expense = models.ForeignKey(
        "brands.AccountLedger", related_name='vat_on_expense', on_delete=models.CASCADE, blank=True, null=True)
    central_gst_on_expense = models.ForeignKey(
        "brands.AccountLedger", related_name='central_gst_on_expense', on_delete=models.CASCADE, blank=True, null=True)
    state_gst_on_payment = models.ForeignKey(
        "brands.AccountLedger", related_name='state_gst_on_payment', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'branchLog_branchLog'
        verbose_name = _('branchLog')
        verbose_name_plural = _('branchLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class Parties(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PartyID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    PartyType = models.CharField(max_length=128, blank=True, null=True)
    LedgerID = models.BigIntegerField()
    PartyCode = models.CharField(max_length=128, blank=True, null=True)
    OpeningBalance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PartyName = models.CharField(max_length=128, blank=True, null=True)
    DisplayName = models.CharField(max_length=128, blank=True, null=True)
    FirstName = models.CharField(max_length=128, blank=True, null=True)
    LastName = models.CharField(max_length=128, blank=True, null=True)
    Attention = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    State = models.CharField(max_length=128, blank=True, null=True)
    Country = models.CharField(max_length=128, blank=True, null=True)
    PostalCode = models.CharField(max_length=128, blank=True, null=True)
    OfficePhone = models.CharField(max_length=128, blank=True, null=True)
    WorkPhone = models.CharField(max_length=128, blank=True, null=True)
    Mobile = models.CharField(max_length=128, blank=True, null=True)
    WebURL = models.CharField(max_length=128, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    IsBillwiseApplicable = models.BooleanField(default=False)
    CreditPeriod = models.BigIntegerField(blank=True, null=True)
    CreditLimit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    CurrencyID = models.BigIntegerField(blank=True, null=True)
    InterestOrNot = models.BooleanField(default=False)
    RouteID = models.BigIntegerField(blank=True, null=True)
    VATNumber = models.CharField(max_length=128, blank=True, null=True)
    GSTNumber = models.CharField(max_length=128, blank=True, null=True)
    Tax1Number = models.CharField(max_length=128, blank=True, null=True)
    Tax2Number = models.CharField(max_length=128, blank=True, null=True)
    Tax3Number = models.CharField(max_length=128, blank=True, null=True)
    PanNumber = models.CharField(max_length=128, blank=True, null=True)
    BankName1 = models.CharField(max_length=128, blank=True, null=True)
    AccountName1 = models.CharField(max_length=128, blank=True, null=True)
    AccountNo1 = models.CharField(max_length=128, blank=True, null=True)
    IBANOrIFSCCode1 = models.CharField(max_length=128, blank=True, null=True)
    BankName2 = models.CharField(max_length=128, blank=True, null=True)
    AccountName2 = models.CharField(max_length=128, blank=True, null=True)
    AccountNo2 = models.CharField(max_length=128, blank=True, null=True)
    IBANOrIFSCCode2 = models.CharField(max_length=128, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    PartyImage = VersatileImageField(
        upload_to='uploads/', blank=True, null=True)
    Attention_Shipping = models.CharField(
        max_length=128, blank=True, null=True)
    Address1_Shipping = models.CharField(max_length=150, blank=True, null=True)
    Address2_Shipping = models.CharField(max_length=150, blank=True, null=True)
    State_Shipping = models.CharField(max_length=128, blank=True, null=True)
    Country_Shipping = models.CharField(max_length=128, blank=True, null=True)
    City_Shipping = models.CharField(max_length=128, blank=True, null=True)
    PostalCode_Shipping = models.CharField(
        max_length=128, blank=True, null=True)
    Phone_Shipping = models.CharField(max_length=128, blank=True, null=True)
    CRNo = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)
    State_Code = models.CharField(max_length=128, blank=True, null=True)
    PlaceOfSupply = models.CharField(max_length=128, blank=True, null=True)
    District = models.CharField(max_length=128, blank=True, null=True)
    AdditionalNo = models.CharField(max_length=128, blank=True, null=True)
    District_shipping = models.CharField(max_length=128, blank=True, null=True)
    AdditionalNo_shipping = models.CharField(
        max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'parties_parties'
        verbose_name = _('parties')
        verbose_name_plural = _('partiess')
        unique_together = (('CompanyID', 'PartyID', 'BranchID'),)
        ordering = ('-CreatedDate', 'PartyID')

    def __unicode__(self):
        return str(self.PartyID)


class Parties_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    PartyType = models.CharField(max_length=128, blank=True, null=True)
    LedgerID = models.BigIntegerField()
    PartyCode = models.CharField(max_length=128, blank=True, null=True)
    OpeningBalance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PartyName = models.CharField(max_length=128, blank=True, null=True)
    DisplayName = models.CharField(max_length=128, blank=True, null=True)
    FirstName = models.CharField(max_length=128, blank=True, null=True)
    LastName = models.CharField(max_length=128, blank=True, null=True)
    Attention = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    State = models.CharField(max_length=128, blank=True, null=True)
    Country = models.CharField(max_length=128, blank=True, null=True)
    PostalCode = models.CharField(max_length=128, blank=True, null=True)
    OfficePhone = models.CharField(max_length=128, blank=True, null=True)
    WorkPhone = models.CharField(max_length=128, blank=True, null=True)
    Mobile = models.CharField(max_length=128, blank=True, null=True)
    WebURL = models.CharField(max_length=128, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    IsBillwiseApplicable = models.BooleanField(default=False)
    CreditPeriod = models.BigIntegerField(blank=True, null=True)
    CreditLimit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    CurrencyID = models.BigIntegerField(blank=True, null=True)
    InterestOrNot = models.BooleanField(default=False)
    RouteID = models.BigIntegerField(blank=True, null=True)
    VATNumber = models.CharField(max_length=128, blank=True, null=True)
    GSTNumber = models.CharField(max_length=128, blank=True, null=True)
    Tax1Number = models.CharField(max_length=128, blank=True, null=True)
    Tax2Number = models.CharField(max_length=128, blank=True, null=True)
    Tax3Number = models.CharField(max_length=128, blank=True, null=True)
    PanNumber = models.CharField(max_length=128, blank=True, null=True)
    BankName1 = models.CharField(max_length=128, blank=True, null=True)
    AccountName1 = models.CharField(max_length=128, blank=True, null=True)
    AccountNo1 = models.CharField(max_length=128, blank=True, null=True)
    IBANOrIFSCCode1 = models.CharField(max_length=128, blank=True, null=True)
    BankName2 = models.CharField(max_length=128, blank=True, null=True)
    AccountName2 = models.CharField(max_length=128, blank=True, null=True)
    AccountNo2 = models.CharField(max_length=128, blank=True, null=True)
    IBANOrIFSCCode2 = models.CharField(max_length=128, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    PartyImage = models.ImageField(upload_to='uploads/', blank=True, null=True)
    Attention_Shipping = models.CharField(
        max_length=128, blank=True, null=True)
    Address1_Shipping = models.CharField(max_length=150, blank=True, null=True)
    Address2_Shipping = models.CharField(max_length=150, blank=True, null=True)
    State_Shipping = models.CharField(max_length=128, blank=True, null=True)
    Country_Shipping = models.CharField(max_length=128, blank=True, null=True)
    City_Shipping = models.CharField(max_length=128, blank=True, null=True)
    PostalCode_Shipping = models.CharField(
        max_length=128, blank=True, null=True)
    Phone_Shipping = models.CharField(max_length=128, blank=True, null=True)
    CRNo = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)
    State_Code = models.CharField(max_length=128, blank=True, null=True)
    PlaceOfSupply = models.CharField(max_length=128, blank=True, null=True)
    District = models.CharField(max_length=128, blank=True, null=True)
    AdditionalNo = models.CharField(max_length=128, blank=True, null=True)
    District_shipping = models.CharField(max_length=128, blank=True, null=True)
    AdditionalNo_shipping = models.CharField(
        max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'partiesLog_partiesLog'
        verbose_name = _('partiesLog')
        verbose_name_plural = _('partiesLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ProductID = models.BigIntegerField()
    BranchID = models.BigIntegerField(blank=True, null=True)
    ProductCode = models.CharField(max_length=255, blank=True, null=True)
    ProductName = models.CharField(max_length=255, blank=True, null=True)
    DisplayName = models.CharField(max_length=255, blank=True, null=True)
    Description = models.TextField(blank=True, null=True)
    ProductGroupID = models.BigIntegerField(default=1, blank=True, null=True)
    BrandID = models.BigIntegerField(default=1, blank=True, null=True)
    InventoryType = models.CharField(max_length=255, blank=True, null=True)
    MinimumSalesPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    StockMinimum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    StockReOrder = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    StockMaximum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MarginPercent = models.CharField(max_length=255, blank=True, null=True)
    ProductImage = VersatileImageField(
        upload_to='uploads/', blank=True, null=True)
    WeighingCalcType = models.CharField(max_length=255, blank=True, null=True)
    PLUNo = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    GST = models.BigIntegerField(blank=True, null=True)
    VatID = models.BigIntegerField(default=1, blank=True, null=True)
    Tax1 = models.BigIntegerField(blank=True, null=True)
    Tax2 = models.BigIntegerField(blank=True, null=True)
    Tax3 = models.BigIntegerField(blank=True, null=True)
    Action = models.CharField(
        max_length=255, blank=True, null=True, default="A")
    IsWeighingScale = models.BooleanField(default=False)
    IsRawMaterial = models.BooleanField(default=False)
    IsFinishedProduct = models.BooleanField(default=False)
    IsSales = models.BooleanField(default=True)
    IsPurchase = models.BooleanField(default=True)
    IsFavourite = models.BooleanField(default=False)
    Active = models.BooleanField(default=True)
    IsKFC = models.BooleanField(default=False)
    HSNCode = models.CharField(max_length=255, blank=True, null=True)
    WarrantyType = models.CharField(max_length=255, blank=True, null=True)
    Warranty = models.CharField(max_length=255, blank=True, null=True)
    is_Service = models.BooleanField(default=False)
    Stock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    is_inclusive = models.BooleanField(default=False)

    class Meta:
        db_table = 'products_product'
        verbose_name = _('product')
        verbose_name_plural = _('products')
        unique_together = (('CompanyID', 'ProductID', 'BranchID'),)
        ordering = ('-CreatedDate', 'ProductID')
        # indexes = [
        #     models.Index(fields=['ProductName',]),
        #     models.Index(fields=['ProductID',]),
        #     models.Index(fields=['ProductCode',]),
        # ]

    def __unicode__(self):
        return str(self.ProductID)


class Product_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField(blank=True, null=True)
    ProductCode = models.CharField(max_length=255, blank=True, null=True)
    ProductName = models.CharField(max_length=255, blank=True, null=True)
    DisplayName = models.CharField(max_length=255, blank=True, null=True)
    Description = models.TextField(blank=True, null=True)
    ProductGroupID = models.BigIntegerField(default=1, blank=True, null=True)
    BrandID = models.BigIntegerField(default=1, blank=True, null=True)
    InventoryType = models.CharField(max_length=255, blank=True, null=True)
    VatID = models.BigIntegerField(default=1, blank=True, null=True)
    MinimumSalesPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    StockMinimum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    StockReOrder = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    StockMaximum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MarginPercent = models.CharField(max_length=255, blank=True, null=True)
    ProductImage = VersatileImageField(
        upload_to='uploads/', blank=True, null=True)
    Active = models.BooleanField(default=False)
    WeighingCalcType = models.CharField(max_length=255, blank=True, null=True)
    PLUNo = models.BigIntegerField(blank=True, null=True)
    IsFavourite = models.BooleanField(default=False)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    GST = models.BigIntegerField(blank=True, null=True)
    Tax1 = models.BigIntegerField(blank=True, null=True)
    Tax2 = models.BigIntegerField(blank=True, null=True)
    Tax3 = models.BigIntegerField(blank=True, null=True)
    Action = models.CharField(
        max_length=255, blank=True, null=True, default="A")
    IsWeighingScale = models.BooleanField(default=False)
    IsRawMaterial = models.BooleanField(default=False)
    IsFinishedProduct = models.BooleanField(default=False)
    IsSales = models.BooleanField(default=False)
    IsPurchase = models.BooleanField(default=False)
    IsKFC = models.BooleanField(default=False)
    HSNCode = models.CharField(max_length=255, blank=True, null=True)
    WarrantyType = models.CharField(max_length=255, blank=True, null=True)
    Warranty = models.CharField(max_length=255, blank=True, null=True)
    is_Service = models.BooleanField(default=False)
    Stock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    is_inclusive = models.BooleanField(default=False)

    class Meta:
        db_table = 'productLogs_productLog'
        verbose_name = _('productLog')
        verbose_name_plural = _('productLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class ProductBarcode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ProductBarcodeID = models.BigIntegerField()
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField(blank=True, null=True)
    Barcode = models.CharField(max_length=128, blank=True, null=True)
    ProductID = models.ForeignKey(
        "brands.Product", on_delete=models.CASCADE, blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'product_barcode'
        verbose_name = _('product_barcode')
        verbose_name_plural = _('product_barcode')
        ordering = ('-ProductBarcodeID',)
        unique_together = (('CompanyID', 'Barcode', 'BranchID', 'ProductID',),)

    def __unicode__(self):
        return str(self.ProductBarcodeID)


class ProductBarcode_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ProductBarcodeID = models.BigIntegerField()
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField(blank=True, null=True)
    Barcode = models.CharField(max_length=128, blank=True, null=True)
    ProductID = models.ForeignKey(
        "brands.Product", on_delete=models.CASCADE, blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'product_barcode_Logs'
        verbose_name = _('product_barcode_Log')
        verbose_name_plural = _('product_barcode_Logs')
        # ordering = ('-ProductBarcodeID',)

    def __unicode__(self):
        return str(self.ProductBarcodeID)


class PriceList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PriceListID = models.BigIntegerField()
    BranchID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    product = models.ForeignKey("brands.Product", on_delete=models.CASCADE)
    # UnitName = models.CharField(max_length=128,blank=True,null=True)
    UnitID = models.BigIntegerField(blank=True, null=True)
    DefaultUnit = models.BooleanField(default=False)
    SalesPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PurchasePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MRP = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MultiFactor = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Barcode = models.CharField(max_length=128, blank=True, null=True)
    AutoBarcode = models.BigIntegerField(blank=True, null=True)
    SalesPrice1 = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SalesPrice2 = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SalesPrice3 = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UnitInSales = models.BooleanField(default=False)
    UnitInPurchase = models.BooleanField(default=False)
    UnitInReports = models.BooleanField(default=False)

    class Meta:
        db_table = 'pricelist_pricelist'
        verbose_name = _('pricelist')
        verbose_name_plural = _('pricelists')
        unique_together = (('CompanyID', 'PriceListID', 'BranchID'),)
        ordering = ('PriceListID',)

    def __unicode__(self):
        return str(self.PriceListID)


class PriceList_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField(blank=True, null=True)
    TransactionID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    # UnitName = models.CharField(max_length=128,blank=True,null=True)
    UnitID = models.BigIntegerField(blank=True, null=True)
    DefaultUnit = models.BooleanField(default=False)
    SalesPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PurchasePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MRP = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MultiFactor = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Barcode = models.CharField(max_length=128, blank=True, null=True)
    AutoBarcode = models.BigIntegerField(blank=True, null=True)
    SalesPrice1 = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SalesPrice2 = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SalesPrice3 = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UnitInSales = models.BooleanField(default=False)
    UnitInPurchase = models.BooleanField(default=False)
    UnitInReports = models.BooleanField(default=False)

    class Meta:
        db_table = 'pricelistLog_pricelistLog'
        verbose_name = _('pricelistLog')
        verbose_name_plural = _('pricelistLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class MasterType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    MasterTypeID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Name = models.CharField(max_length=128)
    Description = models.TextField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CreatedDate = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    IsDefault = models.BooleanField(default=False)

    class Meta:
        db_table = 'mastertype_mastertype'
        verbose_name = _('mastertype')
        verbose_name_plural = _('mastertypes')
        unique_together = (('CompanyID', 'MasterTypeID', 'BranchID'),)
        ordering = ('-MasterTypeID',)

    def __unicode__(self):
        return str(self.MasterTypeID)


class MasterType_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    Name = models.CharField(max_length=128)
    Description = models.TextField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CreatedDate = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    IsDefault = models.BooleanField(default=False)

    class Meta:
        db_table = 'mastertypeLog_mastertypeLog'
        verbose_name = _('mastertypeLog')
        verbose_name_plural = _('mastertypeLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class TransactionTypes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    TransactionTypesID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    MasterTypeID = models.BigIntegerField()
    Name = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    IsDefault = models.BooleanField(default=False)

    class Meta:
        db_table = 'transactionType_transactionType'
        verbose_name = _('transactionType')
        verbose_name_plural = _('transactionTypes')
        unique_together = (('CompanyID', 'TransactionTypesID', 'BranchID'),)
        ordering = ('-TransactionTypesID', 'CreatedDate')

    def __unicode__(self):
        return str(self.TransactionTypesID)


class TransactionTypes_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    MasterTypeID = models.BigIntegerField()
    Name = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    IsDefault = models.BooleanField(default=False)

    class Meta:
        db_table = 'transactionTypeLog_transactionTypeLog'
        verbose_name = _('transactionTypeLog')
        verbose_name_plural = _('transactionTypeLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ColorID = models.BigIntegerField()
    ColorName = models.CharField(max_length=128)
    ColorValue = models.CharField(max_length=128, blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'color_color'
        verbose_name = _('color')
        verbose_name_plural = _('colors')
        ordering = ('-ColorID',)

    def __unicode__(self):
        return str(self.ColorID)


class Color_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    ColorName = models.CharField(max_length=128)
    ColorValue = models.CharField(max_length=128, blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'colorLog_colorLog'
        verbose_name = _('colorLog')
        verbose_name_plural = _('colorLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class CompanySettings(BaseModel):
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CompanyName = models.CharField(max_length=128)
    CompanyLogo = models.ImageField(
        upload_to='company-logo/', blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    State = models.ForeignKey(
        "brands.State", on_delete=models.CASCADE, blank=True, null=True)
    Country = models.ForeignKey(
        "brands.Country", on_delete=models.CASCADE, blank=True, null=True)
    PostalCode = models.CharField(max_length=128, blank=True, null=True)
    Phone = models.CharField(max_length=150, blank=True, null=True)
    Mobile = models.CharField(max_length=150, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    Website = models.CharField(max_length=128, blank=True, null=True)
    # Currency = models.BigIntegerField(blank=True,null=True)
    # FractionalUnit = models.BigIntegerField(blank=True,null=True)
    VATNumber = models.CharField(max_length=128, blank=True, null=True)
    GSTNumber = models.CharField(max_length=128, blank=True, null=True)
    Tax1 = models.CharField(max_length=128, blank=True, null=True)
    Tax2 = models.CharField(max_length=128, blank=True, null=True)
    Tax3 = models.CharField(max_length=128, blank=True, null=True)
    business_type = models.ForeignKey(
        "brands.BusinessType", on_delete=models.CASCADE, blank=True, null=True)
    owner = models.ForeignKey(
        "auth.User", related_name="user%(class)s_objects", on_delete=models.CASCADE)
    ExpiryDate = models.DateField(blank=True, null=True)
    NoOfUsers = models.PositiveIntegerField(blank=True, null=True, default=1)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    DeletedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UpdatedUserID = models.BigIntegerField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    is_vat = models.BooleanField(default=False)
    is_gst = models.BooleanField(default=False)
    CRNumber = models.CharField(max_length=128, blank=True, null=True)
    CINNumber = models.CharField(max_length=128, blank=True, null=True)
    Description = models.CharField(max_length=128, blank=True, null=True)
    IsTrialVersion = models.BooleanField(default=False)
    Edition = models.CharField(
        max_length=128, default="Standard", blank=True, null=True)
    Permission = models.CharField(
        max_length=128, default="3", blank=True, null=True)
    IsPosUser = models.BooleanField(default=False)
    RegistrationType = models.CharField(max_length=128, blank=True, null=True)

    IsBranch = models.BooleanField(default=False)
    NoOfBrances = models.PositiveIntegerField(blank=True, null=True, default=0)

    class Meta:
        db_table = 'companySettings_companySettings'
        verbose_name = _('companySettings')
        verbose_name_plural = _('companySettingss')
        ordering = ('-CompanyName', 'CreatedDate')

    def __unicode__(self):
        return str(self.CompanyName)


class CompanySettings_Log(models.Model):
    ID = models.AutoField(primary_key=True)
    TransactionID = models.CharField(
        max_length=100, blank=True, default=uuid.uuid4)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CompanyName = models.CharField(max_length=128)
    CompanyLogo = models.ImageField(
        upload_to='company-logo/', blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    State = models.ForeignKey(
        "brands.State", on_delete=models.CASCADE, blank=True, null=True)
    Country = models.ForeignKey(
        "brands.Country", on_delete=models.CASCADE, blank=True, null=True)
    PostalCode = models.CharField(max_length=128, blank=True, null=True)
    Phone = models.BigIntegerField(blank=True, null=True)
    Mobile = models.CharField(max_length=150, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    Website = models.CharField(max_length=128, blank=True, null=True)
    # Currency = models.BigIntegerField(blank=True,null=True)
    # FractionalUnit = models.BigIntegerField(blank=True,null=True)
    VATNumber = models.CharField(max_length=128, blank=True, null=True)
    GSTNumber = models.CharField(max_length=128, blank=True, null=True)
    Tax1 = models.CharField(max_length=128, blank=True, null=True)
    Tax2 = models.CharField(max_length=128, blank=True, null=True)
    Tax3 = models.CharField(max_length=128, blank=True, null=True)
    business_type = models.ForeignKey(
        "brands.BusinessType", on_delete=models.CASCADE, blank=True, null=True)
    owner = models.ForeignKey(
        "auth.User", related_name="user%(class)s_objects", on_delete=models.CASCADE)
    ExpiryDate = models.DateField(blank=True, null=True)
    NoOfUsers = models.PositiveIntegerField(blank=True, null=True, default=1)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UpdatedUserID = models.BigIntegerField(blank=True, null=True)
    CRNumber = models.CharField(max_length=128, blank=True, null=True)
    CINNumber = models.CharField(max_length=128, blank=True, null=True)
    Description = models.CharField(max_length=128, blank=True, null=True)
    is_vat = models.BooleanField(default=False)
    is_gst = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    DeletedDate = models.DateTimeField(blank=True, null=True)
    IsTrialVersion = models.BooleanField(default=False)
    Edition = models.CharField(
        max_length=128, blank=True, default="Standard", null=True)
    Permission = models.CharField(
        max_length=128, default="3", blank=True, null=True)
    IsPosUser = models.BooleanField(default=False)
    RegistrationType = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'companySettingsLog_companySettingsLog'
        verbose_name = _('companySettingsLog')
        verbose_name_plural = _('companySettingsLogs')
        ordering = ('-ID', 'CreatedDate')

    def __unicode__(self):
        return str(self.ID)


class GeneralSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    GeneralSettingsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    GroupName = models.CharField(max_length=150, blank=True, null=True)
    SettingsType = models.CharField(max_length=150, blank=True, null=True)
    SettingsValue = models.CharField(max_length=150, blank=True, null=True)
    Action = models.CharField(max_length=150, blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'generalSettings_generalSettings'
        verbose_name = _('generalSettings')
        verbose_name_plural = _('generalSettingss')
        ordering = ('-GeneralSettingsID', 'CreatedDate')

    def __unicode__(self):
        return str(self.GeneralSettingsID)


class BranchSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchSettingsID = models.BigIntegerField()

    SettingsType = models.CharField(max_length=150, blank=True, null=True)
    SettingsValue = models.CharField(max_length=150, blank=True, null=True)
    Action = models.CharField(max_length=150, blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'branchSettings_branchSettings'
        verbose_name = _('branchSettings')
        verbose_name_plural = _('branchSettingss')
        ordering = ('-BranchSettingsID', 'CreatedDate')

    def __unicode__(self):
        return str(self.BranchSettingsID)


class GeneralSettings_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    GroupName = models.CharField(max_length=150, blank=True, null=True)
    SettingsType = models.CharField(max_length=150, blank=True, null=True)
    SettingsValue = models.CharField(max_length=150, blank=True, null=True)
    Action = models.CharField(max_length=150, blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'generalSettingsLog_generalSettingsLog'
        verbose_name = _('generalSettings')
        verbose_name_plural = _('generalSettingss')
        ordering = ('-TransactionID', 'CreatedDate')

    def __unicode__(self):
        return str(self.TransactionID)


class Designation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    DesignationID = models.BigIntegerField(blank=True, null=True)
    BranchID = models.BigIntegerField(blank=True, null=True)
    DesignationName = models.CharField(max_length=128, blank=True, null=True)
    ShortName = models.CharField(max_length=128, blank=True, null=True)
    DesignationUnder = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'designations_designation'
        verbose_name = _('designation')
        verbose_name_plural = _('designations')
        unique_together = (('CompanyID', 'DesignationID', 'BranchID'),)
        ordering = ('-CreatedDate', 'DesignationID')

    def __unicode__(self):
        return str(self.DesignationID)


class Designation_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField(blank=True, null=True)
    BranchID = models.BigIntegerField(blank=True, null=True)
    DesignationName = models.CharField(max_length=128, blank=True, null=True)
    ShortName = models.CharField(max_length=128, blank=True, null=True)
    DesignationUnder = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'designationLogss_designationLogs'
        verbose_name = _('designationLogs')
        verbose_name_plural = _('designationLogss')
        ordering = ('-CreatedDate', 'ID')

    def __unicode__(self):
        return str(self.ID)


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    DepartmentID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    DepartmentName = models.CharField(max_length=128)
    ParentDepartment = models.ForeignKey(
        "brands.Department", on_delete=models.CASCADE, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'departments_department'
        verbose_name = _('department')
        verbose_name_plural = _('departments')
        unique_together = (('CompanyID', 'DepartmentID', 'BranchID'),)
        ordering = ('-CreatedDate', 'DepartmentID')

    def __unicode__(self):
        return str(self.DepartmentName)


class Department_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    DepartmentName = models.CharField(max_length=128)
    ParentDepartment = models.ForeignKey(
        "brands.Department", on_delete=models.CASCADE, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'departmentLogss_departmentLogs'
        verbose_name = _('departmentLogs')
        verbose_name_plural = _('departmentLogss')
        ordering = ('-CreatedDate', 'ID')

    def __unicode__(self):
        return str(self.ID)


class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    EmployeeID = models.BigIntegerField()
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    FirstName = models.CharField(max_length=128, blank=True, null=True)
    LastName = models.CharField(max_length=128, blank=True, null=True)
    DesignationID = models.BigIntegerField(blank=True, null=True)
    DepartmentID = models.BigIntegerField(blank=True, null=True)
    Category = models.ForeignKey(
        "brands.Category", on_delete=models.CASCADE, blank=True, null=True)
    DateOfBirth = models.DateField(blank=True, null=True)
    Gender = models.CharField(max_length=128, blank=True, null=True)
    BloodGroup = models.CharField(max_length=128, blank=True, null=True)
    Nationality = models.CharField(max_length=128, blank=True, null=True)
    State = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    Post = models.CharField(max_length=128, blank=True, null=True)
    Phone = models.CharField(max_length=128, blank=True, null=True)
    Mobile = models.CharField(max_length=128, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    PassportNo = models.CharField(max_length=128, blank=True, null=True)
    PassportExpiryDate = models.DateField(blank=True, null=True)
    VisaDetails = models.CharField(max_length=128, blank=True, null=True)
    VisaExpiryDate = models.DateField(blank=True, null=True)
    ProbationPeriod = models.BigIntegerField(blank=True, null=True)
    periodType = models.CharField(max_length=128, blank=True, null=True)
    DateOfJoining = models.DateField(blank=True, null=True)
    Salary = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AccountNumber = models.CharField(max_length=128, blank=True, null=True)
    AccountHolderName = models.CharField(max_length=128, blank=True, null=True)
    AccountName = models.CharField(max_length=128, blank=True, null=True)
    AccountBranch = models.CharField(max_length=128, blank=True, null=True)
    AccountIFSC = models.CharField(max_length=128, blank=True, null=True)
    NoCasualLeave = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    Qualification = models.CharField(max_length=128, blank=True, null=True)
    EmergencyContactNumber = models.CharField(
        max_length=128, blank=True, null=True)
    EmergencyEmail = models.EmailField(blank=True, null=True)
    EmergencyAddress = models.TextField(blank=True, null=True)
    EmployeeCode = models.CharField(max_length=128, blank=True, null=True)
    EmployeeID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    LedgerID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    EmployeeCardID = models.CharField(max_length=128, blank=True, null=True)
    WorkLocation = models.CharField(max_length=128, blank=True, null=True)
    JobType = models.CharField(max_length=128, blank=True, null=True)
    WorkEmail = models.EmailField(blank=True, null=True)
    OfficialEmail = models.EmailField(blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    ShowInSales = models.BooleanField(default=True)
    ShowInPurchase = models.BooleanField(default=True)
    ShowInPayment = models.BooleanField(default=True)
    ShowInReceipt = models.BooleanField(default=True)

    class Meta:
        db_table = 'employees_employees'
        verbose_name = _('employees')
        verbose_name_plural = _('employeess')
        unique_together = (('CompanyID', 'EmployeeID', 'BranchID'),)
        ordering = ('-CreatedDate', 'EmployeeID')

    def __unicode__(self):
        return str(self.EmployeeID)


class Employee_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    FirstName = models.CharField(max_length=128, blank=True, null=True)
    LastName = models.CharField(max_length=128, blank=True, null=True)
    Category = models.ForeignKey(
        "brands.Category", on_delete=models.CASCADE, blank=True, null=True)
    DesignationID = models.BigIntegerField(blank=True, null=True)
    DepartmentID = models.BigIntegerField(blank=True, null=True)
    DateOfBirth = models.DateField(blank=True, null=True)
    Gender = models.CharField(max_length=128, blank=True, null=True)
    BloodGroup = models.CharField(max_length=128, blank=True, null=True)
    Nationality = models.CharField(max_length=128, blank=True, null=True)
    State = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    Post = models.CharField(max_length=128, blank=True, null=True)
    Phone = models.CharField(max_length=128, blank=True, null=True)
    Mobile = models.CharField(max_length=128, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    PassportNo = models.CharField(max_length=128, blank=True, null=True)
    PassportExpiryDate = models.DateField(blank=True, null=True)
    VisaDetails = models.CharField(max_length=128, blank=True, null=True)
    VisaExpiryDate = models.DateField(blank=True, null=True)
    ProbationPeriod = models.BigIntegerField(blank=True, null=True)
    periodType = models.CharField(max_length=128, blank=True, null=True)
    DateOfJoining = models.DateField(blank=True, null=True)
    Salary = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AccountNumber = models.CharField(max_length=128, blank=True, null=True)
    AccountHolderName = models.CharField(max_length=128, blank=True, null=True)
    AccountName = models.CharField(max_length=128, blank=True, null=True)
    AccountBranch = models.CharField(max_length=128, blank=True, null=True)
    AccountIFSC = models.CharField(max_length=128, blank=True, null=True)
    NoCasualLeave = models.BigIntegerField(blank=True, null=True)

    Notes = models.TextField(blank=True, null=True)
    Qualification = models.CharField(max_length=128, blank=True, null=True)
    EmergencyContactNumber = models.CharField(
        max_length=128, blank=True, null=True)
    EmergencyEmail = models.EmailField(blank=True, null=True)
    EmergencyAddress = models.TextField(blank=True, null=True)

    EmployeeCode = models.CharField(max_length=128, blank=True, null=True)
    BranchID = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    EmployeeCardID = models.CharField(max_length=128, blank=True, null=True)
    WorkLocation = models.CharField(max_length=128, blank=True, null=True)
    JobType = models.CharField(max_length=128, blank=True, null=True)
    WorkEmail = models.EmailField(blank=True, null=True)
    OfficialEmail = models.EmailField(blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    ShowInSales = models.BooleanField(default=False)
    ShowInPurchase = models.BooleanField(default=False)
    ShowInPayment = models.BooleanField(default=False)
    ShowInReceipt = models.BooleanField(default=False)

    class Meta:
        db_table = 'employeesLog_employeesLog'
        verbose_name = _('employeesLog')
        verbose_name_plural = _('employeesLogs')
        ordering = ('-CreatedDate', 'ID')

    def __unicode__(self):
        return str(self.ID)


class FinancialYear(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    FinancialYearID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    FromDate = models.DateField(blank=True, null=True)
    ToDate = models.DateField(blank=True, null=True)
    IsClosed = models.BooleanField(default=False)
    Notes = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'financialYear_financialYear'
        verbose_name = _('financialYear')
        verbose_name_plural = _('financialYears')
        ordering = ('-FinancialYearID',)

    def __unicode__(self):
        return str(self.FinancialYearID)


class FinancialYear_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    FromDate = models.DateField()
    ToDate = models.DateField()
    IsClosed = models.BooleanField(default=False)
    Notes = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'financialYearLog_financialYearLog'
        verbose_name = _('financialYearLog')
        verbose_name_plural = _('financialYearLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class Flavours(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    FlavourID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    FlavourName = models.CharField(max_length=128)
    BgColor = models.CharField(max_length=128, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'flavours_flavour'
        verbose_name = _('flavour')
        verbose_name_plural = _('flavours')
        unique_together = (('CompanyID', 'FlavourID', 'BranchID'),)
        ordering = ('-FlavourID',)

    def __unicode__(self):
        return str(self.FlavourID)


class Flavours_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    FlavourName = models.CharField(max_length=128)
    BgColor = models.CharField(max_length=128, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'flavourLogs_flavourLog'
        verbose_name = _('flavourLog')
        verbose_name_plural = _('flavourLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class JournalDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    JournalDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    JournalMasterID = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    Debit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Credit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Narration = models.TextField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LogID = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'journalDetails_journalDetail'
        verbose_name = _('journalDetail')
        verbose_name_plural = _('journalDetails')
        unique_together = (('CompanyID', 'JournalDetailsID', 'BranchID'),)
        ordering = ('-JournalDetailsID',)

    def __unicode__(self):
        return str(self.JournalDetailsID)


class JournalDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    JournalMasterID = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    Debit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Credit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Narration = models.TextField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'journalDetailLogs_journalDetailLog'
        verbose_name = _('journalDetailLog')
        verbose_name_plural = _('journalDetailLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class JournalMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    JournalMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    TotalDebit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalCredit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Difference = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'journalMaster_journalMaster'
        verbose_name = _('journalMaster')
        verbose_name_plural = _('journalMaster')
        unique_together = (('CompanyID', 'JournalMasterID', 'BranchID'),)
        ordering = ('-JournalMasterID',)

    def __unicode__(self):
        return str(self.JournalMasterID)


class JournalMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    TotalDebit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalCredit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Difference = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'journalMasterlLogs_journalMasterLog'
        verbose_name = _('journalMasterLog')
        verbose_name_plural = _('journalMasterLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class Kitchen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    KitchenID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    KitchenName = models.CharField(max_length=128)
    IPAddress = models.CharField(max_length=128, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'kitchens_kitchen'
        verbose_name = _('kitchen')
        verbose_name_plural = _('kitchens')
        unique_together = (('CompanyID', 'KitchenID', 'BranchID'),)
        ordering = ('-CreatedDate', 'KitchenID')

    def __unicode__(self):
        return str(self.KitchenID)


class Kitchen_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    KitchenName = models.CharField(max_length=128)
    IPAddress = models.CharField(max_length=128, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'kitchenLogs_kitchenLog'
        verbose_name = _('kitchenLog')
        verbose_name_plural = _('kitchenLogs')
        ordering = ('-CreatedDate', 'ID')

    def __unicode__(self):
        return str(self.ID)


class LedgerPosting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    LedgerPostingID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    Date = models.DateField(blank=True, null=True,db_index=True)
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    VoucherMasterID = models.BigIntegerField(blank=True, null=True)
    VoucherDetailID = models.BigIntegerField(blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    RelatedLedgerID = models.BigIntegerField(blank=True, null=True)
    Debit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True,db_index=True)
    Credit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True,db_index=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'ledgerPostings_ledgerPosting'
        verbose_name = _('ledgerPosting')
        verbose_name_plural = _('ledgerPostings')
        unique_together = (('CompanyID', 'LedgerPostingID', 'BranchID'),)
        ordering = ('-LedgerPostingID',)

    def __unicode__(self):
        return str(self.LedgerPostingID)


class LedgerPosting_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    Date = models.DateField(blank=True, null=True)
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    VoucherMasterID = models.BigIntegerField(blank=True, null=True)
    VoucherDetailID = models.BigIntegerField(blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    RelatedLedgerID = models.BigIntegerField(blank=True, null=True)
    Debit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Credit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'ledgerPostingLogs_ledgerPostingLog'
        verbose_name = _('ledgerPostingLog')
        verbose_name_plural = _('ledgerPostingLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class OpeningStockDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    OpeningStockDetailsID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    BranchID = models.BigIntegerField()
    OpeningStockMasterID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'openingStockDetailss_openingStockDetails'
        verbose_name = _('openingStockDetails')
        verbose_name_plural = _('openingStockDetailss')
        unique_together = (('CompanyID', 'OpeningStockDetailsID', 'BranchID'),)
        ordering = ('-OpeningStockDetailsID',)

    def __unicode__(self):
        return str(self.OpeningStockDetailsID)


class OpeningStockDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    BranchID = models.BigIntegerField()
    OpeningStockMasterID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'openingStockDetailsLogs_openingStockDetailsLog'
        verbose_name = _('openingStockDetailsLog')
        verbose_name_plural = _('openingStockDetailsLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class OpeningStockMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    OpeningStockMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'openingStockMasters_openingStockMaster'
        verbose_name = _('openingStockMaster')
        verbose_name_plural = _('openingStockMasters')
        unique_together = (('CompanyID', 'OpeningStockMasterID', 'BranchID'),)
        ordering = ('-OpeningStockMasterID', 'CreatedDate')

    def __unicode__(self):
        return str(self.OpeningStockMasterID)


class OpeningStockMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'openingStockMasterLogs_openingStockMasterLog'
        verbose_name = _('openingStockMasterLog')
        verbose_name_plural = _('openingStockMasterLogs')
        ordering = ('-ID', 'CreatedDate')

    def __unicode__(self):
        return str(self.ID)


class PaymentDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PaymentDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    PaymentMasterID = models.BigIntegerField(blank=True, null=True)
    # payment_master = models.ForeignKey("brands.PaymentMaster",on_delete=models.CASCADE)
    PaymentGateway = models.BigIntegerField(blank=True, null=True)
    RefferenceNo = models.BigIntegerField(blank=True, null=True)
    CardNetwork = models.BigIntegerField(blank=True, null=True)
    PaymentStatus = models.BigIntegerField(blank=True, null=True)
    DueDate = models.DateField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Discount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Narration = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    VoucherType = models.CharField(
        max_length=128, blank=True, null=True, default="CP")
    LogID = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'paymentDetails_paymentDetail'
        verbose_name = _('paymentDetail')
        verbose_name_plural = _('paymentDetails')
        unique_together = (('CompanyID', 'PaymentDetailsID', 'BranchID'),)
        ordering = ('-PaymentDetailsID',)

    def __unicode__(self):
        return str(self.PaymentDetailsID)


class PaymentDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    PaymentMasterID = models.BigIntegerField(blank=True, null=True)
    PaymentGateway = models.BigIntegerField(blank=True, null=True)
    RefferenceNo = models.BigIntegerField(blank=True, null=True)
    CardNetwork = models.BigIntegerField(blank=True, null=True)
    PaymentStatus = models.BigIntegerField(blank=True, null=True)
    DueDate = models.DateField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Discount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Narration = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    VoucherType = models.CharField(
        max_length=128, blank=True, null=True, default="CP")

    class Meta:
        db_table = 'paymentDetailLogs_paymentDetailLog'
        verbose_name = _('paymentDetailLog')
        verbose_name_plural = _('paymentDetailLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class PaymentMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PaymentMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    PaymentNo = models.CharField(max_length=128)
    FinancialYearID = models.BigIntegerField(blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    TotalAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'paymentMasters_paymentMaster'
        verbose_name = _('paymentMaster')
        verbose_name_plural = _('paymentMasters')
        unique_together = (('CompanyID', 'PaymentMasterID', 'BranchID'),)
        ordering = ('-PaymentMasterID',)

    def __unicode__(self):
        return str(self.PaymentMasterID)


class PaymentMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    PaymentNo = models.CharField(max_length=128)
    FinancialYearID = models.BigIntegerField(blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    TotalAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'paymentMasterLogs_paymentMasterLog'
        verbose_name = _('paymentMasterLog')
        verbose_name_plural = _('paymentMasterLogs')
        ordering = ('-ID', 'CreatedDate')

    def __unicode__(self):
        return str(self.ID)


class POSHoldDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    POSHoldDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    POSHoldMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Flavour = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'posholdDetailss_posholdDetails'
        verbose_name = _('posholdDetails')
        verbose_name_plural = _('posholdDetailses')
        unique_together = (('CompanyID', 'POSHoldDetailsID', 'BranchID'),)
        ordering = ('-POSHoldDetailsID',)

    def __unicode__(self):
        return str(self.POSHoldDetailsID)


class POSHoldDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    POSHoldMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField()
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Flavour = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'posholdDetailsLogs_posholdDetailsLog'
        verbose_name = _('posholdDetailsLog')
        verbose_name_plural = _('posholdDetailsLoges')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class POSHoldMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    POSHoldMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    SalesAccount = models.BigIntegerField(blank=True, null=True)
    HoldStatus = models.BooleanField(default=False)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashReceived = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BankAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TableID = models.BigIntegerField(blank=True, null=True)
    SeatNumber = models.CharField(max_length=128, blank=True, null=True)
    NoOfGuests = models.BigIntegerField(blank=True, null=True)
    INOUT = models.BooleanField(default=False)
    TokenNumber = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'posholdMasters_posholdMaster'
        verbose_name = _('posholdMaster')
        verbose_name_plural = _('posholdMasteres')
        unique_together = (('CompanyID', 'POSHoldMasterID', 'BranchID'),)
        ordering = ('-POSHoldMasterID', 'CreatedDate')

    def __unicode__(self):
        return str(self.POSHoldMasterID)


class POSHoldMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    SalesAccount = models.BigIntegerField(blank=True, null=True)
    HoldStatus = models.BooleanField(default=False)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashReceived = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BankAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TableID = models.BigIntegerField(blank=True, null=True)
    SeatNumber = models.CharField(max_length=128, blank=True, null=True)
    NoOfGuests = models.BigIntegerField(blank=True, null=True)
    INOUT = models.BooleanField(default=False, blank=True, null=True)
    TokenNumber = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'posholdMasterLogs_posholdMasterLog'
        verbose_name = _('posholdMasterLog')
        verbose_name_plural = _('posholdMasterLogs')
        ordering = ('-ID', 'CreatedDate')

    def __unicode__(self):
        return str(self.ID)


class PurchaseDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PurchaseDetailsID = models.BigIntegerField(blank=True, null=True)
    purchase_master = models.ForeignKey(
        "brands.PurchaseMaster", on_delete=models.CASCADE)
    BranchID = models.BigIntegerField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    PurchaseMasterID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    # product = models.ForeignKey("brands.Product",on_delete=models.CASCADE)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    ReturnQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    ManufactureDate = models.DateField(blank=True, null=True)
    ExpiryDate = models.DateField(blank=True, null=True)
    LogID = models.BigIntegerField(default=0)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'purchaseDetailses_purchaseDetails'
        verbose_name = _('purchaseDetails')
        verbose_name_plural = _('purchaseDetailses')
        unique_together = (('CompanyID', 'PurchaseDetailsID', 'BranchID'),)
        ordering = ('-PurchaseDetailsID',)

    def __unicode__(self):
        return str(self.PurchaseDetailsID)


class PurchaseDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    PurchaseMasterID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    ReturnQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    ManufactureDate = models.DateField(blank=True, null=True)
    ExpiryDate = models.DateField(blank=True, null=True)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'purchaseDetailsLogs_purchaseDetailsLog'
        verbose_name = _('purchaseDetailsLog')
        verbose_name_plural = _('purchaseDetailsLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class PurchaseMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PurchaseMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    RefferenceBillNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    VenderInvoiceDate = models.DateField(blank=True, null=True)
    CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    PurchaseAccount = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.TextField(blank=True, null=True)
    Address2 = models.TextField(blank=True, null=True)
    Address3 = models.TextField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AdditionalCost = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TransactionTypeID = models.BigIntegerField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashReceived = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BankAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CardTypeID = models.BigIntegerField(blank=True, null=True)
    CardNumber = models.CharField(max_length=128, blank=True, null=True)
    CashID = models.BigIntegerField(blank=True, null=True)
    BankID = models.BigIntegerField(blank=True, null=True)
    ShippingCharge = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    shipping_tax_amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxTypeID = models.CharField(max_length=128, blank=True, null=True)
    SAC = models.CharField(max_length=128, blank=True, null=True)
    PurchaseTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)
    TaxTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NonTaxTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'purchaseMasters_purchaseMaster'
        verbose_name = _('purchaseMaster')
        verbose_name_plural = _('purchaseMasters')
        unique_together = (('CompanyID', 'PurchaseMasterID', 'BranchID'),)
        ordering = ('-PurchaseMasterID',)

    def __unicode__(self):
        return str(self.PurchaseMasterID)


class PurchaseMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    RefferenceBillNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    VenderInvoiceDate = models.DateField(blank=True, null=True)
    CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    PurchaseAccount = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AdditionalCost = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TransactionTypeID = models.BigIntegerField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashReceived = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BankAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CardTypeID = models.BigIntegerField(blank=True, null=True)
    CardNumber = models.CharField(max_length=128, blank=True, null=True)
    CashID = models.BigIntegerField(blank=True, null=True)
    BankID = models.BigIntegerField(blank=True, null=True)

    ShippingCharge = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    shipping_tax_amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxTypeID = models.CharField(max_length=128, blank=True, null=True)
    SAC = models.CharField(max_length=128, blank=True, null=True)
    PurchaseTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'purchaseMasterLogs_purchaseMasterLog'
        verbose_name = _('purchaseMasterLog')
        verbose_name_plural = _('purchaseMasterLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class PurchaseOrderDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PurchaseOrderDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    BatchID = models.BigIntegerField(blank=True, null=True)
    PurchaseOrderMasterID = models.BigIntegerField(blank=True, null=True)
    # DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    # OrederDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    # TaxID = models.BigIntegerField(blank=True, null=True)
    # TaxType = models.CharField(max_length=128, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # Flavour = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'purchaseOrderDetails_purchaseOrderDetail'
        verbose_name = _('purchaseOrderDetail')
        verbose_name_plural = _('purchaseOrderDetails')
        unique_together = (
            ('CompanyID', 'PurchaseOrderDetailsID', 'BranchID'),)
        ordering = ('-PurchaseOrderDetailsID',)

    def __unicode__(self):
        return str(self.PurchaseOrderDetailsID)


class PurchaseOrderDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    BatchID = models.BigIntegerField(blank=True, null=True)
    PurchaseOrderMasterID = models.BigIntegerField(blank=True, null=True)
    # DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    # OrederDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # Flavour = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'purchaseOrderDetailLogs_purchaseOrderDetailLog'
        verbose_name = _('purchaseOrderDetailLog')
        verbose_name_plural = _('purchaseOrderDetailLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class PurchaseOrderMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PurchaseOrderMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    # OrderNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    DeliveryDate = models.DateField(blank=True, null=True)
    # CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    # EmployeeID = models.BigIntegerField(blank=True, null=True)
    # PurchaseAccount = models.BigIntegerField(blank=True, null=True)
    # DeliveryMasterID = models.BigIntegerField(blank=True, null=True)
    # OrderMasterID = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    # Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # AdditionalCost = models.DecimalField(
    # default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsInvoiced = models.CharField(max_length=128, blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    ShippingCharge = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    shipping_tax_amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxTypeID = models.CharField(max_length=128, blank=True, null=True)
    SAC = models.CharField(max_length=128, blank=True, null=True)
    PurchaseTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'purchaseOrderMasters_purchaseOrderMaster'
        verbose_name = _('purchaseOrderMaster')
        verbose_name_plural = _('purchaseOrderMasters')
        unique_together = (('CompanyID', 'PurchaseOrderMasterID', 'BranchID'),)
        ordering = ('-PurchaseOrderMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.PurchaseOrderMasterID)


class PurchaseOrderMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    # OrderNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    DeliveryDate = models.DateField(blank=True, null=True)
    # CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    # EmployeeID = models.BigIntegerField(blank=True, null=True)
    # PurchaseAccount = models.BigIntegerField(blank=True, null=True)
    # DeliveryMasterID = models.BigIntegerField(blank=True, null=True)
    # OrderMasterID = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    # Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AdditionalCost = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsInvoiced = models.CharField(max_length=128, blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    ShippingCharge = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    shipping_tax_amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxTypeID = models.CharField(max_length=128, blank=True, null=True)
    SAC = models.CharField(max_length=128, blank=True, null=True)
    PurchaseTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'purchaseOrderMasterLogs_purchaseOrderMasterLog'
        verbose_name = _('purchaseOrderMasterLog')
        verbose_name_plural = _('purchaseOrderMasterLogs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class PurchaseReturnDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PurchaseReturnDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    PurchaseReturnMasterID = models.BigIntegerField()
    DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    AddlDiscPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'purchaseReturnDetails_purchaseReturnDetail'
        verbose_name = _('purchaseReturnDetail')
        verbose_name_plural = _('purchaseReturnDetails')
        unique_together = (
            ('CompanyID', 'PurchaseReturnDetailsID', 'BranchID'),)
        ordering = ('-PurchaseReturnDetailsID',)

    def __unicode__(self):
        return str(self.PurchaseReturnDetailsID)


class PurchaseReturnDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    PurchaseReturnMasterID = models.BigIntegerField()
    DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    AddlDiscPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'purchaseReturnDetailLogs_purchaseReturnDetailLog'
        verbose_name = _('purchaseReturnDetailLog')
        verbose_name_plural = _('purchaseReturnDetailLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class PurchaseReturnMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PurchaseReturnMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    VoucherDate = models.DateField(blank=True, null=True)
    RefferenceBillNo = models.CharField(max_length=128, blank=True, null=True)
    RefferenceBillDate = models.DateField(blank=True, null=True)
    VenderInvoiceDate = models.DateField(blank=True, null=True)
    CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    PurchaseAccount = models.BigIntegerField(blank=True, null=True)
    DeliveryMasterID = models.BigIntegerField(blank=True, null=True)
    OrderMasterID = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AdditionalCost = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=150, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)
    TaxTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NonTaxTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'purchaseReturnMasters_purchaseReturnMaster'
        verbose_name = _('purchaseReturnMaster')
        verbose_name_plural = _('purchaseReturnMasters')
        unique_together = (
            ('CompanyID', 'PurchaseReturnMasterID', 'BranchID'),)
        ordering = ('-PurchaseReturnMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.PurchaseReturnMasterID)


class PurchaseReturnMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    VoucherDate = models.DateField(blank=True, null=True)
    RefferenceBillNo = models.CharField(max_length=128, blank=True, null=True)
    RefferenceBillDate = models.DateField(blank=True, null=True)
    VenderInvoiceDate = models.DateField(blank=True, null=True)
    CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    PurchaseAccount = models.BigIntegerField(blank=True, null=True)
    DeliveryMasterID = models.BigIntegerField(blank=True, null=True)
    OrderMasterID = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AdditionalCost = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=150, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'purchaseReturnMasterLogs_purchaseReturnMasterLog'
        verbose_name = _('purchaseReturnMasterLog')
        verbose_name_plural = _('purchaseReturnMasterLogs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class ReceiptDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ReceiptDetailID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    ReceiptMasterID = models.BigIntegerField(blank=True, null=True)
    # receipt_master = models.ForeignKey("brands.ReceiptMaster",on_delete=models.CASCADE)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    PaymentGateway = models.BigIntegerField(blank=True, null=True)
    RefferenceNo = models.BigIntegerField(blank=True, null=True)
    CardNetwork = models.BigIntegerField(blank=True, null=True)
    PaymentStatus = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    DueDate = models.DateField(blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Discount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Narration = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LogID = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'receiptDetailses_receiptDetails'
        verbose_name = _('receiptDetails')
        verbose_name_plural = _('receiptDetailses')
        unique_together = (('CompanyID', 'ReceiptDetailID', 'BranchID'),)
        ordering = ('-ReceiptDetailID',)

    def __unicode__(self):
        return str(self.ReceiptDetailID)


class ReceiptDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    ReceiptMasterID = models.BigIntegerField(blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    PaymentGateway = models.BigIntegerField(blank=True, null=True)
    RefferenceNo = models.BigIntegerField(blank=True, null=True)
    CardNetwork = models.BigIntegerField(blank=True, null=True)
    PaymentStatus = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    DueDate = models.DateField(blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Discount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Narration = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'receiptDetailsLogs_receiptDetailsLog'
        verbose_name = _('receiptDetailsLog')
        verbose_name_plural = _('receiptDetailsLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class ReceiptMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ReceiptMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    ReceiptNo = models.CharField(max_length=128, blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    FinancialYearID = models.BigIntegerField(blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    TotalAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'receiptMasters_receiptMaster'
        verbose_name = _('receiptMaster')
        verbose_name_plural = _('receiptMasters')
        unique_together = (('CompanyID', 'ReceiptMasterID', 'BranchID'),)
        ordering = ('-ReceiptMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ReceiptMasterID)


class ReceiptMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    ReceiptNo = models.CharField(max_length=128, blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    FinancialYearID = models.BigIntegerField(blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    TotalAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'receiptMasterLogss_receiptMasterLogs'
        verbose_name = _('receiptMasterLogs')
        verbose_name_plural = _('receiptMasterLogss')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class SalesDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    SalesDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    SalesMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    ReturnQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    AddlDiscPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    Flavour = models.TextField(blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)
    Description = models.CharField(
        max_length=250, blank=True, null=True)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'salesDetails_salesDetail'
        verbose_name = _('salesDetail')
        verbose_name_plural = _('salesDetails')
        unique_together = (('CompanyID', 'SalesDetailsID', 'BranchID'),)
        ordering = ('-SalesDetailsID',)

    def __unicode__(self):
        return str(self.SalesDetailsID)


class SalesDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    SalesMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    ReturnQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    AddlDiscPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    Flavour = models.TextField(blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    Description = models.CharField(
        max_length=250, blank=True, null=True)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'salesDetailLogs_salesDetailLog'
        verbose_name = _('salesDetailLog')
        verbose_name_plural = _('salesDetailLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class QrCode(models.Model):
    voucher_type = models.CharField(max_length=200)
    master_id = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    qr_code = models. ImageField(upload_to='or_codes', blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        qrcode_img = qrcode.make(self.url)

        # canvas = Image.new('RGB', (500, 500), 'white')
        # draw = ImageDraw.Draw(canvas)
        # canvas.paste(qrcode_img, (5, 5))
        fname = 'qr_code'+'.png'
        buffer = BytesIO()
        # img.save(buffer, "PNG")
        qrcode_img.save(buffer, 'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        # canvas.close()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'website_qrcode'
        verbose_name = ('website_qrcode')

    def __unicode__(self):
        return self.name


class SalesMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    LoyaltyCustomerID = models.ForeignKey(
        "brands.LoyaltyCustomer", on_delete=models.CASCADE, blank=True, null=True)
    SalesMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    SalesAccount = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AdditionalCost = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashReceived = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BankAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    SeatNumber = models.CharField(max_length=128, blank=True, null=True)
    NoOfGuests = models.BigIntegerField(blank=True, null=True)
    INOUT = models.BooleanField(default=False)
    TokenNumber = models.BigIntegerField(blank=True, null=True)
    CardTypeID = models.BigIntegerField(blank=True, null=True)
    CardNumber = models.CharField(max_length=128, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    IsPosted = models.BooleanField(default=False)
    SalesType = models.CharField(max_length=150, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TransactionTypeID = models.BigIntegerField(blank=True, null=True)
    OldLedgerBalance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashID = models.BigIntegerField(blank=True, null=True)
    BankID = models.BigIntegerField(blank=True, null=True)
    ShippingCharge = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    shipping_tax_amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxTypeID = models.CharField(max_length=128, blank=True, null=True)
    SAC = models.CharField(max_length=128, blank=True, null=True)
    SalesTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)
    Status = models.CharField(
        max_length=128, blank=True, null=True, default="Invoiced")
    TableID = models.BigIntegerField(blank=True, null=True)
    Table = models.ForeignKey(
        "brands.POS_Table", on_delete=models.CASCADE, blank=True, null=True)
    ShippingAddress = models.ForeignKey(
        "brands.UserAdrress", on_delete=models.CASCADE, blank=True, null=True)
    TaxTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NonTaxTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'salesMasters_salesMaster'
        verbose_name = _('salesMaster')
        verbose_name_plural = _('salesMasters')
        unique_together = (('CompanyID', 'SalesMasterID', 'BranchID'),)
        ordering = ('-SalesMasterID',)

    def __unicode__(self):
        return str(self.SalesMasterID)


class SalesMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)

    LoyaltyCustomerID = models.ForeignKey(
        "brands.LoyaltyCustomer", on_delete=models.CASCADE, blank=True, null=True)

    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    SalesAccount = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AdditionalCost = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashReceived = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BankAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TableID = models.BigIntegerField(blank=True, null=True)
    SeatNumber = models.CharField(max_length=128, blank=True, null=True)
    NoOfGuests = models.BigIntegerField(blank=True, null=True)
    INOUT = models.BooleanField(default=False)
    TokenNumber = models.BigIntegerField(blank=True, null=True)
    CardTypeID = models.BigIntegerField(blank=True, null=True)
    CardNumber = models.CharField(max_length=128, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    IsPosted = models.BooleanField(default=False)
    SalesType = models.CharField(max_length=150, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TransactionTypeID = models.BigIntegerField(blank=True, null=True)
    OldLedgerBalance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashID = models.BigIntegerField(blank=True, null=True)
    BankID = models.BigIntegerField(blank=True, null=True)
    ShippingCharge = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    shipping_tax_amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxTypeID = models.CharField(max_length=128, blank=True, null=True)
    SAC = models.CharField(max_length=128, blank=True, null=True)
    SalesTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)
    Status = models.CharField(
        max_length=128, blank=True, null=True, default="Invoiced")
    Table = models.ForeignKey(
        "brands.POS_Table", on_delete=models.CASCADE, blank=True, null=True)
    ShippingAddress = models.ForeignKey(
        "brands.UserAdrress", on_delete=models.CASCADE, blank=True, null=True)
    TaxTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NonTaxTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'salesMasterLogs_salesMasterLog'
        verbose_name = _('salesMasterLog')
        verbose_name_plural = _('salesMasterLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class SalesOrderDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    SalesOrderDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    SalesOrderMasterID = models.BigIntegerField()
    # DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    # OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # CostPerPrice = models.DecimalField(
    #     default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    # TaxID = models.BigIntegerField(blank=True, null=True)
    # TaxType = models.CharField(max_length=128, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # Flavour = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)
    is_inclusive = models.BooleanField(default=False)
    KitchenPrint = models.BooleanField(default=False)

    class Meta:
        db_table = 'salesOrderDetails_salesOrderDetail'
        verbose_name = _('salesOrderDetail')
        verbose_name_plural = _('salesOrderDetails')
        unique_together = (('CompanyID', 'SalesOrderDetailsID', 'BranchID'),)
        ordering = ('-SalesOrderDetailsID',)

    def __unicode__(self):
        return str(self.SalesOrderDetailsID)


class SalesOrderDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    SalesOrderMasterID = models.BigIntegerField()
    # DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    # OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # CostPerPrice = models.DecimalField(
    #     default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    # TaxID = models.BigIntegerField(blank=True, null=True)
    # TaxType = models.CharField(max_length=128, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # Flavour = models.TextField(blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)
    is_inclusive = models.BooleanField(default=False)
    KitchenPrint = models.BooleanField(default=False)

    class Meta:
        db_table = 'salesOrderDetailLogs_salesOrderDetailLog'
        verbose_name = _('salesOrderDetailLog')
        verbose_name_plural = _('salesOrderDetailLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class SalesOrderMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    SalesOrderMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    # OrderNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    DeliveryDate = models.DateField(blank=True, null=True)
    # CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    # EmployeeID = models.BigIntegerField(blank=True, null=True)
    # SalesAccount = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    # Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # AdditionalCost = models.DecimalField(
    #     default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    IsActive = models.BooleanField(default=True)
    IsInvoiced = models.CharField(max_length=128, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    ShippingCharge = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    shipping_tax_amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxTypeID = models.CharField(max_length=128, blank=True, null=True)
    SAC = models.CharField(max_length=128, blank=True, null=True)
    SalesTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)
    Type = models.CharField(max_length=128, blank=True, null=True)
    ShippingAddress = models.ForeignKey(
        "brands.UserAdrress", on_delete=models.CASCADE, blank=True, null=True)
    Table = models.ForeignKey(
        "brands.POS_Table", on_delete=models.CASCADE, blank=True, null=True)
    Status = models.CharField(max_length=128, blank=True, null=True)
    TokenNumber = models.CharField(max_length=250, blank=True, null=True)
    DeliveryTime = models.CharField(max_length=128, blank=True, null=True)
    Phone = models.CharField(max_length=128, blank=True, null=True)
    CancelReason = models.ForeignKey(
        "brands.CancelReasons", on_delete=models.CASCADE, blank=True, null=True)
    InvoiceID = models.BigIntegerField(blank=True, null=True)
    OrderTime = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'salesOrderMasters_salesOrderMaster'
        verbose_name = _('salesOrderMaster')
        verbose_name_plural = _('salesOrderMasters')
        unique_together = (('CompanyID', 'SalesOrderMasterID', 'BranchID'),)
        ordering = ('-SalesOrderMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.SalesOrderMasterID)


class SalesOrderMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    # OrderNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    DeliveryDate = models.DateField(blank=True, null=True)
    # CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    # EmployeeID = models.BigIntegerField(blank=True, null=True)
    # SalesAccount = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    # Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # AdditionalCost = models.DecimalField(
    #     default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    IsActive = models.BooleanField(default=True)
    IsInvoiced = models.CharField(max_length=128, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    ShippingCharge = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    shipping_tax_amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxTypeID = models.CharField(max_length=128, blank=True, null=True)
    SAC = models.CharField(max_length=128, blank=True, null=True)
    SalesTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)
    Type = models.CharField(max_length=128, blank=True, null=True)
    ShippingAddress = models.ForeignKey(
        "brands.UserAdrress", on_delete=models.CASCADE, blank=True, null=True)
    Table = models.ForeignKey(
        "brands.POS_Table", on_delete=models.CASCADE, blank=True, null=True)
    Status = models.CharField(max_length=128, blank=True, null=True)
    TokenNumber = models.CharField(max_length=250, blank=True, null=True)
    DeliveryTime = models.CharField(max_length=128, blank=True, null=True)
    Phone = models.CharField(max_length=128, blank=True, null=True)
    CancelReason = models.ForeignKey(
        "brands.CancelReasons", on_delete=models.CASCADE, blank=True, null=True)
    InvoiceID = models.BigIntegerField(blank=True, null=True)
    OrderTime = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'salesOrderMasterLogs_salesOrderMasterLog'
        verbose_name = _('salesOrderMasterLog')
        verbose_name_plural = _('salesOrderMasterLogs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class SalesReturnDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    SalesReturnDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    SalesReturnMasterID = models.BigIntegerField(blank=True, null=True)
    DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Flavour = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    AddlDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)
    KFCPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Description = models.CharField(
        max_length=250, blank=True, null=True)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'salesReturnDetails_salesReturnDetail'
        verbose_name = _('salesReturnDetail')
        verbose_name_plural = _('salesReturnDetails')
        unique_together = (('CompanyID', 'SalesReturnDetailsID', 'BranchID'),)
        ordering = ('-SalesReturnDetailsID',)

    def __unicode__(self):
        return str(self.SalesReturnDetailsID)


class SalesReturnDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    SalesReturnMasterID = models.BigIntegerField(blank=True, null=True)
    DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Flavour = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    AddlDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BatchCode = models.CharField(max_length=128, blank=True, null=True)
    KFCPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Description = models.CharField(
        max_length=250, blank=True, null=True)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'salesReturnDetailLogs_salesReturnDetailLog'
        verbose_name = _('salesReturnDetailLog')
        verbose_name_plural = _('salesReturnDetailLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class SalesReturnMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    LoyaltyCustomerID = models.ForeignKey(
        "brands.LoyaltyCustomer", on_delete=models.CASCADE, blank=True, null=True)

    SalesReturnMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    VoucherDate = models.DateField(blank=True, null=True)
    RefferenceBillNo = models.CharField(max_length=128, blank=True, null=True)
    RefferenceBillDate = models.DateField(blank=True, null=True)
    CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    SalesAccount = models.BigIntegerField(blank=True, null=True)
    DeliveryMasterID = models.BigIntegerField(blank=True, null=True)
    OrderMasterID = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AdditionalCost = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashReceived = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BankAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TableID = models.BigIntegerField(blank=True, null=True)
    SeatNumber = models.CharField(max_length=128, blank=True, null=True)
    NoOfGuests = models.BigIntegerField(blank=True, null=True)
    INOUT = models.BooleanField(default=False)
    TokenNumber = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    IsPosted = models.BooleanField(default=False)
    SalesType = models.CharField(max_length=150, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=150, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)
    TaxTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NonTaxTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'salesReturnMasters_salesReturnMaster'
        verbose_name = _('salesReturnMaster')
        verbose_name_plural = _('salesReturnMasters')
        unique_together = (('CompanyID', 'SalesReturnMasterID', 'BranchID'),)
        ordering = ('-SalesReturnMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.SalesReturnMasterID)


class SalesReturnMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    LoyaltyCustomerID = models.ForeignKey(
        "brands.LoyaltyCustomer", on_delete=models.CASCADE, blank=True, null=True)

    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    VoucherDate = models.DateField(blank=True, null=True)
    RefferenceBillNo = models.CharField(max_length=128, blank=True, null=True)
    RefferenceBillDate = models.DateField(blank=True, null=True)
    CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    EmployeeID = models.BigIntegerField(blank=True, null=True)
    SalesAccount = models.BigIntegerField(blank=True, null=True)
    DeliveryMasterID = models.BigIntegerField(blank=True, null=True)
    OrderMasterID = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AdditionalCost = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashReceived = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CashAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BankAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TableID = models.BigIntegerField(blank=True, null=True)
    SeatNumber = models.CharField(max_length=128, blank=True, null=True)
    NoOfGuests = models.BigIntegerField(blank=True, null=True)
    INOUT = models.BooleanField(default=False)
    TokenNumber = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    IsPosted = models.BooleanField(default=False)
    SalesType = models.CharField(max_length=150, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=150, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'salesReturnMasterLogs_salesReturnMasterLog'
        verbose_name = _('salesReturnMasterLog')
        verbose_name_plural = _('salesReturnMasterLogs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class Settings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    SettingsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    PriceList = models.BigIntegerField(blank=True, null=True)
    GroupName = models.CharField(max_length=128, blank=True, null=True)
    SettingsType = models.CharField(max_length=128, blank=True, null=True)
    SettingsValue = models.CharField(max_length=128, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'settings_settings'
        verbose_name = _('settings')
        verbose_name_plural = _('settingses')
        unique_together = (('CompanyID', 'SettingsID', 'BranchID'),)
        ordering = ('-SettingsID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.SettingsID)


class Settings_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    PriceList = models.BigIntegerField(blank=True, null=True)
    GroupName = models.CharField(max_length=128, blank=True, null=True)
    SettingsType = models.CharField(max_length=128, blank=True, null=True)
    SettingsValue = models.CharField(max_length=128, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'settingsLog_settingsLog'
        verbose_name = _('settingsLog')
        verbose_name_plural = _('settingsLogs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class StockAdjustmentDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    StockAdjustmentDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    StockAdjustmentMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    ActualStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PhysicalStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Difference = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'stockAdjustmentDetails_stockAdjustmentDetails'
        verbose_name = _('stockAdjustmentDetails')
        verbose_name_plural = _('stockAdjustmentDetailses')
        unique_together = (
            ('CompanyID', 'StockAdjustmentDetailsID', 'BranchID'),)
        ordering = ('-StockAdjustmentDetailsID',)

    def __unicode__(self):
        return str(self.StockAdjustmentDetailsID)


class StockAdjustmentDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    StockAdjustmentMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    ActualStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PhysicalStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Difference = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'stockAdjustmentDetailsLog_stockAdjustmentDetailsLog'
        verbose_name = _('stockAdjustmentDetailsLog')
        verbose_name_plural = _('stockAdjustmentDetailsLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class StockAdjustmentMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    StockAdjustmentMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    GroupWise = models.BooleanField(default=False)
    ProductGroupID = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'stockAdjustmentMasters_stockAdjustmentMaster'
        verbose_name = _('stockAdjustmentMaster')
        verbose_name_plural = _('StockAdjustmentMasters')
        unique_together = (
            ('CompanyID', 'StockAdjustmentMasterID', 'BranchID'),)
        ordering = ('-StockAdjustmentMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.StockAdjustmentMasterID)


class StockAdjustmentMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    GroupWise = models.BooleanField(default=False)
    ProductGroupID = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'stockAdjustmentMasterLogs_stockAdjustmentMasterLog'
        verbose_name = _('stockAdjustmentMasterLog')
        verbose_name_plural = _('stockAdjustmentMasterLogs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class StockReceiptDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    StockReceiptDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    StockReceiptMasterID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'stockReceiptDetails_stockReceiptDetails'
        verbose_name = _('stockReceiptDetails')
        verbose_name_plural = _('stockReceiptDetailses')
        unique_together = (('CompanyID', 'StockReceiptDetailsID', 'BranchID'),)
        ordering = ('-StockReceiptDetailsID',)

    def __unicode__(self):
        return str(self.StockReceiptDetailsID)


class StockReceiptDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    StockReceiptMasterID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'stockReceiptDetailsLog_stockReceiptDetailsLog'
        verbose_name = _('stockReceiptDetailsLog')
        verbose_name_plural = _('stockReceiptDetailsLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class StockReceiptMaster_ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    StockReceiptMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseFromID = models.BigIntegerField(blank=True, null=True)
    WarehouseToID = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'stockReceiptMasterID_stockReceiptMasterID'
        verbose_name = _('stockReceiptMasterID')
        verbose_name_plural = _('stockReceiptMasterIDs')
        unique_together = (('CompanyID', 'StockReceiptMasterID', 'BranchID'),)
        ordering = ('-StockReceiptMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.StockReceiptMasterID)


class StockReceiptMasterID_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseFromID = models.BigIntegerField(blank=True, null=True)
    WarehouseToID = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'stockReceiptMasterIDLog_stockReceiptMasterIDLog'
        verbose_name = _('stockReceiptMasterIDLog')
        verbose_name_plural = _('stockReceiptMasterIDLogs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class StockTransferDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    StockTransferDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    StockTransferMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MaxRate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MaxAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'stockTransferDetails_stockTransferDetails'
        verbose_name = _('stockTransferDetails')
        verbose_name_plural = _('stockTransferDetailses')
        unique_together = (
            ('CompanyID', 'StockTransferDetailsID',),)
        ordering = ('-StockTransferDetailsID',)

    def __unicode__(self):
        return str(self.StockTransferDetailsID)


class StockTransferDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    StockTransferMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MaxRate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MaxAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'stockTransferDetailsLog_stockTransferDetailsLog'
        verbose_name = _('stockTransferDetailsLog')
        verbose_name_plural = _('stockTransferDetailsLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class StockTransferMaster_ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    StockTransferMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    TransferredByID = models.BigIntegerField(blank=True, null=True)
    WarehouseFromID = models.BigIntegerField(blank=True, null=True)
    WarehouseToID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MaxGrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    BranchFromID = models.BigIntegerField(default=1, blank=True, null=True)
    BranchToID = models.BigIntegerField(default=1, blank=True, null=True)

    class Meta:
        db_table = 'stockTransferMaster_ID_stockTransferMaster_ID'
        verbose_name = _('stockTransferMaster_ID')
        verbose_name_plural = _('stockTransferMaster_IDs')
        unique_together = (('CompanyID', 'StockTransferMasterID',),)
        ordering = ('-StockTransferMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.StockTransferMasterID)


class StockTransferMasterID_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    TransferredByID = models.BigIntegerField(blank=True, null=True)
    WarehouseFromID = models.BigIntegerField(blank=True, null=True)
    WarehouseToID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MaxGrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    BranchFromID = models.BigIntegerField(default=1, blank=True, null=True)
    BranchToID = models.BigIntegerField(default=1, blank=True, null=True)

    class Meta:
        db_table = 'stockTransferMaster_IDLog_stockTransferMaster_IDLog'
        verbose_name = _('stockTransferMaster_IDLog')
        verbose_name_plural = _('stockTransferMaster_IDLogs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class StockPosting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    StockPostingID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    Date = models.DateField(blank=True, null=True)
    VoucherMasterID = models.BigIntegerField(blank=True, null=True)
    VoucherDetailID = models.BigIntegerField(blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    BatchID = models.CharField(max_length=255, blank=True, null=True)
    WareHouseID = models.BigIntegerField(blank=True, null=True)
    QtyIn = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    QtyOut = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    pricelist = models.ForeignKey(
        "brands.PriceList", on_delete=models.CASCADE, blank=True, null=True)
    warehouse = models.ForeignKey(
        "brands.Warehouse", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'stockPosting_stockPosting'
        verbose_name = _('stockPosting')
        verbose_name_plural = _('stockPostings')
        unique_together = (('CompanyID', 'StockPostingID', 'BranchID'),)
        ordering = ('-StockPostingID', 'CreatedDate',)
        # indexes = [
        #     models.Index(fields=['StockPostingID',]),
        #     models.Index(fields=['Date',]),
        #     models.Index(fields=['VoucherMasterID',]),
        #     models.Index(fields=['VoucherType',]),
        #     models.Index(fields=['ProductID',]),
        #     models.Index(fields=['WareHouseID',]),
        #     models.Index(fields=['QtyIn',]),
        #     models.Index(fields=['QtyOut',]),
        #     models.Index(fields=['Rate',]),
        #     models.Index(fields=['PriceListID',]),
        # ]

    def __unicode__(self):
        return str(self.StockPostingID)


class StockPosting_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    Date = models.DateField(blank=True, null=True)
    VoucherMasterID = models.BigIntegerField(blank=True, null=True)
    VoucherDetailID = models.BigIntegerField(blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    BatchID = models.CharField(max_length=255, blank=True, null=True)
    WareHouseID = models.BigIntegerField(blank=True, null=True)
    QtyIn = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    QtyOut = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'stockPosting_Log_stockPosting_Log'
        verbose_name = _('stockPosting_Log')
        verbose_name_plural = _('stockPosting_Logs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class SalesDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    unq_id = models.BigIntegerField(default=0)
    SalesDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    ProductName = models.CharField(
        max_length=128, blank=True, null=True, default="default product name")
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    Flavour = models.TextField(blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    totalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsDeleted = models.BooleanField(default=False)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'salesDetails_salesDetailDummy'
        verbose_name = _('salesDetailDummy')
        verbose_name_plural = _('salesDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class SalesOrderDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    SalesOrderMasterID = models.BigIntegerField()
    DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Flavour = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'salesOrderDetails_salesOrderDetailDummy'
        verbose_name = _('salesOrderDetailDummy')
        verbose_name_plural = _('salesOrderDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class SalesReturnDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    unq_id = models.BigIntegerField(default=0)
    SalesReturnDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    SalesReturnMasterID = models.BigIntegerField(blank=True, null=True)
    DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Flavour = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    AddlDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsDeleted = models.BooleanField(default=False)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'salesReturnDetails_salesReturnDetailDummy'
        verbose_name = _('salesReturnDetailDummy')
        verbose_name_plural = _('salesReturnDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class PurchaseDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    unq_id = models.BigIntegerField(default=0)
    PurchaseDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    IsDeleted = models.BooleanField(default=False)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'purchasesDetails_purchasesDetailDummy'
        verbose_name = _('purchasesDetailDummy')
        verbose_name_plural = _('purchasesDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class PurchaseOrderDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    BatchID = models.BigIntegerField(blank=True, null=True)
    PurchaseOrderMasterID = models.BigIntegerField(blank=True, null=True)
    DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'purchasesOrderDetails_purchasesOrderDetailDummy'
        verbose_name = _('purchasesOrderDetailDummy')
        verbose_name_plural = _('purchasesOrderDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class PurchaseReturnDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    unq_id = models.BigIntegerField(default=0)
    PurchaseReturnDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    PurchaseReturnMasterID = models.BigIntegerField()
    DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    IsDeleted = models.BooleanField(default=False)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)
    AddlDiscPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    AddlDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'purchaseReturnDetails_purchaseReturnDetailDummy'
        verbose_name = _('purchaseReturnDetailDummy')
        verbose_name_plural = _('purchaseReturnDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class DamageStockDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    DamageStockMasterID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'damageStockDetails_damageStockDetailDummy'
        verbose_name = _('damageStockDetailDummy')
        verbose_name_plural = _('damageStockDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class OpeningStockDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    unq_id = models.BigIntegerField(default=0)
    BranchID = models.BigIntegerField()
    OpeningStockMasterID = models.BigIntegerField(blank=True, null=True)
    OpeningStockDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)
    IsDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'openingStockDetails_openingStockDetailDummy'
        verbose_name = _('openingStockDetailDummy')
        verbose_name_plural = _('openingStockDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class PaymentDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    PaymentMasterID = models.BigIntegerField(blank=True, null=True)
    PaymentGateway = models.BigIntegerField(blank=True, null=True)
    RefferenceNo = models.BigIntegerField(blank=True, null=True)
    CardNetwork = models.BigIntegerField(blank=True, null=True)
    PaymentStatus = models.BigIntegerField(blank=True, null=True)
    DueDate = models.DateField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Discount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Narration = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'paymentDetails_paymentDetailDummy'
        verbose_name = _('paymentDetailDummy')
        verbose_name_plural = _('paymentDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class POSHoldDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    POSHoldMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Flavour = models.TextField(blank=True, null=True)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'posHoldDetails_posHoldDetailDummy'
        verbose_name = _('posHoldDetailDummy')
        verbose_name_plural = _('posHoldDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class ReceiptDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    ReceiptMasterID = models.BigIntegerField(blank=True, null=True)
    PaymentGateway = models.BigIntegerField(blank=True, null=True)
    RefferenceNo = models.BigIntegerField(blank=True, null=True)
    CardNetwork = models.BigIntegerField(blank=True, null=True)
    PaymentStatus = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    DueDate = models.DateField(blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Discount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Narration = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'receiptDetails_receiptDetailDummy'
        verbose_name = _('receiptDetailDummy')
        verbose_name_plural = _('receiptDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class StockAdjustmentDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    StockAdjustmentMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    ActualStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PhysicalStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Difference = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'stockAdjustmentDetails_stockAdjustmentDetailsDummy'
        verbose_name = _('stockAdjustmentDetailsDummy')
        verbose_name_plural = _('stockAdjustmentDetailssDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class StockReceiptDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    StockReceiptMasterID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'stockReceiptDetails_stockReceiptDetailsDummy'
        verbose_name = _('stockReceiptDetailsDummy')
        verbose_name_plural = _('stockReceiptDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class StockTransferDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    unq_id = models.BigIntegerField(default=0)
    StockTransferDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    StockTransferMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'stockTransferDetails_stockTransferDetailsDummy'
        verbose_name = _('stockTransferDetailsDummy')
        verbose_name_plural = _('stockTransferDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class JournalDetailsDummy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    JournalDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    LedgerID = models.BigIntegerField(blank=True, null=True)
    Debit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Credit = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Narration = models.TextField(blank=True, null=True)
    detailID = models.BigIntegerField(default=0, blank=True, null=True)

    class Meta:
        db_table = 'journalDetails_journalDetailsDummy'
        verbose_name = _('journalDetailsDummy')
        verbose_name_plural = _('journalDetailsDummy')
        ordering = ('-BranchID',)

    def __unicode__(self):
        return str(self.BranchID)


class StockRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    StockRateID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    BatchID = models.BigIntegerField(blank=True, null=True)
    PurchasePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SalesPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Cost = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    WareHouseID = models.BigIntegerField(blank=True, null=True)
    Date = models.DateTimeField(blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'stockRate_stockRate'
        verbose_name = _('stockRate')
        verbose_name_plural = _('stockRates')
        unique_together = (('CompanyID', 'StockRateID', 'BranchID'),)
        ordering = ('-StockRateID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.StockRateID)


class StockTrans(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    StockTransID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    StockRateID = models.BigIntegerField(blank=True, null=True)
    DetailID = models.BigIntegerField(blank=True, null=True)
    MasterID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'stockTrans_stockTrans'
        verbose_name = _('stockTrans')
        verbose_name_plural = _('stockTrans')
        unique_together = (('CompanyID', 'StockTransID', 'BranchID'),)
        ordering = ('-StockTransID',)

    def __unicode__(self):
        return str(self.StockTransID)


class Bank(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BankID = models.BigIntegerField()
    BranchID = models.BigIntegerField(blank=True, null=True)
    LedgerCode = models.CharField(max_length=128, blank=True, null=True)
    Name = models.CharField(max_length=128)
    LedgerName = models.CharField(max_length=128, blank=True, null=True)
    AccountNumber = models.CharField(max_length=128, blank=True, null=True)
    CrOrDr = models.CharField(max_length=128, blank=True, null=True)
    BranchCode = models.CharField(max_length=128, blank=True, null=True)
    IFSCCode = models.CharField(max_length=128, blank=True, null=True)
    MICRCode = models.CharField(max_length=128, blank=True, null=True)
    Status = models.BooleanField(default=True)
    OpeningBalance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Address = models.TextField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    State = models.CharField(max_length=128, blank=True, null=True)
    Country = models.CharField(max_length=128, blank=True, null=True)
    PostalCode = models.CharField(max_length=128, blank=True, null=True)
    Phone = models.CharField(max_length=128, blank=True, null=True)
    Mobile = models.CharField(max_length=128, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'Bank_Bank'
        verbose_name = _('Bank')
        verbose_name_plural = _('Banks')
        unique_together = (('CompanyID', 'BankID', 'BranchID'),)
        ordering = ('-CreatedDate', 'BankID')

    def __unicode__(self):
        return str(self.BankID)


class Bank_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    LedgerCode = models.CharField(max_length=128, blank=True, null=True)
    Name = models.CharField(max_length=128)
    LedgerName = models.CharField(max_length=128, blank=True, null=True)
    AccountNumber = models.CharField(max_length=128, blank=True, null=True)
    CrOrDr = models.CharField(max_length=128, blank=True, null=True)
    BranchCode = models.CharField(max_length=128, blank=True, null=True)
    IFSCCode = models.CharField(max_length=128, blank=True, null=True)
    MICRCode = models.CharField(max_length=128, blank=True, null=True)
    Status = models.BooleanField(default=True)
    OpeningBalance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Address = models.TextField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    State = models.CharField(max_length=128, blank=True, null=True)
    Country = models.CharField(max_length=128, blank=True, null=True)
    PostalCode = models.CharField(max_length=128, blank=True, null=True)
    Phone = models.CharField(max_length=128, blank=True, null=True)
    Mobile = models.CharField(max_length=128, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'Bank_BankLog'
        verbose_name = _('BankLog')
        verbose_name_plural = _('BankLogs')
        ordering = ('-CreatedDate', 'ID')

    def __unicode__(self):
        return str(self.ID)


class Country(models.Model):
    # CompanyID = models.ForeignKey("brands.CompanySettings",on_delete=models.CASCADE,blank=True,null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CountryCode = models.CharField(max_length=128, blank=True, null=True)
    Country_Name = models.CharField(max_length=128, blank=True, null=True)
    Currency_Name = models.CharField(max_length=128, blank=True, null=True)
    Change = models.CharField(max_length=128, blank=True, null=True)
    Symbol = models.CharField(max_length=128, blank=True, null=True)
    FractionalUnits = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CurrencySymbolUnicode = models.CharField(
        max_length=128, blank=True, null=True)
    ISD_Code = models.CharField(max_length=128, blank=True, null=True)
    Flag = models.ImageField(upload_to='country-flags/', blank=True, null=True)
    Tax_Type = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'country_country'
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        ordering = ('Country_Name',)

    def __unicode__(self):
        return str(self.Country_Name)
        # return smart_text(self.Country_Name)


class State(models.Model):
    Country = models.ForeignKey(
        "brands.Country", on_delete=models.CASCADE, blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Name = models.CharField(max_length=128, blank=True, null=True)
    State_Type = models.CharField(max_length=128, blank=True, null=True)
    State_Code = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'state_state'
        verbose_name = _('state')
        verbose_name_plural = _('states')
        ordering = ('Name',)

    def __str__(self):
        return str(self.Name)


class BusinessType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Name = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'admin_business_type'
        verbose_name = _('business')
        verbose_name_plural = _('business')
        ordering = ('Name',)

    def __str__(self):
        return str(self.Name)


class TestImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    Name = models.CharField(max_length=128)
    Image = VersatileImageField(upload_to='uploads/', blank=True, null=True)

    class Meta:
        db_table = 'test_image'
        verbose_name = _('testImage')
        verbose_name_plural = _('testImages')
        ordering = ('-id',)

    def __unicode__(self):
        return str(self.id)


class TestFormModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ProductID = models.BigIntegerField()
    BranchID = models.BigIntegerField(blank=True, null=True)
    ProductCode = models.CharField(max_length=128, blank=True, null=True)
    ProductName = models.CharField(max_length=128, blank=True, null=True)
    DisplayName = models.CharField(max_length=128, blank=True, null=True)
    Description = models.TextField(blank=True, null=True)
    ProductGroupID = models.BigIntegerField(default=1, blank=True, null=True)
    BrandID = models.BigIntegerField(default=1, blank=True, null=True)
    InventoryType = models.CharField(max_length=128, blank=True, null=True)
    StockMinimum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    StockReOrder = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    StockMaximum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MarginPercent = models.CharField(max_length=128, blank=True, null=True)
    ProductImage = VersatileImageField(
        upload_to='uploads/', blank=True, null=True)
    WeighingCalcType = models.CharField(max_length=128, blank=True, null=True)
    PLUNo = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    GST = models.BigIntegerField(blank=True, null=True)
    VatID = models.BigIntegerField(default=1, blank=True, null=True)
    Tax1 = models.BigIntegerField(blank=True, null=True)
    Tax2 = models.BigIntegerField(blank=True, null=True)
    Tax3 = models.BigIntegerField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    IsWeighingScale = models.BooleanField(default=False)
    IsRawMaterial = models.BooleanField(default=False)
    IsFinishedProduct = models.BooleanField(default=False)
    IsSales = models.BooleanField(default=False)
    IsPurchase = models.BooleanField(default=False)
    IsFavourite = models.BooleanField(default=False)
    Active = models.BooleanField(default=False)

    class Meta:
        db_table = 'testForms_testForm'
        verbose_name = _('testForm')
        verbose_name_plural = _('testForms')
        ordering = ('-CreatedDate', 'ProductID')

    def __unicode__(self):
        return str(self.ProductID)


class TestFormSetModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    PriceListID = models.BigIntegerField()
    BranchID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    product = models.ForeignKey(
        "brands.TestFormModel", on_delete=models.CASCADE)
    UnitName = models.CharField(max_length=128, blank=True, null=True)
    DefaultUnit = models.BooleanField(default=False)
    SalesPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PurchasePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MRP = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    MultiFactor = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Barcode = models.CharField(max_length=128, blank=True, null=True)
    AutoBarcode = models.BigIntegerField(blank=True, null=True)
    SalesPrice1 = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SalesPrice2 = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SalesPrice3 = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UnitInSales = models.BooleanField(default=False)
    UnitInPurchase = models.BooleanField(default=False)
    UnitInReports = models.BooleanField(default=False)

    class Meta:
        db_table = 'testFormSet_testFormSet'
        verbose_name = _('testFormSet')
        verbose_name_plural = _('testFormSets')
        ordering = ('-PriceListID',)

    def __unicode__(self):
        return str(self.PriceListID)


class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    UnitID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    UnitName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    UQC = models.ForeignKey(
        "brands.UQCTable", blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'units_unit'
        verbose_name = _('unit')
        verbose_name_plural = _('units')
        unique_together = (('UnitID', 'BranchID', 'CompanyID'),)
        ordering = ('-CreatedDate', 'UnitID')

    class Admin:
        list_display = ('UnitID', 'BranchID', 'UnitName', 'Notes',
                        'CreatedUserID', 'UpdatedDate', 'Action',)

    def __unicode__(self):
        return str(self.UnitID)


class Unit_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.BigIntegerField()
    UnitName = models.CharField(max_length=128)
    Notes = models.TextField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'unitLogs_unitLog'
        verbose_name = _('unitLog')
        verbose_name_plural = _('unitLogss')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    user = models.ForeignKey(
        "auth.User", related_name="user%(class)s_objects", on_delete=models.CASCADE)
    DateOfBirth = models.DateField(blank=True, null=True)
    Country = models.ForeignKey(
        "brands.Country", on_delete=models.CASCADE, blank=True, null=True)
    Phone = models.BigIntegerField(blank=True, null=True)
    State = models.ForeignKey(
        "brands.State", on_delete=models.CASCADE, blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    Address = models.CharField(max_length=150, blank=True, null=True)
    Gender = models.CharField(max_length=150, blank=True, null=True)
    Language = models.CharField(default="english", max_length=150, blank=True, null=True)
    LastLoginToken = models.CharField(max_length=256, blank=True, null=True)
    LastLoginCompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    LastLoginTokenMobile = models.CharField(
        max_length=256, blank=True, null=True)
    VerificationToken = models.BigIntegerField(blank=True, null=True)
    VerificationTokenTime = models.DateTimeField(blank=True, null=True)
    TimeZone = models.CharField(
        default="Asia/Calcutta", max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'customer'
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ('user',)

    def __unicode__(self):
        return str(self.user)


class Activity_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    log_type = models.CharField(max_length=128, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    user = models.ForeignKey(
        "auth.User", related_name="user%(class)s_objects", on_delete=models.CASCADE)
    device_name = models.CharField(max_length=128, blank=True, null=True)
    location = models.CharField(max_length=256, blank=True, null=True)
    source = models.CharField(max_length=128, blank=True, null=True)
    action = models.CharField(
        max_length=128, blank=True, null=True, default="View")
    message = models.CharField(max_length=1000)
    description = models.CharField(max_length=512, blank=True, null=True)
    is_solved = models.BooleanField(default=False)

    class Meta:
        db_table = 'activity_log'
        verbose_name = _('Activity Log')
        verbose_name_plural = _('Activity Logs')
        ordering = ('-date', '-time',)

    def __unicode__(self):
        return str(self.id)


class ExcessStockMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ExcessStockMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'excessStockMaster_excessStockMaster'
        verbose_name = _('excessStockMaster')
        verbose_name_plural = _('excessStockMasters')
        unique_together = (('CompanyID', 'ExcessStockMasterID', 'BranchID'),)
        ordering = ('-ExcessStockMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ExcessStockMasterID)


class ExcessStockMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'excessStockMaster_log_excessStockMaster_log'
        verbose_name = _('excessStockMaster_log')
        verbose_name_plural = _('excessStockMasters_log')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class ExcessStockDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ExcessStockDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    ExcessStockMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Stock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    ExcessStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'excessStockDetails_excessStockDetails'
        verbose_name = _('excessStockDetails')
        verbose_name_plural = _('excessStockDetailses')
        unique_together = (('CompanyID', 'ExcessStockDetailsID', 'BranchID'),)
        ordering = ('-ExcessStockDetailsID',)

    def __unicode__(self):
        return str(self.ExcessStockDetailsID)


class ExcessStockDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    ExcessStockMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Stock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    ExcessStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'excessStockDetails_log_excessStockDetails_log'
        verbose_name = _('excessStockDetails_log')
        verbose_name_plural = _('excessStockDetailses_log')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class ShortageStockMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ShortageStockMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'shortageStockMaster_shortageStockMaster'
        verbose_name = _('shortageStockMaster')
        verbose_name_plural = _('shortageStockMasters')
        unique_together = (('CompanyID', 'ShortageStockMasterID', 'BranchID'),)
        ordering = ('-ShortageStockMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ShortageStockMasterID)


class ShortageStockMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'shortageStockMaster_log_shortageStockMaster_log'
        verbose_name = _('shortageStockMaster_log')
        verbose_name_plural = _('shortageStockMasters_log')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class ShortageStockDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ShortageStockDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    ShortageStockMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Stock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    ShortageStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'shortageStockDetails_shortageStockDetails'
        verbose_name = _('shortageStockDetails')
        verbose_name_plural = _('shortageStockDetailses')
        unique_together = (
            ('CompanyID', 'ShortageStockDetailsID', 'BranchID'),)
        ordering = ('-ShortageStockDetailsID',)

    def __unicode__(self):
        return str(self.ShortageStockDetailsID)


class ShortageStockDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    ShortageStockMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Stock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    ShortageStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'shortageStockDetails_log_shortageStockDetails_log'
        verbose_name = _('shortageStockDetails_log')
        verbose_name_plural = _('shortageStockDetailses_log')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class DamageStockMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    DamageStockMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'damageStockMaster_damageStockMaster'
        verbose_name = _('damageStockMaster')
        verbose_name_plural = _('damageStockMasters')
        unique_together = (('CompanyID', 'DamageStockMasterID', 'BranchID'),)
        ordering = ('-DamageStockMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.DamageStockMasterID)


class DamageStockMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'damageStockMaster_log_damageStockMaster_log'
        verbose_name = _('damageStockMaster_log')
        verbose_name_plural = _('damageStockMasters_log')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class DamageStockDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    DamageStockDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    DamageStockMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Stock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DamageStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'damageStockDetails_damageStockDetails'
        verbose_name = _('damageStockDetails')
        verbose_name_plural = _('damageStockDetailses')
        unique_together = (('CompanyID', 'DamageStockDetailsID', 'BranchID'),)
        ordering = ('-DamageStockDetailsID',)

    def __unicode__(self):
        return str(self.DamageStockDetailsID)


class DamageStockDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    DamageStockMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Stock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    DamageStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'damageStockDetails_log_damageStockDetails_log'
        verbose_name = _('damageStockDetails_log')
        verbose_name_plural = _('damageStockDetailses_log')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class UsedStockMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    UsedStockMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'usedStockMaster_usedStockMaster'
        verbose_name = _('usedStockMaster')
        verbose_name_plural = _('usedStockMasters')
        unique_together = (('CompanyID', 'UsedStockMasterID', 'BranchID'),)
        ordering = ('-UsedStockMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.UsedStockMasterID)


class UsedStockMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'usedStockMaster_log_usedStockMaster_log'
        verbose_name = _('usedStockMaster_log')
        verbose_name_plural = _('usedStockMasters_log')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class UsedStockDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    UsedStockDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    UsedStockMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Stock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    UsedStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'usedStockDetails_usedStockDetails'
        verbose_name = _('usedStockDetails')
        verbose_name_plural = _('usedStockDetailses')
        unique_together = (('CompanyID', 'UsedStockDetailsID', 'BranchID'),)
        ordering = ('-UsedStockDetailsID',)

    def __unicode__(self):
        return str(self.UsedStockDetailsID)


class UsedStockDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    UsedStockMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    Stock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    UsedStock = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'usedStockDetails_log_usedStockDetails_log'
        verbose_name = _('usedStockDetails_log')
        verbose_name_plural = _('usedStockDetailses_log')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class LoggedInUser(models.Model):
    user = models.OneToOneField(
        "auth.User", related_name='logged_in_user', on_delete=models.CASCADE)
    session_key = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        db_table = 'users_logged_in_user'
        verbose_name = _('logged in user')
        verbose_name_plural = _('logged in users')

    def __str__(self):
        return self.user.username


class PrintSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.CharField(max_length=128, null=True, blank=True)
    IsDefaultThermalPrinter = models.BooleanField(default=False)
    PageSize = models.CharField(max_length=128, null=True, blank=True)
    IsCompanyLogo = models.BooleanField(default=False)
    IsCompanyName = models.BooleanField(default=False)
    IsDescription = models.BooleanField(default=False)
    IsAddress = models.BooleanField(default=False)
    IsMobile = models.BooleanField(default=False)
    IsEmail = models.BooleanField(default=False)
    IsTaxNo = models.BooleanField(default=False)
    IsCRNo = models.BooleanField(default=False)
    IsCurrentBalance = models.BooleanField(default=False)
    SalesInvoiceTrName = models.CharField(
        max_length=128, null=True, blank=True)
    SalesOrderTrName = models.CharField(max_length=128, null=True, blank=True)
    SalesReturnTrName = models.CharField(max_length=128, null=True, blank=True)
    PurchaseInvoiceTrName = models.CharField(
        max_length=128, null=True, blank=True)
    PurchaseOrderTrName = models.CharField(
        max_length=128, null=True, blank=True)
    PurchaseReturnTrName = models.CharField(
        max_length=128, null=True, blank=True)
    CashRecieptTrName = models.CharField(max_length=128, null=True, blank=True)
    BankRecieptTrName = models.CharField(max_length=128, null=True, blank=True)
    CashPaymentTrName = models.CharField(max_length=128, null=True, blank=True)
    BankPaymentTrName = models.CharField(max_length=128, null=True, blank=True)
    IsInclusiveTaxUnitPrice = models.BooleanField(default=False)
    IsInclusiveTaxNetAmount = models.BooleanField(default=False)
    IsFlavour = models.BooleanField(default=False)
    IsShowDescription = models.BooleanField(default=False)
    IsTotalQuantity = models.BooleanField(default=False)
    IsTaxDetails = models.BooleanField(default=False)
    IsHSNCode = models.BooleanField(default=False)
    IsProductCode = models.BooleanField(default=False)
    IsReceivedAmount = models.BooleanField(default=False)
    SalesInvoiceFooter = models.CharField(
        max_length=128, null=True, blank=True)
    SalesReturnFooter = models.CharField(max_length=128, null=True, blank=True)
    SalesOrderFooter = models.CharField(max_length=128, null=True, blank=True)
    PurchaseInvoiceFooter = models.CharField(
        max_length=128, null=True, blank=True)
    PurchaseOrderFooter = models.CharField(
        max_length=128, null=True, blank=True)
    PurchaseReturnFooter = models.CharField(
        max_length=128, null=True, blank=True)
    CashRecieptFooter = models.CharField(max_length=128, null=True, blank=True)
    BankRecieptFooter = models.CharField(max_length=128, null=True, blank=True)
    CashPaymentFooter = models.CharField(max_length=128, null=True, blank=True)
    BankPaymentFooter = models.CharField(max_length=128, null=True, blank=True)
    TermsAndConditionsSales = models.CharField(
        max_length=512, null=True, blank=True)
    TermsAndConditionsPurchase = models.CharField(
        max_length=512, null=True, blank=True)
    TermsAndConditionsSaleEstimate = models.CharField(
        max_length=512, null=True, blank=True)

    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UpdatedUserID = models.BigIntegerField(blank=True, null=True)
    HeadFontSize = models.CharField(max_length=128, null=True, blank=True)
    BodyFontSize = models.CharField(max_length=128, null=True, blank=True)
    ContentFontSize = models.CharField(max_length=128, null=True, blank=True)
    FooterFontSize = models.CharField(max_length=128, null=True, blank=True)

    IsBankDetails = models.BooleanField(default=False)
    BankNameFooter = models.CharField(max_length=128, null=True, blank=True)
    AccountNumberFooter = models.CharField(
        max_length=128, null=True, blank=True)
    BranchIFCFooter = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        db_table = 'print_settings'
        verbose_name = _('print_settings')
        verbose_name_plural = _('print_settings')
        # unique_together = (('CompanyID', 'BranchID'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.id)


class BarcodeSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    One = models.CharField(max_length=128, null=True, blank=True)
    Two = models.CharField(max_length=128, null=True, blank=True)
    Three = models.CharField(max_length=128, null=True, blank=True)
    Four = models.CharField(max_length=128, null=True, blank=True)
    Five = models.CharField(max_length=128, null=True, blank=True)
    Six = models.CharField(max_length=128, null=True, blank=True)
    Seven = models.CharField(max_length=128, null=True, blank=True)
    Eight = models.CharField(max_length=128, null=True, blank=True)
    Nine = models.CharField(max_length=128, null=True, blank=True)
    Zero = models.CharField(max_length=128, null=True, blank=True)
    Dot = models.CharField(max_length=128, null=True, blank=True)
    size = models.CharField(max_length=128, null=True, blank=True)
    template = models.CharField(max_length=128, null=True, blank=True)
    Description = models.CharField(max_length=128, null=True, blank=True)
    IsCompanyName = models.BooleanField(default=False)
    IsProductName = models.BooleanField(default=False)
    IsPrice = models.BooleanField(default=False)
    IsCurrencyName = models.BooleanField(default=False)
    IsPriceCode = models.BooleanField(default=False)
    IsDescription = models.BooleanField(default=False)
    IsReceivedAmount = models.BooleanField(default=False)
    Is_MRP = models.BooleanField(default=True)

    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UpdatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'barcode_settings'
        verbose_name = _('barcode_settings')
        verbose_name_plural = _('barcode_settings')
        # unique_together = (('CompanyID', 'BranchID'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.id)


class Language(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.CharField(
        max_length=128, null=True, blank=True, default="en")
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'language'
        verbose_name = _('language')
        verbose_name_plural = _('language')
        ordering = ('-id',)

    def __unicode__(self):
        return str(self.id)


class ProductUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(upload_to='products_sheets/', max_length=254)
    is_process = models.BooleanField(default=False)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'product_upload'
        verbose_name = _('product upload')
        verbose_name_plural = _('product upload')
        ordering = ('-id',)

    def __unicode__(self):
        return str(self.id)


class Batch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ConnectID = models.BigIntegerField(blank=True, null=True)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    ManufactureDate = models.DateField(blank=True, null=True)
    ExpiryDate = models.DateField(blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    StockIn = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    StockOut = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PurchasePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SalesPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    WareHouseID = models.BigIntegerField(blank=True, null=True)
    Description = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    VoucherType = models.CharField(
        max_length=128, blank=True, null=True, default="PI")

    class Meta:
        db_table = 'batch_batch'
        verbose_name = _('batch')
        verbose_name_plural = _('batchs')
        unique_together = (('CompanyID', 'BranchID', 'BatchCode'),)
        ordering = ('CreatedDate',)

    def __unicode__(self):
        return str(self.BatchCode)


class WorkOrderDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    WorkOrderDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    WorkOrderMasterID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostSum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LogID = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'workOrderDetails_workOrderDetail'
        verbose_name = _('workOrderDetail')
        verbose_name_plural = _('workOrderDetails')
        unique_together = (('CompanyID', 'WorkOrderDetailsID', 'BranchID'),)
        ordering = ('-WorkOrderDetailsID',)

    def __unicode__(self):
        return str(self.WorkOrderDetailsID)


class WorkOrderDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    WorkOrderMasterID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostSum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'workOrderDetailLogs_workOrderDetailLog'
        verbose_name = _('workOrderDetailLog')
        verbose_name_plural = _('workOrderDetailLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class WorkOrderMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    WorkOrderMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    WareHouseID = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    ManufactureDate = models.DateField(blank=True, null=True)
    ExpiryDate = models.DateField(blank=True, null=True)
    ProductQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    CostSum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Weight = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandCostSum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(default=1,blank=True, null=True)

    class Meta:
        db_table = 'WorkOrderMasters_WorkOrderMaster'
        verbose_name = _('WorkOrderMaster')
        verbose_name_plural = _('WorkOrderMasters')
        unique_together = (('CompanyID', 'WorkOrderMasterID', 'BranchID'),)
        ordering = ('-WorkOrderMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.WorkOrderMasterID)


class WorkOrderMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    WareHouseID = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    ManufactureDate = models.DateField(blank=True, null=True)
    ExpiryDate = models.DateField(blank=True, null=True)
    ProductQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CostPerPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    CostSum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Weight = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandCostSum = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(default=1,blank=True, null=True)

    class Meta:
        db_table = 'WorkOrderMasterLogs_WorkOrderMasterLog'
        verbose_name = _('WorkOrderMasterLog')
        verbose_name_plural = _('WorkOrderMasterLogs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class UserTypeSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    UserType = models.ForeignKey(
        "brands.UserType", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    GroupName = models.CharField(max_length=150, blank=True, null=True)
    SettingsType = models.CharField(max_length=150, blank=True, null=True)
    SettingsValue = models.CharField(max_length=150, blank=True, null=True)
    Action = models.CharField(max_length=150, blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UpdatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'userTypeSettings_userTypeSettings'
        verbose_name = _('userTypeSettings')
        verbose_name_plural = _('userTypeSettings')
        ordering = ('CreatedDate',)

    def __unicode__(self):
        return str(self.id)


class UserTypeSettings_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TransactionID = models.BigIntegerField()
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    GroupName = models.CharField(max_length=150, blank=True, null=True)
    SettingsType = models.CharField(max_length=150, blank=True, null=True)
    SettingsValue = models.CharField(max_length=150, blank=True, null=True)
    Action = models.CharField(max_length=150, blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UpdatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'userTypeSettingsLog_userTypeSettingsLog'
        verbose_name = _('userTypeSettingsLog')
        verbose_name_plural = _('userTypeSettingsLog')
        ordering = ('CreatedDate',)

    def __unicode__(self):
        return str(self.id)


class SoftwareVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CurrentVersion = models.CharField(max_length=150, blank=True, null=True)
    MinimumVersion = models.CharField(max_length=150, blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UpdatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'software_version'
        verbose_name = _('Software Version')
        verbose_name_plural = _('Software Version')
        ordering = ('CreatedDate',)

    def __unicode__(self):
        return str(self.id)


class SoftwareVersionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TransactionID = models.CharField(max_length=250)
    CurrentVersion = models.CharField(
        max_length=150, blank=True, null=True, default="1")
    MinimumVersion = models.CharField(
        max_length=150, blank=True, null=True, default="1")
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UpdatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'software_version_log'
        verbose_name = _('Software Version Log')
        verbose_name_plural = _('Software Version Log')
        ordering = ('CreatedDate',)

    def __unicode__(self):
        return str(self.id)


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    Name = models.CharField(max_length=128)
    Code = models.CharField(max_length=128, blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'category'
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class CategoryLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    TransactionID = models.CharField(max_length=250)
    BranchID = models.BigIntegerField()
    Name = models.CharField(max_length=128)
    Code = models.CharField(max_length=128, blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'category_log'
        verbose_name = _('category log')
        verbose_name_plural = _('category logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class Holiday(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    HolidayID = models.BigIntegerField()

    Name = models.CharField(max_length=128)
    Description = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Full_day = models.BooleanField(default=False)
    FromTime = models.TimeField(auto_now=False, auto_now_add=False)
    ToTime = models.TimeField(auto_now=False, auto_now_add=False)
    is_RecurringHoliday = models.BooleanField(default=False)
    # is_RecurringHoliday == True
    HolidayType = models.CharField(max_length=128, blank=True, null=True)
    # WEEKLY
    is_Monday = models.BooleanField(default=False)
    is_Tuesday = models.BooleanField(default=False)
    is_Wednesday = models.BooleanField(default=False)
    is_Thursday = models.BooleanField(default=False)
    is_Friday = models.BooleanField(default=False)
    is_Saturday = models.BooleanField(default=False)
    is_Sunday = models.BooleanField(default=False)
    # Monthly
    Monthly_On = models.CharField(max_length=128, blank=True, null=True)

    Monthly_day = models.CharField(max_length=128, blank=True, null=True)
    Monthly_week = models.CharField(max_length=128, blank=True, null=True)
    Monthly_Weekday = models.CharField(max_length=128, blank=True, null=True)

    # Annually
    Annually_On = models.CharField(max_length=128, blank=True, null=True)

    Annually_month = models.CharField(max_length=128, blank=True, null=True)
    Annually_day = models.CharField(max_length=128, blank=True, null=True)

    Annually_week = models.CharField(max_length=128, blank=True, null=True)
    Annually_Weekday = models.CharField(max_length=128, blank=True, null=True)
    Annually_Weekmonth = models.CharField(
        max_length=128, blank=True, null=True)

    Annual_FromDate = models.DateField(blank=True, null=True)
    Annual_ToDate = models.DateField(blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'holiday'
        verbose_name = _('holiday')
        verbose_name_plural = _('holidays')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class Holiday_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    TransactionID = models.CharField(max_length=250)

    Name = models.CharField(max_length=128)
    Description = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Full_day = models.BooleanField(default=False)
    FromTime = models.TimeField(auto_now=False, auto_now_add=False)
    ToTime = models.TimeField(auto_now=False, auto_now_add=False)
    is_RecurringHoliday = models.BooleanField(default=False)
    # is_RecurringHoliday == True
    HolidayType = models.CharField(max_length=128, blank=True, null=True)
    # WEEKLY
    is_Monday = models.BooleanField(default=False)
    is_Tuesday = models.BooleanField(default=False)
    is_Wednesday = models.BooleanField(default=False)
    is_Thursday = models.BooleanField(default=False)
    is_Friday = models.BooleanField(default=False)
    is_Saturday = models.BooleanField(default=False)
    is_Sunday = models.BooleanField(default=False)
    # Monthly
    Monthly_On = models.CharField(max_length=128, blank=True, null=True)

    Monthly_day = models.CharField(max_length=128, blank=True, null=True)
    Monthly_week = models.CharField(max_length=128, blank=True, null=True)
    Monthly_Weekday = models.CharField(max_length=128, blank=True, null=True)

    # Annually
    Annually_On = models.CharField(max_length=128, blank=True, null=True)

    Annually_month = models.CharField(max_length=128, blank=True, null=True)
    Annually_day = models.CharField(max_length=128, blank=True, null=True)

    Annually_week = models.CharField(max_length=128, blank=True, null=True)
    Annually_Weekday = models.CharField(max_length=128, blank=True, null=True)
    Annually_Weekmonth = models.CharField(
        max_length=128, blank=True, null=True)

    Annual_FromDate = models.DateField(blank=True, null=True)
    Annual_ToDate = models.DateField(blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'holiday_log'
        verbose_name = _('holiday_log')
        verbose_name_plural = _('holiday logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class WorkingTime(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    Name = models.CharField(max_length=128)
    ShiftStartTime = models.TimeField(auto_now=False, auto_now_add=False)
    ShiftEndTime = models.TimeField(auto_now=False, auto_now_add=False)
    BreakStartTime = models.TimeField(auto_now=False, auto_now_add=False)
    BreakEndTime = models.TimeField(auto_now=False, auto_now_add=False)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'working_time'
        verbose_name = _('working time')
        verbose_name_plural = _('working times')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class WorkingTimeLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    TransactionID = models.CharField(max_length=250)
    BranchID = models.BigIntegerField()
    Name = models.CharField(max_length=128)
    ShiftStartTime = models.TimeField(auto_now=False, auto_now_add=False)
    ShiftEndTime = models.TimeField(auto_now=False, auto_now_add=False)
    BreakStartTime = models.TimeField(auto_now=False, auto_now_add=False)
    BreakEndTime = models.TimeField(auto_now=False, auto_now_add=False)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'working_time_log'
        verbose_name = _('working time log')
        verbose_name_plural = _('working time logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class DatabaseSyncTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    Name = models.CharField(max_length=128)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    DataSyncID = models.BigIntegerField()
    IsDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'database_sync'
        verbose_name = _('database sync')
        verbose_name_plural = _('database sync')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)
# ======uvais======


class SalesEstimateDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    SalesEstimateDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    SalesEstimateMasterID = models.BigIntegerField()
    # DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    # OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # CostPerPrice = models.DecimalField(
    #     default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    # TaxID = models.BigIntegerField(blank=True, null=True)
    # TaxType = models.CharField(max_length=128, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # Flavour = models.TextField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'salesEstimateDetails_salesEstimateDetail'
        verbose_name = _('salesEstimateDetail')
        verbose_name_plural = _('salesEstimateDetails')
        unique_together = (
            ('CompanyID', 'SalesEstimateDetailsID', 'BranchID'),)
        ordering = ('-SalesEstimateDetailsID',)

    def __unicode__(self):
        return str(self.SalesEstimateDetailsID)


class SalesEstimateDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    SalesEstimateMaster_LogID = models.BigIntegerField()
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    SalesEstimateMasterID = models.BigIntegerField()
    # DeliveryDetailsID = models.BigIntegerField(blank=True, null=True)
    # OrderDetailsID = models.BigIntegerField(blank=True, null=True)
    ProductID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    FreeQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    UnitPrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    InclusivePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RateWithTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # CostPerPrice = models.DecimalField(
    #     default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    # TaxID = models.BigIntegerField(blank=True, null=True)
    # TaxType = models.CharField(max_length=128, blank=True, null=True)
    DiscountPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrossAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # Flavour = models.TextField(blank=True, null=True)
    TAX1Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Perc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    KFCAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    BatchCode = models.CharField(max_length=255, blank=True, null=True)
    ProductTaxID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'salesEstimateDetailLogs_salesEstimateDetailLog'
        verbose_name = _('salesEstimateDetailLog')
        verbose_name_plural = _('salesEstimateDetailLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class SalesEstimateMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    SalesEstimateMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    # OrderNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    DeliveryDate = models.DateField(blank=True, null=True)
    # CreditPeriod = models.BigIntegerField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    # EmployeeID = models.BigIntegerField(blank=True, null=True)
    # SalesAccount = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    # Address3 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    # AdditionalCost = models.DecimalField(
    #     default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)
    Status = models.CharField(default="N",max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'salesEstimateMasters_salesEstimateMaster'
        verbose_name = _('salesEstimateMaster')
        verbose_name_plural = _('salesEstimateMasters')
        unique_together = (('CompanyID', 'SalesEstimateMasterID', 'BranchID'),)
        ordering = ('-SalesEstimateMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.SalesEstimateMasterID)


class SalesEstimateMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    DeliveryDate = models.DateField(blank=True, null=True)
    LedgerID = models.BigIntegerField(blank=True, null=True)
    PriceCategoryID = models.BigIntegerField(blank=True, null=True)
    CustomerName = models.CharField(max_length=128)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    FinacialYearID = models.BigIntegerField(blank=True, null=True)
    TotalTax = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    IsActive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX1Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX2Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TAX3Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Country_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    State_of_Supply = models.CharField(max_length=128, blank=True, null=True)
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    VAT_Treatment = models.CharField(max_length=128, blank=True, null=True)
    Status = models.CharField(default="N",max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'salesEstimateMasterLogs_salesEstimateMasterLog'
        verbose_name = _('salesEstimateMasterLog')
        verbose_name_plural = _('salesEstimateMasterLogs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class SalaryComponent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    SalaryComponentID = models.BigIntegerField()

    Name = models.CharField(max_length=128)
    Description = models.CharField(max_length=128)
    ComponentType = models.CharField(max_length=128)
    ExpressionType = models.CharField(max_length=128)
    ExpressionValue = models.CharField(max_length=128)
    Status = models.BooleanField(default=False)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'salary_component'
        verbose_name = _('salary_component')
        verbose_name_plural = _('salary_components')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class SalaryComponent_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    SalaryComponentID = models.BigIntegerField()

    Name = models.CharField(max_length=128)
    Description = models.CharField(max_length=128)
    ComponentType = models.CharField(max_length=128)
    ExpressionType = models.CharField(max_length=128)
    ExpressionValue = models.CharField(max_length=128)
    Status = models.BooleanField(default=False)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'salary_component_log'
        verbose_name = _('salary_component_log')
        verbose_name_plural = _('salary_component_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class SalaryKit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    SalaryKitID = models.BigIntegerField()

    # DepartmentId = models.ForeignKey(
    #     "brands.Department", on_delete=models.CASCADE, blank=True, null=True)
    # DesignationId = models.ForeignKey(
    #     "brands.Designation", on_delete=models.CASCADE, blank=True, null=True)

    DepartmentID = models.BigIntegerField()
    DesignationID = models.BigIntegerField()
    BasicSalaryId = models.ForeignKey(
        "brands.SalaryComponent", on_delete=models.CASCADE, blank=True, null=True)

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    EmployeeCode = models.CharField(max_length=128, blank=True, null=True)
    CategoryId = models.ForeignKey(
        "brands.Category", on_delete=models.CASCADE, blank=True, null=True)

    Type = models.CharField(max_length=128)
    SalaryFreequency = models.CharField(max_length=128)
    SalaryComponentType = models.CharField(max_length=128)
    Date = models.DateField(max_length=128)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'salary_kit'
        verbose_name = _('salary_kit')
        verbose_name_plural = _('salary_kits')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class SalaryKit_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    SalaryKitID = models.BigIntegerField()

    DepartmentID = models.BigIntegerField()
    DesignationID = models.BigIntegerField()
    BasicSalaryId = models.ForeignKey(
        "brands.SalaryComponent", on_delete=models.CASCADE, blank=True, null=True)

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    EmployeeCode = models.CharField(max_length=128, blank=True, null=True)
    CategoryId = models.ForeignKey(
        "brands.Category", on_delete=models.CASCADE, blank=True, null=True)

    Type = models.CharField(max_length=128)
    SalaryFreequency = models.CharField(max_length=128)
    SalaryComponentType = models.CharField(max_length=128)
    Date = models.DateField(max_length=128)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'salary_kit_log'
        verbose_name = _('salary_kit_log')
        verbose_name_plural = _('salary_kit_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class SalaryKitDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    SalaryKitID = models.BigIntegerField()
    SalaryComponentID = models.ForeignKey(
        "brands.SalaryComponent", on_delete=models.CASCADE, blank=True, null=True)

    ExpressionType = models.CharField(max_length=128)
    ComponentType = models.CharField(max_length=128)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'salary_kit_detail'
        verbose_name = _('salary_kit_detail')
        verbose_name_plural = _('salary_kit_details')
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.SalaryKitID)


class SalaryKitDetails_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    SalaryKitID = models.BigIntegerField()
    SalaryComponentID = models.ForeignKey(
        "brands.SalaryComponent", on_delete=models.CASCADE, blank=True, null=True)

    ExpressionType = models.CharField(max_length=128)
    ComponentType = models.CharField(max_length=128)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'salary_kit_detail_log'
        verbose_name = _('salary_kit_detail_log')
        verbose_name_plural = _('salary_kit_detail_logs')
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.SalaryKitID)


class SalaryPeriod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    SalaryPeriodID = models.BigIntegerField()

    Name = models.CharField(max_length=128)
    Note = models.CharField(max_length=128)
    Year = models.CharField(max_length=128)
    FromDate = models.DateField(blank=True, null=True)
    ToDate = models.DateField(blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'salary_period'
        verbose_name = _('salary_period')
        verbose_name_plural = _('salary_periods')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class SalaryPeriod_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    SalaryPeriodID = models.BigIntegerField()

    Name = models.CharField(max_length=128)
    Note = models.CharField(max_length=128)
    Year = models.CharField(max_length=128)
    FromDate = models.DateField(blank=True, null=True)
    ToDate = models.DateField(blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'salary_period_log'
        verbose_name = _('salary_period_log')
        verbose_name_plural = _('salary_period_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LeaveType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LeaveTypeID = models.BigIntegerField()

    Name = models.CharField(max_length=128)
    Type = models.CharField(max_length=128)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'leave_type'
        verbose_name = _('leave_type')
        verbose_name_plural = _('leave_types')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LeaveType_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LeaveTypeID = models.BigIntegerField()

    Name = models.CharField(max_length=128)
    Type = models.CharField(max_length=128)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'leave_type_log'
        verbose_name = _('leave_type_log')
        verbose_name_plural = _('leave_type_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LoanType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LoanTypeID = models.BigIntegerField()

    Name = models.CharField(max_length=128)
    Interest = models.CharField(max_length=128)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'loan_type'
        verbose_name = _('loan_type')
        verbose_name_plural = _('loan_types')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LoanType_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LoanTypeID = models.BigIntegerField()

    Name = models.CharField(max_length=128)
    Interest = models.CharField(max_length=128)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'loan_type_log'
        verbose_name = _('loan_type_log')
        verbose_name_plural = _('loan_type_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class Leave(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LeaveID = models.BigIntegerField()

    FinancialYear = models.CharField(max_length=128)
    PreviousYear = models.CharField(max_length=128)
    Type = models.CharField(max_length=128)
    DepartmentID = models.BigIntegerField()
    DesignationID = models.BigIntegerField()
    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    EmployeeCode = models.CharField(max_length=128, blank=True, null=True)
    CategoryId = models.ForeignKey(
        "brands.Category", on_delete=models.CASCADE, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'leave'
        verbose_name = _('leave')
        verbose_name_plural = _('leaves')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LeaveDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LeaveID = models.ForeignKey(
        "brands.Leave", on_delete=models.CASCADE, blank=True, null=True)

    Type = models.CharField(max_length=128)

    LeaveTypeID = models.ForeignKey(
        "brands.LeaveType", on_delete=models.CASCADE, blank=True, null=True)
    Days = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'leave_detail'
        verbose_name = _('leave_detail')
        verbose_name_plural = _('leave_details')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LeaveDetails_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LeaveID = models.ForeignKey(
        "brands.Leave", on_delete=models.CASCADE, blank=True, null=True)

    Type = models.CharField(max_length=128)

    LeaveTypeID = models.ForeignKey(
        "brands.LeaveType", on_delete=models.CASCADE, blank=True, null=True)
    Days = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'leave_detail_log'
        verbose_name = _('leave_detail_log')
        verbose_name_plural = _('leave_detail_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class Leave_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LeaveID = models.BigIntegerField()

    FinancialYear = models.CharField(max_length=128)
    PreviousYear = models.CharField(max_length=128)
    Type = models.CharField(max_length=128)
    DepartmentID = models.BigIntegerField()
    DesignationID = models.BigIntegerField()
    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    EmployeeCode = models.CharField(max_length=128, blank=True, null=True)
    CategoryId = models.ForeignKey(
        "brands.Category", on_delete=models.CASCADE, blank=True, null=True)
    Balance = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'leave_log'
        verbose_name = _('leave_log')
        verbose_name_plural = _('leave_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class AttendanceMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    AttendanceMasterID = models.BigIntegerField()

    Shift = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField()
    DepartmentID = models.BigIntegerField()
    DesignationID = models.BigIntegerField()
    CategoryId = models.ForeignKey(
        "brands.Category", on_delete=models.CASCADE, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'attendance_master'
        verbose_name = _('attendance_master')
        verbose_name_plural = _('attendance_masters')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class AttendanceMaster_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    AttendanceMasterID = models.BigIntegerField()

    Shift = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField()
    DepartmentID = models.BigIntegerField()
    DesignationID = models.BigIntegerField()
    CategoryId = models.ForeignKey(
        "brands.Category", on_delete=models.CASCADE, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'attendance_master_log'
        verbose_name = _('attendance_master_log')
        verbose_name_plural = _('attendance_master_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)
# =============


class AttendanceDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    AttendanceId = models.ForeignKey(
        "brands.AttendanceMaster", on_delete=models.CASCADE, blank=True, null=True)

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    EmployeeCode = models.CharField(max_length=128, blank=True, null=True)
    Status = models.CharField(max_length=128, blank=True, null=True)
    ShiftStartTime = models.TimeField(auto_now=False, auto_now_add=False)
    ShiftEndTime = models.TimeField(auto_now=False, auto_now_add=False)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'attendance_detail'
        verbose_name = _('attendance_detail')
        verbose_name_plural = _('attendance_details')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class AttendanceDetail_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    AttendanceId = models.ForeignKey(
        "brands.AttendanceMaster", on_delete=models.CASCADE, blank=True, null=True)

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    EmployeeCode = models.CharField(max_length=128, blank=True, null=True)
    Status = models.CharField(max_length=128, blank=True, null=True)
    ShiftStartTime = models.TimeField(auto_now=False, auto_now_add=False)
    ShiftEndTime = models.TimeField(auto_now=False, auto_now_add=False)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'attendance_detail_log'
        verbose_name = _('attendance_detail_log')
        verbose_name_plural = _('attendance_detail_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class SerialNumbers(models.Model):
    SerialNoID = models.AutoField(primary_key=True)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField(blank=True, null=True, default=1)
    SerialNo = models.CharField(
        max_length=128, blank=True, null=True)
    ItemCode = models.CharField(
        max_length=128, blank=True, null=True)
    SalesMasterID = models.BigIntegerField(blank=True, null=True)
    SalesDetailsID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'serailNos_serailNos'
        verbose_name = _('serailNos')
        verbose_name_plural = _('serailNoss')
        ordering = ('-SerialNoID',)

    def __unicode__(self):
        return str(self.SerialNoID)


class AdvanceRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    AdvanceRequestID = models.BigIntegerField()

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NumOfInstalment = models.CharField(max_length=128, blank=True, null=True)
    InstalmentAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RepaymentDate = models.DateField()
    Status = models.CharField(max_length=128, blank=True, null=True)

    # payment
    ModeOfPayment = models.CharField(max_length=128, blank=True, null=True)
    PaymentAccount = models.CharField(max_length=128, blank=True, null=True)
    PaymentAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'advance_request'
        verbose_name = _('advance_request')
        verbose_name_plural = _('advance_requests')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class AdvanceRequest_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    AdvanceRequestID = models.BigIntegerField()

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NumOfInstalment = models.CharField(max_length=128, blank=True, null=True)
    InstalmentAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RepaymentDate = models.DateField()
    Status = models.CharField(max_length=128, blank=True, null=True)

    # payment
    ModeOfPayment = models.CharField(max_length=128, blank=True, null=True)
    PaymentAccount = models.CharField(max_length=128, blank=True, null=True)
    PaymentAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'advance_request_log'
        verbose_name = _('advance_request_log')
        verbose_name_plural = _('advance_request_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LoanRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LoanRequestID = models.BigIntegerField()

    LoanTypeID = models.ForeignKey(
        "brands.LoanType", on_delete=models.CASCADE, blank=True, null=True)

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NumOfInstalment = models.CharField(max_length=128, blank=True, null=True)
    InstalmentAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Interest = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RepaymentDate = models.DateField()
    Status = models.CharField(max_length=128, blank=True, null=True)

    # payment
    ModeOfPayment = models.CharField(max_length=128, blank=True, null=True)
    PaymentAccount = models.CharField(max_length=128, blank=True, null=True)
    PaymentAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'loan_request'
        verbose_name = _('loan_request')
        verbose_name_plural = _('loan_requests')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LoanRequest_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LoanRequestID = models.BigIntegerField()

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    LoanTypeID = models.ForeignKey(
        "brands.LoanType", on_delete=models.CASCADE, blank=True, null=True)

    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NumOfInstalment = models.CharField(max_length=128, blank=True, null=True)
    InstalmentAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Interest = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RepaymentDate = models.DateField()
    Status = models.CharField(max_length=128, blank=True, null=True)

    # payment
    ModeOfPayment = models.CharField(max_length=128, blank=True, null=True)
    PaymentAccount = models.CharField(max_length=128, blank=True, null=True)
    PaymentAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'loan_request_log'
        verbose_name = _('loan_request_log')
        verbose_name_plural = _('loan_request_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class RelieveRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    RelieveRequestID = models.BigIntegerField()

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    RequestDate = models.DateField()
    Reportto = models.CharField(max_length=128, blank=True, null=True)
    ReliveType = models.CharField(max_length=128, blank=True, null=True)
    ReasonforRelive = models.CharField(max_length=128, blank=True, null=True)

    # Leave Approval
    Status = models.CharField(max_length=128, blank=True, null=True)
    ApprovedBy = models.BigIntegerField(blank=True, null=True)
    ApprovedDate = models.DateField(blank=True, null=True)
    ReasonforApprove = models.CharField(max_length=128, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'relieve_request'
        verbose_name = _('relieve_request')
        verbose_name_plural = _('relieve_requests')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class RelieveRequest_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    RelieveRequestID = models.BigIntegerField()

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    RequestDate = models.DateField()
    Reportto = models.CharField(max_length=128, blank=True, null=True)
    ReliveType = models.CharField(max_length=128, blank=True, null=True)
    ReasonforRelive = models.CharField(max_length=128, blank=True, null=True)
    # Leave Approval
    Status = models.CharField(max_length=128, blank=True, null=True)
    ApprovedBy = models.BigIntegerField(blank=True, null=True)
    ApprovedDate = models.DateField(blank=True, null=True)
    ReasonforApprove = models.CharField(max_length=128, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'relieve_request_log'
        verbose_name = _('relieve_request_log')
        verbose_name_plural = _('relieve_request_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LeaveRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LeaveRequestID = models.BigIntegerField()

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    FromDate = models.DateField()
    ToDate = models.DateField()
    Reportto = models.CharField(max_length=128, blank=True, null=True)
    LeaveTypeID = models.ForeignKey(
        "brands.LeaveType", on_delete=models.CASCADE, blank=True, null=True)
    ReasonforLeave = models.CharField(max_length=128, blank=True, null=True)

    # Leave Approval
    Status = models.CharField(max_length=128, blank=True, null=True)
    ApprovedBy = models.BigIntegerField(blank=True, null=True)
    ApprovedDate = models.DateField(blank=True, null=True)
    ReasonforApprove = models.CharField(max_length=128, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'leave_request'
        verbose_name = _('leave_request')
        verbose_name_plural = _('leave_requests')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LeaveRequest_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LeaveRequestID = models.BigIntegerField()

    EmployeeId = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    FromDate = models.DateField()
    ToDate = models.DateField()
    Reportto = models.CharField(max_length=128, blank=True, null=True)
    LeaveTypeID = models.ForeignKey(
        "brands.LeaveType", on_delete=models.CASCADE, blank=True, null=True)
    ReasonforLeave = models.CharField(max_length=128, blank=True, null=True)
    # Leave Approval
    Status = models.CharField(max_length=128, blank=True, null=True)
    ApprovedBy = models.BigIntegerField(blank=True, null=True)
    ApprovedDate = models.DateField(blank=True, null=True)
    ReasonforApprove = models.CharField(max_length=128, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'leave_request_log'
        verbose_name = _('leave_request_log')
        verbose_name_plural = _('leave_request_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


# class Notification(models.Model):
#     user = models.ForeignKey("auth.User",related_name="user_%(class)s_objects",on_delete=models.CASCADE)
#     who = models.ForeignKey("auth.User",blank=True,null=True,related_name="who_%(class)s_objects",on_delete=models.CASCADE)

#     subject = models.TextField(blank=True,null=True)
#     description = models.TextField(blank=True,null=True)

#     is_read = models.BooleanField(default=False)
#     is_deleted = models.BooleanField(default=False)
#     time = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'users_notification'
#         verbose_name = _('notification')
#         verbose_name_plural = _('notifications')
#         ordering = ('-time',)

#     def __unicode__(self):
#         return self.subject.name


class LoyaltyCustomer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LoyaltyCustomerID = models.BigIntegerField()

    # MobileNo = models.CharField(max_length=128)
    MobileNo = models.CharField(
        max_length=16,
        validators=[
            RegexValidator(r'^\d{1,10}$')
        ]
    )
    FirstName = models.CharField(max_length=128, blank=True, null=True)
    LastName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    Point_Value = models.CharField(max_length=128, blank=True, null=True)
    CurrentPoint = models.CharField(max_length=128)

    AccountLedgerID = models.ForeignKey(
        "brands.AccountLedger", on_delete=models.CASCADE, blank=True, null=True)
    CardNumber = models.CharField(max_length=128)
    CardTypeID = models.ForeignKey(
        "brands.TransactionTypes", related_name="type_%(class)s_objects", on_delete=models.CASCADE, blank=True, null=True)
    CardStatusID = models.ForeignKey(
        "brands.TransactionTypes", related_name="status_%(class)s_objects", on_delete=models.CASCADE, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'loyality_customer'
        verbose_name = _('loyality_customer')
        verbose_name_plural = _('loyality_customers')
        unique_together = (('CompanyID', 'BranchID', 'MobileNo'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LoyaltyCustomer_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LoyaltyCustomerID = models.BigIntegerField()

    CurrentPoint = models.CharField(max_length=128)
    MobileNo = models.CharField(max_length=128)
    Point_Value = models.CharField(max_length=128, blank=True, null=True)
    FirstName = models.CharField(max_length=128, blank=True, null=True)
    LastName = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    AccountLedgerID = models.ForeignKey(
        "brands.AccountLedger", on_delete=models.CASCADE, blank=True, null=True)
    CardNumber = models.CharField(max_length=128)
    CardTypeID = models.ForeignKey(
        "brands.TransactionTypes", related_name="type_%(class)s_objects", on_delete=models.CASCADE, blank=True, null=True)
    CardStatusID = models.ForeignKey(
        "brands.TransactionTypes", related_name="status_%(class)s_objects", on_delete=models.CASCADE, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'loyality_customer_log'
        verbose_name = _('loyality_customer_log')
        verbose_name_plural = _('loyality_customer_logs')
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LoyaltyProgram(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LoyaltyProgramID = models.BigIntegerField()

    Calculate_with = models.CharField(max_length=128, blank=True, null=True)
    ProductType = models.CharField(max_length=128, blank=True, null=True)

    Name = models.CharField(max_length=128, blank=True, null=True)
    FromDate = models.DateField(blank=True, null=True)
    ToDate = models.DateField(blank=True, null=True)
    NoOFDayExpPoint = models.CharField(max_length=128, blank=True, null=True)
    CardTypeID = models.ForeignKey(
        "brands.TransactionTypes", related_name="type_%(class)s_objects", on_delete=models.CASCADE, blank=True, null=True)

    MinimumSalePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount_Point = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    Percentage = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    product = models.ForeignKey("brands.Product", related_name="type_%(class)s_objects",
                                on_delete=models.CASCADE, blank=True, null=True)
    # productcategory = models.ForeignKey("brands.ProductCategory",related_name="type_%(class)s_objects", on_delete=models.CASCADE, blank=True, null=True)
    # productgroup = models.ForeignKey("brands.ProductGroup",related_name="type_%(class)s_objects", on_delete=models.CASCADE, blank=True, null=True)
    ProductGroupIDs = models.CharField(max_length=128, blank=True, null=True)
    ProductCategoryIDs = models.CharField(
        max_length=128, blank=True, null=True)
    is_offer = models.BooleanField(default=False)
    is_Return_MinimumSalePrice = models.BooleanField(default=False)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'loyality_program'
        verbose_name = _('loyality_program')
        verbose_name_plural = _('loyality_programs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LoyaltyProgram_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    LoyaltyProgramID = models.BigIntegerField()
    is_Return_MinimumSalePrice = models.BooleanField(default=False)

    ProductType = models.CharField(max_length=128, blank=True, null=True)
    Calculate_with = models.CharField(max_length=128, blank=True, null=True)

    Name = models.CharField(max_length=128, blank=True, null=True)
    FromDate = models.DateField(blank=True, null=True)
    ToDate = models.DateField(blank=True, null=True)
    NoOFDayExpPoint = models.CharField(max_length=128, blank=True, null=True)
    CardTypeID = models.ForeignKey(
        "brands.TransactionTypes", related_name="type_%(class)s_objects", on_delete=models.CASCADE, blank=True, null=True)

    MinimumSalePrice = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Amount_Point = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    Percentage = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    product = models.ForeignKey("brands.Product", related_name="type_%(class)s_objects",
                                on_delete=models.CASCADE, blank=True, null=True)
    ProductGroupIDs = models.CharField(max_length=128, blank=True, null=True)
    ProductCategoryIDs = models.CharField(
        max_length=128, blank=True, null=True)
    is_offer = models.BooleanField(default=False)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'loyality_program_log'
        verbose_name = _('loyality_program_log')
        verbose_name_plural = _('loyality_program_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LoyaltyPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)

    is_Radeem = models.BooleanField(default=False)

    BranchID = models.BigIntegerField()
    LoyaltyPointID = models.BigIntegerField()
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    VoucherMasterID = models.BigIntegerField(blank=True, null=True)
    # VoucherMasterID = models.ForeignKey(
    #     "brands.SalesMaster", on_delete=models.CASCADE, blank=True, null=True)
    LoyaltyProgramID = models.ForeignKey(
        "brands.LoyaltyProgram", on_delete=models.CASCADE, blank=True, null=True)
    Point = models.CharField(max_length=128, blank=True, null=True)
    Radeemed_Point = models.CharField(max_length=128, blank=True, null=True)
    Value = models.CharField(max_length=128, blank=True, null=True)
    ExpiryDate = models.DateField(blank=True, null=True)
    LoyaltyCustomerID = models.ForeignKey(
        "brands.LoyaltyCustomer", on_delete=models.CASCADE, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'loyalty_point'
        verbose_name = _('loyalty_point')
        verbose_name_plural = _('loyalty_points')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class LoyaltyPoint_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    is_Radeem = models.BooleanField(default=False)

    BranchID = models.BigIntegerField()
    LoyaltyPointID = models.BigIntegerField()
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    VoucherMasterID = models.BigIntegerField(blank=True, null=True)
    Value = models.CharField(max_length=128, blank=True, null=True)

    # VoucherMasterID = models.ForeignKey(
    #     "brands.SalesMaster", on_delete=models.CASCADE, blank=True, null=True)
    LoyaltyProgramID = models.ForeignKey(
        "brands.LoyaltyProgram", on_delete=models.CASCADE, blank=True, null=True)
    Radeemed_Point = models.CharField(max_length=128, blank=True, null=True)
    Point = models.CharField(max_length=128, blank=True, null=True)
    ExpiryDate = models.DateField(blank=True, null=True)
    LoyaltyCustomerID = models.ForeignKey(
        "brands.LoyaltyCustomer", on_delete=models.CASCADE, blank=True, null=True)

    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")

    class Meta:
        db_table = 'loyalty_point_log'
        verbose_name = _('loyalty_point_log')
        verbose_name_plural = _('loyalty_point_logs')
        unique_together = (('CompanyID', 'BranchID', 'id'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.BrandID)


class ProductDemo(models.Model):
    image = VersatileImageField(blank=True, null=True)
    rate = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)

    class Meta:
        db_table = 'product_demo'
        verbose_name = _('product_demo')
        verbose_name_plural = _('product_demo')

    def __unicode__(self):
        return str(self.name)


class UQCTable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    UQC_Name = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'UQC_UQC'
        verbose_name = _('UQC')
        verbose_name_plural = _('UQCs')
        ordering = ('UQC_Name',)

    def __str__(self):
        return str(self.UQC_Name)


class Edition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Name = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'edition_edition'
        verbose_name = _('edition')
        verbose_name_plural = _('editions')
        ordering = ('Name',)

    def __str__(self):
        return str(self.Name)


class VoucherNoTable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    UserID = models.BigIntegerField(blank=True, null=True)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    PreFix = models.CharField(max_length=128, blank=True, null=True)
    Seperater = models.CharField(max_length=128, blank=True, null=True)
    LastInvoiceNo = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'voucherTable_voucherTable'
        verbose_name = _('voucherTable')
        verbose_name_plural = _('voucherTables')
        unique_together = (('CompanyID', 'UserID', 'VoucherType'),)
        ordering = ('id',)

    def __str__(self):
        return str(self.id)


class POS_Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    RoleName = models.CharField(max_length=128, blank=True, null=True)
    show_dining = models.BooleanField(default=False)
    show_take_away = models.BooleanField(default=False)
    show_online = models.BooleanField(default=False)
    show_car = models.BooleanField(default=False)
    show_kitchen = models.BooleanField(default=False)

    class Meta:
        db_table = 'pos_role_pos_role'
        verbose_name = _('pos_role')
        verbose_name_plural = _('pos_roles')
        ordering = ('RoleName',)

    def __str__(self):
        return str(self.RoleName)


class POS_Role_Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    MasterID = models.CharField(max_length=128, blank=True, null=True)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    RoleName = models.CharField(max_length=128, blank=True, null=True)
    show_dining = models.BooleanField(default=False)
    show_take_away = models.BooleanField(default=False)
    show_online = models.BooleanField(default=False)
    show_car = models.BooleanField(default=False)
    show_kitchen = models.BooleanField(default=False)

    class Meta:
        db_table = 'pos_role_log_pos_role_log'
        verbose_name = _('pos_role_log')
        verbose_name_plural = _('pos_roles_log')
        ordering = ('RoleName',)

    def __str__(self):
        return str(self.RoleName)


class POS_User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    User = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    Role = models.ForeignKey(
        "brands.POS_Role", on_delete=models.CASCADE, blank=True, null=True)
    PinNo = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'pos_user_pos_user'
        verbose_name = _('pos_user')
        verbose_name_plural = _('pos_users')
        unique_together = (('CompanyID', 'PinNo', 'BranchID'),)
        ordering = ('User',)

    def __str__(self):
        return str(self.User)


class POS_User_log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    MasterID = models.CharField(max_length=128, blank=True, null=True)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    User = models.ForeignKey(
        "brands.Employee", on_delete=models.CASCADE, blank=True, null=True)
    Role = models.ForeignKey(
        "brands.POS_Role", on_delete=models.CASCADE, blank=True, null=True)
    PinNo = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'pos_user_log_pos_user_log'
        verbose_name = _('pos_user_log')
        verbose_name_plural = _('pos_user_logs')
        ordering = ('User',)

    def __str__(self):
        return str(self.User)


class POS_Table(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    TableName = models.CharField(max_length=128, blank=True, null=True)
    PriceCategory = models.ForeignKey(
        "brands.PriceCategory", on_delete=models.CASCADE, blank=True, null=True)
    Status = models.CharField(
        max_length=128, blank=True, null=True, default="Vacant")
    Position = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'pos_table_pos_table'
        verbose_name = _('pos_table')
        verbose_name_plural = _('pos_tables')
        ordering = ('TableName',)

    def __str__(self):
        return str(self.TableName)


class POS_Table_log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    MasterID = models.CharField(max_length=128, blank=True, null=True)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    TableName = models.CharField(max_length=128, blank=True, null=True)
    PriceCategory = models.ForeignKey(
        "brands.PriceCategory", on_delete=models.CASCADE, blank=True, null=True)
    Status = models.CharField(
        max_length=128, blank=True, null=True, default="vacant")
    Position = models.BigIntegerField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'pos_table_log_pos_table_log'
        verbose_name = _('pos_table_log')
        verbose_name_plural = _('pos_table_logs')
        ordering = ('TableName',)

    def __str__(self):
        return str(self.TableName)


class POS_Settings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField(default=1)
    Warehouse = models.ForeignKey(
        "brands.Warehouse", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'pos_settings_pos_settings'
        verbose_name = _('pos_settings')
        verbose_name_plural = _('pos_settingss')
        unique_together = (('CompanyID', 'BranchID',),)
        ordering = ('id',)

    def __str__(self):
        return str(self.id)


class CancelReasons(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField(default=1)
    Reason = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cancel_reasons_cancel_reason'
        verbose_name = _('cancel_reason')
        verbose_name_plural = _('cancel_reasons')
        ordering = ('id',)

    def __str__(self):
        return str(self.id)


class ExpenseDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ExpenseDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    ExpenseMasterID = models.BigIntegerField()
    Ledger = models.ForeignKey(
        "brands.AccountLedger", on_delete=models.CASCADE, blank=True, null=True, related_name='LedgerDetail')
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'expenseDetails_expenseDetail'
        verbose_name = _('expenseDetail')
        verbose_name_plural = _('expenseDetails')
        unique_together = (('CompanyID', 'ExpenseDetailsID', 'BranchID'),)
        ordering = ('-ExpenseDetailsID',)

    def __unicode__(self):
        return str(self.ExpenseDetailsID)


class ExpenseDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    BranchID = models.BigIntegerField()
   
    ExpenseMasterID = models.BigIntegerField()
    Ledger = models.ForeignKey(
        "brands.AccountLedger", on_delete=models.CASCADE, blank=True, null=True, related_name='LedgerDetailLog')
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxID = models.BigIntegerField(blank=True, null=True)
    TaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    DiscountAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    NetTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    VATPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    VATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    IGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    SGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTPerc = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)

    class Meta:
        db_table = 'expenseDetailLogs_expenseDetailLog'
        verbose_name = _('expenseDetailLog')
        verbose_name_plural = _('expenseDetailLogs')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)


class ExpenseMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ExpenseMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Supplier = models.ForeignKey(
        "brands.AccountLedger", on_delete=models.CASCADE, blank=True, null=True, related_name='supplier')
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    PlaceOfSupply = models.ForeignKey(
        "brands.State", on_delete=models.CASCADE, blank=True, null=True)
    InvoiceNo = models.CharField(max_length=128, blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    TaxTypeID = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    PaymentMode = models.CharField(max_length=150, blank=True, null=True)
    PaymentID = models.ForeignKey(
        "brands.AccountLedger", on_delete=models.CASCADE, blank=True, null=True, related_name='payment')
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalNetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxInclusive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TotalVATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalIGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalSGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalCGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxNo = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'expenseMasters_expenseMaster'
        verbose_name = _('expenseMaster')
        verbose_name_plural = _('expenseMasters')
        unique_together = (('CompanyID', 'ExpenseMasterID', 'BranchID'),)
        ordering = ('-ExpenseMasterID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ExpenseMasterID)


class ExpenseMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Supplier = models.ForeignKey(
        "brands.AccountLedger", on_delete=models.CASCADE, blank=True, null=True, related_name='supplierLog')
    GST_Treatment = models.CharField(max_length=128, blank=True, null=True)
    PlaceOfSupply = models.ForeignKey(
        "brands.State", on_delete=models.CASCADE, blank=True, null=True)
    InvoiceNo = models.CharField(max_length=128, blank=True, null=True)
    TaxType = models.CharField(max_length=128, blank=True, null=True)
    TaxTypeID = models.BigIntegerField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    PaymentMode = models.CharField(max_length=150, blank=True, null=True)
    PaymentID = models.ForeignKey(
        "brands.AccountLedger", on_delete=models.CASCADE, blank=True, null=True, related_name='paymentLog')
    Amount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscPercent = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BillDiscAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalGrossAmt = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxableAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalDiscount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalTaxAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalNetAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    RoundOff = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxInclusive = models.BooleanField(default=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    TotalVATAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalIGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalSGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TotalCGSTAmount = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    TaxNo = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'expenseMasterLogs_expenseMasterLog'
        verbose_name = _('expenseMasterLog')
        verbose_name_plural = _('expenseMasterLogs')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class UserAdrress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    Branch = models.ForeignKey(
        "brands.Branch", on_delete=models.CASCADE, blank=True, null=True)
    Type = models.CharField(max_length=128, blank=True, null=True)
    Party = models.ForeignKey(
        "brands.Parties", on_delete=models.CASCADE, blank=True, null=True)
    Attention = models.CharField(max_length=128, blank=True, null=True)
    Address1 = models.CharField(max_length=150, blank=True, null=True)
    Address2 = models.CharField(max_length=150, blank=True, null=True)
    City = models.CharField(max_length=128, blank=True, null=True)
    District = models.CharField(max_length=128, blank=True, null=True)
    state = models.ForeignKey(
        "brands.State", on_delete=models.CASCADE, blank=True, null=True)
    country = models.ForeignKey(
        "brands.Country", on_delete=models.CASCADE, blank=True, null=True)
    PostalCode = models.CharField(max_length=128, blank=True, null=True)
    OfficePhone = models.CharField(max_length=128, blank=True, null=True)
    WorkPhone = models.CharField(max_length=128, blank=True, null=True)
    Mobile = models.CharField(max_length=128, blank=True, null=True)
    WebURL = models.CharField(max_length=128, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    IsDefault = models.BooleanField(default=False)
    AdditionalNo = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'userAddress_userAddress'
        verbose_name = _('userAddress')
        verbose_name_plural = _('userAddress')
        ordering = ('id',)

    def __str__(self):
        return str(self.id)


class FormsetSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    VoucherType = models.CharField(max_length=150, blank=True, null=True)
    SettingsName = models.CharField(max_length=150, blank=True, null=True)
    SettingsValue = models.BooleanField(default=False)

    class Meta:
        db_table = 'fromsetSettings_fromsetSettings'
        verbose_name = _('fromsetSettings')
        verbose_name_plural = _('fromsetSettingss')
        ordering = ('-id',)

    def __unicode__(self):
        return str(self.id)


# class InvoiceType(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Name = models.CharField(max_length=128, null=True, blank=True)
#     CreatedDate = models.DateTimeField(auto_now_add=True)


#     class Meta:
#         db_table = 'invoice_type'
#         verbose_name = _('invoice type')
#         verbose_name_plural = _('invoice types')
#         # unique_together = (('CompanyID', 'BranchID'),)
#         ordering = ('-CreatedDate',)

#     def __unicode__(self):
#         return str(self.id)


class PrintSettingsNew(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    InvoiceType = models.CharField(
        max_length=128, null=True, blank=True, default="sales_invoice")
    template = models.CharField(
        max_length=128, null=True, blank=True, default="template1")
    TransactionName = models.CharField(
        max_length=128, null=True, blank=True, default="Invoice")
    IsProductName = models.BooleanField(default=True)
    IsDescription = models.BooleanField(default=False)
    IsProductDescription = models.BooleanField(default=False)
    IsSerialNo = models.BooleanField(default=False)
    IsItemCode = models.BooleanField(default=False)
    IsProductCode = models.BooleanField(default=False)
    IsRate = models.BooleanField(default=True)
    IsUnit = models.BooleanField(default=False)
    IsTax = models.BooleanField(default=False)
    IsDiscount = models.BooleanField(default=False)
    IsNetTotal = models.BooleanField(default=True)
    IsTenderCash = models.BooleanField(default=False)
    IsQuantity = models.BooleanField(default=True)
    IsHSNCode = models.BooleanField(default=False)
    IsSlNo = models.BooleanField(default=True)
    IsLogo = models.BooleanField(default=True)
    # payment
    IsLedgerName = models.BooleanField(default=True)
    IsRefNo = models.BooleanField(default=True)
    IsDiscount = models.BooleanField(default=True)
    # payment ends
    # batch
    IsBatchCode = models.BooleanField(default=False)
    IsExpiryDate = models.BooleanField(default=False)
    IsManufacturingDate = models.BooleanField(default=False)
    HeaderFour = RichTextField(blank=True,null=True)
    HeaderOne = RichTextField(blank=True,null=True)
    HeaderThree = RichTextField(blank=True,null=True)
    HeaderTwo = RichTextField(blank=True,null=True)

    # batch ends
    TermsAndConditions = models.CharField(
        max_length=512, null=True, blank=True)
    Notes = models.CharField(max_length=512, null=True, blank=True)
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField(default=1)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    UpdatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'print_settings_new'
        verbose_name = _('print_settings_new')
        verbose_name_plural = _('print_settings_new')
        # unique_together = (('CompanyID', 'BranchID'),)
        ordering = ('-CreatedDate',)

    def __unicode__(self):
        return str(self.id)


class PartyBankDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    Branch = models.ForeignKey(
        "brands.Branch", on_delete=models.CASCADE, blank=True, null=True)
    Party = models.ForeignKey(
        "brands.Parties", on_delete=models.CASCADE, blank=True, null=True)
    BankName1 = models.CharField(max_length=128, blank=True, null=True)
    AccountName1 = models.CharField(max_length=150, blank=True, null=True)
    AccountNo1 = models.CharField(max_length=150, blank=True, null=True)
    IBANOrIFSCCode1 = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'party_bank_details_party_bank_details'
        verbose_name = _('party_bank_details')
        verbose_name_plural = _('party_bank_details')
        ordering = ('id',)

    def __str__(self):
        return str(self.id)


class InviteUsers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Email = models.CharField(max_length=128, blank=True, null=True)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    InvitedUserID = models.BigIntegerField(blank=True, null=True)
    InvitedDate = models.DateField(blank=True, null=True)
    Status = models.CharField(max_length=128, blank=True, null=True)
    UserType = models.ForeignKey(
        "brands.UserType", on_delete=models.CASCADE, blank=True, null=True)
    DefaultAccountForUser = models.BooleanField(
        default=False, blank=True, null=True)
    Cash_Account = models.BigIntegerField(blank=True, null=True, default=None)
    Bank_Account = models.BigIntegerField(blank=True, null=True, default=None)
    Sales_Account = models.BigIntegerField(blank=True, null=True, default=None)
    Sales_Return_Account = models.BigIntegerField(
        blank=True, null=True, default=None)
    Purchase_Account = models.BigIntegerField(
        blank=True, null=True, default=None)
    Purchase_Return_Account = models.BigIntegerField(
        blank=True, null=True, default=None)
    ExpiryDate = models.DateField(blank=True, null=True)
    is_web = models.BooleanField(default=True, blank=True, null=True)
    is_mobile = models.BooleanField(default=True, blank=True, null=True)
    is_pos = models.BooleanField(default=False, blank=True, null=True)
    BranchID = models.BigIntegerField(default=1, blank=True, null=True)

    class Meta:
        db_table = 'invitedUsers_invitedUsers'
        verbose_name = _('invitedUsers')
        verbose_name_plural = _('invitedUsers')
        ordering = ('id',)

    def __str__(self):
        return str(self.id)


class VoucherNoGenerateTable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    UserID = models.BigIntegerField(blank=True, null=True)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    VoucherType = models.CharField(max_length=128, blank=True, null=True)
    PreFix = models.CharField(max_length=128, blank=True, null=True)
    Seperater = models.CharField(max_length=128, blank=True, null=True)
    LastInvoiceNo = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'voucherGenerateTable_voucherGenerateTable'
        verbose_name = _('voucherGenerateTable')
        verbose_name_plural = _('voucherGenerateTables')
        unique_together = (('CompanyID', 'VoucherType'),)
        ordering = ('id',)

    def __str__(self):
        return str(self.id)


class POS_Devices(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    DeviceName = models.CharField(max_length=256, blank=True, null=True)
    DeviceMachineID = models.CharField(max_length=128, blank=True, null=True)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    WareHouseID = models.ForeignKey(
        "brands.Warehouse", on_delete=models.CASCADE, blank=True, null=True)
    AutoIncrimentQty = models.BooleanField(
        default=False, blank=True, null=True)
    IsActive = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        db_table = 'pos_devices'
        verbose_name = _('pos_devices')
        verbose_name_plural = _('pos_devicess')
        ordering = ('DeviceName',)

    def __unicode__(self):
        return str(self.DeviceName)


class UserRoleSettingsModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    UserType = models.ForeignKey(
        "brands.UserType", on_delete=models.CASCADE, blank=True, null=True)
    BranchID = models.BigIntegerField()
    parent = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=150, blank=True, null=True)
    view_permission = models.BooleanField(default=False, blank=True, null=True)
    save_permission = models.BooleanField(default=False, blank=True, null=True)
    edit_permission = models.BooleanField(default=False, blank=True, null=True)
    delete_permission = models.BooleanField(
        default=False, blank=True, null=True)
    print_permission = models.BooleanField(
        default=False, blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    UpdatedUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'userRoleSettings_userRoleSettings'
        verbose_name = _('userRoleSettings')
        verbose_name_plural = _('userRoleSettings')
        ordering = ('id',)

    def __unicode__(self):
        return str(self.id)


class POSVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CurrentVersion = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = 'pos_version'
        verbose_name = _('pos Version')
        verbose_name_plural = _('pos Version')
        ordering = ('id',)

    def __unicode__(self):
        return str(self.id)


class VersionDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Version = models.CharField(max_length=150, blank=True, null=True)
    Message = models.CharField(max_length=150, blank=True, null=True)
    is_updation = models.BooleanField(default=False, blank=True, null=True)
    is_web = models.BooleanField(default=False, blank=True, null=True)
    is_mobile = models.BooleanField(default=False, blank=True, null=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'version_details'
        verbose_name = _('version_details')
        verbose_name_plural = _('version_details')
        ordering = ('id',)

    def __unicode__(self):
        return str(self.id)



class StockManagementMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    StockMasterID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    StockType = models.CharField(max_length=128, blank=True, null=True)
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'stock_management_master'
        verbose_name = _('stock_management_master')
        verbose_name_plural = _('stock_management_master')
        unique_together = (('CompanyID', 'StockMasterID','BranchID'),)
        ordering = ('-id', 'CreatedDate',)

    def __unicode__(self):
        return str(self.id)


class StockManagementMaster_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    StockType = models.CharField(max_length=128, blank=True, null=True)
    VoucherNo = models.CharField(max_length=128, blank=True, null=True)
    Date = models.DateField(blank=True, null=True)
    Notes = models.TextField(blank=True, null=True)
    WarehouseID = models.BigIntegerField(blank=True, null=True)
    TotalQty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    GrandTotal = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'stock_management_master_log'
        verbose_name = _('stock_management_master_log')
        verbose_name_plural = _('stock_management_masters_log')
        ordering = ('-ID', 'CreatedDate',)

    def __unicode__(self):
        return str(self.ID)


class StockManagementDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    StockDetailsID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    StockMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Excess_or_Shortage = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Stock = models.DecimalField(default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    LogID = models.BigIntegerField(default=0)
    BatchCode = models.CharField(default="0",max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'stock_management_details'
        verbose_name = _('stock_management_details')
        verbose_name_plural = _('stock_management_detailses')
        unique_together = (('CompanyID', 'StockDetailsID','BranchID'),)
        ordering = ('-id',)

    def __unicode__(self):
        return str(self.id)


class StockManagementDetails_Log(models.Model):
    CompanyID = models.ForeignKey(
        "brands.CompanySettings", on_delete=models.CASCADE, blank=True, null=True)
    ID = models.AutoField(primary_key=True)
    TransactionID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    Action = models.CharField(
        max_length=128, blank=True, null=True, default="A")
    StockMasterID = models.BigIntegerField()
    ProductID = models.BigIntegerField(blank=True, null=True)
    PriceListID = models.BigIntegerField(blank=True, null=True)
    Qty = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Excess_or_Shortage = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    CreatedDate = models.DateTimeField(blank=True, null=True)
    LastUPDDate = models.DateTimeField(blank=True, null=True)
    CreatedUserID = models.BigIntegerField(blank=True, null=True)
    LastUPDUserID = models.BigIntegerField(blank=True, null=True)
    CostPerItem = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    Stock = models.DecimalField(default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    BatchCode = models.CharField(default="0",max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'stock_management_details_log'
        verbose_name = _('stock_management_details_log')
        verbose_name_plural = _('stock_management_details_log')
        ordering = ('-ID',)

    def __unicode__(self):
        return str(self.ID)