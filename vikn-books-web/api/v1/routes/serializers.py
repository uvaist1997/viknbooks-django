from rest_framework import serializers
from brands.models import Route


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ('id','BranchID','RouteName','Notes','CreatedUserID')


class RouteRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ('id','RouteID','BranchID','RouteName','Notes','CreatedUserID','CreatedDate','UpdatedDate','Action',)
