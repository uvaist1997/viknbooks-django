from rest_framework import serializers
from brands.models import MasterType


class MasterTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = MasterType
        fields = ('id','BranchID','Name','Description','CreatedUserID','CreatedDate','IsDefault')


class MasterTypeRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = MasterType
        fields = ('id','MasterTypeID','BranchID','Name','Description','CreatedUserID','CreatedDate','Action','IsDefault')
