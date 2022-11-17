from rest_framework import serializers
from brands.models import PaymentDetails, PaymentDetailsDummy, AccountLedger, TransactionTypes


class PaymentDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentDetails
        fields = ('id','BranchID','PaymentMasterID','PaymentGateway','RefferenceNo',
            'CardNetwork','PaymentStatus','DueDate','LedgerID','Amount','Balance','Discount','NetAmount','Narration','CreatedUserID')


class PaymentDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentDetails
        fields = ('id','PaymentDetailsID','BranchID','Action','PaymentMasterID','PaymentGateway','RefferenceNo',
            'CardNetwork','PaymentStatus','DueDate','LedgerID','Amount','Balance','Discount','NetAmount','Narration','CreatedDate','CreatedUserID')


class PaymentDetailsDummySerializer(serializers.ModelSerializer):

    Amount = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    Discount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    PaymentGatewayName = serializers.SerializerMethodField()
    CardNetworkName = serializers.SerializerMethodField()
    PaymentStatusName = serializers.SerializerMethodField()


    class Meta:
        model = PaymentDetailsDummy
        fields = ('id','BranchID','PaymentMasterID','PaymentGateway','PaymentGatewayName','RefferenceNo',
            'CardNetwork','CardNetworkName','PaymentStatus','PaymentStatusName','DueDate','LedgerID','LedgerName','Amount','Balance','Discount','NetAmount','Narration','CreatedUserID',
        	'detailID')


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

        DataBase = self.context.get("DataBase")

        PaymentGateway = instances.PaymentGateway
        BranchID = instances.BranchID
        try:
            transType = TransactionTypes.objects.get(TransactionTypesID=PaymentGateway,BranchID=BranchID)
            PaymentGatewayName = transType.Name
        except:
            PaymentGatewayName = None
        

        return PaymentGatewayName


    def get_CardNetworkName(self, instances):

        DataBase = self.context.get("DataBase")

        CardNetwork = instances.CardNetwork
        BranchID = instances.BranchID
        try:
            transType = TransactionTypes.objects.get(TransactionTypesID=CardNetwork,BranchID=BranchID)
            CardNetworkName = transType.Name
        except:
            CardNetworkName = None
        

        return CardNetworkName


    def get_PaymentStatusName(self, instances):

        DataBase = self.context.get("DataBase")

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

