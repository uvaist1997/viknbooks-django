from brands.models import Warehouse, Warehouse_Log, SalesMaster, PurchaseMaster, StockPosting, UserTable
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.warehouses.functions import generate_serializer_errors
from rest_framework import status
from api.v3.warehouses.functions import get_auto_id
import datetime
from main.functions import get_company, activity_log
from googletrans import Translator


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def translate(request):
    data = request.data
    keyword = data['keyword']
    language = data['language']
    translator = Translator()
    if keyword and language:
        out = translator.translate(keyword, dest=language)
        response_data = {
            "StatusCode": 6000,
            "data": str(out.text),
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Wrong input"
        }

        return Response(response_data, status=status.HTTP_200_OK)
