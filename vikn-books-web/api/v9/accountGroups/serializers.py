from rest_framework import serializers

from brands.models import AccountGroup


class AccountGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGroup
        fields = (
            "id",
            "AccountGroupName",
            "GroupCode",
            "AccountGroupUnder",
            "Notes",
            "IsActive",
            "IsDefault",
        )


class AccountGroupRestSerializer(serializers.ModelSerializer):

    GroupUnderName = serializers.SerializerMethodField()

    class Meta:
        model = AccountGroup
        fields = (
            "id",
            "AccountGroupID",
            "AccountGroupName",
            "GroupCode",
            "AccountGroupUnder",
            "GroupUnderName",
            "Notes",
            "CreatedUserID",
            "CreatedDate",
            "UpdatedDate",
            "IsActive",
            "IsDefault",
            "Action",
        )

    def get_GroupUnderName(self, instances):
        CompanyID = self.context.get("CompanyID")
        AccountGroupUnder = instances.AccountGroupUnder

        GroupUnderName = AccountGroup.objects.get(
            CompanyID=CompanyID, AccountGroupID=AccountGroupUnder
        ).AccountGroupName

        return GroupUnderName
