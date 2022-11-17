from rest_framework import serializers
from brands.models import PaymentMaster, PaymentDetails, AccountLedger, TransactionTypes


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

    class Meta:
        model = PaymentMaster
        fields = ('id','PaymentMasterID','BranchID','Action','VoucherNo','VoucherType','LedgerID','LedgerName',
            'EmployeeID','PaymentNo',
            'FinancialYearID','Date','TotalAmount','Notes','IsActive','CreatedDate','UpdatedDate','CreatedUserID','PaymentDetails')


    def get_PaymentDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        payments_details = PaymentDetails.objects.filter(CompanyID=CompanyID,PaymentMasterID=instances.PaymentMasterID,BranchID=instances.BranchID)
        serialized = PaymentDetailsRestSerializer(payments_details,many=True,context = {"CompanyID": CompanyID,"PriceRounding":PriceRounding })

        return serialized.data 


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
            'detailID'
            )


    def get_detailID(self, payments_details):

        detailID = 0
        return detailID


    def get_Amount(self, payments_details):
        PriceRounding = int(self.context.get("PriceRounding"))

        Amount = payments_details.Amount

        Amount = round(Amount,PriceRounding)

        return float(Amount)


    def get_Balance(self, payments_details):

        Balance = payments_details.Balance

        Balance = round(Balance,2)

        return float(Balance)


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