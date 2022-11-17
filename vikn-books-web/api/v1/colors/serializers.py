from rest_framework import serializers
from brands.models import Color, TestImage,ProductDemo
from inventories.models import TaskFormReact, TaskFormSetReact


class ProductDemoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductDemo
        fields = ('id','rate','name','description')

class ProductDemoRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductDemo
        fields = ('id','image','rate','name','description')


class ColorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Color
        fields = ('id','ColorName','ColorValue')


class ColorRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Color
        fields = ('id','ColorID','ColorName','ColorValue','Action')


class TestImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestImage
        fields = ('id','Name','Image')



class TaskFormReactSerializer(serializers.ModelSerializer):

    TaskFormSetReact = serializers.SerializerMethodField()
    Date = serializers.DateTimeField(format='%d%m%Y')

    class Meta:
        model = TaskFormReact
        fields = ('id','Date','Description','TaskFormSetReact')


    def get_TaskFormSetReact(self, instance):
        taskFormid = instance.id
        CompanyID = self.context.get("CompanyID")
        tskfrmst = TaskFormSetReact.objects.filter(taskFormId=taskFormid,CompanyID=CompanyID)
  
        serialized = TaskFormSetReactSerializer(tskfrmst,many=True,)

        return serialized.data


class TaskFormSetReactSerializer(serializers.ModelSerializer):

    detailID = serializers.SerializerMethodField()

    class Meta:
        model = TaskFormSetReact
        fields = ('id','projectName','task','taskNotes','taskStatus','taskFormId','detailID')



    def get_detailID(self, instance):
        

        return 0

