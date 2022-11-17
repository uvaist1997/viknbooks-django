import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
import re
from api.v4.sales.serializers import StockValueInventoryFlowSerializer
from brands.models import StockPosting,Product
from django.db.models import Sum
from api.v4.ledgerPosting.functions import convertOrderdDict
from datetime import date, timedelta
import calendar 
import datetime 
from api.v4.loyaltyProgram.functions import get_point_auto_id
from api.v4.accountLedgers.functions import get_auto_LedgerPostid
from brands.models import SalesMaster, SalesMaster_Log, SalesDetails, SalesDetails_Log, StockPosting, LedgerPosting,\
    StockPosting_Log, LedgerPosting_Log, Parties, SalesDetailsDummy, StockRate, StockTrans, PriceList, DamageStockMaster, JournalMaster,\
    OpeningStockMaster, PaymentMaster, PurchaseMaster, PurchaseOrderMaster, PurchaseReturnMaster, ReceiptMaster, SalesOrderMaster, SalesEstimateMaster,\
    SalesReturnMaster, StockReceiptMaster_ID, DamageStockMaster, StockTransferMaster_ID, AccountGroup, SalesReturnDetails,\
    AccountLedger, PurchaseDetails, PurchaseReturnDetails, Product, UserTable, ProductGroup, ExcessStockMaster, ShortageStockMaster, DamageStockMaster,\
    UsedStockMaster, GeneralSettings, CompanySettings, WorkOrderMaster, Batch,SerialNumbers,LoyaltyCustomer,LoyaltyProgram,LoyaltyPoint,LoyaltyPoint_Log


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]


def get_auto_idMaster(model,BranchID,CompanyID):
    SalesMasterID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('SalesMasterID'))

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('SalesMasterID'))
        

        if max_value:
            max_salesMasterId = max_value.get('SalesMasterID__max', 0)
            
            SalesMasterID = max_salesMasterId + 1
            
        else:
            SalesMasterID = 1


    return SalesMasterID


def get_auto_id(model,BranchID,CompanyID):
    SalesDetailsID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('SalesDetailsID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('SalesDetailsID'))
        

        if max_value:
            max_salesDetailsId = max_value.get('SalesDetailsID__max', 0)
            
            SalesDetailsID = max_salesDetailsId + 1
            
        else:
            SalesDetailsID = 1


    return SalesDetailsID


def get_auto_stockPostid(model,BranchID,CompanyID):
    StockPostingID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('StockPostingID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('StockPostingID'))
        

        if max_value:
            max_stockPostingId = max_value.get('StockPostingID__max', 0)
            
            StockPostingID = max_stockPostingId + 1
            
        else:
            StockPostingID = 1


    return StockPostingID


def get_auto_VoucherNo(model,BranchID,CompanyID):
    VoucherNo = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('VoucherNo'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('VoucherNo'))
        

        if max_value:
            max_VoucherNo = max_value.get('VoucherNo__max', 0)
            
            VoucherNo = max_VoucherNo + 1
            
        else:
            VoucherNo = 1

    return VoucherNo


def get_Genrate_VoucherNo(model,BranchID,CompanyID,VoucherType):
    VoucherNo = VoucherType + str(1)
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        instance = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).first()
        OldVoucherNo = instance.VoucherNo
        if not OldVoucherNo.isdecimal():
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            VoucherNo = VoucherType + str(new_num)
        else:
            # VoucherNo = float(OldVoucherNo) + 1
            VoucherNo = str(int(OldVoucherNo) +
                                1).zfill(len(OldVoucherNo))

    return VoucherNo


def get_month(m):
    month = m
    if m == "01":
        month = "January"
    elif m == "02":
        month = "February"
    elif m == "03":
        month = "March"
    elif m == "04":
        month = "April"
    elif m == "05":
        month = "May"
    elif m == "06":
        month = "June"
    elif m == "07":
        month = "July"
    elif m == "08":
        month = "August"
    elif m == "09":
        month = "September"
    elif m == "10":
        month = "October"
    elif m == "11":
        month = "November"
    elif m == "12":
        month = "December"
    return month


def get_stock_value(CompanyID,BranchID,FromDate,ToDate,WarehouseID,PriceRounding):
    GrandTotalCost = 0
    if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate).exists():
        stock_instances = StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate)
        if not WarehouseID == 0:
            stock_instances = stock_instances.filter(WareHouseID=WarehouseID)

        product_arry = []
        product_ids = stock_instances.values_list('ProductID')

        for product_id in product_ids:
            if product_id[0] not in product_arry:
                product_arry.append(product_id[0])

        qurried_instances = stock_instances.values('ProductID').annotate(in_stock_quantity=Sum('QtyIn') - Sum('QtyOut')).order_by('ProductID')

        product_instances = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_arry)

        stockSerializer = StockValueInventoryFlowSerializer(product_instances, many=True, context={
                                          "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WareHouseID": WarehouseID,"FromDate": FromDate, "ToDate": ToDate})

        orderdDict = stockSerializer.data
        jsnDatas = convertOrderdDict(orderdDict)
        TotalQty = 0
        
        for i in jsnDatas:
            if not float(i['Qty']) == 0:
                cost = i['Cost']
                qty = i['Qty']
                TotalCost = float(cost) * float(qty)
                
                TotalQty += float(i['Qty'])
                GrandTotalCost += TotalCost

    return GrandTotalCost


def get_date_list(start_date):

    # start_date = date(y, m, d)
    days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
    print("----------------------------")
    # date_month1 = start_date - timedelta(days=days_in_month)
    date_month1 = start_date.date()
    date_month2 = date_month1 - timedelta(days=days_in_month)
    date_month3 = date_month2 - timedelta(days=days_in_month)
    date_month4 = date_month3 - timedelta(days=days_in_month)
    date_month5 = date_month4 - timedelta(days=days_in_month)
    date_month6 = date_month5 - timedelta(days=days_in_month)
    date_month = [date_month1, date_month2, date_month3, date_month4, date_month5, date_month6]
    print(date_month)
    return date_month

