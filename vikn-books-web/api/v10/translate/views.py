import datetime

from googletrans import Translator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v10.warehouses.functions import generate_serializer_errors, get_auto_id
from brands.models import (
    PurchaseMaster,
    SalesMaster,
    StockPosting,
    UserTable,
    Warehouse,
    Warehouse_Log,
)
from main.functions import activity_log, get_company


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def translate(request):
    data = request.data
    keyword = data["keyword"]
    language = data["language"]
    translator = Translator()
    if keyword and language:
        out = translator.translate(keyword, dest=language)
        response_data = {
            "StatusCode": 6000,
            "data": str(out.text),
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "Wrong input"}

        return Response(response_data, status=status.HTTP_200_OK)
