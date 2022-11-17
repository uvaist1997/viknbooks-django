from brands.models import PurchaseReturnMaster, PurchaseReturnMaster_Log, PurchaseReturnDetails, PurchaseReturnDetails_Log,\
StockPosting, LedgerPosting, StockPosting_Log, LedgerPosting_Log, PurchaseReturnDetailsDummy, PriceList, StockRate, StockTrans,\
PurchaseMaster, PurchaseDetails
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.purchaseReturns.serializers import PurchaseReturnMasterSerializer, PurchaseReturnMasterRestSerializer, PurchaseReturnDetailsSerializer, PurchaseReturnDetailsRestSerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.purchaseReturns.functions import generate_serializer_errors
from rest_framework import status
from api.v2.sales.serializers import ListSerializerforReport
from api.v2.purchaseReturns.functions import get_auto_id, get_auto_idMaster
from api.v2.sales.functions import get_auto_stockPostid
from api.v2.accountLedgers.functions import get_auto_LedgerPostid
from api.v2.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
import datetime
from main.functions import get_company, activity_log, list_pagination


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_purchaseReturn(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']

    BranchID = data['BranchID']
    VoucherDate = data['VoucherDate']
    VoucherNo = data['VoucherNo']
    RefferenceBillNo = data['RefferenceBillNo']
    RefferenceBillDate = data['RefferenceBillDate']
    VenderInvoiceDate = data['VenderInvoiceDate']
    CreditPeriod = data['CreditPeriod']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    PurchaseAccount = data['PurchaseAccount']
    DeliveryMasterID = data['DeliveryMasterID']
    OrderMasterID = data['OrderMasterID']
    CustomerName = data['CustomerName']
    Address1 = data['Address1']
    Address2 = data['Address2']
    Address3 = data['Address3']
    Notes = data['Notes']
    FinacialYearID = data['FinacialYearID']
    IsActive = data['IsActive']
    WarehouseID = data['WarehouseID']
    BatchID = data['BatchID']
    TaxID = data['TaxID']
    TaxType = data['TaxType']

    TotalTax = float(data['TotalTax'])
    NetTotal = float(data['NetTotal'])
    AdditionalCost = float(data['AdditionalCost'])
    GrandTotal = float(data['GrandTotal'])
    RoundOff = float(data['RoundOff'])
    TotalGrossAmt = float(data['TotalGrossAmt'])
    VATAmount = float(data['VATAmount'])
    SGSTAmount = float(data['SGSTAmount'])
    CGSTAmount = float(data['CGSTAmount'])
    IGSTAmount = float(data['IGSTAmount'])
    TAX1Amount = float(data['TAX1Amount'])
    TAX2Amount = float(data['TAX2Amount'])
    TAX3Amount = float(data['TAX3Amount'])
    AddlDiscPercent = float(data['AddlDiscPercent'])
    AddlDiscAmt = float(data['AddlDiscAmt'])
    TotalDiscount = float(data['TotalDiscount'])
    BillDiscPercent = float(data['BillDiscPercent'])
    BillDiscAmt = float(data['BillDiscAmt'])

    TotalTax = round(TotalTax,PriceRounding)
    NetTotal = round(NetTotal,PriceRounding)
    AdditionalCost = round(AdditionalCost,PriceRounding)
    GrandTotal = round(GrandTotal,PriceRounding)
    RoundOff = round(RoundOff,PriceRounding)

    TotalGrossAmt = round(TotalGrossAmt,PriceRounding)
    VATAmount = round(VATAmount,PriceRounding)
    SGSTAmount = round(SGSTAmount,PriceRounding)
    CGSTAmount = round(CGSTAmount,PriceRounding)
    IGSTAmount = round(IGSTAmount,PriceRounding)

    TAX1Amount = round(TAX1Amount,PriceRounding)
    TAX2Amount = round(TAX2Amount,PriceRounding)
    TAX3Amount = round(TAX3Amount,PriceRounding)
    AddlDiscPercent = round(AddlDiscPercent,PriceRounding)
    AddlDiscAmt = round(AddlDiscAmt,PriceRounding)

    TotalDiscount = round(TotalDiscount,PriceRounding)
    BillDiscPercent = round(BillDiscPercent,PriceRounding)
    BillDiscAmt = round(BillDiscAmt,PriceRounding)


    Action = "A"

    #checking voucher number already exist
    VoucherNoLow = VoucherNo.lower()
    is_voucherExist = False
    insts = PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    if not is_voucherExist:
        
        PurchaseReturnMasterID = get_auto_idMaster(PurchaseReturnMaster,BranchID,CompanyID)

        PurchaseReturnMaster.objects.create(
            PurchaseReturnMasterID=PurchaseReturnMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            VoucherDate=VoucherDate,
            RefferenceBillNo=RefferenceBillNo,
            RefferenceBillDate=RefferenceBillDate,
            VenderInvoiceDate=VenderInvoiceDate,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            PurchaseAccount=PurchaseAccount,
            DeliveryMasterID=DeliveryMasterID,
            OrderMasterID=OrderMasterID,
            CustomerName=CustomerName,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            Notes=Notes,
            FinacialYearID=FinacialYearID,
            TotalGrossAmt=TotalGrossAmt,
            TotalTax=TotalTax,
            NetTotal=NetTotal,
            AdditionalCost=AdditionalCost,
            GrandTotal=GrandTotal,
            RoundOff=RoundOff,
            WarehouseID=WarehouseID,
            IsActive=IsActive,
            CreatedUserID=CreatedUserID,
            Action=Action,
            CreatedDate=today,
            UpdatedDate=today,
            TaxID=TaxID,
            TaxType=TaxType,
            VATAmount=VATAmount,
            SGSTAmount=SGSTAmount,
            CGSTAmount=CGSTAmount,
            IGSTAmount=IGSTAmount,
            TAX1Amount=TAX1Amount,
            TAX2Amount=TAX2Amount,
            TAX3Amount=TAX3Amount,
            AddlDiscPercent=AddlDiscPercent,
            AddlDiscAmt=AddlDiscAmt,
            TotalDiscount=TotalDiscount,
            BillDiscPercent=BillDiscPercent,
            BillDiscAmt=BillDiscAmt,
            CompanyID=CompanyID,
            )

        PurchaseReturnMaster_Log.objects.create(
            TransactionID=PurchaseReturnMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            VoucherDate=VoucherDate,
            RefferenceBillNo=RefferenceBillNo,
            RefferenceBillDate=RefferenceBillDate,
            VenderInvoiceDate=VenderInvoiceDate,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            PurchaseAccount=PurchaseAccount,
            DeliveryMasterID=DeliveryMasterID,
            OrderMasterID=OrderMasterID,
            CustomerName=CustomerName,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            Notes=Notes,
            FinacialYearID=FinacialYearID,
            TotalGrossAmt=TotalGrossAmt,
            TotalTax=TotalTax,
            NetTotal=NetTotal,
            AdditionalCost=AdditionalCost,
            GrandTotal=GrandTotal,
            RoundOff=RoundOff,
            WarehouseID=WarehouseID,
            IsActive=IsActive,
            CreatedUserID=CreatedUserID,
            Action=Action,
            CreatedDate=today,
            UpdatedDate=today,
            TaxID=TaxID,
            TaxType=TaxType,
            VATAmount=VATAmount,
            SGSTAmount=SGSTAmount,
            CGSTAmount=CGSTAmount,
            IGSTAmount=IGSTAmount,
            TAX1Amount=TAX1Amount,
            TAX2Amount=TAX2Amount,
            TAX3Amount=TAX3Amount,
            AddlDiscPercent=AddlDiscPercent,
            AddlDiscAmt=AddlDiscAmt,
            TotalDiscount=TotalDiscount,
            BillDiscPercent=BillDiscPercent,
            BillDiscAmt=BillDiscAmt,
            CompanyID=CompanyID,
            )

        VoucherType = "PR"

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=PurchaseAccount,
            Credit=TotalGrossAmt,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

        LedgerPosting_Log.objects.create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=PurchaseAccount,
            Credit=TotalGrossAmt,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=GrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

        LedgerPosting_Log.objects.create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=GrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

        if float(TotalTax) > 0:

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

            LedgerID = "55"

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Credit=TotalTax,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Credit=TotalTax,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

        if float(BillDiscAmt) > 0:

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

            LedgerID = "74"

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Debit=BillDiscAmt,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Debit=BillDiscAmt,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

        if float(RoundOff) > 0:

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

            LedgerID = "78"

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Credit=RoundOff,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Credit=RoundOff,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

        if float(RoundOff) < 0:

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

            RoundOff = abs(float(RoundOff))

            LedgerID = "78"

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Debit=RoundOff,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Debit=RoundOff,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

        purchaseReturnDetails = data["PurchaseReturnDetails"]

        for purchaseReturnDetail in purchaseReturnDetails:

            # PurchaseReturnMasterID = serialized.data['PurchaseReturnMasterID']
            DeliveryDetailsID = purchaseReturnDetail['DeliveryDetailsID']
            OrderDetailsID = purchaseReturnDetail['OrderDetailsID']
            ProductID = purchaseReturnDetail['ProductID']
            Qty = purchaseReturnDetail['Qty']
            FreeQty = purchaseReturnDetail['FreeQty']
            PriceListID = purchaseReturnDetail['PriceListID']

            DiscountPerc = float(purchaseReturnDetail['DiscountPerc'])
            DiscountAmount = float(purchaseReturnDetail['DiscountAmount'])
            GrossAmount = float(purchaseReturnDetail['GrossAmount'])
            TaxableAmount = float(purchaseReturnDetail['TaxableAmount'])
            VATPerc = float(purchaseReturnDetail['VATPerc'])
            VATAmount = float(purchaseReturnDetail['VATAmount'])
            SGSTPerc = float(purchaseReturnDetail['SGSTPerc'])
            SGSTAmount = float(purchaseReturnDetail['SGSTAmount'])
            CGSTPerc = float(purchaseReturnDetail['CGSTPerc'])
            CGSTAmount = float(purchaseReturnDetail['CGSTAmount'])
            IGSTPerc = float(purchaseReturnDetail['IGSTPerc'])
            IGSTAmount = float(purchaseReturnDetail['IGSTAmount'])
            NetAmount = float(purchaseReturnDetail['NetAmount'])
            RateWithTax = float(purchaseReturnDetail['RateWithTax'])
            CostPerPrice = float(purchaseReturnDetail['CostPerPrice'])
            UnitPrice = float(purchaseReturnDetail['UnitPrice'])
            InclusivePrice = float(purchaseReturnDetail['InclusivePrice'])
            AddlDiscPerc = float(purchaseReturnDetail['AddlDiscPerc'])
            AddlDiscAmt = float(purchaseReturnDetail['AddlDiscAmt'])
            TAX1Perc = float(purchaseReturnDetail['TAX1Perc'])
            TAX1Amount = float(purchaseReturnDetail['TAX1Amount'])
            TAX2Perc = float(purchaseReturnDetail['TAX2Perc'])
            TAX2Amount = float(purchaseReturnDetail['TAX2Amount'])
            TAX3Perc = float(purchaseReturnDetail['TAX3Perc'])
            TAX3Amount = float(purchaseReturnDetail['TAX3Amount'])
        
            DiscountPerc = round(DiscountPerc,PriceRounding)
            DiscountAmount = round(DiscountAmount,PriceRounding)
            GrossAmount = round(GrossAmount,PriceRounding)
            TaxableAmount = round(TaxableAmount,PriceRounding)
            VATPerc = round(VATPerc,PriceRounding)

            VATAmount = round(VATAmount,PriceRounding)
            SGSTPerc = round(SGSTPerc,PriceRounding)
            SGSTAmount = round(SGSTAmount,PriceRounding)
            CGSTPerc = round(CGSTPerc,PriceRounding)
            CGSTAmount = round(CGSTAmount,PriceRounding)

            IGSTPerc = round(IGSTPerc,PriceRounding)
            IGSTAmount = round(IGSTAmount,PriceRounding)
            NetAmount = round(NetAmount,PriceRounding)
            RateWithTax = round(RateWithTax,PriceRounding)
            CostPerPrice = round(CostPerPrice,PriceRounding)

            UnitPrice = round(UnitPrice,PriceRounding)
            InclusivePrice = round(InclusivePrice,PriceRounding)
            AddlDiscPerc = round(AddlDiscPerc,PriceRounding)
            AddlDiscAmt = round(AddlDiscAmt,PriceRounding)
            TAX1Perc = round(TAX1Perc,PriceRounding)

            TAX1Amount = round(TAX1Amount,PriceRounding)
            TAX2Perc = round(TAX2Perc,PriceRounding)
            TAX2Amount = round(TAX2Amount,PriceRounding)
            TAX3Perc = round(TAX3Perc,PriceRounding)
            TAX3Amount = round(TAX3Amount,PriceRounding)



            PurchaseReturnQty = Qty
            PurchaseReturnDetailsID = get_auto_id(PurchaseReturnDetails,BranchID,CompanyID)

            PurchaseReturnDetails.objects.create(
                PurchaseReturnDetailsID=PurchaseReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                PurchaseReturnMasterID=PurchaseReturnMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                InclusivePrice=InclusivePrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                DiscountPerc=DiscountPerc,
                DiscountAmount=DiscountAmount,
                GrossAmount=GrossAmount,
                TaxableAmount=TaxableAmount,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                AddlDiscPerc=AddlDiscPerc,
                AddlDiscAmt=AddlDiscAmt,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                )

            PurchaseReturnDetails_Log.objects.create(
                TransactionID=PurchaseReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                PurchaseReturnMasterID=PurchaseReturnMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                InclusivePrice=InclusivePrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                DiscountPerc=DiscountPerc,
                DiscountAmount=DiscountAmount,
                GrossAmount=GrossAmount,
                TaxableAmount=TaxableAmount,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                AddlDiscPerc=AddlDiscPerc,
                AddlDiscAmt=AddlDiscAmt,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                )


            # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID)

            # PriceListID_DefUnit = priceList.PriceListID
            # MultiFactor = priceList.MultiFactor

            MultiFactor = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).MultiFactor
            PriceListID_DefUnit = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID).PriceListID

            # PurchasePrice = priceList.PurchasePrice
            # SalesPrice = priceList.SalesPrice

            qty = float(FreeQty) + float(Qty)

            Qty = float(MultiFactor) * float(qty)
            Cost = float(CostPerPrice) /  float(MultiFactor)

            Qy = round(Qty,4)
            Qty = str(Qy)

            Ct = round(Cost,4)
            Cost = str(Ct)

            princeList_instance = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,BranchID=BranchID)
            PurchasePrice = princeList_instance.PurchasePrice
            SalesPrice = princeList_instance.SalesPrice

            
            changQty = Qty
            if StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,WareHouseID=WarehouseID,Qty__gt=0).exists():
                stockRate_instances = StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,WareHouseID=WarehouseID,Qty__gt=0)
                for stockRate_instance in stockRate_instances:
                    StockRateID = stockRate_instance.StockRateID
                    if float(stockRate_instance.Qty) > float(Qty):
                        stockRate_instance.Qty = float(stockRate_instance.Qty) - float(Qty)
                        changQty = 0
                        stockRate_instance.save()

                        if StockPosting.objects.filter(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                            VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit).exists():
                            stockPost_instance = StockPosting.objects.get(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                                VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit)
                            QtyOut = stockPost_instance.QtyOut
                            newQty = float(QtyOut) + float(Qty)
                            stockPost_instance.save()
                        else:
                            StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=PurchaseReturnMasterID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                                )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=PurchaseReturnMasterID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                                )

                        if StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).exists():
                            stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).first()
                            stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                            stockTra_in.save()
                        else:
                            StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                            StockTrans.objects.create(
                                StockTransID=StockTransID,
                                BranchID=BranchID,
                                VoucherType=VoucherType,
                                StockRateID=StockRateID,
                                DetailID=PurchaseReturnDetailsID,
                                MasterID=PurchaseReturnMasterID,
                                Qty=Qty,
                                IsActive=IsActive,
                                CompanyID=CompanyID,
                                )

                        
                    elif float(stockRate_instance.Qty) < float(Qty):

                        if float(changQty) > float(stockRate_instance.Qty):
                            changQty = float(changQty) - float(stockRate_instance.Qty)
                            stockRate_instance.Qty = 0
                            stockRate_instance.save()

                            if StockPosting.objects.filter(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                                VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit).exists():
                                stockPost_instance = StockPosting.objects.get(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                                    VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit)
                                QtyOut = stockPost_instance.QtyOut
                                newQty = QtyOut + stockRate_instance.Qty
                                stockPost_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
                                StockPosting.objects.create(
                                    StockPostingID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=VoucherDate,
                                    VoucherMasterID=PurchaseReturnMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
                                    WareHouseID=WarehouseID,
                                    QtyOut=stockRate_instance.Qty,
                                    Rate=Cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                    )

                                StockPosting_Log.objects.create(
                                    TransactionID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=VoucherDate,
                                    VoucherMasterID=PurchaseReturnMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
                                    WareHouseID=WarehouseID,
                                    QtyOut=stockRate_instance.Qty,
                                    Rate=Cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                    )
                        else:
                            if changQty < 0:
                                changQty=0
                            chqty = changQty
                            changQty = float(stockRate_instance.Qty) - float(changQty)
                            stockRate_instance.Qty = changQty
                            changQty = 0
                            stockRate_instance.save()

                            if StockPosting.objects.filter(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                                VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit).exists():
                                stockPost_instance = StockPosting.objects.get(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                                    VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit)
                                QtyOut = stockPost_instance.QtyOut
                                newQty = QtyOut + chqty
                                stockPost_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
                                StockPosting.objects.create(
                                    StockPostingID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=VoucherDate,
                                    VoucherMasterID=PurchaseReturnMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
                                    WareHouseID=WarehouseID,
                                    QtyOut=chqty,
                                    Rate=Cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                    )

                                StockPosting_Log.objects.create(
                                    TransactionID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=VoucherDate,
                                    VoucherMasterID=PurchaseReturnMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
                                    WareHouseID=WarehouseID,
                                    QtyOut=chqty,
                                    Rate=Cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                    )

                        if StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).exists():
                            stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).first()
                            stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                            stockTra_in.save()
                        else:
                            StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                            StockTrans.objects.create(
                                StockTransID=StockTransID,
                                BranchID=BranchID,
                                VoucherType=VoucherType,
                                StockRateID=StockRateID,
                                DetailID=PurchaseReturnDetailsID,
                                MasterID=PurchaseReturnMasterID,
                                Qty=Qty,
                                IsActive=IsActive,
                                CompanyID=CompanyID,
                                )

                    elif float(stockRate_instance.Qty) == float(Qty):
                        stockRate_instance.Qty = 0
                        changQty = 0
                        stockRate_instance.save()

                        if StockPosting.objects.filter(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                            VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit).exists():
                            stockPost_instance = StockPosting.objects.get(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                                VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit)
                            QtyOut = stockPost_instance.QtyOut
                            newQty = QtyOut + stockRate_instance.Qty
                            stockPost_instance.save()
                        else:
                            StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=PurchaseReturnMasterID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseID,
                                QtyOut=stockRate_instance.Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                                )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=PurchaseReturnMasterID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseID,
                                QtyOut=stockRate_instance.Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                                )

                        if StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).exists():
                            stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).first()
                            stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                            stockTra_in.save()
                        else:
                            StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                            StockTrans.objects.create(
                                StockTransID=StockTransID,
                                BranchID=BranchID,
                                VoucherType=VoucherType,
                                StockRateID=StockRateID,
                                DetailID=PurchaseReturnDetailsID,
                                MasterID=PurchaseReturnMasterID,
                                Qty=Qty,
                                IsActive=IsActive,
                                CompanyID=CompanyID,
                                )

            if StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,Cost=Cost,WareHouseID=WarehouseID,Qty__lte=0).exists():
                stockRate_instance = StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,Cost=Cost,WareHouseID=WarehouseID,Qty__lte=0).first()
                if float(changQty) > 0:
                    stockRate_instance.Qty = float(stockRate_instance.Qty) - float(changQty)
                    stockRate_instance.save()

                    if StockPosting.objects.filter(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                        VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit).exists():
                        stockPost_instance = StockPosting.objects.get(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                            VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit)
                        QtyOut = stockPost_instance.QtyOut
                        newQty = float(QtyOut) + float(changQty)
                        stockPost_instance.save()
                    else:
                        StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            BatchID=BatchID,
                            WareHouseID=WarehouseID,
                            QtyOut=changQty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=IsActive,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            )

                        StockPosting_Log.objects.create(
                            TransactionID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            BatchID=BatchID,
                            WareHouseID=WarehouseID,
                            QtyOut=changQty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=IsActive,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            )

                    if StockTrans.objects.filter(CompanyID=CompanyID,StockRateID=stockRate_instance.StockRateID,
                                                    DetailID=PurchaseReturnDetailsID,
                                                    MasterID=PurchaseReturnMasterID,
                                                    VoucherType=VoucherType,
                                                    BranchID=BranchID).exists():

                        stockTrance_instance = StockTrans.objects.get(CompanyID=CompanyID,StockRateID=stockRate_instance.StockRateID,
                                                    DetailID=PurchaseReturnDetailsID,
                                                    MasterID=PurchaseReturnMasterID,
                                                    VoucherType=VoucherType,
                                                    BranchID=BranchID)

                        stockTrance_instance.Qty = changQty
                        stockTrance_instance.save()

                    else:
                        StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                        StockTrans.objects.create(
                            StockTransID=StockTransID,
                            BranchID=BranchID,
                            VoucherType=VoucherType,
                            StockRateID=stockRate_instance.StockRateID,
                            DetailID=PurchaseReturnDetailsID,
                            MasterID=PurchaseReturnMasterID,
                            Qty=Qty,
                            IsActive=IsActive,
                            CompanyID=CompanyID,
                            )
            else:
                if float(changQty) > 0:
                    qty = float(Qty) * -1
                    StockRateID = get_auto_StockRateID(StockRate,BranchID,CompanyID)
                    StockRate.objects.create(
                        StockRateID=StockRateID,
                        BranchID=BranchID,
                        BatchID=BatchID,
                        PurchasePrice=PurchasePrice,
                        SalesPrice=SalesPrice,
                        Qty=qty,
                        Cost=Cost,
                        ProductID=ProductID,
                        WareHouseID=WarehouseID,
                        Date=VoucherDate,
                        PriceListID=PriceListID_DefUnit,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                        )

                    StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
                        WareHouseID=WarehouseID,
                        QtyOut=qty,
                        Rate=Cost,
                        PriceListID=PriceListID_DefUnit,
                        IsActive=IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                        )

                    StockPosting_Log.objects.create(
                        TransactionID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
                        WareHouseID=WarehouseID,
                        QtyOut=qty,
                        Rate=Cost,
                        PriceListID=PriceListID_DefUnit,
                        IsActive=IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                        )

                    StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                    StockTrans.objects.create(
                        StockTransID=StockTransID,
                        BranchID=BranchID,
                        VoucherType=VoucherType,
                        StockRateID=StockRateID,
                        DetailID=PurchaseReturnDetailsID,
                        MasterID=PurchaseReturnMasterID,
                        Qty=Qty,
                        IsActive=IsActive,
                        CompanyID=CompanyID,
                        )


            if PurchaseMaster.objects.filter(CompanyID=CompanyID,VoucherNo=RefferenceBillNo,BranchID=BranchID).exists():
                
                PurchaseMaster_instance = PurchaseMaster.objects.get(CompanyID=CompanyID,VoucherNo=RefferenceBillNo,BranchID=BranchID)
                PurchaseMasterID = PurchaseMaster_instance.PurchaseMasterID

                if PurchaseDetails.objects.filter(CompanyID=CompanyID,PurchaseMasterID=PurchaseMasterID,BranchID=BranchID,ProductID=ProductID).exists():
                    PurchaseDetails_instances = PurchaseDetails.objects.filter(CompanyID=CompanyID,PurchaseMasterID=PurchaseMasterID,BranchID=BranchID,ProductID=ProductID)

                    for i in PurchaseDetails_instances:
                        ReturnQty = i.ReturnQty
                        PurchaseReturnQty = PurchaseReturnQty
                        ReturnQty = float(ReturnQty) - float(PurchaseReturnQty)
                        i.ReturnQty = ReturnQty

                        i.save()


        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturns', 'Create', 'Purchase Returns created Successfully.', 'Purchase Returns created Successfully.')
        response_data = {
            "StatusCode" : 6000,
            "message" : "Purchase Return created Successfully!!!",
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseReturns', 'Create', 'Purchase Returns created Failed.', 'VoucherNo already exist!')
        
        response_data = {
        "StatusCode" : 6001,
        "message" : "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_purchaseReturn(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()

    purchaseReturnMaster_instance = None
    purchaseReturnDetails = None

    purchaseReturnMaster_instance = PurchaseReturnMaster.objects.get(CompanyID=CompanyID,pk=pk)

    PurchaseReturnMasterID = purchaseReturnMaster_instance.PurchaseReturnMasterID
    BranchID = purchaseReturnMaster_instance.BranchID
    VoucherNo = purchaseReturnMaster_instance.VoucherNo

    Action = "M"

    if LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR").exists():

        ledgerPostInstances = LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR")
        
        for ledgerPostInstance in ledgerPostInstances:
            
            ledgerPostInstance.delete()

    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR").exists():
        stockPostingInstances = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR")
        for stockPostingInstance in stockPostingInstances:
            stockPostingInstance.delete()
    
    VoucherDate = data['VoucherDate']
    RefferenceBillNo = data['RefferenceBillNo']
    RefferenceBillDate = data['RefferenceBillDate']
    VenderInvoiceDate = data['VenderInvoiceDate']
    CreditPeriod = data['CreditPeriod']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    PurchaseAccount = data['PurchaseAccount']
    DeliveryMasterID = data['DeliveryMasterID']
    OrderMasterID = data['OrderMasterID']
    CustomerName = data['CustomerName']
    Address1 = data['Address1']
    Address2 = data['Address2']
    Address3 = data['Address3']
    Notes = data['Notes']
    FinacialYearID = data['FinacialYearID']
    WarehouseID = data['WarehouseID']
    IsActive = data['IsActive']
    BatchID = data['BatchID']
    TaxID = data['TaxID']
    TaxType = data['TaxType']


    TotalTax = float(data['TotalTax'])
    NetTotal = float(data['NetTotal'])
    AdditionalCost = float(data['AdditionalCost'])
    GrandTotal = float(data['GrandTotal'])
    RoundOff = float(data['RoundOff'])
    TotalGrossAmt = float(data['TotalGrossAmt'])
    VATAmount = float(data['VATAmount'])
    SGSTAmount = float(data['SGSTAmount'])
    CGSTAmount = float(data['CGSTAmount'])
    IGSTAmount = float(data['IGSTAmount'])
    TAX1Amount = float(data['TAX1Amount'])
    TAX2Amount = float(data['TAX2Amount'])
    TAX3Amount = float(data['TAX3Amount'])
    AddlDiscPercent = float(data['AddlDiscPercent'])
    AddlDiscAmt = float(data['AddlDiscAmt'])
    TotalDiscount = float(data['TotalDiscount'])
    BillDiscPercent = float(data['BillDiscPercent'])
    BillDiscAmt = float(data['BillDiscAmt'])

    TotalTax = round(TotalTax,PriceRounding)
    NetTotal = round(NetTotal,PriceRounding)
    AdditionalCost = round(AdditionalCost,PriceRounding)
    GrandTotal = round(GrandTotal,PriceRounding)
    RoundOff = round(RoundOff,PriceRounding)

    TotalGrossAmt = round(TotalGrossAmt,PriceRounding)
    VATAmount = round(VATAmount,PriceRounding)
    SGSTAmount = round(SGSTAmount,PriceRounding)
    CGSTAmount = round(CGSTAmount,PriceRounding)
    IGSTAmount = round(IGSTAmount,PriceRounding)

    TAX1Amount = round(TAX1Amount,PriceRounding)
    TAX2Amount = round(TAX2Amount,PriceRounding)
    TAX3Amount = round(TAX3Amount,PriceRounding)
    AddlDiscPercent = round(AddlDiscPercent,PriceRounding)
    AddlDiscAmt = round(AddlDiscAmt,PriceRounding)

    TotalDiscount = round(TotalDiscount,PriceRounding)
    BillDiscPercent = round(BillDiscPercent,PriceRounding)
    BillDiscAmt = round(BillDiscAmt,PriceRounding)


    purchaseReturnMaster_instance.VoucherDate = VoucherDate
    purchaseReturnMaster_instance.RefferenceBillNo = RefferenceBillNo
    purchaseReturnMaster_instance.RefferenceBillDate = RefferenceBillDate
    purchaseReturnMaster_instance.VenderInvoiceDate = VenderInvoiceDate
    purchaseReturnMaster_instance.CreditPeriod = CreditPeriod
    purchaseReturnMaster_instance.LedgerID = LedgerID
    purchaseReturnMaster_instance.PriceCategoryID = PriceCategoryID
    purchaseReturnMaster_instance.EmployeeID = EmployeeID
    purchaseReturnMaster_instance.PurchaseAccount = PurchaseAccount
    purchaseReturnMaster_instance.DeliveryMasterID = DeliveryMasterID
    purchaseReturnMaster_instance.OrderMasterID = OrderMasterID
    purchaseReturnMaster_instance.CustomerName = CustomerName
    purchaseReturnMaster_instance.Address1 = Address1
    purchaseReturnMaster_instance.Address2 = Address2
    purchaseReturnMaster_instance.Address3 = Address3
    purchaseReturnMaster_instance.Notes = Notes
    purchaseReturnMaster_instance.FinacialYearID = FinacialYearID
    purchaseReturnMaster_instance.TotalTax = TotalTax
    purchaseReturnMaster_instance.NetTotal = NetTotal
    purchaseReturnMaster_instance.AdditionalCost = AdditionalCost
    purchaseReturnMaster_instance.GrandTotal = GrandTotal
    purchaseReturnMaster_instance.RoundOff = RoundOff
    purchaseReturnMaster_instance.WarehouseID = WarehouseID
    purchaseReturnMaster_instance.IsActive = IsActive
    purchaseReturnMaster_instance.TotalGrossAmt = TotalGrossAmt
    purchaseReturnMaster_instance.Action = Action
    purchaseReturnMaster_instance.CreatedUserID = CreatedUserID
    purchaseReturnMaster_instance.UpdatedDate = today
    purchaseReturnMaster_instance.TaxID = TaxID
    purchaseReturnMaster_instance.TaxType = TaxType
    purchaseReturnMaster_instance.VATAmount = VATAmount
    purchaseReturnMaster_instance.SGSTAmount = SGSTAmount
    purchaseReturnMaster_instance.CGSTAmount = CGSTAmount
    purchaseReturnMaster_instance.IGSTAmount = IGSTAmount
    purchaseReturnMaster_instance.TAX1Amount = TAX1Amount
    purchaseReturnMaster_instance.TAX2Amount = TAX2Amount
    purchaseReturnMaster_instance.TAX3Amount = TAX3Amount
    purchaseReturnMaster_instance.AddlDiscPercent = AddlDiscPercent
    purchaseReturnMaster_instance.AddlDiscAmt = AddlDiscAmt
    purchaseReturnMaster_instance.TotalDiscount = TotalDiscount
    purchaseReturnMaster_instance.BillDiscPercent = BillDiscPercent
    purchaseReturnMaster_instance.BillDiscAmt = BillDiscAmt
    purchaseReturnMaster_instance.save()


    PurchaseReturnMaster_Log.objects.create(
        TransactionID=PurchaseReturnMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        VoucherDate=VoucherDate,
        RefferenceBillNo=RefferenceBillNo,
        RefferenceBillDate=RefferenceBillDate,
        VenderInvoiceDate=VenderInvoiceDate,
        CreditPeriod=CreditPeriod,
        LedgerID=LedgerID,
        PriceCategoryID=PriceCategoryID,
        EmployeeID=EmployeeID,
        PurchaseAccount=PurchaseAccount,
        DeliveryMasterID=DeliveryMasterID,
        OrderMasterID=OrderMasterID,
        CustomerName=CustomerName,
        Address1=Address1,
        Address2=Address2,
        Address3=Address3,
        Notes=Notes,
        FinacialYearID=FinacialYearID,
        TotalGrossAmt=TotalGrossAmt,
        TotalTax=TotalTax,
        NetTotal=NetTotal,
        AdditionalCost=AdditionalCost,
        GrandTotal=GrandTotal,
        RoundOff=RoundOff,
        WarehouseID=WarehouseID,
        IsActive=IsActive,
        CreatedUserID=CreatedUserID,
        Action=Action,
        CreatedDate=today,
        UpdatedDate=today,
        TaxID=TaxID,
        TaxType=TaxType,
        VATAmount=VATAmount,
        SGSTAmount=SGSTAmount,
        CGSTAmount=CGSTAmount,
        IGSTAmount=IGSTAmount,
        TAX1Amount=TAX1Amount,
        TAX2Amount=TAX2Amount,
        TAX3Amount=TAX3Amount,
        AddlDiscPercent=AddlDiscPercent,
        AddlDiscAmt=AddlDiscAmt,
        TotalDiscount=TotalDiscount,
        BillDiscPercent=BillDiscPercent,
        BillDiscAmt=BillDiscAmt,
        CompanyID=CompanyID,
        )

    VoucherType = "PR"

    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

    LedgerPosting.objects.create(
        LedgerPostingID=LedgerPostingID,
        BranchID=BranchID,
        Date=VoucherDate,
        VoucherMasterID=PurchaseReturnMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=PurchaseAccount,
        Credit=TotalGrossAmt,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        CompanyID=CompanyID,
        )

    LedgerPosting_Log.objects.create(
        TransactionID=LedgerPostingID,
        BranchID=BranchID,
        Date=VoucherDate,
        VoucherMasterID=PurchaseReturnMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=PurchaseAccount,
        Credit=TotalGrossAmt,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        CompanyID=CompanyID,
        )

    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

    LedgerPosting.objects.create(
        LedgerPostingID=LedgerPostingID,
        BranchID=BranchID,
        Date=VoucherDate,
        VoucherMasterID=PurchaseReturnMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=LedgerID,
        Debit=GrandTotal,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        CompanyID=CompanyID,
        )

    LedgerPosting_Log.objects.create(
        TransactionID=LedgerPostingID,
        BranchID=BranchID,
        Date=VoucherDate,
        VoucherMasterID=PurchaseReturnMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=LedgerID,
        Debit=GrandTotal,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        CompanyID=CompanyID,
        )

    if float(TotalTax) > 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        LedgerID = "55"

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=TotalTax,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

        LedgerPosting_Log.objects.create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=TotalTax,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

    if float(BillDiscAmt) > 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        LedgerID = "74"

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=BillDiscAmt,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

        LedgerPosting_Log.objects.create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=BillDiscAmt,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

    if float(RoundOff) > 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        LedgerID = "78"

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=RoundOff,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

        LedgerPosting_Log.objects.create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=RoundOff,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

    if float(RoundOff) < 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        RoundOff = abs(float(RoundOff))

        LedgerID = "78"

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=RoundOff,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

        LedgerPosting_Log.objects.create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=PurchaseReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=RoundOff,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )


    # deleted_datas = data["deleted_data"]
    # if deleted_datas:
    #     for deleted_Data in deleted_datas:
    #         PurchaseReturnDetailsID = deleted_Data['PurchaseReturnDetailsID']
    #         pk = deleted_Data['unq_id']
            
    #         if not pk == '':
    #             if PurchaseReturnDetails.objects.filter(CompanyID=CompanyID,pk=pk).exists():
    #                 deleted_detail = PurchaseReturnDetails.objects.filter(CompanyID=CompanyID,pk=pk)
    #                 deleted_detail.delete()

    #             stockTrans_instance = None
    #             if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
    #                 stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True)
    #                 qty_in_stockTrans = stockTrans_instance.Qty
    #                 StockRateID = stockTrans_instance.StockRateID
    #                 stockTrans_instance.IsActive = False
    #                 stockTrans_instance.save()

    #                 stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseID)
    #                 stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
    #                 stockRate_instance.save()


    deleted_datas = data["deleted_data"]
    if deleted_datas:
        for deleted_Data in deleted_datas:
            deleted_pk = deleted_Data['unq_id']
            PurchaseReturnDetailsID_Deleted = deleted_Data['PurchaseReturnDetailsID']
            ProductID_Deleted = deleted_Data['ProductID']
            PriceListID_Deleted = deleted_Data['PriceListID']
            Rate_Deleted = deleted_Data['Rate']
            PurchaseReturnMasterID_Deleted = deleted_Data['PurchaseReturnMasterID']
            WarehouseID_Deleted = deleted_Data['WarehouseID']

            if PriceList.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,DefaultUnit=True).exists():
                priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,DefaultUnit=True)
                MultiFactor = priceList.MultiFactor
                Cost = float(Rate_Deleted) /  float(MultiFactor)
                Ct = round(Cost,4)
                Cost_Deleted = str(Ct)

                if not deleted_pk == '' or not deleted_pk == 0:
                    if PurchaseReturnDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk).exists():
                        deleted_detail = PurchaseReturnDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk)
                        deleted_detail.delete()

                        # if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID).exists():
                        #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID)
                        #     StockRateID = stockRate_instance.StockRateID
                        #     if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID_Deleted,MasterID=PurchaseReturnMasterID_Deleted,BranchID=BranchID,
                        #         VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID).exists():
                        #         stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID_Deleted,MasterID=PurchaseReturnMasterID_Deleted,BranchID=BranchID,
                        #             VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)
                        #         qty_in_stockTrans = stockTrans_instance.Qty
                        #         stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
                        #         stockRate_instance.save()
                        #         stockTrans_instance.IsActive = False
                        #         stockTrans_instance.save()

                        if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID_Deleted,MasterID=PurchaseReturnMasterID_Deleted,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
                            stockTrans_instance = StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID_Deleted,MasterID=PurchaseReturnMasterID_Deleted,BranchID=BranchID,VoucherType=VoucherType,IsActive=True)
                            for stck in stockTrans_instance:
                                StockRateID = stck.StockRateID
                                stck.IsActive = False
                                qty_in_stockTrans = stck.Qty
                                if StockRate.objects.filter(CompanyID=CompanyID,StockRateID=StockRateID,BranchID=BranchID).exists():
                                    stockRateInstance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=StockRateID,BranchID=BranchID)
                                    stockRateInstance.Qty = float(stockRateInstance.Qty) + float(qty_in_stockTrans)
                                    stockRateInstance.save()
                                stck.save()


    purchaseReturnDetails = data["PurchaseReturnDetails"]

    for purchaseReturnDetail in purchaseReturnDetails:

        # PurchaseReturnMasterID = serialized.data['PurchaseReturnMasterID']
        pk = purchaseReturnDetail['unq_id']
        detailID = purchaseReturnDetail['detailID']
        DeliveryDetailsID = purchaseReturnDetail['DeliveryDetailsID']
        OrderDetailsID = purchaseReturnDetail['OrderDetailsID']
        ProductID = purchaseReturnDetail['ProductID']
        Qty_detail = purchaseReturnDetail['Qty']
        PriceListID = purchaseReturnDetail['PriceListID']
        FreeQty = purchaseReturnDetail['FreeQty']

        
        # UnitPrice = purchaseReturnDetail['UnitPrice']
        # InclusivePrice = purchaseReturnDetail['InclusivePrice']
        # RateWithTax = purchaseReturnDetail['RateWithTax']
        # CostPerPrice = purchaseReturnDetail['CostPerPrice']
        # DiscountPerc = purchaseReturnDetail['DiscountPerc']
        # DiscountAmount = purchaseReturnDetail['DiscountAmount']
        # GrossAmount = purchaseReturnDetail['GrossAmount']
        # TaxableAmount = purchaseReturnDetail['TaxableAmount']
        # VATPerc = purchaseReturnDetail['VATPerc']
        # VATAmount = purchaseReturnDetail['VATAmount']
        # SGSTPerc = purchaseReturnDetail['SGSTPerc']
        # SGSTAmount = purchaseReturnDetail['SGSTAmount']
        # CGSTPerc = purchaseReturnDetail['CGSTPerc']
        # CGSTAmount = purchaseReturnDetail['CGSTAmount']
        # IGSTPerc = purchaseReturnDetail['IGSTPerc']
        # IGSTAmount = purchaseReturnDetail['IGSTAmount']
        # NetAmount = purchaseReturnDetail['NetAmount']

        # AddlDiscPerc = purchaseReturnDetail['AddlDiscPerc']
        # AddlDiscAmt = purchaseReturnDetail['AddlDiscAmt']
        # TAX1Perc = purchaseReturnDetail['TAX1Perc']
        # TAX1Amount = purchaseReturnDetail['TAX1Amount']
        # TAX2Perc = purchaseReturnDetail['TAX2Perc']
        # TAX2Amount = purchaseReturnDetail['TAX2Amount']
        # TAX3Perc = purchaseReturnDetail['TAX3Perc']
        # TAX3Amount = purchaseReturnDetail['TAX3Amount']

        DiscountPerc = float(purchaseReturnDetail['DiscountPerc'])
        DiscountAmount = float(purchaseReturnDetail['DiscountAmount'])
        GrossAmount = float(purchaseReturnDetail['GrossAmount'])
        TaxableAmount = float(purchaseReturnDetail['TaxableAmount'])
        VATPerc = float(purchaseReturnDetail['VATPerc'])
        VATAmount = float(purchaseReturnDetail['VATAmount'])
        SGSTPerc = float(purchaseReturnDetail['SGSTPerc'])
        SGSTAmount = float(purchaseReturnDetail['SGSTAmount'])
        CGSTPerc = float(purchaseReturnDetail['CGSTPerc'])
        CGSTAmount = float(purchaseReturnDetail['CGSTAmount'])
        IGSTPerc = float(purchaseReturnDetail['IGSTPerc'])
        IGSTAmount = float(purchaseReturnDetail['IGSTAmount'])
        NetAmount = float(purchaseReturnDetail['NetAmount'])
        RateWithTax = float(purchaseReturnDetail['RateWithTax'])
        CostPerPrice = float(purchaseReturnDetail['CostPerPrice'])
        
        UnitPrice = float(purchaseReturnDetail['UnitPrice'])
        InclusivePrice = float(purchaseReturnDetail['InclusivePrice'])
        AddlDiscPerc = float(purchaseReturnDetail['AddlDiscPerc'])
        AddlDiscAmt = float(purchaseReturnDetail['AddlDiscAmt'])
        TAX1Perc = float(purchaseReturnDetail['TAX1Perc'])
        TAX1Amount = float(purchaseReturnDetail['TAX1Amount'])
        TAX2Perc = float(purchaseReturnDetail['TAX2Perc'])
        TAX2Amount = float(purchaseReturnDetail['TAX2Amount'])
        TAX3Perc = float(purchaseReturnDetail['TAX3Perc'])
        TAX3Amount = float(purchaseReturnDetail['TAX3Amount'])
    
        DiscountPerc = round(DiscountPerc,PriceRounding)
        DiscountAmount = round(DiscountAmount,PriceRounding)
        GrossAmount = round(GrossAmount,PriceRounding)
        TaxableAmount = round(TaxableAmount,PriceRounding)
        VATPerc = round(VATPerc,PriceRounding)

        VATAmount = round(VATAmount,PriceRounding)
        SGSTPerc = round(SGSTPerc,PriceRounding)
        SGSTAmount = round(SGSTAmount,PriceRounding)
        CGSTPerc = round(CGSTPerc,PriceRounding)
        CGSTAmount = round(CGSTAmount,PriceRounding)

        IGSTPerc = round(IGSTPerc,PriceRounding)
        IGSTAmount = round(IGSTAmount,PriceRounding)
        NetAmount = round(NetAmount,PriceRounding)
        RateWithTax = round(RateWithTax,PriceRounding)
        CostPerPrice = round(CostPerPrice,PriceRounding)

        UnitPrice = round(UnitPrice,PriceRounding)
        InclusivePrice = round(InclusivePrice,PriceRounding)
        AddlDiscPerc = round(AddlDiscPerc,PriceRounding)
        AddlDiscAmt = round(AddlDiscAmt,PriceRounding)
        TAX1Perc = round(TAX1Perc,PriceRounding)

        TAX1Amount = round(TAX1Amount,PriceRounding)
        TAX2Perc = round(TAX2Perc,PriceRounding)
        TAX2Amount = round(TAX2Amount,PriceRounding)
        TAX3Perc = round(TAX3Perc,PriceRounding)
        TAX3Amount = round(TAX3Amount,PriceRounding)


        # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True)

        # PriceListID_DefUnit = priceList.PriceListID
        # MultiFactor = priceList.MultiFactor

        MultiFactor = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).MultiFactor
        PriceListID_DefUnit = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID).PriceListID

        # PurchasePrice = priceList.PurchasePrice
        # SalesPrice = priceList.SalesPrice

        qty = float(FreeQty) + float(Qty_detail)

        Qty = float(MultiFactor) * float(qty)
        Cost = float(CostPerPrice) /  float(MultiFactor)

        Qy = round(Qty,4)
        Qty = str(Qy)


        Ct = round(Cost,4)
        Cost = str(Ct)



        princeList_instance = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,BranchID=BranchID)
        PurchasePrice = princeList_instance.PurchasePrice
        SalesPrice = princeList_instance.SalesPrice


        PurchaseReturnDetailsID = get_auto_id(PurchaseReturnDetails,BranchID,CompanyID)
        StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)

        if detailID == 0:
            purchaseReturnDetail_instance = PurchaseReturnDetails.objects.get(CompanyID=CompanyID,pk=pk)
            PurchaseReturnDetailsID = purchaseReturnDetail_instance.PurchaseReturnDetailsID
            purchaseReturnDetail_instance.DeliveryDetailsID = DeliveryDetailsID
            purchaseReturnDetail_instance.OrderDetailsID = OrderDetailsID
            purchaseReturnDetail_instance.ProductID = ProductID
            purchaseReturnDetail_instance.Qty = Qty_detail
            purchaseReturnDetail_instance.FreeQty = FreeQty
            purchaseReturnDetail_instance.UnitPrice = UnitPrice
            purchaseReturnDetail_instance.InclusivePrice = InclusivePrice
            purchaseReturnDetail_instance.RateWithTax = RateWithTax
            purchaseReturnDetail_instance.CostPerPrice = CostPerPrice
            purchaseReturnDetail_instance.PriceListID = PriceListID
            purchaseReturnDetail_instance.DiscountPerc = DiscountPerc
            purchaseReturnDetail_instance.DiscountAmount = DiscountAmount
            purchaseReturnDetail_instance.GrossAmount = GrossAmount
            purchaseReturnDetail_instance.TaxableAmount = TaxableAmount
            purchaseReturnDetail_instance.VATPerc = VATPerc
            purchaseReturnDetail_instance.VATAmount = VATAmount
            purchaseReturnDetail_instance.SGSTPerc = SGSTPerc
            purchaseReturnDetail_instance.SGSTAmount = SGSTAmount
            purchaseReturnDetail_instance.CGSTPerc = CGSTPerc
            purchaseReturnDetail_instance.CGSTAmount = CGSTAmount
            purchaseReturnDetail_instance.IGSTPerc = IGSTPerc
            purchaseReturnDetail_instance.IGSTAmount = IGSTAmount
            purchaseReturnDetail_instance.NetAmount = NetAmount
            purchaseReturnDetail_instance.Action = Action
            purchaseReturnDetail_instance.UpdatedDate = today
            purchaseReturnDetail_instance.CreatedUserID = CreatedUserID
            purchaseReturnDetail_instance.AddlDiscPerc = AddlDiscPerc
            purchaseReturnDetail_instance.AddlDiscAmt = AddlDiscAmt
            purchaseReturnDetail_instance.TAX1Perc = TAX1Perc
            purchaseReturnDetail_instance.TAX1Amount = TAX1Amount
            purchaseReturnDetail_instance.TAX2Perc = TAX2Perc
            purchaseReturnDetail_instance.TAX2Amount = TAX2Amount
            purchaseReturnDetail_instance.TAX3Perc = TAX3Perc
            purchaseReturnDetail_instance.TAX3Amount = TAX3Amount

            purchaseReturnDetail_instance.save()

            PurchaseReturnDetails_Log.objects.create(
                TransactionID=PurchaseReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                PurchaseReturnMasterID=PurchaseReturnMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
                ProductID=ProductID,
                Qty=Qty_detail,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                InclusivePrice=InclusivePrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                DiscountPerc=DiscountPerc,
                DiscountAmount=DiscountAmount,
                GrossAmount=GrossAmount,
                TaxableAmount=TaxableAmount,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                AddlDiscPerc=AddlDiscPerc,
                AddlDiscAmt=AddlDiscAmt,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                )

            StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=WarehouseID,
                QtyOut=Qty,
                Rate=Cost,
                PriceListID=PriceListID_DefUnit,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                )

            StockPosting_Log.objects.create(
                TransactionID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=WarehouseID,
                QtyOut=Qty,
                Rate=Cost,
                PriceListID=PriceListID_DefUnit,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                )

        if detailID == 1:

            Action = "A"

            PurchaseReturnDetails.objects.create(
                PurchaseReturnDetailsID=PurchaseReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                PurchaseReturnMasterID=PurchaseReturnMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
                ProductID=ProductID,
                Qty=Qty_detail,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                InclusivePrice=InclusivePrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                DiscountPerc=DiscountPerc,
                DiscountAmount=DiscountAmount,
                GrossAmount=GrossAmount,
                TaxableAmount=TaxableAmount,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                AddlDiscPerc=AddlDiscPerc,
                AddlDiscAmt=AddlDiscAmt,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                )

            PurchaseReturnDetails_Log.objects.create(
                TransactionID=PurchaseReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                PurchaseReturnMasterID=PurchaseReturnMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
                ProductID=ProductID,
                Qty=Qty_detail,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                InclusivePrice=InclusivePrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                DiscountPerc=DiscountPerc,
                DiscountAmount=DiscountAmount,
                GrossAmount=GrossAmount,
                TaxableAmount=TaxableAmount,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                AddlDiscPerc=AddlDiscPerc,
                AddlDiscAmt=AddlDiscAmt,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                )

            StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=WarehouseID,
                QtyOut=Qty,
                Rate=Cost,
                PriceListID=PriceListID_DefUnit,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                )

            StockPosting_Log.objects.create(
                TransactionID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=WarehouseID,
                QtyOut=Qty,
                Rate=Cost,
                PriceListID=PriceListID_DefUnit,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                )


            if StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID).exists():
                stockRateInstance = StockRate.objects.get(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID)
                
                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(stockRateInstance.Qty) - float(Qty)
                stockRateInstance.save()

               

                if StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).exists():
                    stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).first()
                    stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                    stockTra_in.save()
                else:
                    StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                    StockTrans.objects.create(
                        StockTransID=StockTransID,
                        BranchID=BranchID,
                        VoucherType=VoucherType,
                        StockRateID=StockRateID,
                        DetailID=PurchaseReturnDetailsID,
                        MasterID=PurchaseReturnMasterID,
                        Qty=Qty,
                        IsActive=IsActive,
                        CompanyID=CompanyID,
                        )
            else:
                StockRateID = get_auto_StockRateID(StockRate,BranchID,CompanyID)
                StockRate.objects.create(
                    StockRateID=StockRateID,
                    BranchID=BranchID,
                    BatchID=BatchID,
                    PurchasePrice=PurchasePrice,
                    SalesPrice=SalesPrice,
                    Qty=Qty,
                    Cost=Cost,
                    ProductID=ProductID,
                    WareHouseID=WarehouseID,
                    Date=VoucherDate,
                    PriceListID=PriceListID_DefUnit,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )

                # StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
                # StockPosting.objects.create(
                #     StockPostingID=StockPostingID,
                #     BranchID=BranchID,
                #     Action=Action,
                #     Date=VoucherDate,
                #     VoucherMasterID=PurchaseReturnMasterID,
                #     VoucherType=VoucherType,
                #     ProductID=ProductID,
                #     BatchID=BatchID,
                #     WareHouseID=WarehouseID,
                #     QtyOut=qty,
                #     Rate=Cost,
                #     PriceListID=PriceListID_DefUnit,
                #     IsActive=IsActive,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                #     )

                # StockPosting_Log.objects.create(
                #     TransactionID=StockPostingID,
                #     BranchID=BranchID,
                #     Action=Action,
                #     Date=VoucherDate,
                #     VoucherMasterID=PurchaseReturnMasterID,
                #     VoucherType=VoucherType,
                #     ProductID=ProductID,
                #     BatchID=BatchID,
                #     WareHouseID=WarehouseID,
                #     QtyOut=qty,
                #     Rate=Cost,
                #     PriceListID=PriceListID_DefUnit,
                #     IsActive=IsActive,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                #     )

                StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                StockTrans.objects.create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    DetailID=PurchaseReturnDetailsID,
                    MasterID=PurchaseReturnMasterID,
                    Qty=Qty,
                    IsActive=IsActive,
                    CompanyID=CompanyID,
                    )
        else:
            if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,Cost=Cost,WareHouseID=WarehouseID).exists():
                stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,Cost=Cost,WareHouseID=WarehouseID)
                StockRateID = stockRate_instance.StockRateID
                if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,
                        VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID).exists():
                    stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,
                        VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)

                    if float(stockTrans_instance.Qty) < float(Qty):
                        deff = float(Qty) - float(stockTrans_instance.Qty)
                        stockTrans_instance.Qty = float(stockTrans_instance.Qty) + float(deff)
                        stockTrans_instance.save()

                        stockRate_instance.Qty = float(stockRate_instance.Qty) - float(deff)
                        stockRate_instance.save()

                        # if StockPosting.objects.filter(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                        #     VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit).exists():
                        #     stockPost_instance = StockPosting.objects.get(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                        #         VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit)
                        #     QtyOut = stockPost_instance.QtyOut
                        #     newQty = float(QtyOut) + float(deff)
                        #     stockPost_instance.save()
                        # else:
                        #     StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
                        #     StockPosting.objects.create(
                        #         StockPostingID=StockPostingID,
                        #         BranchID=BranchID,
                        #         Action=Action,
                        #         Date=VoucherDate,
                        #         VoucherMasterID=PurchaseReturnMasterID,
                        #         VoucherType=VoucherType,
                        #         ProductID=ProductID,
                        #         BatchID=BatchID,
                        #         WareHouseID=WarehouseID,
                        #         QtyOut=deff,
                        #         Rate=Cost,
                        #         PriceListID=PriceListID_DefUnit,
                        #         IsActive=IsActive,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         CreatedUserID=CreatedUserID,
                        #         CompanyID=CompanyID,
                        #         )

                        #     StockPosting_Log.objects.create(
                        #         TransactionID=StockPostingID,
                        #         BranchID=BranchID,
                        #         Action=Action,
                        #         Date=VoucherDate,
                        #         VoucherMasterID=PurchaseReturnMasterID,
                        #         VoucherType=VoucherType,
                        #         ProductID=ProductID,
                        #         BatchID=BatchID,
                        #         WareHouseID=WarehouseID,
                        #         QtyOut=deff,
                        #         Rate=Cost,
                        #         PriceListID=PriceListID_DefUnit,
                        #         IsActive=IsActive,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         CreatedUserID=CreatedUserID,
                        #         CompanyID=CompanyID,
                        #         )


                    elif float(stockTrans_instance.Qty) > float(Qty):
                        deff = float(stockTrans_instance.Qty) - float(Qty)
                        stockTrans_instance.Qty = float(stockTrans_instance.Qty) - float(deff)
                        stockTrans_instance.save()

                        stockRate_instance.Qty = float(stockRate_instance.Qty) + float(deff)
                        stockRate_instance.save()

                        # if StockPosting.objects.filter(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                        #     VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit).exists():
                        #     stockPost_instance = StockPosting.objects.get(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                        #         VoucherMasterID=PurchaseReturnMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit)
                        #     QtyOut = stockPost_instance.QtyOut
                        #     newQty = float(QtyOut) + float(deff)
                        #     stockPost_instance.save()
                        # else:
                        #     StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
                        #     StockPosting.objects.create(
                        #         StockPostingID=StockPostingID,
                        #         BranchID=BranchID,
                        #         Action=Action,
                        #         Date=VoucherDate,
                        #         VoucherMasterID=PurchaseReturnMasterID,
                        #         VoucherType=VoucherType,
                        #         ProductID=ProductID,
                        #         BatchID=BatchID,
                        #         WareHouseID=WarehouseID,
                        #         QtyOut=deff,
                        #         Rate=Cost,
                        #         PriceListID=PriceListID_DefUnit,
                        #         IsActive=IsActive,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         CreatedUserID=CreatedUserID,
                        #         CompanyID=CompanyID,
                        #         )

                        #     StockPosting_Log.objects.create(
                        #         TransactionID=StockPostingID,
                        #         BranchID=BranchID,
                        #         Action=Action,
                        #         Date=VoucherDate,
                        #         VoucherMasterID=PurchaseReturnMasterID,
                        #         VoucherType=VoucherType,
                        #         ProductID=ProductID,
                        #         BatchID=BatchID,
                        #         WareHouseID=WarehouseID,
                        #         QtyOut=deff,
                        #         Rate=Cost,
                        #         PriceListID=PriceListID_DefUnit,
                        #         IsActive=IsActive,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         CreatedUserID=CreatedUserID,
                        #         CompanyID=CompanyID,
                        #         )

            # if StockTrans.objects.filter(CompanyID=CompanyID,MasterID=PurchaseReturnMasterID,DetailID=PurchaseReturnDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
            #     stockTrans_instance = StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).first()
            #     stockRateID = stockTrans_instance.StockRateID
            #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID,WareHouseID=WarehouseID)
                
            #     if float(stockTrans_instance.Qty) < float(Qty):
            #         deff = float(Qty) - float(stockTrans_instance.Qty)
            #         stockTrans_instance.Qty = float(stockTrans_instance.Qty) + float(deff)
            #         stockTrans_instance.save()

            #         stockRate_instance.Qty = float(stockRate_instance.Qty) - float(deff)
            #         stockRate_instance.save()

            #     elif float(stockTrans_instance.Qty) > float(Qty):
            #         deff = float(stockTrans_instance.Qty) - float(Qty)
            #         stockTrans_instance.Qty = float(stockTrans_instance.Qty) - float(deff)
            #         stockTrans_instance.save() 

            #         stockRate_instance.Qty = float(stockRate_instance.Qty) + float(deff)
            #         stockRate_instance.save()

    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturns', 'Edit', 'Purchase Returns Updated Successfully.', 'Purchase Returns Updated Successfully')

    response_data = {
        "StatusCode" : 6000,
        "message" : "Purchase Return Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)
    


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_purchaseReturnMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
 
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        
        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():

            instances = PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

            serialized = PurchaseReturnMasterRestSerializer(instances,many=True,context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturns', 'List', 'Purchase Returns List Viewed Successfully.', 'Purchase Returns List Viewed Successfully.')
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseReturns', 'List', 'Purchase Returns List Viewed Failed.', 'Purchase Return not found under this branch.')
            
            response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Return Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch you enterd is not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def purchase_return_pagination(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    page_number = data['page_no']
    items_per_page = data['items_per_page']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']


        if page_number and items_per_page:
            purchase_return_object = PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

            purchase_return_sort_pagination = list_pagination(
                purchase_return_object,
                items_per_page,
                page_number
            )
            purchase_return_serializer = PurchaseReturnMasterRestSerializer(
                purchase_return_sort_pagination,
                many=True,
                context={"request":request,"CompanyID":CompanyID,"PriceRounding" : PriceRounding}
            )
            data = purchase_return_serializer.data
            if not data==None:
                response_data = {
                    "StatusCode" : 6000,
                    "data" : data,
                    "count": len(purchase_return_object)
                }
            else:
                response_data = {
                    "StatusCode" : 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def purchaseReturnMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = PurchaseReturnMaster.objects.get(CompanyID=CompanyID,pk=pk)
        serialized = PurchaseReturnMasterRestSerializer(instance,context = {"CompanyID": CompanyID,
        "PriceRounding" : PriceRounding })

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturns', 'View', 'Purchase Returns Single Viewed Successfully.', 'Purchase Returns Single Viewed Successfully.')
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseReturns', 'View', 'Purchase Returns Single Viewed Failed.', 'Purchase Return Not Found!')
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Return Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_purchaseReturnMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = PurchaseReturnMaster.objects.get(CompanyID=CompanyID,pk=pk)

        PurchaseReturnMasterID = instance.PurchaseReturnMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        VoucherDate = instance.VoucherDate
        RefferenceBillNo = instance.RefferenceBillNo
        RefferenceBillDate = instance.RefferenceBillDate
        VenderInvoiceDate = instance.VenderInvoiceDate
        CreditPeriod = instance.CreditPeriod
        LedgerID = instance.LedgerID
        PriceCategoryID = instance.PriceCategoryID
        EmployeeID = instance.EmployeeID
        PurchaseAccount = instance.PurchaseAccount
        DeliveryMasterID = instance.DeliveryMasterID
        OrderMasterID = instance.OrderMasterID
        CustomerName = instance.CustomerName
        Address1 = instance.Address1
        Address2 = instance.Address2
        Address3 = instance.Address3
        Notes = instance.Notes
        FinacialYearID = instance.FinacialYearID
        TotalGrossAmt = instance.TotalGrossAmt
        TotalTax = instance.TotalTax
        NetTotal = instance.NetTotal
        AdditionalCost = instance.AdditionalCost
        GrandTotal = instance.GrandTotal
        RoundOff = instance.RoundOff
        WarehouseID = instance.WarehouseID
        IsActive = instance.IsActive
        TaxID = instance.TaxID
        TaxType = instance.TaxType
        VATAmount = instance.VATAmount
        SGSTAmount = instance.SGSTAmount
        CGSTAmount = instance.CGSTAmount
        IGSTAmount = instance.IGSTAmount
        TAX1Amount = instance.TAX1Amount
        TAX2Amount = instance.TAX2Amount
        TAX3Amount = instance.TAX3Amount
        AddlDiscPercent = instance.AddlDiscPercent
        AddlDiscAmt = instance.AddlDiscAmt
        TotalDiscount = instance.TotalDiscount
        BillDiscPercent = instance.BillDiscPercent
        BillDiscAmt = instance.BillDiscAmt
        Action = "D"

        PurchaseReturnMaster_Log.objects.create(
            TransactionID=PurchaseReturnMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            VoucherDate=VoucherDate,
            RefferenceBillNo=RefferenceBillNo,
            RefferenceBillDate=RefferenceBillDate,
            VenderInvoiceDate=VenderInvoiceDate,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            PurchaseAccount=PurchaseAccount,
            DeliveryMasterID=DeliveryMasterID,
            OrderMasterID=OrderMasterID,
            CustomerName=CustomerName,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            Notes=Notes,
            FinacialYearID=FinacialYearID,
            TotalGrossAmt=TotalGrossAmt,
            TotalTax=TotalTax,
            NetTotal=NetTotal,
            AdditionalCost=AdditionalCost,
            GrandTotal=GrandTotal,
            RoundOff=RoundOff,
            WarehouseID=WarehouseID,
            IsActive=IsActive,
            CreatedUserID=CreatedUserID,
            Action=Action,
            CreatedDate=today,
            UpdatedDate=today,
            TaxID=TaxID,
            TaxType=TaxType,
            VATAmount=VATAmount,
            SGSTAmount=SGSTAmount,
            CGSTAmount=CGSTAmount,
            IGSTAmount=IGSTAmount,
            TAX1Amount=TAX1Amount,
            TAX2Amount=TAX2Amount,
            TAX3Amount=TAX3Amount,
            AddlDiscPercent=AddlDiscPercent,
            AddlDiscAmt=AddlDiscAmt,
            TotalDiscount=TotalDiscount,
            BillDiscPercent=BillDiscPercent,
            BillDiscAmt=BillDiscAmt,
            CompanyID=CompanyID,
            )

        instance.delete()

        if LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR").exists():

            ledgerPostInstances = LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR")
            
            for ledgerPostInstance in ledgerPostInstances:
                
                LedgerPostingID = ledgerPostInstance.LedgerPostingID
                VoucherType = ledgerPostInstance.VoucherType
                VoucherNo = ledgerPostInstance.VoucherNo
                Debit = ledgerPostInstance.Debit
                Credit = ledgerPostInstance.Credit
                IsActive = ledgerPostInstance.IsActive
                Date = ledgerPostInstance.Date
                LedgerID = ledgerPostInstance.LedgerID

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    Credit=Credit,
                    Debit=Debit,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )

                ledgerPostInstance.delete()

        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR").exists():

            stockPostingInstances = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR")
            
            for stockPostingInstance in stockPostingInstances:
                
                StockPostingID = stockPostingInstance.StockPostingID
                BranchID = stockPostingInstance.BranchID
                Date = stockPostingInstance.Date
                VoucherMasterID = stockPostingInstance.VoucherMasterID
                VoucherType = stockPostingInstance.VoucherType
                ProductID = stockPostingInstance.ProductID
                BatchID = stockPostingInstance.BatchID
                WareHouseID = stockPostingInstance.WareHouseID
                QtyIn = stockPostingInstance.QtyIn
                QtyOut = stockPostingInstance.QtyOut
                Rate = stockPostingInstance.Rate
                PriceListID = stockPostingInstance.PriceListID
                IsActive = stockPostingInstance.IsActive

                StockPosting_Log.objects.create(
                    TransactionID=StockPostingID,
                    BranchID=BranchID,
                    Action=Action,
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    ProductID=ProductID,
                    BatchID=BatchID,
                    WareHouseID=WareHouseID,
                    QtyIn=QtyIn,
                    QtyOut=QtyOut,
                    Rate=Rate,
                    PriceListID=PriceListID,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    )

                stockPostingInstance.delete()

        detail_instances = PurchaseReturnDetails.objects.filter(CompanyID=CompanyID,PurchaseReturnMasterID=PurchaseReturnMasterID)

        for detail_instance in detail_instances:

            PurchaseReturnDetailsID = detail_instance.PurchaseReturnDetailsID
            BranchID = detail_instance.BranchID
            PurchaseReturnMasterID = detail_instance.PurchaseReturnMasterID
            DeliveryDetailsID = detail_instance.DeliveryDetailsID
            OrderDetailsID = detail_instance.OrderDetailsID
            ProductID = detail_instance.ProductID
            Qty = detail_instance.Qty
            FreeQty = detail_instance.FreeQty
            UnitPrice = detail_instance.UnitPrice
            InclusivePrice = detail_instance.InclusivePrice
            RateWithTax = detail_instance.RateWithTax
            CostPerPrice = detail_instance.CostPerPrice
            PriceListID = detail_instance.PriceListID
            DiscountPerc = detail_instance.DiscountPerc
            DiscountAmount = detail_instance.DiscountAmount
            GrossAmount = detail_instance.GrossAmount
            TaxableAmount = detail_instance.TaxableAmount
            VATPerc = detail_instance.VATPerc
            VATAmount = detail_instance.VATAmount
            SGSTPerc = detail_instance.SGSTPerc
            SGSTAmount = detail_instance.SGSTAmount
            CGSTPerc = detail_instance.CGSTPerc
            CGSTAmount = detail_instance.CGSTAmount
            IGSTPerc = detail_instance.IGSTPerc
            IGSTAmount = detail_instance.IGSTAmount
            NetAmount = detail_instance.NetAmount
            
            AddlDiscPerc = detail_instance.AddlDiscPerc
            AddlDiscAmt = detail_instance.AddlDiscAmt
            TAX1Perc = detail_instance.TAX1Perc
            TAX1Amount = detail_instance.TAX1Amount
            TAX2Perc = detail_instance.TAX2Perc
            TAX2Amount = detail_instance.TAX2Amount
            TAX3Perc = detail_instance.TAX3Perc
            TAX3Amount = detail_instance.TAX3Amount

            PurchaseReturnDetails_Log.objects.create(
                TransactionID=PurchaseReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                PurchaseReturnMasterID=PurchaseReturnMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                InclusivePrice=InclusivePrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                DiscountPerc=DiscountPerc,
                DiscountAmount=DiscountAmount,
                GrossAmount=GrossAmount,
                TaxableAmount=TaxableAmount,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                AddlDiscPerc=AddlDiscPerc,
                AddlDiscAmt=AddlDiscAmt,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                )

            detail_instance.delete()

            if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR",IsActive = True).exists():
                stockTrans_instances = StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR",IsActive = True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
                    stockRate_instance.Qty = float(stockRate_instance.Qty) - float(i.Qty)
                    stockRate_instance.save()
            # if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR").exists():
            #     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR")

            #     stockRateID = stockTrans_instance.StockRateID
            #     stockTrans_instance.IsActive = False
            #     stockTrans_instance.save()

            #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
            #     stockRate_instance.Qty = stockTrans_instance.Qty
            #     stockRate_instance.save()

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturns', 'Delete', 'Purchase Returns Deleted Successfully.', 'Purchase Returns Deleted Successfully.')
        response_data = {
            "StatusCode" : 6000,
            "title" : "Success",
            "message" : "Purchase Return Master Deleted Successfully!"
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseReturns', 'Delete', 'Purchase Returns Deleted Failed.', 'Purchase Return Not Found.')
        response_data = {
            "StatusCode" : 6001,
            "title" : "Failed",
            "message" : "Purchase Return Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def report_purchaseReturns(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        ToDate = serialized1.data['ToDate']

        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherDate__lte=ToDate).exists():
            instances = PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherDate__lte=ToDate)

            serialized = PurchaseReturnMasterRestSerializer(instances,many=True,context = {"CompanyID": CompanyID })

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturnsReports', 'Report', 'Purchase Returns Reports viewed Successfully.', 'Purchase Returns Reports viewed Successfully.')
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseReturnsReports', 'Report', 'Purchase Returns Reports viewed Failed.', 'No datas under this date.')
            response_data = {
                "StatusCode" : 6001,
                "message" : "No data under this date!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
            
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)