# month_list = previous_six_month(2014,12,25)

# month_one = month_list[0]
# print(month_one.year)
def get_Program(instance, loyalty_customer,details, Loyalty_Point_Expire, Action, RadeemPoint):
    today = datetime.datetime.now()
    for salesdetail in details:
        ProductID = salesdetail['ProductID']
        group_id = Product.objects.get(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductID=ProductID).ProductGroupID
        print(ProductID,'##################################',group_id)
        if LoyaltyProgram.objects.filter(CardTypeID=loyalty_customer.CardTypeID,FromDate__lte=instance.Date,ToDate__gte=instance.Date).exists():
            loyalty_program_insrances = LoyaltyProgram.objects.filter(CardTypeID=loyalty_customer.CardTypeID,FromDate__lte=instance.Date,ToDate__gte=instance.Date)
            for i in loyalty_program_insrances:
                if i.ProductType == "Product_group":
                    ProductGroupIDs_arry1 = i.ProductGroupIDs.split(",")
                    while("" in ProductGroupIDs_arry1) :
                        ProductGroupIDs_arry1.remove("")
                    if str(group_id) in ProductGroupIDs_arry1:
                        print(group_id,"qqqqqqqqqqqqqqqqqqqqqqqq")
                        loyalty_program = i
                        # ExpiryDate
                        # import datetime
                        # Loyalty_Point_Expire = data['Loyalty_Point_Expire']
                        ExpiryDate = None
                        if Loyalty_Point_Expire:
                            current_date = "12/6/20"
                            current_date_temp = datetime.datetime.strptime(instance.Date, "%Y-%m-%d")
                            ExpiryDate = current_date_temp + datetime.timedelta(days=int(loyalty_program.NoOFDayExpPoint))
                        else:
                            current_date_temp = datetime.datetime.strptime(instance.Date, "%Y-%m-%d")
                            ExpiryDate = current_date_temp + datetime.timedelta(days=int(365))
                        # ====

                        # Loyalty Calculation Start heare************
                        salesdetails = details
                        Group_ids = loyalty_program.ProductGroupIDs.split(',')
                        Cat_ids = loyalty_program.ProductCategoryIDs.split(',')

                        ProductGroupIDs = [i for i in Group_ids if i]
                        ProductCategoryIDs = [i for i in Cat_ids if i]
                        print(ProductGroupIDs,"QQQQQUVAISQQQQQQ",ProductCategoryIDs)
                        # test_list.remove("")
                        tot_TaxableAmount = 0
                        if SalesDetails:
                            for salesdetail in salesdetails:

                                ProductID = salesdetail['ProductID']
                                if ProductGroupIDs:
                                    if Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupIDs):
                                        pro_instance = Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupIDs)
                                        for i in pro_instance:
                                            if ProductID == i.ProductID:
                                                tot_TaxableAmount += int(salesdetail['TaxableAmount'])
                                elif ProductCategoryIDs:
                                    ProductGroupID = ProductGroup.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,CategoryID__in=ProductCategoryIDs).values_list('ProductGroupID',flat=True)
                                    if Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupID):
                                        pro_instance = Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupID)
                                        for i in pro_instance:
                                            if ProductID == i.ProductID:
                                                tot_TaxableAmount += int(salesdetail['TaxableAmount'])
                                else:
                                    if Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID):
                                        pro_instance = Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID)
                                        for i in pro_instance:
                                            if ProductID == i.ProductID:
                                                tot_TaxableAmount += int(salesdetail['TaxableAmount'])
                                        TaxableAmount = float(salesdetail['TaxableAmount'])
                                        # =======*******************============
                        actual_point = 0
                        if tot_TaxableAmount > loyalty_program.MinimumSalePrice:
                            print("VALUTHAAAAN")
                            MinimumSalePrice = loyalty_program.MinimumSalePrice
                            Calculate_with = loyalty_program.Calculate_with

                            if Calculate_with == "Amount":
                                Amount = loyalty_program.Amount
                                Amount_Point = loyalty_program.Amount_Point
                                # ======1st
                                p_amount = Amount_Point/Amount*100
                                # ======2st
                                print(tot_TaxableAmount,"Amount......")
                                actual_point = int(tot_TaxableAmount)/100*int(p_amount)
                            elif Calculate_with == "Percentage":
                                print("Percentage......")
                                Percentage = loyalty_program.Percentage
                                actual_point = int(tot_TaxableAmount)/100*int(Percentage)

                           
                            
                            print(tot_TaxableAmount,"tot_TaxableAmount")

                            if actual_point:
                                LoyaltyPointID = get_point_auto_id(LoyaltyPoint, instance.BranchID, instance.CompanyID)
                                LoyaltyPoint.objects.create(
                                    BranchID=instance.BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=actual_point,
                                    VoucherType="SI",
                                    VoucherMasterID=instance.SalesMasterID,
                                    Point=actual_point,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=loyalty_program,
                                    is_Radeem=False,

                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CompanyID=instance.CompanyID,
                                )
                                LoyaltyPoint_Log.objects.create(
                                    BranchID=instance.BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=actual_point,
                                    VoucherType="SI",
                                    VoucherMasterID=instance.SalesMasterID,
                                    Point=actual_point,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=loyalty_program,
                                    is_Radeem=False,
                                
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CompanyID=instance.CompanyID,
                                )
                        print(loyalty_program.MinimumSalePrice,actual_point,'LoyaltyCustomerIDLoyaltyCustomerIDLoyaltyCustomerID')
                        # Loyalty Calculation END heare******************
                        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Radeem Loyalty Point Start heare>>>>>>>>>>>>
                        
                        if RadeemPoint:
                            radeem = RadeemPoint.split("-")
                            radeem_value = radeem[1]
                            radeem_point = int(radeem[0]) * -1
                            if int(instance.GrandTotal) >= int(radeem_value):
                                print(radeem_point,'radeem_point +++++++++++++++++ RadeemPoint',RadeemPoint)
                                LoyaltyPointID = get_point_auto_id(LoyaltyPoint, instance.BranchID, instance.CompanyID)
                                LoyaltyPoint.objects.create(
                                    BranchID=instance.BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=radeem_value,
                                    VoucherType="SI",
                                    VoucherMasterID=instance.SalesMasterID,
                                    Point=radeem_point,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=loyalty_program,
                                    is_Radeem=True,
                                
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CompanyID=instance.CompanyID,
                                )
                                LoyaltyPoint_Log.objects.create(
                                    BranchID=instance.BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=radeem_value,
                                    VoucherType="SI",
                                    VoucherMasterID=instance.SalesMasterID,
                                    Point=radeem_point,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=loyalty_program,
                                    is_Radeem=True,
                                
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CompanyID=instance.CompanyID,
                                )

                                # <<<<<LedgerPosting>>>
                                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting, instance.BranchID, instance.CompanyID)
                                LedgerPosting.objects.create(
                                    LedgerPostingID=LedgerPostingID,
                                    BranchID=instance.BranchID,
                                    Date=instance.Date,
                                    VoucherMasterID=instance.SalesMasterID,
                                    VoucherType="SI",
                                    VoucherNo=instance.VoucherNo,
                                    LedgerID=73,
                                    Debit=radeem_value,
                                    IsActive=instance.IsActive,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=instance.CompanyID,
                                )

                                LedgerPosting_Log.objects.create(
                                    TransactionID=LedgerPostingID,
                                    BranchID=instance.BranchID,
                                    Date=instance.Date,
                                    VoucherMasterID=instance.SalesMasterID,
                                    VoucherType="SI",
                                    VoucherNo=instance.VoucherNo,
                                    LedgerID=73,
                                    Debit=radeem_value,
                                    IsActive=instance.IsActive,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=instance.CompanyID,
                                )
                                # <<<<<LedgerPosting END HEARE>>>

                            print(radeem_point,RadeemPoint.split("-"))
                            sale_date = str_To_Date(instance.Date)
                            if LoyaltyPoint.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,LoyaltyCustomerID=loyalty_customer,VoucherType="SI",ExpiryDate__gte=sale_date,is_Radeem=False).exists():
                                point_instances = LoyaltyPoint.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,LoyaltyCustomerID=loyalty_customer,VoucherType="SI",ExpiryDate__gte=sale_date,is_Radeem=False).order_by("LoyaltyPointID")
                                balance_point = float(radeem[0])
                                for i in point_instances:
                                    Point = float(i.Point)
                                    if i.Radeemed_Point:
                                        Radeemed_Point = float(i.Radeemed_Point)
                                        float(i.Radeemed_Point)
                                    else:
                                        Radeemed_Point = 0 
                                    Point = float(i.Point)
                                    if not balance_point <= 0:
                                        w = Point - Radeemed_Point
                                        if float(w) <= float(balance_point) and Point != Radeemed_Point:
                                           
                                            # =================

                                            # =================



                                            print(Point,'ifAAAAAAAAAAA',Radeemed_Point,'UVAISANNNNNNNNNNNNN',balance_point)
                                            print("IFFFFFFF")
                                            balance_point -= w
                                            # balance_point = balance_point+Radeemed_Point - Point
                                            b = float(Radeemed_Point) + w
                                            i.Radeemed_Point = b
                                        elif w>= balance_point and Point != Radeemed_Point:
                                            print(Point,'ElseAAAAAAAAAAA',Radeemed_Point,'UVAISANNNNNNNNNNNNN',balance_point)

                                            i.Radeemed_Point = balance_point+Radeemed_Point
                                            balance_point -= balance_point 
                                            

                                            # b = Radeemed_Point + balance_point
                                            # q = Point - Radeemed_Point
                                            # ==========
                                            # i.Radeemed_Point = Radeemed_Point + q
                                            # ==========


                                           
                                            
                                            # if Point <= q:
                                            #     i.Radeemed_Point = balance_point
                                            #     balance_point = 0
                                            #     print(balance_point,"ELSEIFFFFFFF1")
                                            # elif Point >= Radeemed_Point:
                                            #     balance_point = balance_point - q
                                            #     if balance_point > 0:
                                            #         i.Radeemed_Point = Radeemed_Point + q
                                            #         print(balance_point,"!!!!!!!!!!!!!!!!!!!!1")
                                            #     else:
                                            #         print(balance_point,"2222222222222222222")
                                            #         i.Radeemed_Point = Radeemed_Point+abs(balance_point)
                                            #         balance_point = 0
                                            #     print(balance_point,"ELSEIFFFFFFF2")
                                        i.save()
                                        if balance_point <= 0:
                                            break

                        # TOTAL LOYALTY Customer Point
                        is_edit = False
                        if LoyaltyPoint.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,VoucherType="SI",LoyaltyCustomerID=loyalty_customer,is_Radeem=True).exists():
                            is_edit = True
                        if LoyaltyPoint.objects.filter(LoyaltyCustomerID=loyalty_customer,BranchID=instance.BranchID, CompanyID=instance.CompanyID).exists():
                            loyalty_instances = LoyaltyPoint.objects.filter(
                                LoyaltyCustomerID=loyalty_customer,BranchID=instance.BranchID, CompanyID=instance.CompanyID)

                            tot_Point = 0
                            # today_date = datetime.datetime.now().date()
                            today_date = str_To_Date(instance.Date)
                           
                            for i in loyalty_instances:
                                if i.Point:
                                    if Loyalty_Point_Expire:
                                        if i.ExpiryDate:
                                            if not today_date >= i.ExpiryDate:
                                                if Action == "M":
                                                    if is_edit:
                                                        tot_Point = float(tot_Point) + float(i.Point) 
                                                elif Action == "A":
                                                    tot_Point = float(tot_Point) + float(i.Point) 
                                    else:
                                        if Action == "M":
                                            if is_edit:
                                                tot_Point = float(tot_Point) + float(i.Point) 
                                        elif Action == "A":
                                            tot_Point  += float(i.Point) 
                            if LoyaltyCustomer.objects.filter(pk=loyalty_customer.pk).exists():
                                ins = LoyaltyCustomer.objects.get(pk=loyalty_customer.pk)
                                ins.CurrentPoint = tot_Point
                                ins.save()
                    print(ProductGroupIDs_arry1,'oooooooooooProduct_group')


