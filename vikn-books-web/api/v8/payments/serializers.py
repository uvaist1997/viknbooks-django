from rest_framework import serializers
from brands.models import Parties,PaymentMaster, PaymentDetails, AccountLedger, TransactionTypes


class PaymentMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMaster
        fields = ('id','BranchID','VoucherNo','VoucherType','LedgerID',
            'EmployeeID','PaymentNo',
            'FinancialYearID','Date','TotalAmount','Notes','IsActive','CreatedUserID')


class PaymentMasterRestSerializer(serializers.ModelSerializer):

    PaymentDetails = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalAmount = serializers.SerializerMethodField()
    TotalAmount_rounded = serializers.SerializerMethodField()
    selected_ledgers = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMaster
        fields = ('id','PaymentMasterID','BranchID','Action','VoucherNo','VoucherType','LedgerID','LedgerName',
            'EmployeeID','PaymentNo','TotalAmount_rounded','selected_ledgers',
            'FinancialYearID','Date','TotalAmount','Notes','IsActive','CreatedDate','UpdatedDate','CreatedUserID','PaymentDetails')


    def get_PaymentDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        VoucherType = instances.VoucherType
        payments_details = PaymentDetails.objects.filter(CompanyID=CompanyID,PaymentMasterID=instances.PaymentMasterID,BranchID=instances.BranchID,VoucherType=VoucherType).order_by('PaymentDetailsID')
        serialized = PaymentDetailsRestSerializer(payments_details,many=True,context = {"CompanyID": CompanyID,"PriceRounding":PriceRounding })

        return serialized.data 


    def get_selected_ledgers(self, instances):
        CompanyID = self.context.get("CompanyID")
        payment_details = PaymentDetails.objects.filter(PaymentMasterID=instances.PaymentMasterID,BranchID=instances.BranchID,CompanyID=CompanyID)
        selected_ledgers = payment_details.values_list('LedgerID',flat=True)
        return selected_ledgers


    def get_LedgerName(self, instances):

        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID)
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

        TotalAmount_rounded = round(TotalAmount_rounded,PriceRounding)

        return str(TotalAmount_rounded)



class PaymentDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentDetails
        fields = ('id','BranchID','PaymentMasterID','PaymentGateway','RefferenceNo',
            'CardNetwork','PaymentStatus','DueDate','LedgerID','Amount','Balance','Discount','NetAmount','Narration','CreatedUserID')


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

    class Meta:
        model = PaymentDetails
        fields = ('id',
            'PaymentDetailsID',
            'BranchID','Action',
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
            )


    def get_detailID(self, payments_details):

        detailID = 0
        return detailID

    def get_LedgerList_detail(self, journal_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = journal_details.BranchID
        LedgerName = ""
        LedgerID = journal_details.LedgerID
        LedgerList_detail = []
        if AccountLedger.objects.filter(LedgerID=LedgerID,BranchID=BranchID,CompanyID=CompanyID).exists():
            ledger = AccountLedger.objects.get(LedgerID=LedgerID,BranchID=BranchID,CompanyID=CompanyID)
            LedgerName = ledger.LedgerName

        LedgerList_detail.append({"LedgerName" : LedgerName, "LedgerID" : LedgerID})
        return LedgerList_detail


    def get_Amount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))

        Amount = payments_details.Amount

        # Amount = round(Amount,PriceRounding)

        return float(Amount)


    def get_Balance(self, payments_details):

        Balance = payments_details.Balance

        Balance = round(Balance,2)

        return float(Balance)


    def get_Discount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))

        Discount = payments_details.Discount

        # Discount = round(Discount,PriceRounding)

        return float(Discount)


    def get_NetAmount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))

        NetAmount = payments_details.NetAmount

        # NetAmount = round(NetAmount,PriceRounding)

        return float(NetAmount)

    def get_PaymentGatewayName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")
        PaymentGateway = payments_details.PaymentGateway
        if TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=PaymentGateway).exists():
            PaymentGateway = TransactionTypes.objects.get(CompanyID=CompanyID,TransactionTypesID=PaymentGateway).Name
        else:
            PaymentGateway = ""
        return str(PaymentGateway)

    def get_CardNetworkName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        CardNetwork = payments_details.CardNetwork
        if TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=CardNetwork).exists():
            CardNetwork = TransactionTypes.objects.get(CompanyID=CompanyID,TransactionTypesID=CardNetwork).Name
        else:
            CardNetwork = ""
        return str(CardNetwork)

    def get_PaymentStatusName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        PaymentStatus = payments_details.PaymentStatus
        if TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=PaymentStatus).exists():
            PaymentStatus = TransactionTypes.objects.get(CompanyID=CompanyID,TransactionTypesID=PaymentStatus).Name
        else:
            PaymentStatus = ""
        return str(PaymentStatus)

    def get_LedgerName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        Ledger = payments_details.LedgerID
        BranchID = payments_details.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=Ledger,BranchID=BranchID).exists():
            Ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=Ledger,BranchID=BranchID).LedgerName
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
            'Date','Notes',
            'VoucherDetails',
            'TaxNo',
            'PhoneNo',
            'CustomerCRNo',
            'DisplayName')


    def get_VoucherDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        VoucherType = instances.VoucherType
        payments_details = PaymentDetails.objects.filter(CompanyID=CompanyID,PaymentMasterID=instances.PaymentMasterID,BranchID=instances.BranchID,VoucherType=VoucherType).order_by('PaymentDetailsID')
        serialized = PaymentDetailsPrintSerializer(payments_details,many=True,context = {"CompanyID": CompanyID,"PriceRounding":PriceRounding })
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
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID)
            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""
        return LedgerName


    def get_TotalAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalAmount = instances.TotalAmount
        TotalAmount = round(TotalAmount,PriceRounding)
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
        Amount = round(Amount,PriceRounding)
        return float(Amount)

    def get_Discount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Discount = payments_details.Discount
        Discount = round(Discount,PriceRounding)
        return float(Discount)


    def get_NetAmount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = payments_details.NetAmount
        NetAmount = round(NetAmount,PriceRounding)
        return float(NetAmount)


    def get_LedgerName(self, payments_details):
        CompanyID = self.context.get("CompanyID")
        Ledger = payments_details.LedgerID
        BranchID = payments_details.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=Ledger,BranchID=BranchID).exists():
            Ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=Ledger,BranchID=BranchID).LedgerName
        else:
            Ledger = ""
        return str(Ledger)