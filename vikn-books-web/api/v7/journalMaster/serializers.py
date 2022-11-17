from rest_framework import serializers
from brands.models import JournalMaster


class JournalMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = JournalMaster
        fields = ('id','BranchID','VoucherNo','Date','Notes',
            'TotalDebit','TotalCredit','Difference','IsActive','Action','CreatedDate','CreatedUserID')


class JournalMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = JournalMaster
        fields = ('id','JournalMasterID','BranchID','VoucherNo','Date','Notes',
            'TotalDebit','TotalCredit','Difference','IsActive','Action','CreatedDate','CreatedUserID')
