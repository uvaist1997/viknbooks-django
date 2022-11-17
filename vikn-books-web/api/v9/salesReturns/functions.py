import random
import string
from decimal import Decimal

from django.db.models import Max
from django.http import HttpResponse

from brands.models import (
    LoyaltyCustomer,
    LoyaltyPoint,
    LoyaltyProgram,
    LoyaltyProgram_Log,
    Product,
    ProductCategory,
    ProductGroup,
    TransactionTypes,
)


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def get_auto_idMaster(model, BranchID, CompanyID):
    SalesReturnMasterID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(CompanyID=CompanyID).aggregate(
        Max("SalesReturnMasterID")
    )

    if model.objects.filter(BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).aggregate(Max("SalesReturnMasterID"))

        if max_value:
            max_salesReturnMasterId = max_value.get("SalesReturnMasterID__max", 0)
            if max_salesReturnMasterId:
                SalesReturnMasterID = max_salesReturnMasterId + 1

    return SalesReturnMasterID


def get_auto_id(model, BranchID, CompanyID):
    SalesReturnDetailsID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(CompanyID=CompanyID).aggregate(
        Max("SalesReturnDetailsID")
    )

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).aggregate(Max("SalesReturnDetailsID"))

        if max_value:
            max_salesReturnDetailsId = max_value.get("SalesReturnDetailsID__max", 0)

            SalesReturnDetailsID = max_salesReturnDetailsId + 1
        else:
            SalesReturnDetailsID = 1

    return SalesReturnDetailsID


def sales_return_point(
    instance, product_id, TaxableAmount, BranchID, CompanyID, is_MinimumSalePrice
):
    tot_taxable_amnt = 0
    if instance.ProductType == "All_product":
        print("All_product")
        products = Product.objects.filter(BranchID=BranchID, CompanyID=CompanyID)
        for i in products:
            if i.ProductID == product_id:
                print("All_product MONE")
                print(TaxableAmount, "NDDDDDDDD MONE", instance.MinimumSalePrice)

                if is_MinimumSalePrice:
                    if TaxableAmount > instance.MinimumSalePrice:
                        print("VALUTH$$$$$$$$$$444AAAAN")
                        tot_taxable_amnt += TaxableAmount
                else:
                    tot_taxable_amnt += TaxableAmount

    elif instance.ProductType == "Product_group":
        print("Product_group")
        Group_ids = instance.ProductGroupIDs.split(",")
        ProductGroupIDs = [i for i in Group_ids if i]
        print(ProductGroupIDs, "ProductGroupIDs")
        products = Product.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, ProductGroupID__in=ProductGroupIDs
        )
        for i in products:
            if i:
                if i.ProductID == product_id:
                    print("All_product MONE")
                    print(TaxableAmount, "NDDDDDDDD MONE", instance.MinimumSalePrice)

                    if is_MinimumSalePrice:
                        if TaxableAmount > instance.MinimumSalePrice:
                            print("VALUTH$$$$$$$$$$444AAAAN")
                            tot_taxable_amnt += TaxableAmount
                    else:
                        tot_taxable_amnt += TaxableAmount
    elif instance.ProductType == "Product_category":
        Cat_ids = instance.ProductCategoryIDs.split(",")
        ProductCategoryIDs = [i for i in Cat_ids if i]
        print("Product_category")
        group_instance = ProductGroup.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, CategoryID__in=ProductCategoryIDs
        )
        ProductGroupIDs = []
        for i in group_instance:
            ProductGroupIDs.append(i.ProductGroupID)
        print(ProductGroupIDs, "ProductGroupIDs/./././")
        products = Product.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, ProductGroupID__in=ProductGroupIDs
        )
        actual_point = 0
        for i in products:
            if i:
                if i.ProductID == product_id:
                    print(TaxableAmount, "NDDDDDDDD MONE", instance.MinimumSalePrice)
                    # taiking single product point

                    if is_MinimumSalePrice:
                        if TaxableAmount > instance.MinimumSalePrice:
                            print("VALUTH$$$$$$$$$$444AAAAN")
                            tot_taxable_amnt += TaxableAmount
                    else:
                        tot_taxable_amnt += TaxableAmount

    return tot_taxable_amnt
