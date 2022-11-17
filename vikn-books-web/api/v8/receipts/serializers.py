from rest_framework import serializers
from brands.models import Parties,ReceiptMaster, ReceiptDetails, AccountLedger, TransactionTypes


class ReceiptMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReceiptMaster
        fields = ('id','BranchID','VoucherNo','VoucherType','ReceiptNo','LedgerID',
            'EmployeeID','FinancialYearID','Date',
            'TotalAmount','Notes','IsActive','CreatedUserID')


class ReceiptMasterRestSerializer(serializers.ModelSerializer):

    ReceiptDetails = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalAmount = serializers.SerializerMethodField()
    selected_ledgers = serializers.SerializerMethodField()

    class Meta:
        model = ReceiptMaster
        fields = (
            'id',
            'ReceiptMasterID',
            'BranchID','Action',
            'VoucherNo',
            'VoucherType',
            'ReceiptNo',
            'LedgerID',
            'LedgerName',
            'EmployeeID',
            'FinancialYearID',
            'Date',
            'TotalAmount',
            'Notes',
            'IsActive',
            'CreatedDate',
            'UpdatedDate',
            'CreatedUserID',
            'ReceiptDetails',
            'selected_ledgers',
            )


    def get_ReceiptDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        VoucherType = instances.VoucherType
        receipt_details = ReceiptDetails.objects.filter(CompanyID=CompanyID,ReceiptMasterID=instances.ReceiptMasterID,BranchID=instances.BranchID,VoucherType=VoucherType).order_by('ReceiptDetailID')
        serialized = ReceiptDetailsRestSerializer(receipt_details,many=True,context = {"CompanyID": CompanyID })

        return serialized.data 


    def get_selected_ledgers(self, instances):
        CompanyID = self.context.get("CompanyID")
        receipt_details = ReceiptDetails.objects.filter(ReceiptMasterID=instances.ReceiptMasterID,BranchID=instances.BranchID,CompanyID=CompanyID)
        selected_ledgers = receipt_details.values_list('LedgerID',flat=True)
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

        TotalAmount = instances.TotalAmount

        # TotalAmount = round(TotalAmount,2)

        return str(TotalAmount)

    # def get_PaymentGatewayName(self, instances):
    #     print(instances.objects.all())
    #     print("hello1234")
    #     TotalAmount = instances.TotalAmount

    #     TotalAmount = round(TotalAmount,2)

    #     return str(TotalAmount)

    # def get_CardNetworkName(self, instances):

    #     TotalAmount = instances.TotalAmount

    #     TotalAmount = round(TotalAmount,2)

    #     return str(TotalAmount)

    # def get_PaymentStatusName(self, instances):

    #     TotalAmount = instances.TotalAmount

    #     TotalAmount = round(TotalAmount,2)

    #     return str(TotalAmount)


class ReceiptDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReceiptDetails
        fields = ('id','BranchID','ReceiptMasterID','VoucherType','PaymentGateway','RefferenceNo',
            'CardNetwork','PaymentStatus','LedgerID','DueDate','Amount','Discount','NetAmount','Balance','Narration','CreatedUserID')


