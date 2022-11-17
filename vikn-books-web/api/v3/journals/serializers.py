from rest_framework import serializers
from brands.models import JournalMaster, JournalDetails, AccountLedger


class JournalMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = JournalMaster
        fields = ('id','BranchID','VoucherNo','Date','Notes',
            'TotalDebit','TotalCredit','Difference','IsActive','Action','CreatedDate','CreatedUserID')


class JournalMasterRestSerializer(serializers.ModelSerializer):

    JournalDetails = serializers.SerializerMethodField()
    TotalDebit = serializers.SerializerMethodField()
    TotalCredit = serializers.SerializerMethodField()
    Difference = serializers.SerializerMethodField()

    class Meta:
        model = JournalMaster
        fields = ('id','JournalMasterID','BranchID','VoucherNo','Date','Notes',
            'TotalDebit','TotalCredit','Difference','IsActive','Action','CreatedDate','CreatedUserID','JournalDetails')


    def get_JournalDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        journal_details = JournalDetails.objects.filter(JournalMasterID=instances.JournalMasterID,BranchID=instances.BranchID,CompanyID=CompanyID)
        serialized = JournalDetailsRestSerializer(journal_details,many=True,context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding, "BranchID" : instances.BranchID })

        return serialized.data


    def get_TotalDebit(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDebit = instances.TotalDebit

        TotalDebit = round(TotalDebit,PriceRounding)

        return str(TotalDebit)


    def get_TotalCredit(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalCredit = instances.TotalCredit

        TotalCredit = round(TotalCredit,PriceRounding)

        return str(TotalCredit)


    def get_Difference(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        Difference = instances.Difference

        Difference = round(Difference,PriceRounding)

        return str(Difference)



class JournalDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = JournalDetails
        fields = ('id','BranchID','JournalMasterID','LedgerID','Debit','Credit','Narration','Action','CreatedDate','CreatedUserID')


class JournalDetailsRestSerializer(serializers.ModelSerializer):

    Debit = serializers.SerializerMethodField()
    Credit = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()

    class Meta:
        model = JournalDetails
        fields = ('id','JournalDetailsID','BranchID','JournalMasterID','LedgerID','LedgerName','Debit','Credit','Narration','Action','CreatedDate','CreatedUserID',
            'detailID')


    def get_Debit(self, journal_details):
        PriceRounding = self.context.get("PriceRounding")
        Debit = journal_details.Debit

        Debit = round(Debit,PriceRounding)

        return str(Debit)


    def get_Credit(self, journal_details):
        PriceRounding = self.context.get("PriceRounding")
        Credit = journal_details.Credit

        Credit = round(Credit,PriceRounding)

        return str(Credit)


    def get_LedgerName(self, journal_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = self.context.get("BranchID")
        LedgerName = ""
        LedgerID = journal_details.LedgerID
        if AccountLedger.objects.filter(LedgerID=LedgerID,BranchID=BranchID,CompanyID=CompanyID).exists():
            ledger = AccountLedger.objects.get(LedgerID=LedgerID,BranchID=BranchID,CompanyID=CompanyID)

            LedgerName = ledger.LedgerName

        return LedgerName


    def get_detailID(self, journal_details):
        detailID = 0
        return detailID