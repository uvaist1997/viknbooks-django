from rest_framework import serializers
from brands.models import ReceiptDetails, ReceiptDetailsDummy, AccountLedger, TransactionTypes


class ReceiptDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReceiptDetails
        fields = ('id','BranchID','ReceiptMasterID','OldVoucherMasterID','LedgerID','Date',
        	'Amount','Discount','Narration')


class ReceiptDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReceiptDetails
        fields = ('id','ReceiptDetailID','BranchID','Action','ReceiptMasterID','OldVoucherMasterID','LedgerID','Date',
        	'Amount','Discount','Narration')


class ReceiptDetailsDummySerializer(serializers.ModelSerializer):

    Amount = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    Discount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    PaymentGatewayName = serializers.SerializerMethodField()
    CardNetworkName = serializers.SerializerMethodField()
    PaymentStatusName = serializers.SerializerMethodField()


    class Meta:
        model = ReceiptDetailsDummy
        fields = ('id','BranchID','ReceiptMasterID','PaymentGateway','PaymentGatewayName','RefferenceNo',
            'CardNetwork','CardNetworkName','PaymentStatusName','PaymentStatus','LedgerID','LedgerName','DueDate','Amount','Discount','NetAmount','Balance','Narration','CreatedUserID','detailID')


    def get_Amount(self, instances):


        Amount = instances.Amount

        Amount = round(Amount,2)

        return str(Amount)


    def get_LedgerName(self, instances):

        DataBase = self.context.get("DataBase")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(LedgerID=LedgerID,BranchID=BranchID)

        LedgerName = ledger.LedgerName

        return LedgerName


    def get_PaymentGatewayName(self, instances):

        transType = None

        PaymentGateway = instances.PaymentGateway
        BranchID = instances.BranchID
        try:
            transType = TransactionTypes.objects.get(TransactionTypesID=PaymentGateway,BranchID=BranchID)
            PaymentGatewayName = transType.Name
        except:
            PaymentGatewayName = None
        

        return PaymentGatewayName


    def get_CardNetworkName(self, instances):

        transType = None

        CardNetwork = instances.CardNetwork
        BranchID = instances.BranchID
        try:
            transType = TransactionTypes.objects.get(TransactionTypesID=CardNetwork,BranchID=BranchID)
            CardNetworkName = transType.Name
        except:
            CardNetworkName = None
        

        return CardNetworkName


    def get_PaymentStatusName(self, instances):

        transType = None

        PaymentStatus = instances.PaymentStatus
        BranchID = instances.BranchID
        try:
            transType = TransactionTypes.objects.get(TransactionTypesID=PaymentStatus,BranchID=BranchID)
            PaymentStatusName = transType.Name
        except:
            PaymentStatusName = None
        
        return PaymentStatusName


    def get_Balance(self, instances):


        Balance = int(instances.Balance)

        Balance = round(Balance,2)

        return str(Balance)


    def get_Discount(self, instances):


        Discount = instances.Discount

        Discount = round(Discount,2)

        return str(Discount)


    def get_NetAmount(self, instances):


        NetAmount = instances.NetAmount

        NetAmount = round(NetAmount,2)

        return str(NetAmount)