class ReceiptDetailsRestSerializer(serializers.ModelSerializer):
    Amount = serializers.SerializerMethodField()
    Discount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    PaymentGatewayName = serializers.SerializerMethodField()
    CardNetworkName = serializers.SerializerMethodField()
    PaymentStatusName = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    LedgerList_detail = serializers.SerializerMethodField()

    class Meta:
        model = ReceiptDetails
        fields = (
            'id',
            'ReceiptDetailID',
            'BranchID',
            'Action',
            'ReceiptMasterID',
            'VoucherType',
            'PaymentGateway',
            'RefferenceNo',
            'CardNetwork',
            'PaymentStatus',
            'LedgerID',
            'DueDate',
            'Amount',
            'Discount',
            'NetAmount',
            'Balance',
            'Narration',
            'CreatedDate',
            'CreatedUserID',
            'PaymentGatewayName',
            'CardNetworkName',
            'PaymentStatusName',
            'LedgerName',
            'detailID',
            'LedgerList_detail'
            )


    def get_Amount(self, receipt_details):

        Amount = receipt_details.Amount

        # Amount = round(Amount,2)

        return float(Amount)


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


    def get_Balance(self, receipt_details):

        Balance = receipt_details.Balance

        # Balance = round(Balance,2)

        return float(Balance)


    def get_detailID(self, receipt_details):
        detailID = 0
        return detailID


    def get_Discount(self, receipt_details):

        Discount = receipt_details.Discount

        # Discount = round(Discount,2)

        return float(Discount)


    def get_NetAmount(self, receipt_details):

        NetAmount = receipt_details.NetAmount

        # NetAmount = round(NetAmount,2)

        return float(NetAmount)

    def get_PaymentGatewayName(self, receipt_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        PaymentGateway = receipt_details.PaymentGateway
        if TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=PaymentGateway).exists():
            PaymentGateway = TransactionTypes.objects.get(CompanyID=CompanyID,TransactionTypesID=PaymentGateway).Name
        else:
            PaymentGateway = ""
        return str(PaymentGateway)

    def get_CardNetworkName(self, receipt_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        CardNetwork = receipt_details.CardNetwork
        if TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=CardNetwork).exists():
            CardNetwork = TransactionTypes.objects.get(CompanyID=CompanyID,TransactionTypesID=CardNetwork).Name
        else:
            CardNetwork = ""
        return str(CardNetwork)

    def get_PaymentStatusName(self, receipt_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        PaymentStatus = receipt_details.PaymentStatus
        if TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=PaymentStatus).exists():
            PaymentStatus = TransactionTypes.objects.get(CompanyID=CompanyID,TransactionTypesID=PaymentStatus).Name
        else:
            PaymentStatus = ""
        return str(PaymentStatus)

    def get_LedgerName(self, receipt_details):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = self.context.get("CreatedUserID")

        Ledger = receipt_details.LedgerID
        BranchID = receipt_details.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=Ledger,BranchID=BranchID).exists():
            Ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=Ledger,BranchID=BranchID).LedgerName
        else:
            Ledger = ""
        return str(Ledger)



class ReceiptPrintSerializer(serializers.ModelSerializer):
    VoucherDetails = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalAmount = serializers.SerializerMethodField()
    TotalAmount = serializers.SerializerMethodField()
    TaxNo = serializers.SerializerMethodField()
    PhoneNo = serializers.SerializerMethodField()
    CustomerCRNo = serializers.SerializerMethodField()
    DisplayName = serializers.SerializerMethodField()
    class Meta:
        model = ReceiptMaster
        fields = (
            'id',
            'VoucherNo',
            'LedgerName',
            'Date',
            'TotalAmount',
            'Notes',
            'VoucherDetails',
            'TaxNo',
            'PhoneNo',
            'CustomerCRNo',
            'DisplayName'
            )


    def get_VoucherDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        VoucherType = instances.VoucherType
        receipt_details = ReceiptDetails.objects.filter(CompanyID=CompanyID,ReceiptMasterID=instances.ReceiptMasterID,BranchID=instances.BranchID,VoucherType=VoucherType).order_by('ReceiptDetailID')
        serialized = ReceiptDetailsPrintSerializer(receipt_details,many=True,context = {"CompanyID": CompanyID })
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
        TotalAmount = instances.TotalAmount
        TotalAmount = round(TotalAmount,2)
        return str(TotalAmount)


    
class ReceiptDetailsPrintSerializer(serializers.ModelSerializer):
    Amount = serializers.SerializerMethodField()
    Discount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()

    class Meta:
        model = ReceiptDetails
        fields = (
            'id',
            'Amount',
            'Discount',
            'NetAmount',
            'Narration',
            'LedgerName'
            )


    def get_Amount(self, receipt_details):
        Amount = receipt_details.Amount
        Amount = round(Amount,2)
        return float(Amount)

    def get_Discount(self, receipt_details):
        Discount = receipt_details.Discount
        Discount = round(Discount,2)
        return float(Discount)


    def get_NetAmount(self, receipt_details):
        NetAmount = receipt_details.NetAmount
        NetAmount = round(NetAmount,2)
        return float(NetAmount)

    def get_LedgerName(self, receipt_details):
        CompanyID = self.context.get("CompanyID")
        Ledger = receipt_details.LedgerID
        BranchID = receipt_details.BranchID
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=Ledger,BranchID=BranchID).exists():
            Ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=Ledger,BranchID=BranchID).LedgerName
        else:
            Ledger = ""
        return str(Ledger)