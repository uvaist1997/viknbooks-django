from main.functions import converted_float, get_GeneralSettings
from rest_framework import serializers
from brands.models import BillWiseDetails, BillWiseMaster, Branch, Parties, PaymentMaster, PaymentDetails, AccountLedger, PurchaseMaster, PurchaseReturnMaster, SalesMaster, SalesReturnMaster, TransactionTypes
from django.db.models import Sum


class PaymentMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMaster
        fields = ('id', 'BranchID', 'VoucherNo', 'VoucherType', 'LedgerID',
                  'EmployeeID', 'PaymentNo',
                  'FinancialYearID', 'Date', 'TotalAmount', 'Notes', 'IsActive', 'CreatedUserID')


class PaymentMasterRestSerializer(serializers.ModelSerializer):

    PaymentDetails = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalAmount = serializers.SerializerMethodField()
    TotalAmount_rounded = serializers.SerializerMethodField()
    selected_ledgers = serializers.SerializerMethodField()
    is_ShowDiscount = serializers.SerializerMethodField()


    class Meta:
        model = PaymentMaster
        fields = ('id','is_ShowDiscount', 'PaymentMasterID', 'BranchID', 'Action', 'VoucherNo', 'VoucherType', 'LedgerID', 'LedgerName',
                  'EmployeeID', 'PaymentNo', 'TotalAmount_rounded', 'selected_ledgers',
                  'FinancialYearID', 'Date', 'TotalAmount', 'Notes', 'IsActive', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'PaymentDetails')


    def get_is_ShowDiscount(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        is_ShowDiscount = get_GeneralSettings(
            CompanyID, instances.BranchID, "ShowDiscountInPayments"
        )
        return is_ShowDiscount
        
    
    def get_PaymentDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        VoucherType = instances.VoucherType
        payments_details = PaymentDetails.objects.filter(
            CompanyID=CompanyID, PaymentMasterID=instances.PaymentMasterID, BranchID=instances.BranchID, VoucherType=VoucherType).order_by('PaymentDetailsID')
        serialized = PaymentDetailsRestSerializer(payments_details, many=True, context={
                                                  "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_selected_ledgers(self, instances):
        CompanyID = self.context.get("CompanyID")
        payment_details = PaymentDetails.objects.filter(
            PaymentMasterID=instances.PaymentMasterID, BranchID=instances.BranchID, CompanyID=CompanyID)
        selected_ledgers = payment_details.values_list('LedgerID', flat=True)
        return selected_ledgers

    def get_LedgerName(self, instances):

        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            ledger = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID)
            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""

        return LedgerName

    def get_TotalAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        TotalAmount = instances.TotalAmount

        # TotalAmount = round(TotalAmount,PriceRounding)

        return str(TotalAmount)

    def get_TotalAmount_rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        TotalAmount_rounded = instances.TotalAmount

        TotalAmount_rounded = round(TotalAmount_rounded, PriceRounding)

        return str(TotalAmount_rounded)


class PaymentDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentDetails
        fields = ('id', 'BranchID', 'PaymentMasterID', 'PaymentGateway', 'RefferenceNo',
                  'CardNetwork', 'PaymentStatus', 'DueDate', 'LedgerID', 'Amount', 'Balance', 'Discount', 'NetAmount', 'Narration', 'CreatedUserID')


class PaymentDetailsRestSerializer(serializers.ModelSerializer):
    Amount = serializers.SerializerMethodField()
    Discount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    PaymentGatewayName = serializers.SerializerMethodField()
    CardNetworkName = serializers.SerializerMethodField()
    PaymentStatusName = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    LedgerList_detail = serializers.SerializerMethodField()
    LedgerIDVal = serializers.SerializerMethodField()


    class Meta:
        model = PaymentDetails
        fields = ('id',
                  'PaymentDetailsID',
                  'BranchID', 'Action',
                  'PaymentMasterID',
                  'PaymentGateway',
                  'RefferenceNo',
                  'CardNetwork',
                  'PaymentStatus',
                  'DueDate',
                  'LedgerID',
                  'Amount',
                  'Balance',
                  'Discount',
                  'NetAmount',
                  'Narration',
                  'CreatedDate',
                  'UpdatedDate',
                  'CreatedUserID',
                  'PaymentGatewayName',
                  'CardNetworkName',
                  'PaymentStatusName',
                  'LedgerName',
                  'detailID',
                  'LedgerList_detail',
                  'LedgerIDVal',
                  )


    
    def get_detailID(self, payments_details):
        detailID = 0
        return detailID

    def get_LedgerIDVal(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        LedgerID = payments_details.LedgerID
        LedgerIDVal = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            LedgerIDVal = AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID).first().LedgerName
        return LedgerIDVal

    def get_LedgerList_detail(self, journal_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = journal_details.BranchID
        LedgerName = ""
        LedgerID = journal_details.LedgerID
        LedgerList_detail = []
        if AccountLedger.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            ledger = AccountLedger.objects.get(
                LedgerID=LedgerID, CompanyID=CompanyID)
            LedgerName = ledger.LedgerName

        LedgerList_detail.append(
            {"LedgerName": LedgerName, "LedgerID": LedgerID})
        return LedgerList_detail

    def get_Amount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))

        Amount = payments_details.Amount

        # Amount = round(Amount,PriceRounding)

        return converted_float(Amount)

    def get_Balance(self, payments_details):

        Balance = payments_details.Balance

        Balance = round(Balance, 2)

        return converted_float(Balance)

    def get_Discount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))

        Discount = payments_details.Discount

        # Discount = round(Discount,PriceRounding)

        return converted_float(Discount)

    def get_NetAmount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))

        NetAmount = payments_details.NetAmount

        # NetAmount = round(NetAmount,PriceRounding)

        return converted_float(NetAmount)

    def get_PaymentGatewayName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")
        PaymentGateway = payments_details.PaymentGateway
        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=PaymentGateway).exists():
            PaymentGateway = TransactionTypes.objects.get(
                CompanyID=CompanyID, TransactionTypesID=PaymentGateway).Name
        else:
            PaymentGateway = ""
        return str(PaymentGateway)

    def get_CardNetworkName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        CardNetwork = payments_details.CardNetwork
        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=CardNetwork).exists():
            CardNetwork = TransactionTypes.objects.get(
                CompanyID=CompanyID, TransactionTypesID=CardNetwork).Name
        else:
            CardNetwork = ""
        return str(CardNetwork)

    def get_PaymentStatusName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        PaymentStatus = payments_details.PaymentStatus
        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=PaymentStatus).exists():
            PaymentStatus = TransactionTypes.objects.get(
                CompanyID=CompanyID, TransactionTypesID=PaymentStatus).Name
        else:
            PaymentStatus = ""
        return str(PaymentStatus)

    def get_LedgerName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        Ledger = payments_details.LedgerID
        BranchID = payments_details.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Ledger).exists():
            Ledger = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=Ledger).LedgerName
        else:
            Ledger = ""
        return str(Ledger)


class ListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()
    VoucherType = serializers.CharField()


class PaymentPrintSerializer(serializers.ModelSerializer):
    VoucherDetails = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalAmount = serializers.SerializerMethodField()
    TaxNo = serializers.SerializerMethodField()
    PhoneNo = serializers.SerializerMethodField()
    CustomerCRNo = serializers.SerializerMethodField()
    DisplayName = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMaster
        fields = ('id',
                  'VoucherNo',
                  'LedgerName',
                  'TotalAmount',
                  'Date', 'Notes',
                  'VoucherDetails',
                  'TaxNo',
                  'PhoneNo',
                  'CustomerCRNo',
                  'DisplayName')

    def get_VoucherDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        VoucherType = instances.VoucherType
        payments_details = PaymentDetails.objects.filter(
            CompanyID=CompanyID, PaymentMasterID=instances.PaymentMasterID, BranchID=instances.BranchID, VoucherType=VoucherType).order_by('PaymentDetailsID')
        serialized = PaymentDetailsPrintSerializer(payments_details, many=True, context={
                                                   "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        return serialized.data

    def get_TaxNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        TaxNo = ""
        if Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            party_instance = Parties.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID).first()
            if party_instance.VATNumber:
                TaxNo = party_instance.VATNumber
            elif party_instance.GSTNumber:
                TaxNo = party_instance.GSTNumber
        return TaxNo

    def get_DisplayName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        DisplayName = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]).exists():
            DisplayName = Parties.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID).DisplayName
        return DisplayName

    def get_PhoneNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        Mobile = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]).exists():
            if Parties.objects.get(CompanyID=CompanyID, LedgerID=LedgerID).Mobile:
                Mobile = Parties.objects.get(
                    CompanyID=CompanyID, LedgerID=LedgerID).Mobile
        return Mobile

    def get_CustomerCRNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        CRNo = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]).exists():
            if Parties.objects.get(CompanyID=CompanyID, LedgerID=LedgerID).CRNo:
                CRNo = Parties.objects.get(
                    CompanyID=CompanyID, LedgerID=LedgerID).CRNo
        return CRNo

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            ledger = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""
        return LedgerName

    def get_TotalAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalAmount = instances.TotalAmount
        TotalAmount = round(TotalAmount, PriceRounding)
        return str(TotalAmount)


