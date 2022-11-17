import string
from django.contrib.auth.models import User
from main.functions import get_company
from api.v6.products.functions import get_auto_id, get_auto_priceListid, get_ProductCode, get_auto_AutoBarcode, get_auto_BatchNo, get_auto_AutoBatchCode
from django.utils.crypto import get_random_string
from celery_progress.backend import ProgressRecorder
from celery import shared_task
from brands import models
import datetime
import xlrd
from django.db.models import Q, Sum, F


# @shared_task
# def create_random_user_accounts(total):
#     for i in range(total):
#         username = 'user_{}'.format(
#             get_random_string(10, string.ascii_letters))
#         email = '{}@example.com'.format(username)
#         password = get_random_string(50)
#         models.User.objects.create_user(
#             username=username, email=email, password=password)
#     return '{} random users created with success!'.format(total)


@shared_task(bind=True)
def runAPIforChangeDatasInDB(self):
    progress_recorder = ProgressRecorder(self)
    
    from brands.models import TaxCategory,SalesMaster, SalesDetails, PurchaseMaster, PurchaseDetails, PriceList, StockRate, StockPosting, StockTrans, StockPosting_Log,\
     CompanySettings, ReceiptDetails, LedgerPosting, AccountLedger, UserTable, LedgerPosting_Log, PaymentDetails,GeneralSettings,UserTable,Product,\
     PurchaseReturnMaster,PurchaseReturnDetails,SalesReturnMaster,SalesReturnDetails,OpeningStockMaster,OpeningStockDetails,StockTransferMaster_ID,\
     StockTransferDetails,PaymentMaster,PaymentDetails,ReceiptMaster,ReceiptDetails,JournalMaster,JournalDetails,Parties,AccountLedger_Log,Bank
    from api.v5.sales.functions import get_auto_stockPostid
    from api.v5.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v5.accountLedgers.functions import get_auto_LedgerPostid
    from api.v5.accountLedgers.functions import get_LedgerCode, get_auto_id as generated_ledgerID
    import time
    import re
    from brands import models as table


    start_time = time.time()
    companies = table.CompanySettings.objects.filter(is_deleted=False)
    count = 0
    total = companies.count()
    for i in companies:
        count += 1
        print("starttttttttttttttttttttttttttttttttttttt")
        CompanyID = i
        BranchID = 1
        if table.StockPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            stock_instances = table.StockPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for i in stock_instances:
                PriceListID = i.PriceListID
                if table.PriceList.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PriceListID=PriceListID).exists():
                    pricelist = table.PriceList.objects.get(CompanyID=CompanyID,BranchID=BranchID,PriceListID=PriceListID)
                    i.pricelist = pricelist
                    i.save()

            progress_recorder.set_progress(
                int(count), int(total), description="hello world")

    end_time = time.time() - start_time
    print("--------------------------------------------------")
    print(end_time)
    return '{} Qury Run successfully!'.format(total)

