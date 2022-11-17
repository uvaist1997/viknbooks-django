import string
from django.utils.crypto import get_random_string
from celery_progress.backend import ProgressRecorder
from celery import shared_task
import datetime
import xlrd
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, get_object_or_404
import datetime
from datetime import date
from brands.models import SalesMaster, SalesMaster_Log, SalesDetails, SalesDetails_Log, StockPosting, LedgerPosting,\
    StockPosting_Log, LedgerPosting_Log, Parties, SalesDetailsDummy, StockRate, StockTrans, PriceList, DamageStockMaster, JournalMaster,\
    OpeningStockMaster, PaymentMaster, PurchaseMaster, PurchaseOrderMaster, PurchaseReturnMaster, ReceiptMaster, SalesOrderMaster, SalesEstimateMaster,\
    SalesReturnMaster, StockReceiptMaster_ID, DamageStockMaster, StockTransferMaster_ID, AccountGroup, SalesReturnDetails,\
    AccountLedger, PurchaseDetails, PurchaseReturnDetails, Product, UserTable, ProductGroup, ExcessStockMaster, ShortageStockMaster, DamageStockMaster,\
    UsedStockMaster, GeneralSettings, CompanySettings, WorkOrderMaster, Batch, SerialNumbers, LoyaltyCustomer, LoyaltyProgram, LoyaltyPoint, LoyaltyPoint_Log,\
    SalesOrderDetails,AccountLedger_Log

from api.v9.sales.serializers import GST_CDNR_Serializer,GST_B2B_Serializer,SalesEstimateForOrderSerializer, SalesMasterSerializer, SalesMasterRestSerializer,SalesMasterRest1Serializer, SalesDetailsSerializer,\
    SalesDetailsRestSerializer, BatchSerializer, ListSerializerforReport, SalesMasterReportSerializer, SalesMasterForReturnSerializer, StockSerializer, StockRateSerializer, SalesIntegratedSerializer,\
    SalesSummaryReportSerializer, SupplierVsProductReportSerializer, SalesGSTReportSerializer, ProductVsSuppliersReportSerializer, FilterOrderSerializer,BillWiseSerializer
from api.v9.brands.serializers import ListSerializer

from api.v9.salesReturns.serializers import SalesReturnMasterRestSerializer, SalesReturnMasterReportSerializer
from api.v9.sales.functions import set_LoyaltyCalculation,get_Program, edit_LoyaltyCalculation, generate_serializer_errors, get_month, get_stock_value
from rest_framework import status
import re,sys, os
from main.functions import get_company, activity_log
from django.db.models import Max
from api.v9.sales.functions import get_Genrate_VoucherNo
from django.db.models import Q, Prefetch, Sum
from django.db import transaction,IntegrityError
import math
from operator import itemgetter
import time


@shared_task(bind=True)
def taskAPIfor_gstr1_report(self,data,user):
    print("INSIDE 111111111111111111TA",user)
    progress_recorder = ProgressRecorder(self)
    start_time = time.time()

    # ================
    total = len([ele for ele in Sales if isinstance(ele, dict)])
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",total,"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    count = 0
    # ===================
    
    # ===================
    progress_recorder.set_progress(
        int(count), int(total), description="hello world")

    end_time = time.time() - start_time
    print("--------------------------------------------------")
    print(end_time)
    return '{} Qury Run successfully!'.format(total)