class PaymentDetailsPrintSerializer(serializers.ModelSerializer):
    Amount = serializers.SerializerMethodField()
    Discount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()

    class Meta:
        model = PaymentDetails
        fields = ('id',
                  'Amount',
                  'Discount',
                  'NetAmount',
                  'Narration',
                  'LedgerName'
                  )

    def get_Amount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Amount = payments_details.Amount
        Amount = round(Amount, PriceRounding)
        return converted_float(Amount)

    def get_Discount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Discount = payments_details.Discount
        Discount = round(Discount, PriceRounding)
        return converted_float(Discount)

    def get_NetAmount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = payments_details.NetAmount
        NetAmount = round(NetAmount, PriceRounding)
        return converted_float(NetAmount)

    def get_LedgerName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        Ledger = payments_details.LedgerID
        BranchID = payments_details.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Ledger, BranchID=BranchID).exists():
            Ledger = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=Ledger, BranchID=BranchID).LedgerName
        else:
            Ledger = ""
        return str(Ledger)


class BillwiseMasterSerializer(serializers.ModelSerializer):
    AmountDue = serializers.SerializerMethodField()
    Amount = serializers.SerializerMethodField()
    full_amt = serializers.SerializerMethodField()
    show_negative = serializers.SerializerMethodField()
    actualAmount = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()

    class Meta:
        model = BillWiseMaster
        fields = ('id',
                  'BillwiseMasterID',
                  'InvoiceNo',
                  'TransactionID',
                  'VoucherType',
                  'VoucherDate',
                  'InvoiceAmount',
                  'Payments',
                  'DueDate',
                  'CustomerID',
                  'AmountDue',
                  'Amount',
                  'full_amt',
                  'show_negative',
                  'actualAmount',
                  'created_date'
                  )

    # def get_AmountDue(self, instance):
    #     call_type = self.context.get("call_type")
    #     InvoiceAmount = instance.InvoiceAmount
    #     Payments = instance.Payments
    #     if call_type == "update":
    #         AmountDue = converted_float(
    #             InvoiceAmount) - converted_float(Payments)
    #     else:
    #         AmountDue = converted_float(InvoiceAmount) - converted_float(Payments)
    #     return converted_float(AmountDue)
    
    def get_created_date(self, instance):
        CompanyID = self.context.get("CompanyID")
        VoucherType = instance.VoucherType
        InvoiceNo = instance.InvoiceNo
        created_date = ""
        if VoucherType == "SI" and SalesMaster.objects.filter(CompanyID=CompanyID, VoucherNo=InvoiceNo).exists():
            created_date = SalesMaster.objects.filter(
                CompanyID=CompanyID, VoucherNo=InvoiceNo).first().CreatedDate
        elif VoucherType == "PI" and PurchaseMaster.objects.filter(CompanyID=CompanyID, VoucherNo=InvoiceNo).exists():
            created_date = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, VoucherNo=InvoiceNo).first().CreatedDate
        elif VoucherType == "SR" and SalesReturnMaster.objects.filter(CompanyID=CompanyID, VoucherNo=InvoiceNo).exists():
            created_date = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, VoucherNo=InvoiceNo).first().CreatedDate
        elif VoucherType == "PR" and PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, VoucherNo=InvoiceNo).exists():
            created_date = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, VoucherNo=InvoiceNo).first().CreatedDate
        
        return str(created_date)
    
    def get_actualAmount(self, instance):
        CompanyID = self.context.get("CompanyID")
        PaymentVoucherNo = self.context.get("PaymentVoucherNo")
        PaymentVoucherType = self.context.get("PaymentVoucherType")
        call_type = self.context.get("call_type")
        BranchID = instance.BranchID
        BillwiseMasterID = instance.BillwiseMasterID
        VoucherType = instance.VoucherType

        InvoiceAmount = instance.InvoiceAmount
        Payments = instance.Payments
        AmountDue = 0
        if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
            details = BillWiseDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID)
            payment_sum = details.aggregate(Sum("Payments"))
            payment_sum = payment_sum["Payments__sum"]
            AmountDue = converted_float(
                InvoiceAmount) - converted_float(payment_sum)
        if call_type == "update":
            if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=PaymentVoucherNo, PaymentVoucherType=PaymentVoucherType).exists():
                billwise_detail_ins = BillWiseDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=PaymentVoucherNo, PaymentVoucherType=PaymentVoucherType)

                # Amount = billwise_detail_ins.Payments
                Amount = billwise_detail_ins.aggregate(Sum('Payments'))
                Amount = Amount["Payments__sum"]
                AmountDue = converted_float(
                    InvoiceAmount) - (converted_float(payment_sum) - converted_float(Amount))

        return converted_float(AmountDue)
    
    def get_AmountDue(self, instance):
        CompanyID = self.context.get("CompanyID")
        PaymentVoucherNo = self.context.get("PaymentVoucherNo")
        PaymentVoucherType = self.context.get("PaymentVoucherType")
        call_type = self.context.get("call_type")
        BranchID = instance.BranchID
        BillwiseMasterID = instance.BillwiseMasterID
        VoucherType = instance.VoucherType
        
        InvoiceAmount = instance.InvoiceAmount
        Payments = instance.Payments
        # AmountDue = converted_float(
        #     InvoiceAmount) - converted_float(Payments)
        AmountDue = 0
        if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
            details = BillWiseDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID)
            payment_sum = details.aggregate(Sum("Payments"))
            payment_sum = payment_sum["Payments__sum"]
            AmountDue = converted_float(
                InvoiceAmount) - converted_float(payment_sum)
        if call_type == "update":
            if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=PaymentVoucherNo, PaymentVoucherType=PaymentVoucherType).exists():
                billwise_detail_ins = BillWiseDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=PaymentVoucherNo, PaymentVoucherType=PaymentVoucherType)
                
                # Amount = billwise_detail_ins.Payments
                Amount = billwise_detail_ins.aggregate(Sum('Payments'))
                Amount = Amount["Payments__sum"]
                AmountDue = converted_float(
                    InvoiceAmount) - (converted_float(payment_sum) - converted_float(Amount))
                
            
        # if PaymentVoucherType == "CR" or PaymentVoucherType == "BR":
        #     if VoucherType == "PI" or VoucherType == "PR":
        #         AmountDue = converted_float(AmountDue) * -1
        return converted_float(AmountDue)
    
    def get_Amount(self, instance):
        CompanyID = self.context.get("CompanyID")
        PaymentVoucherNo = self.context.get("PaymentVoucherNo")
        PaymentVoucherType = self.context.get("PaymentVoucherType")
        BranchID = instance.BranchID
        BillwiseMasterID = instance.BillwiseMasterID
        Amount = 0
        if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=PaymentVoucherNo, PaymentVoucherType=PaymentVoucherType).exists():
            billwise_detail_ins = BillWiseDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=PaymentVoucherNo, PaymentVoucherType=PaymentVoucherType).first()
            Amount = billwise_detail_ins.Payments
        return converted_float(Amount)
    
    def get_full_amt(self, instance):
        CompanyID = self.context.get("CompanyID")
        PaymentVoucherNo = self.context.get("PaymentVoucherNo")
        PaymentVoucherType = self.context.get("PaymentVoucherType")
        BranchID = instance.BranchID
        BillwiseMasterID = instance.BillwiseMasterID
        full_amt = False
        InvoiceAmount = instance.InvoiceAmount
        Amount = 0
        if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=PaymentVoucherNo, PaymentVoucherType=PaymentVoucherType).exists():
            billwise_detail_ins = BillWiseDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=PaymentVoucherNo, PaymentVoucherType=PaymentVoucherType).first()
            Amount = billwise_detail_ins.Payments
        if converted_float(InvoiceAmount) == converted_float(Amount):
            full_amt = True
        return full_amt
    
    def get_show_negative(self, instance):
        PaymentVoucherType = self.context.get("PaymentVoucherType")
        VoucherType = instance.VoucherType
        show_negative = False
        if PaymentVoucherType == "CR" or PaymentVoucherType == "BR":
            if VoucherType == "PI" or VoucherType == "SR":
                show_negative = True
        elif PaymentVoucherType == "CP" or PaymentVoucherType == "BP":
            if VoucherType == "SI" or VoucherType == "PR":
                show_negative = True
        return show_negative


class BillwiseDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = BillWiseDetails
        fields = '__all__'

 
class PaymentDetailsListSerializer(serializers.ModelSerializer):
    Amount = serializers.SerializerMethodField()
    Discount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    PaymentGatewayName = serializers.SerializerMethodField()
    CardNetworkName = serializers.SerializerMethodField()
    PaymentStatusName = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    LedgerList_detail = serializers.SerializerMethodField()
    LedgerIDVal = serializers.SerializerMethodField()
    MasterUid = serializers.SerializerMethodField()
    MasterVoucherNo = serializers.SerializerMethodField()
    Masterdate = serializers.SerializerMethodField()
    MasterLedgerName = serializers.SerializerMethodField()
    MasterVoucherType = serializers.SerializerMethodField()
    MasterNotes = serializers.SerializerMethodField()

    class Meta:
        model = PaymentDetails
        fields = ('id',
                  'PaymentDetailsID',
                  'BranchID', 'Action',
                  'PaymentMasterID',
                  'PaymentGateway',
                  'RefferenceNo',
                  'CardNetwork',
                  'PaymentStatus',
                  'DueDate',
                  'LedgerID',
                  'Amount',
                  'Balance',
                  'Discount',
                  'NetAmount',
                  'Narration',
                  'CreatedDate',
                  'UpdatedDate',
                  'CreatedUserID',
                  'PaymentGatewayName',
                  'CardNetworkName',
                  'PaymentStatusName',
                  'LedgerName',
                  'detailID',
                  'LedgerList_detail',
                  'LedgerIDVal',
                  'MasterUid',
                  'MasterVoucherNo',
                  'Masterdate',
                  'MasterLedgerName',
                  'MasterVoucherType',
                  'MasterNotes'
                  )

    def get_MasterUid(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = payments_details.PaymentMasterID
        BranchID = payments_details.BranchID
        MasterUid = PaymentMaster.objects.filter(
            CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID).first().id
        return str(MasterUid)

    def get_MasterVoucherNo(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = payments_details.PaymentMasterID
        BranchID = payments_details.BranchID
        MasterVoucherNo = PaymentMaster.objects.filter(
            CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID).first().VoucherNo
        return str(MasterVoucherNo)

    def get_Masterdate(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = payments_details.PaymentMasterID
        BranchID = payments_details.BranchID
        Masterdate = PaymentMaster.objects.filter(
            CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID).first().Date
        return str(Masterdate)

    def get_MasterLedgerName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = payments_details.PaymentMasterID
        BranchID = payments_details.BranchID
        MasterLedgerName = ""
        Ledger = PaymentMaster.objects.filter(
            CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID).first().LedgerID
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Ledger).exists():
            MasterLedgerName = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=Ledger).LedgerName
        return str(MasterLedgerName)

    def get_MasterVoucherType(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = payments_details.PaymentMasterID
        BranchID = payments_details.BranchID
        MasterVoucherType = PaymentMaster.objects.filter(
            CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID).first().VoucherType
        return str(MasterVoucherType)

    def get_MasterNotes(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = payments_details.PaymentMasterID
        BranchID = payments_details.BranchID
        MasterNotes = PaymentMaster.objects.filter(
            CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID).first().Notes
        return str(MasterNotes)

    def get_detailID(self, payments_details):
        detailID = 0
        return detailID

    def get_LedgerIDVal(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        LedgerID = payments_details.LedgerID
        LedgerIDVal = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            LedgerIDVal = AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID).first().LedgerName
        return LedgerIDVal

    def get_LedgerList_detail(self, journal_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = journal_details.BranchID
        LedgerName = ""
        LedgerID = journal_details.LedgerID
        LedgerList_detail = []
        if AccountLedger.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            ledger = AccountLedger.objects.get(
                LedgerID=LedgerID, CompanyID=CompanyID)
            LedgerName = ledger.LedgerName

        LedgerList_detail.append(
            {"LedgerName": LedgerName, "LedgerID": LedgerID})
        return LedgerList_detail

    def get_Amount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))

        Amount = payments_details.Amount

        # Amount = round(Amount,PriceRounding)

        return converted_float(Amount)

    def get_Balance(self, payments_details):

        Balance = payments_details.Balance

        Balance = round(Balance, 2)

        return converted_float(Balance)

    def get_Discount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))

        Discount = payments_details.Discount

        # Discount = round(Discount,PriceRounding)

        return converted_float(Discount)

    def get_NetAmount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))

        NetAmount = payments_details.NetAmount

        # NetAmount = round(NetAmount,PriceRounding)

        return converted_float(NetAmount)

    def get_PaymentGatewayName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")
        PaymentGateway = payments_details.PaymentGateway
        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=PaymentGateway).exists():
            PaymentGateway = TransactionTypes.objects.get(
                CompanyID=CompanyID, TransactionTypesID=PaymentGateway).Name
        else:
            PaymentGateway = ""
        return str(PaymentGateway)

    def get_CardNetworkName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        CardNetwork = payments_details.CardNetwork
        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=CardNetwork).exists():
            CardNetwork = TransactionTypes.objects.get(
                CompanyID=CompanyID, TransactionTypesID=CardNetwork).Name
        else:
            CardNetwork = ""
        return str(CardNetwork)

    def get_PaymentStatusName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        PaymentStatus = payments_details.PaymentStatus
        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=PaymentStatus).exists():
            PaymentStatus = TransactionTypes.objects.get(
                CompanyID=CompanyID, TransactionTypesID=PaymentStatus).Name
        else:
            PaymentStatus = ""
        return str(PaymentStatus)

    def get_LedgerName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        Ledger = payments_details.LedgerID
        BranchID = payments_details.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Ledger).exists():
            Ledger = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=Ledger).LedgerName
        else:
            Ledger = ""
        return str(Ledger)
