from brands.models import SalesReturnMaster, SalesReturnMaster_Log, SalesReturnDetails, SalesReturnDetails_Log,\
StockPosting, LedgerPosting, StockPosting_Log, LedgerPosting_Log, Parties, SalesReturnDetailsDummy, PriceList,\
StockRate, StockTrans, SalesMaster, SalesDetails
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.salesReturns.serializers import SalesReturnMasterSerializer, SalesReturnMasterRestSerializer,\
SalesReturnDetailsSerializer, SalesReturnDetailsRestSerializer, SalesReturnMasterReportSerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.sales.serializers import ListSerializerforReport
from api.v1.salesReturns.functions import generate_serializer_errors
from rest_framework import status
from api.v1.salesReturns.functions import get_auto_id, get_auto_idMaster
from api.v1.sales.functions import get_auto_stockPostid
from api.v1.accountLedgers.functions import get_auto_LedgerPostid
from api.v1.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
import datetime
from main.functions import get_company, activity_log, list_pagination


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_salesReturn(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    

    today = datetime.datetime.now()
    BranchID = data['BranchID']
    VoucherDate = data['VoucherDate']
    VoucherNo = data['VoucherNo']
    RefferenceBillNo = data['RefferenceBillNo']
    RefferenceBillDate = data['RefferenceBillDate']
    CreditPeriod = data['CreditPeriod']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    SalesAccount = data['SalesAccount']
    DeliveryMasterID = data['DeliveryMasterID']
    OrderMasterID = data['OrderMasterID']
    CustomerName = data['CustomerName']
    Address1 = data['Address1']
    Address2 = data['Address2']
    Address3 = data['Address3']
    Notes = data['Notes']
    FinacialYearID = data['FinacialYearID']
    WarehouseID = data['WarehouseID']
    TableID = data['TableID']
    SeatNumber = data['SeatNumber']
    NoOfGuests = data['NoOfGuests']
    INOUT = data['INOUT']
    TokenNumber = data['TokenNumber']
    IsActive = data['IsActive']
    IsPosted = data['IsPosted']
    SalesType = data['SalesType']
    BatchID = data['BatchID']
    TaxID = data['TaxID']
    TaxType = data['TaxType']
    # CashAmount = data['CashAmount']

    TotalGrossAmt = float(data['TotalGrossAmt'])
    TotalTax = float(data['TotalTax'])
    NetTotal = float(data['NetTotal'])
    AdditionalCost = float(data['AdditionalCost'])
    GrandTotal = float(data['GrandTotal'])
    RoundOff = float(data['RoundOff'])
    CashReceived = float(data['CashReceived'])
    BankAmount = float(data['BankAmount'])
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

    TotalGrossAmt = round(TotalGrossAmt,PriceRounding)
    TotalTax = round(TotalTax,PriceRounding)
    NetTotal = round(NetTotal,PriceRounding)
    AdditionalCost = round(AdditionalCost,PriceRounding)
    GrandTotal = round(GrandTotal,PriceRounding)

    RoundOff = round(RoundOff,PriceRounding)
    CashReceived = round(CashReceived,PriceRounding)
    BankAmount = round(BankAmount,PriceRounding)
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
    insts = SalesReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    if not is_voucherExist:

        SalesReturnMasterID = get_auto_idMaster(SalesReturnMaster,BranchID,CompanyID)

        if Parties.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID).exists():
            
            party_instances = Parties.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID)

            for party_instance in party_instances:

                party_instance.PartyName = CustomerName

                party_instance.save()

        CashAmount = float(GrandTotal) - float(BankAmount)

        SalesReturnMaster.objects.create(
            SalesReturnMasterID=SalesReturnMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherDate=VoucherDate,
            RefferenceBillNo=RefferenceBillNo,
            RefferenceBillDate=RefferenceBillDate,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
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
            CashReceived=CashReceived,
            CashAmount=CashAmount,
            BankAmount=BankAmount,
            WarehouseID=WarehouseID,
            TableID=TableID,
            SeatNumber=SeatNumber,
            NoOfGuests=NoOfGuests,
            INOUT=INOUT,
            TokenNumber=TokenNumber,
            IsActive=IsActive,
            IsPosted=IsPosted,
            SalesType=SalesType,
            CreatedUserID=CreatedUserID,
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

        SalesReturnMaster_Log.objects.create(
            TransactionID=SalesReturnMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherDate=VoucherDate,
            RefferenceBillNo=RefferenceBillNo,
            RefferenceBillDate=RefferenceBillDate,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
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
            CashReceived=CashReceived,
            CashAmount=CashAmount,
            BankAmount=BankAmount,
            WarehouseID=WarehouseID,
            TableID=TableID,
            SeatNumber=SeatNumber,
            NoOfGuests=NoOfGuests,
            INOUT=INOUT,
            TokenNumber=TokenNumber,
            IsActive=IsActive,
            IsPosted=IsPosted,
            SalesType=SalesType,
            CreatedUserID=CreatedUserID,
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


        VoucherType = "SR"

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=SalesReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=SalesAccount,
            Debit=TotalGrossAmt,
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
            VoucherMasterID=SalesReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=SalesAccount,
            Debit=TotalGrossAmt,
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
            VoucherMasterID=SalesReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=GrandTotal,
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
            VoucherMasterID=SalesReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=GrandTotal,
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
                VoucherMasterID=SalesReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Debit=TotalTax,
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
                VoucherMasterID=SalesReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Debit=TotalTax,
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
                VoucherMasterID=SalesReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Credit=BillDiscAmt,
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
                VoucherMasterID=SalesReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Credit=BillDiscAmt,
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
                VoucherMasterID=SalesReturnMasterID,
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
                VoucherMasterID=SalesReturnMasterID,
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

        if float(RoundOff) < 0:

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

            RoundOff = abs(float(RoundOff))

            LedgerID = "78"

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=VoucherDate,
                VoucherMasterID=SalesReturnMasterID,
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
                VoucherMasterID=SalesReturnMasterID,
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

        salesReturnDetails = data["SalesReturnDetails"]

        for salesReturnDetail in salesReturnDetails:

            # SalesReturnMasterID = serialized.data['SalesReturnMasterID']
            DeliveryDetailsID = salesReturnDetail['DeliveryDetailsID']
            OrderDetailsID = salesReturnDetail['OrderDetailsID']
            ProductID = salesReturnDetail['ProductID']
            Qty = salesReturnDetail['Qty']
            FreeQty = salesReturnDetail['FreeQty']
            Flavour = salesReturnDetail['Flavour']

            UnitPrice = float(salesReturnDetail['UnitPrice'])
            InclusivePrice = float(salesReturnDetail['InclusivePrice'])
            RateWithTax = float(salesReturnDetail['RateWithTax'])
            CostPerPrice = float(salesReturnDetail['CostPerPrice'])
            PriceListID = float(salesReturnDetail['PriceListID'])
            DiscountPerc = float(salesReturnDetail['DiscountPerc'])
            DiscountAmount = float(salesReturnDetail['DiscountAmount'])
            GrossAmount = float(salesReturnDetail['GrossAmount'])
            TaxableAmount = float(salesReturnDetail['TaxableAmount'])
            VATPerc = float(salesReturnDetail['VATPerc'])
            VATAmount = float(salesReturnDetail['VATAmount'])
            SGSTPerc = float(salesReturnDetail['SGSTPerc'])
            SGSTAmount = float(salesReturnDetail['SGSTAmount'])
            CGSTPerc = float(salesReturnDetail['CGSTPerc'])
            CGSTAmount = float(salesReturnDetail['CGSTAmount'])
            IGSTPerc = float(salesReturnDetail['IGSTPerc'])
            IGSTAmount = float(salesReturnDetail['IGSTAmount'])
            NetAmount = float(salesReturnDetail['NetAmount'])
            AddlDiscPercent = float(salesReturnDetail['AddlDiscPerc'])
            AddlDiscAmt = float(salesReturnDetail['AddlDiscAmt'])
            TAX1Perc = float(salesReturnDetail['TAX1Perc'])
            TAX1Amount = float(salesReturnDetail['TAX1Amount'])
            TAX2Perc = float(salesReturnDetail['TAX2Perc'])
            TAX2Amount = float(salesReturnDetail['TAX2Amount'])
            TAX3Perc = float(salesReturnDetail['TAX3Perc'])
            TAX3Amount = float(salesReturnDetail['TAX3Amount'])
            
            UnitPrice = round(UnitPrice,PriceRounding)
            InclusivePrice = round(InclusivePrice,PriceRounding)
            RateWithTax = round(RateWithTax,PriceRounding)
            CostPerPrice = round(CostPerPrice,PriceRounding)
            PriceListID = round(PriceListID,PriceRounding)
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
            AddlDiscPercent = round(AddlDiscPercent,PriceRounding)
            AddlDiscAmt = round(AddlDiscAmt,PriceRounding)
            TAX1Perc = round(TAX1Perc,PriceRounding)

            TAX1Amount = round(TAX1Amount,PriceRounding)
            TAX2Perc = round(TAX2Perc,PriceRounding)
            TAX2Amount = round(TAX2Amount,PriceRounding)
            TAX3Perc = round(TAX3Perc,PriceRounding)
            TAX3Amount = round(TAX3Amount,PriceRounding)

            SalesReturnQty = Qty
            SalesReturnDetailsID = get_auto_id(SalesReturnDetails,BranchID,CompanyID)


            SalesReturnDetails.objects.create(
                SalesReturnDetailsID=SalesReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesReturnMasterID=SalesReturnMasterID,
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
                Flavour=Flavour,
                CreatedUserID = CreatedUserID,
                CreatedDate = today,
                UpdatedDate=today,
                AddlDiscPercent=AddlDiscPercent,
                AddlDiscAmt=AddlDiscAmt,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                )

            SalesReturnDetails_Log.objects.create(
                TransactionID=SalesReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesReturnMasterID=SalesReturnMasterID,
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
                Flavour=Flavour,
                CreatedUserID = CreatedUserID,
                CreatedDate = today,
                UpdatedDate=today,
                AddlDiscPercent=AddlDiscPercent,
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

            # PriceListID = priceList.PriceListID
            # MultiFactor = priceList.MultiFactor

            MultiFactor = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).MultiFactor
            PriceListID = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID).PriceListID

            # PurchasePrice = priceList.PurchasePrice
            # SalesPrice = priceList.SalesPrice

            qty = float(FreeQty) + float(Qty)

            Qty = float(MultiFactor) * float(qty)
            Cost = float(CostPerPrice) /  float(MultiFactor)

            Qy = round(Qty,4)
            Qty = str(Qy)

            Ct = round(Cost,4)
            Cost = str(Ct)

            princeList_instance = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID,BranchID=BranchID)
            PurchasePrice = princeList_instance.PurchasePrice
            SalesPrice = princeList_instance.SalesPrice

            StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)

            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=VoucherDate,
                VoucherMasterID=SalesReturnMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=WarehouseID,
                QtyIn=Qty,
                Rate=Cost,
                PriceListID=PriceListID,
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
                VoucherMasterID=SalesReturnMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=WarehouseID,
                QtyIn=Qty,
                Rate=Cost,
                PriceListID=PriceListID,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                )

            stockRateInstance = None

            if StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID).exists():
                stockRateInstance = StockRate.objects.get(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID)
                
                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
                stockRateInstance.save()

                if StockTrans.objects.filter(StockRateID=StockRateID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).exists():
                    stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).first()
                    stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                    stockTra_in.save()
                else:
                    StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                    StockTrans.objects.create(
                        StockTransID=StockTransID,
                        BranchID=BranchID,
                        VoucherType=VoucherType,
                        StockRateID=StockRateID,
                        DetailID=SalesReturnDetailsID,
                        MasterID=SalesReturnMasterID,
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
                    PriceListID=PriceListID,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )

                StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                StockTrans.objects.create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    DetailID=SalesReturnDetailsID,
                    MasterID=SalesReturnMasterID,
                    Qty=Qty,
                    IsActive=IsActive,
                    CompanyID=CompanyID,
                    )


            if SalesMaster.objects.filter(CompanyID=CompanyID,VoucherNo=RefferenceBillNo,BranchID=BranchID).exists():
                SalesMaster_instance = SalesMaster.objects.get(CompanyID=CompanyID,VoucherNo=RefferenceBillNo,BranchID=BranchID)
                SalesMasterID = SalesMaster_instance.SalesMasterID

                if SalesDetails.objects.filter(CompanyID=CompanyID,SalesMasterID=SalesMasterID,BranchID=BranchID,ProductID=ProductID).exists():
                    SalesDetails_instances = SalesDetails.objects.filter(CompanyID=CompanyID,SalesMasterID=SalesMasterID,BranchID=BranchID,ProductID=ProductID)

                    for i in SalesDetails_instances:
                        ReturnQty = i.ReturnQty
                        SalesReturnQty = SalesReturnQty
                        ReturnQty = float(ReturnQty) - float(SalesReturnQty)
                        i.ReturnQty = ReturnQty

                        i.save()

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Return', 'Create', 'Sales Return created successfully.', 'Sales Return saved successfully.')

        response_data = {
            "StatusCode" : 6000,
            "message" : "Sales Return created Successfully!!!",
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Return', 'Create', 'Sales Return created Failed.', 'VoucherNo already exist')

        response_data = {
        "StatusCode" : 6001,
        "message" : "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_salesReturn(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    salesReturnkMaster_instance = None
    salesReturnDetails = None
    salesReturnkMaster_instance = SalesReturnMaster.objects.get(CompanyID=CompanyID,pk=pk)
    SalesReturnMasterID = salesReturnkMaster_instance.SalesReturnMasterID
    BranchID = salesReturnkMaster_instance.BranchID
    VoucherNo = salesReturnkMaster_instance.VoucherNo

    Action = "M"

    if LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR").exists():

        ledgerPostInstances = LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR")
        
        for ledgerPostInstance in ledgerPostInstances:
            
            ledgerPostInstance.delete()

    if StockPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR").exists():

        stockPostingInstances = StockPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR")
        
        for stockPostingInstance in stockPostingInstances:
    
            stockPostingInstance.delete()

    data = request.data
        
    VoucherDate = data['VoucherDate']
    RefferenceBillNo = data['RefferenceBillNo']
    RefferenceBillDate = data['RefferenceBillDate']
    CreditPeriod = data['CreditPeriod']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    SalesAccount = data['SalesAccount']
    DeliveryMasterID = data['DeliveryMasterID']
    OrderMasterID = data['OrderMasterID']
    CustomerName = data['CustomerName']
    Address1 = data['Address1']
    Address2 = data['Address2']
    Address3 = data['Address3']
    Notes = data['Notes']
    FinacialYearID = data['FinacialYearID']
    WarehouseID = data['WarehouseID']
    TableID = data['TableID']
    SeatNumber = data['SeatNumber']
    NoOfGuests = data['NoOfGuests']
    INOUT = data['INOUT']
    TokenNumber = data['TokenNumber']
    IsActive = data['IsActive']
    IsPosted = data['IsPosted']
    SalesType = data['SalesType']
    BatchID = data['BatchID']
    TaxID = data['TaxID']
    TaxType = data['TaxType']
    # CashAmount = data['CashAmount']

    TotalGrossAmt = float(data['TotalGrossAmt'])
    TotalTax = float(data['TotalTax'])
    NetTotal = float(data['NetTotal'])
    AdditionalCost = float(data['AdditionalCost'])
    GrandTotal = float(data['GrandTotal'])
    RoundOff = float(data['RoundOff'])
    CashReceived = float(data['CashReceived'])
    BankAmount = float(data['BankAmount'])
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

    TotalGrossAmt = round(TotalGrossAmt,PriceRounding)
    TotalTax = round(TotalTax,PriceRounding)
    NetTotal = round(NetTotal,PriceRounding)
    AdditionalCost = round(AdditionalCost,PriceRounding)
    GrandTotal = round(GrandTotal,PriceRounding)

    RoundOff = round(RoundOff,PriceRounding)
    CashReceived = round(CashReceived,PriceRounding)
    BankAmount = round(BankAmount,PriceRounding)
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

    CashAmount = float(GrandTotal) - float(BankAmount)


    salesReturnkMaster_instance.VoucherDate = VoucherDate
    salesReturnkMaster_instance.RefferenceBillNo = RefferenceBillNo
    salesReturnkMaster_instance.RefferenceBillDate = RefferenceBillDate
    salesReturnkMaster_instance.CreditPeriod = CreditPeriod
    salesReturnkMaster_instance.LedgerID = LedgerID
    salesReturnkMaster_instance.PriceCategoryID = PriceCategoryID
    salesReturnkMaster_instance.EmployeeID = EmployeeID
    salesReturnkMaster_instance.SalesAccount = SalesAccount
    salesReturnkMaster_instance.DeliveryMasterID = DeliveryMasterID
    salesReturnkMaster_instance.OrderMasterID = OrderMasterID
    salesReturnkMaster_instance.CustomerName = CustomerName
    salesReturnkMaster_instance.Address1 = Address1
    salesReturnkMaster_instance.Address2 = Address2
    salesReturnkMaster_instance.Address3 = Address3
    salesReturnkMaster_instance.Notes = Notes
    salesReturnkMaster_instance.FinacialYearID = FinacialYearID
    salesReturnkMaster_instance.TotalGrossAmt = TotalGrossAmt
    salesReturnkMaster_instance.TotalTax = TotalTax
    salesReturnkMaster_instance.NetTotal = NetTotal
    salesReturnkMaster_instance.AdditionalCost = AdditionalCost
    salesReturnkMaster_instance.GrandTotal = GrandTotal
    salesReturnkMaster_instance.RoundOff = RoundOff
    salesReturnkMaster_instance.CashReceived = CashReceived
    salesReturnkMaster_instance.CashAmount = CashAmount
    salesReturnkMaster_instance.BankAmount = BankAmount
    salesReturnkMaster_instance.WarehouseID = WarehouseID
    salesReturnkMaster_instance.TableID = TableID
    salesReturnkMaster_instance.SeatNumber = SeatNumber
    salesReturnkMaster_instance.NoOfGuests = NoOfGuests
    salesReturnkMaster_instance.INOUT = INOUT
    salesReturnkMaster_instance.TokenNumber = TokenNumber
    salesReturnkMaster_instance.IsActive = IsActive
    salesReturnkMaster_instance.IsPosted = IsPosted
    salesReturnkMaster_instance.SalesType = SalesType
    salesReturnkMaster_instance.Action = Action
    salesReturnkMaster_instance.CreatedUserID = CreatedUserID
    salesReturnkMaster_instance.UpdatedDate = today
    salesReturnkMaster_instance.TaxID = TaxID
    salesReturnkMaster_instance.TaxType = TaxType
    salesReturnkMaster_instance.VATAmount = VATAmount
    salesReturnkMaster_instance.SGSTAmount = SGSTAmount
    salesReturnkMaster_instance.CGSTAmount = CGSTAmount
    salesReturnkMaster_instance.IGSTAmount = IGSTAmount
    salesReturnkMaster_instance.TAX1Amount = TAX1Amount
    salesReturnkMaster_instance.TAX2Amount = TAX2Amount
    salesReturnkMaster_instance.TAX3Amount = TAX3Amount
    salesReturnkMaster_instance.AddlDiscPercent = AddlDiscPercent
    salesReturnkMaster_instance.AddlDiscAmt = AddlDiscAmt
    salesReturnkMaster_instance.TotalDiscount = TotalDiscount
    salesReturnkMaster_instance.BillDiscPercent = BillDiscPercent
    salesReturnkMaster_instance.BillDiscAmt = BillDiscAmt
    salesReturnkMaster_instance.save()

    SalesReturnMaster_Log.objects.create(
        TransactionID=SalesReturnMasterID,
        BranchID=BranchID,
        Action=Action,
        VoucherNo=VoucherNo,
        VoucherDate=VoucherDate,
        RefferenceBillNo=RefferenceBillNo,
        RefferenceBillDate=RefferenceBillDate,
        CreditPeriod=CreditPeriod,
        LedgerID=LedgerID,
        PriceCategoryID=PriceCategoryID,
        EmployeeID=EmployeeID,
        SalesAccount=SalesAccount,
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
        CashReceived=CashReceived,
        CashAmount=CashAmount,
        BankAmount=BankAmount,
        WarehouseID=WarehouseID,
        TableID=TableID,
        SeatNumber=SeatNumber,
        NoOfGuests=NoOfGuests,
        INOUT=INOUT,
        TokenNumber=TokenNumber,
        IsActive=IsActive,
        IsPosted=IsPosted,
        SalesType=SalesType,
        CreatedUserID=CreatedUserID,
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

    VoucherType = "SR"

    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

    LedgerPosting.objects.create(
        LedgerPostingID=LedgerPostingID,
        BranchID=BranchID,
        Date=VoucherDate,
        VoucherMasterID=SalesReturnMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=SalesAccount,
        Debit=TotalGrossAmt,
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
        VoucherMasterID=SalesReturnMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=SalesAccount,
        Debit=TotalGrossAmt,
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
        VoucherMasterID=SalesReturnMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=LedgerID,
        Credit=GrandTotal,
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
        VoucherMasterID=SalesReturnMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=LedgerID,
        Credit=GrandTotal,
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
            VoucherMasterID=SalesReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=TotalTax,
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
            VoucherMasterID=SalesReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Debit=TotalTax,
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
            VoucherMasterID=SalesReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=BillDiscAmt,
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
            VoucherMasterID=SalesReturnMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=BillDiscAmt,
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
            VoucherMasterID=SalesReturnMasterID,
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
            VoucherMasterID=SalesReturnMasterID,
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

    if float(RoundOff) < 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        RoundOff = abs(float(RoundOff))

        LedgerID = "78"

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=VoucherDate,
            VoucherMasterID=SalesReturnMasterID,
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
            VoucherMasterID=SalesReturnMasterID,
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
    #         SalesReturnDetailsID = deleted_Data['SalesReturnDetailsID']
    #         pk = deleted_Data['unq_id']

    #         if not pk == '':
    #             if SalesReturnDetails.objects.filter(pk=pk).exists():
    #                 deleted_detail = SalesReturnDetails.objects.get(pk=pk)
    #                 deleted_detail.delete()

    #             stockTrans_instance = None
    #             if StockTrans.objects.filter(DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
    #                 stockTrans_instance = StockTrans.objects.get(DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True)
    #                 qty_in_stockTrans = stockTrans_instance.Qty
    #                 StockRateID = stockTrans_instance.StockRateID
    #                 stockTrans_instance.IsActive = False
    #                 stockTrans_instance.save()

    #                 stockRate_instance = StockRate.objects.get(StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseID)
    #                 stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
    #                 stockRate_instance.save()


    deleted_datas = data["deleted_data"]
    if deleted_datas:
        for deleted_Data in deleted_datas:
            deleted_pk = deleted_Data['unq_id']
            SalesReturnDetailsID_Deleted = deleted_Data['SalesReturnDetailsID']
            ProductID_Deleted = deleted_Data['ProductID']
            PriceListID_Deleted = deleted_Data['PriceListID']
            Rate_Deleted = deleted_Data['Rate']
            SalesReturnMasterID_Deleted = deleted_Data['SalesReturnMasterID']
            WarehouseID_Deleted = deleted_Data['WarehouseID']

            if PriceList.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,DefaultUnit=True).exists():
                priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,DefaultUnit=True)
                MultiFactor = priceList.MultiFactor
                Cost = float(Rate_Deleted) /  float(MultiFactor)
                Ct = round(Cost,4)
                Cost_Deleted = str(Ct)

                if not deleted_pk == '' or not deleted_pk == 0:
                    if SalesReturnDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk).exists():
                        deleted_detail = SalesReturnDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk)
                        deleted_detail.delete()
                        # if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID).exists():
                        #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID)
                        #     StockRateID = stockRate_instance.StockRateID
                        #     if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=SalesReturnDetailsID_Deleted,MasterID=SalesReturnMasterID_Deleted,BranchID=BranchID,
                        #         VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID).exists():
                        #         stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=SalesReturnDetailsID_Deleted,MasterID=SalesReturnMasterID_Deleted,BranchID=BranchID,
                        #             VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)
                        #         qty_in_stockTrans = stockTrans_instance.Qty
                        #         stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
                        #         stockRate_instance.save()
                        #         stockTrans_instance.IsActive = False
                        #         stockTrans_instance.save()

                        if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=SalesReturnDetailsID_Deleted,MasterID=SalesReturnMasterID_Deleted,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
                            stockTrans_instance = StockTrans.objects.filter(CompanyID=CompanyID,DetailID=SalesReturnDetailsID_Deleted,MasterID=SalesReturnMasterID_Deleted,BranchID=BranchID,VoucherType=VoucherType,IsActive=True)
                            for stck in stockTrans_instance:
                                StockRateID = stck.StockRateID
                                stck.IsActive = False
                                qty_in_stockTrans = stck.Qty
                                if StockRate.objects.filter(CompanyID=CompanyID,StockRateID=StockRateID,BranchID=BranchID).exists():
                                    stockRateInstance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=StockRateID,BranchID=BranchID)
                                    stockRateInstance.Qty = float(stockRateInstance.Qty) - float(qty_in_stockTrans)
                                    stockRateInstance.save()
                                stck.save()


    salesReturnDetails = data["SalesReturnDetails"]

    for salesReturnDetail in salesReturnDetails:
        pk = salesReturnDetail['unq_id']
        detailID = salesReturnDetail['detailID']
        # SalesReturnMasterID = serialized.data['SalesReturnMasterID']
        DeliveryDetailsID = salesReturnDetail['DeliveryDetailsID']
        OrderDetailsID = salesReturnDetail['OrderDetailsID']
        ProductID = salesReturnDetail['ProductID']
        Qty_detail = salesReturnDetail['Qty']
        FreeQty = salesReturnDetail['FreeQty']
        Flavour = salesReturnDetail['Flavour']
        # AddlDiscPercent = salesReturnDetail['AddlDiscPerc']

        UnitPrice = float(salesReturnDetail['UnitPrice'])
        InclusivePrice = float(salesReturnDetail['InclusivePrice'])
        RateWithTax = float(salesReturnDetail['RateWithTax'])
        CostPerPrice = float(salesReturnDetail['CostPerPrice'])
        PriceListID = float(salesReturnDetail['PriceListID'])
        DiscountPerc = float(salesReturnDetail['DiscountPerc'])
        DiscountAmount = float(salesReturnDetail['DiscountAmount'])
        GrossAmount = float(salesReturnDetail['GrossAmount'])
        TaxableAmount = float(salesReturnDetail['TaxableAmount'])
        VATPerc = float(salesReturnDetail['VATPerc'])
        VATAmount = float(salesReturnDetail['VATAmount'])
        SGSTPerc = float(salesReturnDetail['SGSTPerc'])
        SGSTAmount = float(salesReturnDetail['SGSTAmount'])
        CGSTPerc = float(salesReturnDetail['CGSTPerc'])
        CGSTAmount = float(salesReturnDetail['CGSTAmount'])
        IGSTPerc = float(salesReturnDetail['IGSTPerc'])
        IGSTAmount = float(salesReturnDetail['IGSTAmount'])
        NetAmount = float(salesReturnDetail['NetAmount'])
        AddlDiscPercent = AddlDiscPercent
        AddlDiscAmt = float(salesReturnDetail['AddlDiscAmt'])
        TAX1Perc = float(salesReturnDetail['TAX1Perc'])
        TAX1Amount = float(salesReturnDetail['TAX1Amount'])
        TAX2Perc = float(salesReturnDetail['TAX2Perc'])
        TAX2Amount = float(salesReturnDetail['TAX2Amount'])
        TAX3Perc = float(salesReturnDetail['TAX3Perc'])
        TAX3Amount = float(salesReturnDetail['TAX3Amount'])

        UnitPrice = round(UnitPrice,PriceRounding)
        InclusivePrice = round(InclusivePrice,PriceRounding)
        RateWithTax = round(RateWithTax,PriceRounding)
        CostPerPrice = round(CostPerPrice,PriceRounding)
        PriceListID = round(PriceListID,PriceRounding)

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

        # deleted_datas = data["deleted_data"]
        # if deleted_datas:
        #     for deleted_Data in deleted_datas:
        #         deleted_pk = deleted_Data['unq_id']
        #         SalesReturnDetailsID = deleted_Data['SalesReturnDetailsID']
        #         if not deleted_pk == '':
        #             if SalesReturnDetails.objects.filter(pk=deleted_pk).exists():
        #                 deleted_detail = SalesReturnDetails.objects.filter(pk=deleted_pk)
        #                 deleted_detail.delete()

        #                 if StockRate.objects.filter(ProductID=ProductID,PriceListID=PriceListID,Cost=Cost,WareHouseID=WarehouseID).exists():
        #                     stockRate_instance = StockRate.objects.get(ProductID=ProductID,PriceListID=PriceListID,Cost=Cost,WareHouseID=WarehouseID)
        #                     StockRateID = stockRate_instance.StockRateID
        #                     stockTrans_instance = StockTrans.objects.get(DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,
        #                         VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)
        #                     qty_in_stockTrans = stockTrans_instance.Qty
        #                     stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
        #                     stockRate_instance.save()
        #                     stockTrans_instance.IsActive = False
        #                     stockTrans_instance.save()
                                

        princeList_instance = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,BranchID=BranchID)
        PurchasePrice = princeList_instance.PurchasePrice
        SalesPrice = princeList_instance.SalesPrice
        
        StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)

        if detailID == 0:
            salesReturnDetail_instance = SalesReturnDetails.objects.get(CompanyID=CompanyID,pk=pk)
            
            SalesReturnDetailsID = salesReturnDetail_instance.SalesReturnDetailsID
            salesReturnDetail_instance.DeliveryDetailsID = DeliveryDetailsID
            salesReturnDetail_instance.OrderDetailsID = OrderDetailsID
            salesReturnDetail_instance.ProductID = ProductID
            salesReturnDetail_instance.Qty = Qty_detail
            salesReturnDetail_instance.FreeQty = FreeQty
            salesReturnDetail_instance.UnitPrice = UnitPrice
            salesReturnDetail_instance.InclusivePrice = InclusivePrice
            salesReturnDetail_instance.RateWithTax = RateWithTax
            salesReturnDetail_instance.CostPerPrice = CostPerPrice
            salesReturnDetail_instance.PriceListID = PriceListID
            salesReturnDetail_instance.DiscountPerc = DiscountPerc
            salesReturnDetail_instance.DiscountAmount = DiscountAmount
            salesReturnDetail_instance.GrossAmount = GrossAmount
            salesReturnDetail_instance.TaxableAmount = TaxableAmount
            salesReturnDetail_instance.VATPerc = VATPerc
            salesReturnDetail_instance.VATAmount = VATAmount
            salesReturnDetail_instance.SGSTPerc = SGSTPerc
            salesReturnDetail_instance.SGSTAmount = SGSTAmount
            salesReturnDetail_instance.CGSTPerc = CGSTPerc
            salesReturnDetail_instance.CGSTAmount = CGSTAmount
            salesReturnDetail_instance.IGSTPerc = IGSTPerc
            salesReturnDetail_instance.IGSTAmount = IGSTAmount
            salesReturnDetail_instance.NetAmount = NetAmount
            salesReturnDetail_instance.Flavour = Flavour
            salesReturnDetail_instance.Action = Action
            salesReturnDetail_instance.CreatedUserID = CreatedUserID
            salesReturnDetail_instance.UpdatedDate = today
            salesReturnDetail_instance.AddlDiscPercent = AddlDiscPercent
            salesReturnDetail_instance.AddlDiscAmt = AddlDiscAmt
            salesReturnDetail_instance.TAX1Perc = TAX1Perc
            salesReturnDetail_instance.TAX1Amount = TAX1Amount
            salesReturnDetail_instance.TAX2Perc = TAX2Perc
            salesReturnDetail_instance.TAX2Amount = TAX2Amount
            salesReturnDetail_instance.TAX3Perc = TAX3Perc
            salesReturnDetail_instance.TAX3Amount = TAX3Amount

            salesReturnDetail_instance.save()

            SalesReturnDetails_Log.objects.create(
                TransactionID=SalesReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesReturnMasterID=SalesReturnMasterID,
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
                Flavour=Flavour,
                CreatedUserID = CreatedUserID,
                CreatedDate = today,
                UpdatedDate=today,
                AddlDiscPercent=AddlDiscPercent,
                AddlDiscAmt=AddlDiscAmt,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                )

            
            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=VoucherDate,
                VoucherMasterID=SalesReturnMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=WarehouseID,
                QtyIn=Qty,
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
                VoucherMasterID=SalesReturnMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=WarehouseID,
                QtyIn=Qty,
                Rate=Cost,
                PriceListID=PriceListID_DefUnit,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                )

        if detailID == 1:

            SalesReturnDetailsID = get_auto_id(SalesReturnDetails,BranchID,CompanyID)

            Action = "A"

            SalesReturnDetails.objects.create(
                SalesReturnDetailsID=SalesReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesReturnMasterID=SalesReturnMasterID,
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
                Flavour=Flavour,
                CreatedUserID = CreatedUserID,
                CreatedDate = today,
                UpdatedDate=today,
                AddlDiscPercent=AddlDiscPercent,
                AddlDiscAmt=AddlDiscAmt,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                )

            SalesReturnDetails_Log.objects.create(
                TransactionID=SalesReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesReturnMasterID=SalesReturnMasterID,
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
                Flavour=Flavour,
                CreatedUserID = CreatedUserID,
                CreatedDate = today,
                UpdatedDate=today,
                AddlDiscPercent=AddlDiscPercent,
                AddlDiscAmt=AddlDiscAmt,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                )

            

            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=VoucherDate,
                VoucherMasterID=SalesReturnMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=WarehouseID,
                QtyIn=Qty,
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
                VoucherMasterID=SalesReturnMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=WarehouseID,
                QtyIn=Qty,
                Rate=Cost,
                PriceListID=PriceListID_DefUnit,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                )

        

        if detailID == 1:
            if StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID).exists():
                stockRateInstance = StockRate.objects.get(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID)
                
                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
                stockRateInstance.save()

                if StockTrans.objects.filter(StockRateID=StockRateID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).exists():
                    stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,VoucherType=VoucherType,BranchID=BranchID).first()
                    stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                    stockTra_in.save()
                else:
                    StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                    StockTrans.objects.create(
                        StockTransID=StockTransID,
                        BranchID=BranchID,
                        VoucherType=VoucherType,
                        StockRateID=StockRateID,
                        DetailID=SalesReturnDetailsID,
                        MasterID=SalesReturnMasterID,
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

                StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                StockTrans.objects.create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    DetailID=SalesReturnDetailsID,
                    MasterID=SalesReturnMasterID,
                    Qty=Qty,
                    IsActive=IsActive,
                    CompanyID=CompanyID,
                    )
        else:
            if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,Cost=Cost,WareHouseID=WarehouseID).exists():
                stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,Cost=Cost,WareHouseID=WarehouseID)
                StockRateID = stockRate_instance.StockRateID
                if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,
                        VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID).exists():
                    stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,
                        VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)

                    if float(stockTrans_instance.Qty) < float(Qty):
                        deff = float(Qty) - float(stockTrans_instance.Qty)
                        stockTrans_instance.Qty = float(stockTrans_instance.Qty) + float(deff)
                        stockTrans_instance.save()

                        stockRate_instance.Qty = float(stockRate_instance.Qty) + float(deff)
                        stockRate_instance.save()

                    elif float(stockTrans_instance.Qty) > float(Qty):
                        deff = float(stockTrans_instance.Qty) - float(Qty)
                        stockTrans_instance.Qty = float(stockTrans_instance.Qty) - float(deff)
                        stockTrans_instance.save() 

                        stockRate_instance.Qty = float(stockRate_instance.Qty) - float(deff)
                        stockRate_instance.save()
                        
            # if StockTrans.objects.filter(MasterID=SalesReturnMasterID,DetailID=SalesReturnDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
            #     stockTrans_instance = StockTrans.objects.filter(MasterID=SalesReturnMasterID,DetailID=SalesReturnDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).first()
            #     stockRateID = stockTrans_instance.StockRateID
            #     stockRate_instance = StockRate.objects.get(StockRateID=stockRateID,BranchID=BranchID,WareHouseID=WarehouseID)
                
            #     if float(stockTrans_instance.Qty) < float(Qty):
            #         deff = float(Qty) - float(stockTrans_instance.Qty)
            #         stockTrans_instance.Qty = float(stockTrans_instance.Qty) + float(deff)
            #         stockTrans_instance.save()

            #         stockRate_instance.Qty = float(stockRate_instance.Qty) + float(deff)
            #         stockRate_instance.save()

            #     elif float(stockTrans_instance.Qty) > float(Qty):
            #         deff = float(stockTrans_instance.Qty) - float(Qty)
            #         stockTrans_instance.Qty = float(stockTrans_instance.Qty) - float(deff)
            #         stockTrans_instance.save() 

            #         stockRate_instance.Qty = float(stockRate_instance.Qty) - float(deff)
            #         stockRate_instance.save()

    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Return', 'Edit', 'Sales Return Updated Successfully.', 'Sales Return Updated Successfully.')

    response_data = {
    "StatusCode" : 6000,
    "message" : "Sales Returns Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_salesReturnMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if SalesReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():

            instances = SalesReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

            serialized = SalesReturnMasterRestSerializer(instances,many=True,context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Return', 'List', 'Sales Return List Viewed Successfully.', 'Sales Return List Viewed Successfully.')

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Return', 'List', 'Sales Return List Viewed Failed.', 'Sales Return not found in this branch')
            response_data = {
            "StatusCode" : 6001,
            "message" : "Sales Return Master not found in this branch."
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
def sales_return_pagination(request):
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
            sales_return_object = SalesReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

            sale_return_sort_pagination = list_pagination(
                sales_return_object,
                items_per_page,
                page_number
            )
            sale_serializer = SalesReturnMasterRestSerializer(
                sale_return_sort_pagination,
                many=True,
                context={"request":request,"CompanyID":CompanyID,"PriceRounding" : PriceRounding}
            )
            data = sale_serializer.data
            if not data==None:
                response_data = {
                    "StatusCode" : 6000,
                    "data" : data,
                    "count": len(sales_return_object)
                }
            else:
                response_data = {
                    "StatusCode" : 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def salesReturnMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    instance = None
    if SalesReturnMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = SalesReturnMaster.objects.get(CompanyID=CompanyID,pk=pk)

        serialized = SalesReturnMasterRestSerializer(instance,context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Return', 'View', 'Sales Return Single Viewed Successfully.', 'Sales Return Single Viewed Successfully.')

        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Return', 'View', 'Sales Return Single Viewed Failed.', 'Sales Return Not Found')
        response_data = {
            "StatusCode" : 6001,
            "message" : "Sales Return Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_salesReturnMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if SalesReturnMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = SalesReturnMaster.objects.get(CompanyID=CompanyID,pk=pk)
        SalesReturnMasterID = instance.SalesReturnMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        VoucherDate = instance.VoucherDate
        RefferenceBillNo = instance.RefferenceBillNo
        RefferenceBillDate = instance.RefferenceBillDate
        CreditPeriod = instance.CreditPeriod
        LedgerID = instance.LedgerID
        PriceCategoryID = instance.PriceCategoryID
        EmployeeID = instance.EmployeeID
        SalesAccount = instance.SalesAccount
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
        CashReceived = instance.CashReceived
        CashAmount = instance.CashAmount
        BankAmount = instance.BankAmount
        WarehouseID = instance.WarehouseID
        TableID = instance.TableID
        SeatNumber = instance.SeatNumber
        NoOfGuests = instance.NoOfGuests
        INOUT = instance.INOUT
        TokenNumber = instance.TokenNumber
        IsActive = instance.IsActive
        IsPosted = instance.IsPosted
        SalesType = instance.SalesType
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

        SalesReturnMaster_Log.objects.create(
            TransactionID=SalesReturnMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherDate=VoucherDate,
            RefferenceBillNo=RefferenceBillNo,
            RefferenceBillDate=RefferenceBillDate,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
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
            CashReceived=CashReceived,
            CashAmount=CashAmount,
            BankAmount=BankAmount,
            WarehouseID=WarehouseID,
            TableID=TableID,
            SeatNumber=SeatNumber,
            NoOfGuests=NoOfGuests,
            INOUT=INOUT,
            TokenNumber=TokenNumber,
            IsActive=IsActive,
            IsPosted=IsPosted,
            SalesType=SalesType,
            CreatedUserID=CreatedUserID,
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

        if LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR").exists():

            ledgerPostInstances = LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR")
            
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
                    Date=Date,
                    VoucherMasterID=SalesReturnMasterID,
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

        if StockPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR").exists():

            stockPostingInstances = StockPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR")
            
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
                    Date=Date,
                    VoucherMasterID=SalesReturnMasterID,
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

        detail_instances = SalesReturnDetails.objects.filter(CompanyID=CompanyID,SalesReturnMasterID=SalesReturnMasterID)

        for detail_instance in detail_instances:

            SalesReturnDetailsID = detail_instance.SalesReturnDetailsID
            BranchID = detail_instance.BranchID
            SalesReturnMasterID = detail_instance.SalesReturnMasterID
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
            Flavour = detail_instance.Flavour
            CreatedUserID = detail_instance.CreatedUserID
            AddlDiscPercent = detail_instance.AddlDiscPercent
            AddlDiscAmt = detail_instance.AddlDiscAmt
            TAX1Perc = detail_instance.TAX1Perc
            TAX1Amount = detail_instance.TAX1Amount
            TAX2Perc = detail_instance.TAX2Perc
            TAX2Amount = detail_instance.TAX2Amount
            TAX3Perc = detail_instance.TAX3Perc
            TAX3Amount = detail_instance.TAX3Amount

            SalesReturnDetails_Log.objects.create(
                TransactionID=SalesReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesReturnMasterID=SalesReturnMasterID,
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
                Flavour=Flavour,
                CreatedUserID = CreatedUserID,
                CreatedDate = today,
                UpdatedDate=today,
                AddlDiscPercent=AddlDiscPercent,
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
                
            # if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR").exists():
            #     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR")

            #     stockRateID = stockTrans_instance.StockRateID
            #     stockTrans_instance.IsActive = False
            #     stockTrans_instance.save()

            #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
            #     stockRate_instance.Qty = stockTrans_instance.Qty
            #     stockRate_instance.save()

            if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR",IsActive = True).exists():
                stockTrans_instances = StockTrans.objects.filter(CompanyID=CompanyID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR",IsActive = True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
                    stockRate_instance.Qty = float(stockRate_instance.Qty) - float(i.Qty)
                    stockRate_instance.save()

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Return', 'Delete', 'Sales Return Deleted Successfully.', 'Sales Return Deleted Successfully.')

        response_data = {
            "StatusCode" : 6000,
            "title" : "Success",
            "message" : "Sales Return Master Deleted Successfully!"
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Return', 'Delete', 'Sales Return Deleted Failed.', 'Sales Return Master Not Found')

        response_data = {
            "StatusCode" : 6001,
            "title" : "Failed",
            "message" : "Sales Return Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def report_salesReturns(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        ToDate = serialized1.data['ToDate']

        if SalesReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherDate__lte=ToDate).exists():
            instances = SalesReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherDate__lte=ToDate)

            serialized = SalesReturnMasterReportSerializer(instances,many=True,context = {"CompanyID": CompanyID })

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Return Report', 'Report', 'Sales Return Report Viewed Successfully.', 'Sales Return Report Viewed Successfully.')
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Return Report', 'Report', 'Sales Return Report Viewed Failed.', 'No data under this date')
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