def set_LoyaltyCalculation(instance,loyalty_customer,details,Loyalty_Point_Expire,Action,RadeemPoint):
    print("CUSTPOMEERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
    # ====== Loyalty Program Point       
    today = datetime.datetime.now()
    loyalty_program = None
    if LoyaltyProgram.objects.filter(CardTypeID=loyalty_customer.CardTypeID,FromDate__lte=instance.Date,ToDate__gte=instance.Date).exists():
        loyalty_program = LoyaltyProgram.objects.get(CardTypeID=loyalty_customer.CardTypeID,FromDate__lte=instance.Date,ToDate__gte=instance.Date)
    if loyalty_program:
        # ExpiryDate
        # import datetime
        # Loyalty_Point_Expire = data['Loyalty_Point_Expire']
        ExpiryDate = None
        if Loyalty_Point_Expire:
            current_date = "12/6/20"
            current_date_temp = datetime.datetime.strptime(instance.Date, "%Y-%m-%d")
            ExpiryDate = current_date_temp + datetime.timedelta(days=int(loyalty_program.NoOFDayExpPoint))
        else:
            current_date_temp = datetime.datetime.strptime(instance.Date, "%Y-%m-%d")
            ExpiryDate = current_date_temp + datetime.timedelta(days=int(365))
        # ====

        # Loyalty Calculation Start heare************
        salesdetails = details
        Group_ids = loyalty_program.ProductGroupIDs.split(',')
        Cat_ids = loyalty_program.ProductCategoryIDs.split(',')

        ProductGroupIDs = [i for i in Group_ids if i]
        ProductCategoryIDs = [i for i in Cat_ids if i]
        
        # test_list.remove("")
        tot_TaxableAmount = 0
        if SalesDetails:
            for salesdetail in salesdetails:

                ProductID = salesdetail['ProductID']
                if ProductGroupIDs:
                    if Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupIDs):
                        pro_instance = Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupIDs)
                        print(pro_instance,"QQQQQUVA*****2******ISQQQQQQ",tot_TaxableAmount)
                        for i in pro_instance:
                            if ProductID == i.ProductID:
                                tot_TaxableAmount += int(salesdetail['TaxableAmount'])
                                print(loyalty_program.MinimumSalePrice,"QQQQQUVA*****3******ISQQQQQQ",tot_TaxableAmount)
                elif ProductCategoryIDs:
                    ProductGroupID = ProductGroup.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,CategoryID__in=ProductCategoryIDs).values_list('ProductGroupID',flat=True)
                    if Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupID):
                        pro_instance = Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupID)
                        for i in pro_instance:
                            if ProductID == i.ProductID:
                                tot_TaxableAmount += int(salesdetail['TaxableAmount'])
                else:
                    if Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID):
                        pro_instance = Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID)
                        for i in pro_instance:
                            if ProductID == i.ProductID:
                                tot_TaxableAmount += int(salesdetail['TaxableAmount'])
                        TaxableAmount = float(salesdetail['TaxableAmount'])
                        # =======*******************============
        actual_point = 0
        print(loyalty_program.MinimumSalePrice,"QQQQQUVA*****laast******ISQQQQQQ",tot_TaxableAmount)
        if tot_TaxableAmount > loyalty_program.MinimumSalePrice:
            print("VALUTHAAAAN")
            MinimumSalePrice = loyalty_program.MinimumSalePrice
            Calculate_with = loyalty_program.Calculate_with

            if Calculate_with == "Amount":
                Amount = loyalty_program.Amount
                Amount_Point = loyalty_program.Amount_Point
                # ======1st
                p_amount = Amount_Point/Amount*100
                # ======2st
                print(tot_TaxableAmount,"Amount......")
                actual_point = int(tot_TaxableAmount)/100*int(p_amount)
            elif Calculate_with == "Percentage":
                print("Percentage......")
                Percentage = loyalty_program.Percentage
                actual_point = int(tot_TaxableAmount)/100*int(Percentage)

           
            
            print(tot_TaxableAmount,"tot_TaxableAmount")

            if actual_point:
                LoyaltyPointID = get_point_auto_id(LoyaltyPoint, instance.BranchID, instance.CompanyID)
                LoyaltyPoint.objects.create(
                    BranchID=instance.BranchID,
                    LoyaltyPointID=LoyaltyPointID,
                    Value=actual_point,
                    VoucherType="SI",
                    VoucherMasterID=instance.SalesMasterID,
                    Point=actual_point,
                    ExpiryDate=ExpiryDate,
                    LoyaltyCustomerID=loyalty_customer,
                    LoyaltyProgramID=loyalty_program,
                    is_Radeem=False,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CompanyID=instance.CompanyID,
                )
                LoyaltyPoint_Log.objects.create(
                    BranchID=instance.BranchID,
                    LoyaltyPointID=LoyaltyPointID,
                    Value=actual_point,
                    VoucherType="SI",
                    VoucherMasterID=instance.SalesMasterID,
                    Point=actual_point,
                    ExpiryDate=ExpiryDate,
                    LoyaltyCustomerID=loyalty_customer,
                    LoyaltyProgramID=loyalty_program,
                    is_Radeem=False,
                
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CompanyID=instance.CompanyID,
                )
        print(loyalty_program.MinimumSalePrice,actual_point,'LoyaltyCustomerIDLoyaltyCustomerIDLoyaltyCustomerID')
        # Loyalty Calculation END heare******************
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Radeem Loyalty Point Start heare>>>>>>>>>>>>
        loyalty_point_value = None
        if GeneralSettings.objects.filter(CompanyID=instance.CompanyID, SettingsType="loyalty_point_value").exists():
            loyalty_point_value = GeneralSettings.objects.get(CompanyID=instance.CompanyID, SettingsType="loyalty_point_value").SettingsValue
        if RadeemPoint and loyalty_point_value:
            print(RadeemPoint,"*********************************************************************************************************",loyalty_point_value)
            # radeem = RadeemPoint.split("-")
            # radeem_value = radeem[1]
            # radeem_point = int(radeem[0]) * -1
            radeem_value = int(loyalty_point_value)*int(RadeemPoint)
            radeem_point = int(RadeemPoint) * -1
            if int(instance.GrandTotal) >= int(radeem_value):
                LoyaltyPointID = get_point_auto_id(LoyaltyPoint, instance.BranchID, instance.CompanyID)
                a = LoyaltyPoint.objects.create(
                    BranchID=instance.BranchID,
                    LoyaltyPointID=LoyaltyPointID,
                    Value=radeem_value,
                    VoucherType="SI",
                    VoucherMasterID=instance.SalesMasterID,
                    Point=radeem_point,
                    ExpiryDate=ExpiryDate,
                    LoyaltyCustomerID=loyalty_customer,
                    LoyaltyProgramID=loyalty_program,
                    is_Radeem=True,
                
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CompanyID=instance.CompanyID,
                )
                LoyaltyPoint_Log.objects.create(
                    BranchID=instance.BranchID,
                    LoyaltyPointID=LoyaltyPointID,
                    Value=radeem_value,
                    VoucherType="SI",
                    VoucherMasterID=instance.SalesMasterID,
                    Point=radeem_point,
                    ExpiryDate=ExpiryDate,
                    LoyaltyCustomerID=loyalty_customer,
                    LoyaltyProgramID=loyalty_program,
                    is_Radeem=True,
                
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CompanyID=instance.CompanyID,
                )

                # <<<<<LedgerPosting>>>
                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting, instance.BranchID, instance.CompanyID)
                print(radeem_point,'radeem_point ++++++++*********HAB',a,'EEB*********+++++++++ RadeemPoint',RadeemPoint)
                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=instance.BranchID,
                    Date=instance.Date,
                    VoucherMasterID=instance.SalesMasterID,
                    VoucherType="SI",
                    VoucherNo=instance.VoucherNo,
                    LedgerID=73,
                    Debit=radeem_value,
                    IsActive=instance.IsActive,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=instance.CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=instance.BranchID,
                    Date=instance.Date,
                    VoucherMasterID=instance.SalesMasterID,
                    VoucherType="SI",
                    VoucherNo=instance.VoucherNo,
                    LedgerID=73,
                    Debit=radeem_value,
                    IsActive=instance.IsActive,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=instance.CompanyID,
                )
                # <<<<<LedgerPosting END HEARE>>>

            # print(radeem_point,RadeemPoint.split("-"))
            sale_date = str_To_Date(instance.Date)
            if LoyaltyPoint.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,LoyaltyCustomerID=loyalty_customer,VoucherType="SI",ExpiryDate__gte=sale_date,is_Radeem=False).exists():
                point_instances = LoyaltyPoint.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,LoyaltyCustomerID=loyalty_customer,VoucherType="SI",ExpiryDate__gte=sale_date,is_Radeem=False).order_by("LoyaltyPointID")
                # balance_point = float(radeem[0])
                balance_point = int(RadeemPoint)
                for i in point_instances:
                    Point = float(i.Point)
                    if i.Radeemed_Point:
                        Radeemed_Point = float(i.Radeemed_Point)
                        float(i.Radeemed_Point)
                    else:
                        Radeemed_Point = 0 
                    Point = float(i.Point)
                    if not balance_point <= 0:
                        w = Point - Radeemed_Point
                        if float(w) <= float(balance_point) and Point != Radeemed_Point:
                           
                            # =================

                            # =================



                            print(Point,'ifAAAAAAAAAAA',Radeemed_Point,'UVAISANNNNNNNNNNNNN',balance_point)
                            print("IFFFFFFF")
                            balance_point -= w
                            # balance_point = balance_point+Radeemed_Point - Point
                            b = float(Radeemed_Point) + w
                            i.Radeemed_Point = b
                        elif w>= balance_point and Point != Radeemed_Point:
                            print(Point,'ElseAAAAAAAAAAA',Radeemed_Point,'UVAISANNNNNNNNNNNNN',balance_point)

                            i.Radeemed_Point = balance_point+Radeemed_Point
                            balance_point -= balance_point 
                            

                            # b = Radeemed_Point + balance_point
                            # q = Point - Radeemed_Point
                            # ==========
                            # i.Radeemed_Point = Radeemed_Point + q
                            # ==========


                           
                            
                            # if Point <= q:
                            #     i.Radeemed_Point = balance_point
                            #     balance_point = 0
                            #     print(balance_point,"ELSEIFFFFFFF1")
                            # elif Point >= Radeemed_Point:
                            #     balance_point = balance_point - q
                            #     if balance_point > 0:
                            #         i.Radeemed_Point = Radeemed_Point + q
                            #         print(balance_point,"!!!!!!!!!!!!!!!!!!!!1")
                            #     else:
                            #         print(balance_point,"2222222222222222222")
                            #         i.Radeemed_Point = Radeemed_Point+abs(balance_point)
                            #         balance_point = 0
                            #     print(balance_point,"ELSEIFFFFFFF2")
                        i.save()
                        if balance_point <= 0:
                            break

        # TOTAL LOYALTY Customer Point
        is_edit = False
        if LoyaltyPoint.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,VoucherType="SI",LoyaltyCustomerID=loyalty_customer,is_Radeem=True).exists():
            is_edit = True
        if LoyaltyPoint.objects.filter(LoyaltyCustomerID=loyalty_customer,BranchID=instance.BranchID, CompanyID=instance.CompanyID).exists():
            loyalty_instances = LoyaltyPoint.objects.filter(
                LoyaltyCustomerID=loyalty_customer,BranchID=instance.BranchID, CompanyID=instance.CompanyID)

            tot_Point = 0
            # today_date = datetime.datetime.now().date()
            today_date = str_To_Date(instance.Date)
           
            for i in loyalty_instances:
                if i.Point:
                    if Loyalty_Point_Expire:
                        if i.ExpiryDate:
                            if not today_date >= i.ExpiryDate:
                                if Action == "M":
                                    if is_edit:
                                        tot_Point = float(tot_Point) + float(i.Point) 
                                elif Action == "A":
                                    tot_Point = float(tot_Point) + float(i.Point) 
                    else:
                        if Action == "M":
                            if is_edit:
                                tot_Point = float(tot_Point) + float(i.Point) 
                        elif Action == "A":
                            tot_Point  += float(i.Point) 
            if LoyaltyCustomer.objects.filter(pk=loyalty_customer.pk).exists():
                ins = LoyaltyCustomer.objects.get(pk=loyalty_customer.pk)
                ins.CurrentPoint = tot_Point
                ins.save()


        # >>>>>>>>>>>>>>>Radeem Loyalty Point End heare>>>>>>>>>>>>>>

