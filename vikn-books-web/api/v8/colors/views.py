from brands.models import Color, Color_Log, TestImage
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.colors.serializers import ColorSerializer, ColorRestSerializer, TestImageSerializer, TaskFormReactSerializer
from api.v8.colors.functions import generate_serializer_errors
from rest_framework import status
from api.v8.colors.functions import get_auto_id
import datetime
import base64
from django.core.files.base import ContentFile
from main.functions import get_company


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_color(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = ColorSerializer(data=request.data)
    if serialized.is_valid():

        ColorName = serialized.data['ColorName']
        ColorValue = serialized.data['ColorValue']

        Action = "A"

        ColorID = get_auto_id(Color, CompanyID)

        Color.objects.create(
            ColorID=ColorID,
            ColorName=ColorName,
            ColorValue=ColorValue,
            Action=Action,
            CompanyID=CompanyID,
        )

        Color_Log.objects.create(
            ColorName=ColorName,
            TransactionID=ColorID,
            ColorValue=ColorValue,
            Action=Action,
            CompanyID=CompanyID,
        )

        data = {"ColorID": ColorID}
        data.update(serialized.data)
        response_data = {
            "StatusCode": 6000,
            "data": data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_color(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = ColorSerializer(data=request.data)
    instance = None
    if Color.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Color.objects.get(pk=pk, CompanyID=CompanyID)
    if instance:
        if serialized.is_valid():

            ColorName = serialized.data['ColorName']
            ColorValue = serialized.data['ColorValue']
            ColorID = instance.ColorID

            Action = "M"
            instance.Action = Action
            instance.save()
            serialized.update(instance, serialized.data)

            Color_Log.objects.create(
                ColorName=ColorName,
                TransactionID=ColorID,
                ColorValue=ColorValue,
                Action=Action,
                CompanyID=CompanyID,
            )

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors)
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Color Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def colors(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instances = Color.objects.filter(CompanyID=CompanyID)
    serialized = ColorRestSerializer(instances, many=True)
    response_data = {
        "StatusCode": 6000,
        "data": serialized.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def color(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Color.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Color.objects.get(pk=pk, CompanyID=CompanyID)
    if instance:
        serialized = ColorRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Color Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_color(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    if Color.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Color.objects.get(pk=pk, CompanyID=CompanyID)

        ColorName = instance.ColorName
        ColorID = instance.ColorID
        ColorValue = instance.ColorValue
        Action = "D"

        instance.delete()
        Color_Log.objects.create(
            ColorName=ColorName,
            TransactionID=ColorID,
            ColorValue=ColorValue,
            Action=Action,
            CompanyID=CompanyID
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Color Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Color Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_testImage(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = TestImageSerializer(
        data=request.data, context={"request": request})
    if serialized.is_valid():

        Name = serialized.data['Name']
        Image = data['Image']
        TestImage.objects.create(
            Name=Name,
            Image=Image,
            CompanyID=CompanyID,
        )
        # serialized.save(using=CompanyID)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def testImage_list(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instances = TestImage.objects.filter(CompanyID=CompanyID)
    serialized = TestImageSerializer(
        instances, many=True, context={"request": request})
    response_data = {
        "StatusCode": 6000,
        "data": serialized.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_taskReact(request):
    from inventories.models import TaskFormReact, TaskFormSetReact

    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    Date = data['date']
    Description = data['description']

    tasks = data['taskList']

    instance = TaskFormReact.objects.create(
        Date=Date,
        Description=Description,
        CompanyID=CompanyID,
    )

    for tsk in tasks:
        projectName = tsk['projectName']
        task = tsk['task']
        taskStatus = tsk['taskStatus']
        taskNotes = tsk['taskNotes']

        TaskFormSetReact.objects.create(
            projectName=projectName,
            task=task,
            taskNotes=taskNotes,
            taskStatus=taskStatus,
            taskFormId=instance.id,
            CompanyID=CompanyID,
        )

    response_data = {
        "StatusCode": 6000,
        "message": 'Successfully Created'
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def taskReacts(request):
    from inventories.models import TaskFormReact, TaskFormSetReact
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instances = TaskFormReact.objects.filter(CompanyID=CompanyID)
    serialized = TaskFormReactSerializer(
        instances, many=True, context={"CompanyID": CompanyID})
    response_data = {
        "StatusCode": 6000,
        "data": serialized.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def taskReact(request, pk):
    from inventories.models import TaskFormReact, TaskFormSetReact
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    if TaskFormReact.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = TaskFormReact.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = TaskFormReactSerializer(
            instance, context={"CompanyID": CompanyID})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Task Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_taskReact(request, pk):
    from inventories.models import TaskFormReact, TaskFormSetReact

    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = TaskFormReact.objects.get(pk=pk, CompanyID=CompanyID)

    Date = data['date']
    Description = data['description']

    instance.Date = Date
    instance.Description = Description

    instance.save()

    tasks = data['taskList']

    for tsk in tasks:
        ID = tsk['id']
        projectName = tsk['projectName']
        task = tsk['task']
        taskNotes = tsk['taskNotes']
        taskStatus = tsk['taskStatus']
        detailID = tsk['detailID']

        if detailID == 0:
            detailInstance = TaskFormSetReact.objects.get(
                pk=ID, CompanyID=CompanyID)

            detailInstance.projectName = projectName
            detailInstance.task = task
            detailInstance.taskNotes = taskNotes
            detailInstance.taskStatus = taskStatus

            detailInstance.save()

        elif detailID == 1:
            TaskFormSetReact.objects.create(
                projectName=projectName,
                task=task,
                taskNotes=taskNotes,
                taskStatus=taskStatus,
                taskFormId=instance.id,
                CompanyID=CompanyID,
            )

    response_data = {
        "StatusCode": 6000,
        "message": 'Successfully Updated'
    }

    return Response(response_data, status=status.HTTP_200_OK)
