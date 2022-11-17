from rest_framework import serializers
from brands.models import JournalDetails, JournalDetailsDummy, AccountLedger


class JournalDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = JournalDetails
        fields = ('id','BranchID','JournalMasterID','LedgerID','Debit','Credit','Narration','Action','CreatedDate','CreatedUserID')


class JournalDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = JournalDetails
        fields = ('id','JournalDetailsID','BranchID','JournalMasterID','LedgerID','Debit','Credit','Narration','Action','CreatedDate','CreatedUserID')


class JournalDetailsDummySerializer(serializers.ModelSerializer):

    LedgerName = serializers.SerializerMethodField()
    Debit = serializers.SerializerMethodField()
    Credit = serializers.SerializerMethodField()

    class Meta:
        model = JournalDetailsDummy
        fields = ('id','JournalDetailsID','BranchID','LedgerID','LedgerName','Debit','Credit','Narration','detailID')


    def get_LedgerName(self, instance):

        DataBase = self.context.get("DataBase")

        LedgerID = instance.LedgerID
        BranchID = instance.BranchID

        ledger = AccountLedger.objects.get(LedgerID=LedgerID,BranchID=BranchID)

        LedgerName = ledger.LedgerName

        return LedgerName


    def get_Debit(self, instance):

        Debit = instance.Debit

        Debit = round(Debit,2)

        return str(Debit)


    def get_Credit(self, instance):

        Credit = instance.Credit

        Credit = round(Credit,2)

        return str(Credit)