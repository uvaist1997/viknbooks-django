from rest_framework import serializers
from brands import models
from rest_framework.fields import CurrentUserDefault


class WorkingTimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.WorkingTime
        fields = ("Name", "ShiftStartTime", "ShiftEndTime", "BreakStartTime", "BreakEndTime",)
    

class WorkingTimeRestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkingTime
        fields = ('id','BranchID',"Name", "ShiftStartTime", "ShiftEndTime", "BreakStartTime", "BreakEndTime",'CreatedUserID','CreatedDate','UpdatedDate','Action')


class ListSerializer(serializers.Serializer):
    BranchID = serializers.IntegerField()

