from rest_framework import serializers
from brands import models



class CustomerSerializer(serializers.ModelSerializer):

    Balance = serializers.SerializerMethodField()
    PartyImage = serializers.SerializerMethodField()

    class Meta:
        model = models.Parties
        fields = ('id','PartyName','LedgerID','OpeningBalance','Balance','PartyImage','PartyImage')


    def get_Balance(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        Debit = 0
        Credit = 0
        ledger_posting_instances = models.LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID)
        for i in ledger_posting_instances:
            Debit += float(i.Debit)
            Credit += float(i.Credit)
        Balance = float(Debit) - float(Credit)
        return Balance

    def get_PartyImage(self, instances):
        PartyImage = ''
        if instances.PartyImage:
            PartyImage = instances.PartyImage.url
        return PartyImage

class SupplierSerializer(serializers.ModelSerializer):

    Balance = serializers.SerializerMethodField()
    PartyImage = serializers.SerializerMethodField()

    class Meta:
        model = models.Parties
        fields = ('id','PartyName','LedgerID','OpeningBalance','Balance','PartyImage')


    def get_Balance(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        Debit = 0
        Credit = 0
        ledger_posting_instances = models.LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID)
        for i in ledger_posting_instances:
            Debit += float(i.Debit)
            Credit += float(i.Credit)
        Balance = float(Debit) - float(Credit)
        return Balance

    def get_PartyImage(self, instances):
        PartyImage = ''
        if instances.PartyImage:
            PartyImage = instances.PartyImage.url
        return PartyImage


class BankSerializer(serializers.ModelSerializer):

    Balance = serializers.SerializerMethodField()

    class Meta:
        model = models.AccountLedger
        fields = ('id','OpeningBalance','Balance','LedgerName')


    # def get_Balance(self, instances):
    #     CompanyID = self.context.get("CompanyID")
    #     BranchID = self.context.get("BranchID")
    #     Debit = 0
    #     Credit = 0
    #     Balance = 0
    #     LedgerID = []
    #     account_ledger_instances = models.AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerCode=instances.LedgerCode)
    #     for i in account_ledger_instances:
    #         ledger_posting_instances = models.LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=i.LedgerID)
    #         for j in ledger_posting_instances:
    #             Debit += float(j.Debit)
    #             Credit += float(j.Credit)
    #         Balance = float(Debit) - float(Credit)
    #     return str(Balance)

    def get_Balance(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = self.context.get("BranchID")
        Debit = 0
        Credit = 0
        Balance = 0
        LedgerID = []
        ledger_posting_instances = models.LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=instances.LedgerID)
        for i in ledger_posting_instances:
            Debit += float(i.Debit)
            Credit += float(i.Credit)
        Balance = float(Debit) - float(Credit)
        return str(Balance)