def str_To_Date(date):
    # converting string type to date type
    date_time_str = str(date) + str(" ") + str('00:00:00')
    date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    date = date_time_obj.date()
    return date


def get_actual_point(tot_TaxableAmount,instance):
    if instance.Calculate_with == "Amount":
        Amount = instance.Amount
        Amount_Point = instance.Amount_Point
        # ======1st
        p_amount = Amount_Point/Amount*100
        # ======2st
        print(tot_TaxableAmount,"Amount......")
        actual_point = int(tot_TaxableAmount)/100*int(p_amount)
    elif instance.Calculate_with == "Percentage":
        print("Percentage......")
        Percentage = instance.Percentage
        actual_point = int(tot_TaxableAmount)/100*int(Percentage)
    return actual_point


def edit_LoyaltyCalculation(instance,loyalty_customer,details,Loyalty_Point_Expire,RadeemPoint):
    today = datetime.datetime.now()
    print(loyalty_customer.CardTypeID.Name)
    loyalty_program = None
    if LoyaltyProgram.objects.filter(CardTypeID=loyalty_customer.CardTypeID,FromDate__lte=instance.Date,ToDate__gte=instance.Date).exists():
        loyalty_program = LoyaltyProgram.objects.get(CardTypeID=loyalty_customer.CardTypeID,FromDate__lte=instance.Date,ToDate__gte=instance.Date)

    # ExpiryDate
    # import datetime
    # Loyalty_Point_Expire = data['Loyalty_Point_Expire']
    ExpiryDate = None
    if Loyalty_Point_Expire:
        current_date = "12/6/20"
        current_date_temp = datetime.datetime.strptime(instance.Date, "%Y-%m-%d")
        ExpiryDate = current_date_temp + datetime.timedelta(days=int(loyalty_program.NoOFDayExpPoint))
    else:
        current_date_temp = datetime.datetime.strptime(instance.Date, "%Y-%m-%d")
        ExpiryDate = current_date_temp + datetime.timedelta(days=int(365))
    # ====

    # Loyalty Calculation Start heare************
    salesdetails = details
    Group_ids = loyalty_program.ProductGroupIDs.split(',')
    Cat_ids = loyalty_program.ProductCategoryIDs.split(',')

    ProductGroupIDs = [i for i in Group_ids if i]
    ProductCategoryIDs = [i for i in Cat_ids if i]
    print(ProductGroupIDs,"QQQQQUVAISQQQQQQ",ProductCategoryIDs)
    tot_TaxableAmount = 0
    if SalesDetails:
        for salesdetail in salesdetails:

            ProductID = salesdetail['ProductID']
            # BranchID = instance.BranchID
            # CompanyID = instance.CompanyID
            if ProductGroupIDs:
                if Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupIDs):
                    pro_instance = Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupIDs)
                    for i in pro_instance:
                        if ProductID == i.ProductID:
                            tot_TaxableAmount += int(salesdetail['TaxableAmount'])
            elif ProductCategoryIDs:
                ProductGroupID = ProductGroup.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,CategoryID__in=ProductCategoryIDs).values_list('ProductGroupID',flat=True)
                if Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupID):
                    pro_instance = Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,ProductGroupID__in=ProductGroupID)
                    for i in pro_instance:
                        if ProductID == i.ProductID:
                            tot_TaxableAmount += int(salesdetail['TaxableAmount'])
            else:
                if Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID):
                    pro_instance = Product.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID)
                    for i in pro_instance:
                        if ProductID == i.ProductID:
                            tot_TaxableAmount += int(salesdetail['TaxableAmount'])
                    TaxableAmount = float(salesdetail['TaxableAmount'])
                    # =======*******************============
    actual_point = 0
    if tot_TaxableAmount > loyalty_program.MinimumSalePrice:
        print("VALUTHAAAAN")
        MinimumSalePrice = loyalty_program.MinimumSalePrice
        Calculate_with = loyalty_program.Calculate_with

        if Calculate_with == "Amount":
            Amount = loyalty_program.Amount
            Amount_Point = loyalty_program.Amount_Point
            # ======1st
            p_amount = Amount_Point/Amount*100
            # ======2st
            print(tot_TaxableAmount,"Amount......")
            actual_point = int(tot_TaxableAmount)/100*int(p_amount)
        elif Calculate_with == "Percentage":
            print("Percentage......")
            Percentage = loyalty_program.Percentage
            actual_point = int(tot_TaxableAmount)/100*int(Percentage)

       
        
        print(actual_point,"instance")

        if actual_point:
            point_radeemd = []
            LoyaltyPointID = None
            if LoyaltyPoint.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,VoucherType="SI",VoucherMasterID=instance.SalesMasterID,is_Radeem=False).exists():
                point_instance = LoyaltyPoint.objects.get(BranchID=instance.BranchID,CompanyID=instance.CompanyID,VoucherType="SI",VoucherMasterID=instance.SalesMasterID,is_Radeem=False)
                # point_instance.Point = actual_point
                # point_instance.Value = actual_point
                # LoyaltyPointID = point_instance.LoyaltyPointID
                point_radeemd.append(point_instance.Radeemed_Point) 
                point_instance.delete()
            print(point_radeemd,'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY')
           
            LoyaltyPointID = get_point_auto_id(LoyaltyPoint, instance.BranchID, instance.CompanyID)
            LoyaltyPoint.objects.create(
                BranchID=instance.BranchID,
                LoyaltyPointID=LoyaltyPointID,
                Value=actual_point,
                VoucherType="SI",
                VoucherMasterID=instance.SalesMasterID,
                Point=actual_point,
                ExpiryDate=ExpiryDate,
                LoyaltyCustomerID=loyalty_customer,
                LoyaltyProgramID=loyalty_program,
                is_Radeem=False,

                CreatedDate=today,
                UpdatedDate=today,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CompanyID=instance.CompanyID,
            )
            LoyaltyPoint_Log.objects.create(
                BranchID=instance.BranchID,
                LoyaltyPointID=LoyaltyPointID,
                Value=actual_point,
                VoucherType="SI",
                VoucherMasterID=instance.SalesMasterID,
                Point=actual_point,
                ExpiryDate=ExpiryDate,
                LoyaltyCustomerID=loyalty_customer,
                LoyaltyProgramID=loyalty_program,
                is_Radeem=False,
            
                CreatedDate=today,
                UpdatedDate=today,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CompanyID=instance.CompanyID,
            )
    # Loyalty Calculation END heare******************
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Radeem Loyalty Point Start heare>>>>>>>>>>>>
    if RadeemPoint:
        RadeemPoint = RadeemPoint
    else:
        RadeemPoint = None
    loyalty_point_value = None
    if GeneralSettings.objects.filter(CompanyID=instance.CompanyID, SettingsType="loyalty_point_value").exists():
        loyalty_point_value = GeneralSettings.objects.get(CompanyID=instance.CompanyID, SettingsType="loyalty_point_value").SettingsValue
    if RadeemPoint and loyalty_point_value:
        # radeem = RadeemPoint.split("-")
        # radeem_value = radeem[1]
        radeem_value = int(loyalty_point_value)*int(RadeemPoint)
        radeem_point = int(RadeemPoint) * -1
        if int(instance.GrandTotal) >= int(radeem_value):
            if LoyaltyPoint.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,VoucherType="SI",VoucherMasterID=instance.SalesMasterID,is_Radeem=True).exists():
                radeem_instance = LoyaltyPoint.objects.get(BranchID=instance.BranchID,CompanyID=instance.CompanyID,VoucherType="SI",VoucherMasterID=instance.SalesMasterID,is_Radeem=True)
                # radeem_instance.Value=radeem_value,
                # radeem_instance.VoucherType="SI",
                # radeem_instance.VoucherMasterID=instance.SalesMasterID,
                # radeem_instance.Point=radeem_point,
                # radeem_instance.ExpiryDate=ExpiryDate,
                # radeem_instance.LoyaltyCustomerID=loyalty_customer,
                # radeem_instance.LoyaltyProgramID=loyalty_program,
                radeem_instance.delete()
            print(radeem_point,'radeem_point +++++++++++++++++ RadeemPoint',RadeemPoint)
            LoyaltyPointID = get_point_auto_id(LoyaltyPoint, instance.BranchID, instance.CompanyID)
            LoyaltyPoint.objects.create(
                BranchID=instance.BranchID,
                LoyaltyPointID=LoyaltyPointID,
                Value=radeem_value,
                VoucherType="SI",
                VoucherMasterID=instance.SalesMasterID,
                Point=radeem_point,
                ExpiryDate=ExpiryDate,
                LoyaltyCustomerID=loyalty_customer,
                LoyaltyProgramID=loyalty_program,
                is_Radeem=True,
            
                CreatedDate=today,
                UpdatedDate=today,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CompanyID=instance.CompanyID,
            )
            LoyaltyPoint_Log.objects.create(
                BranchID=instance.BranchID,
                LoyaltyPointID=LoyaltyPointID,
                Value=radeem_value,
                VoucherType="SI",
                VoucherMasterID=instance.SalesMasterID,
                Point=radeem_point,
                ExpiryDate=ExpiryDate,
                LoyaltyCustomerID=loyalty_customer,
                LoyaltyProgramID=loyalty_program,
                is_Radeem=True,
            
                CreatedDate=today,
                UpdatedDate=today,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CompanyID=instance.CompanyID,
            )

            # <<<<<LedgerPosting>>>
            # delete and add LedgerPosting
            if LedgerPosting.objects.filter(CompanyID=instance.CompanyID,BranchID=instance.BranchID,VoucherMasterID=instance.SalesMasterID,VoucherType="SI",LedgerID=73).exists():
                print("DELETELEDGERPOST....")
                ledger_ins = LedgerPosting.objects.get(CompanyID=instance.CompanyID,BranchID=instance.BranchID,VoucherMasterID=instance.SalesMasterID,VoucherType="SI",LedgerID=73)
                ledger_ins.delete()
            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting, instance.BranchID, instance.CompanyID)
            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=instance.BranchID,
                Date=instance.Date,
                VoucherMasterID=instance.SalesMasterID,
                VoucherType="SI",
                VoucherNo=instance.VoucherNo,
                LedgerID=73,
                Debit=radeem_value,
                IsActive=instance.IsActive,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=instance.CompanyID,
            )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=instance.BranchID,
                Date=instance.Date,
                VoucherMasterID=instance.SalesMasterID,
                VoucherType="SI",
                VoucherNo=instance.VoucherNo,
                LedgerID=73,
                Debit=radeem_value,
                IsActive=instance.IsActive,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=instance.CompanyID,
            )
            # <<<<<LedgerPosting END HEARE>>>

            print(radeem_point,RadeemPoint.split("-"))
            sale_date = str_To_Date(instance.Date)
            if LoyaltyPoint.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,LoyaltyCustomerID=loyalty_customer,VoucherType="SI",ExpiryDate__gte=sale_date,is_Radeem=False).exists():
                point_instances = LoyaltyPoint.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,LoyaltyCustomerID=loyalty_customer,VoucherType="SI",ExpiryDate__gte=sale_date,is_Radeem=False)
                print(radeem_point,'2POOOOOOOOOOOOOOO(++++++++++++++++++++++++++++++++++++++++++++++++++))NNNNNNNNNTTTTTTT')
                balance_point = int(RadeemPoint)
                for i in point_instances:
                    Point = float(i.Point)
                    if i.Radeemed_Point:
                        Radeemed_Point = float(i.Radeemed_Point)
                        float(i.Radeemed_Point)
                    else:
                        Radeemed_Point = 0 
                    Point = float(i.Point)
                    print(Point,'EQUALAAAAAAAAAAA',Radeemed_Point,'UVAISANNNNNNNNNNNNN',balance_point)
                    if float(Point) <= float(balance_point)+float(Radeemed_Point) and Point != Radeemed_Point:
                    # if Point <= balance_point+Radeemed_Point and Point != Radeemed_Point:
                        print("IFFFFFFF")
                        balance_point = balance_point+Radeemed_Point - Point
                        b = float(Radeemed_Point) + Point
                        i.Radeemed_Point = b
                    elif Point>= balance_point and Point != Radeemed_Point:
                        i.Radeemed_Point = Radeemed_Point + balance_point
                        # i.Radeemed_Point =  balance_point
                        balance_point = 0
                        print(balance_point,"ELSEIFFFFFFF")
                    i.save()

            print(radeem_point,RadeemPoint.split("-"))
    # >>>>>>>>>>>>>>>Radeem Loyalty Point End heare>>>>>>>>>>>>>>
    # TOTAL LOYALTY Customer Point
    is_edit = False
    if LoyaltyPoint.objects.filter(BranchID=instance.BranchID,CompanyID=instance.CompanyID,VoucherType="SI",LoyaltyCustomerID=loyalty_customer,is_Radeem=True).exists():
        is_edit = True
    if LoyaltyPoint.objects.filter(LoyaltyCustomerID=loyalty_customer,BranchID=instance.BranchID, CompanyID=instance.CompanyID,VoucherType="SI").exists():
        instances = LoyaltyPoint.objects.filter(
            LoyaltyCustomerID=loyalty_customer,BranchID=instance.BranchID, CompanyID=instance.CompanyID,VoucherType="SI")

        tot_Point = 0
        # today_date = datetime.datetime.now().date()
        today_date = str_To_Date(instance.Date)

        for i in instances:
            print(tot_Point,i.Point)
            if i.Point:
                if Loyalty_Point_Expire:
                    if i.ExpiryDate:
                        if not today_date >= i.ExpiryDate:
                            if instance.Action == "M":
                                # if is_edit:
                                tot_Point = float(tot_Point) + float(i.Point) 
                                print(("1 i.ExpiryDate Kayaryyyyyyyyyyyyyy"))
                            elif instance.Action == "A":
                                tot_Point = float(tot_Point) + float(i.Point) 
                                print(("2 i.ExpiryDate Kayaryyyyyyyyyyyyyy"))
                else:
                    if instance.Action == "M":
                        # if is_edit:
                        tot_Point = float(tot_Point) + float(i.Point) 
                        print((tot_Point,"3 i.ExpiryDate Kayaryyyyyyyyyyyyyy",i.Point))
                    elif instance.Action == "A":
                        tot_Point = float(tot_Point) + float(i.Point) 
                        print(("4 i.ExpiryDate Kayaryyyyyyyyyyyyyy"))
        if LoyaltyCustomer.objects.filter(pk=loyalty_customer.pk).exists():
            print((tot_Point,"i.ExpiryDate Kayaryyyyyyyyyyyyyy()_()_()_()_"))
            ins = LoyaltyCustomer.objects.get(pk=loyalty_customer.pk)
            ins.CurrentPoint = tot_Point
            ins.save()

