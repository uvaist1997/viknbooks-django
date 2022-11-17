import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from main.functions import converted_float, get_GeneralSettings
from brands.models import AccountLedger, Batch, Product,SalesMaster,SalesDetails,PurchaseMaster,PurchaseDetails



def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]


def get_auto_id(model,BranchID,DataBase):
    PriceListID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('PriceListID'))
    
    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('PriceListID'))
        
        if max_value:
            max_priceListId = max_value.get('PriceListID__max', 0)
            
            PriceListID = max_priceListId + 1
            
        else:
            PriceListID = 1

    return PriceListID


def get_LastSalesPrice_PurchasePrice(Type, Price, CompanyID, BranchID, LedgerID, ProductID, PriceListID=1):
    check_EnableProductBatchWise = get_GeneralSettings(CompanyID,BranchID,"EnableProductBatchWise")
    ShowCustomerLastSalesPriceinSales = get_GeneralSettings(CompanyID,BranchID,"ShowCustomerLastSalesPriceinSales")
    ShowSupplierLastPurchasePriceinPurchase = get_GeneralSettings(CompanyID,BranchID,"ShowSupplierLastPurchasePriceinPurchase")
    is_customer = False
    if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID).exists():
        ledger_instance = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID)
        AccountGroupUnder = ledger_instance.AccountGroupUnder
        if AccountGroupUnder == 10 or AccountGroupUnder == 29:
            is_customer = True
    is_inclusive = False
    if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
        is_inclusive = Product.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID).first().is_inclusive
    if is_customer:
        if Type == "Sales":
            if ShowCustomerLastSalesPriceinSales == True and check_EnableProductBatchWise == True:
                if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
                    sales_ledger_ins = SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID)
                    sales_master_ids = sales_ledger_ins.values_list("SalesMasterID", flat=True)
                    if SalesDetails.objects.filter(CompanyID=CompanyID, SalesMasterID__in=sales_master_ids, ProductID=ProductID, PriceListID=PriceListID).exists():
                        sales_product_details = SalesDetails.objects.filter(
                            CompanyID=CompanyID,
                            SalesMasterID__in=sales_master_ids,
                            ProductID=ProductID,
                            PriceListID=PriceListID
                        ).order_by("-SalesDetailsID").first()
                        
                        Price = sales_product_details.UnitPrice
                        if is_inclusive == True:
                            Price = sales_product_details.InclusivePrice
                        # if sales_product_details.UnitPrice > 0:
                        #     Price = sales_product_details.UnitPrice
                            
            elif ShowCustomerLastSalesPriceinSales == True:
                if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
                    sales_ledger_ins = SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID)
                    sales_master_ids = sales_ledger_ins.values_list("SalesMasterID", flat=True)
                    if SalesDetails.objects.filter(CompanyID=CompanyID, SalesMasterID__in=sales_master_ids, ProductID=ProductID, PriceListID=PriceListID).exists():
                        sales_product_details = SalesDetails.objects.filter(
                            CompanyID=CompanyID,
                            SalesMasterID__in=sales_master_ids,
                            ProductID=ProductID,
                            PriceListID=PriceListID
                        ).order_by("-SalesDetailsID").first()
                        Price = sales_product_details.UnitPrice
                        if is_inclusive == True:
                            Price = sales_product_details.InclusivePrice
                        # if sales_product_details.UnitPrice > 0:
                        #     Price = sales_product_details.UnitPrice
                
        elif Type == "Purchase":                
            if ShowSupplierLastPurchasePriceinPurchase == True:
                if PurchaseMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                ).exists():
                    purchase_ledger_ins = PurchaseMaster.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                    )
                    purchase_master_ids = purchase_ledger_ins.values_list(
                        "PurchaseMasterID", flat=True)
                    print(purchase_master_ids)
                    if PurchaseDetails.objects.filter(
                        CompanyID=CompanyID,
                        PurchaseMasterID__in=purchase_master_ids,
                        ProductID=ProductID,
                        PriceListID=PriceListID
                    ).exists():
                        sales_product_details = PurchaseDetails.objects.filter(
                            CompanyID=CompanyID,
                            PurchaseMasterID__in=purchase_master_ids,
                            ProductID=ProductID,
                            PriceListID=PriceListID
                        ).order_by("-PurchaseDetailsID").first()
                        Price = sales_product_details.UnitPrice
                        if is_inclusive == True:
                            Price = sales_product_details.InclusivePrice
                        # if sales_product_details.UnitPrice > 0:
                        #     Price = sales_product_details.UnitPrice
    return Price
