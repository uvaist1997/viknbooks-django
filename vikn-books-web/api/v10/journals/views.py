from brands.models import JournalMaster, JournalMaster_Log, JournalDetails, JournalDetails_Log, LedgerPosting, LedgerPosting_Log, JournalDetailsDummy, FinancialYear,\
    GeneralSettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.journals.serializers import JournalMasterSerializer, JournalMasterRestSerializer, JournalDetailsSerializer, JournalDetailsRestSerializer
from api.v10.brands.serializers import ListSerializer
from api.v10.journals.functions import generate_serializer_errors
from rest_framework import status
from api.v10.journals.functions import get_auto_id, get_auto_idMaster
from api.v10.sales.functions import get_auto_VoucherNo
import datetime
from api.v10.accountLedgers.functions import get_auto_LedgerPostid, UpdateLedgerBalance
from main.functions import converted_float, get_company, activity_log
from api.v10.sales.functions import get_Genrate_VoucherNo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
from django.db import transaction, IntegrityError
import re
import sys
import os
from main.functions import update_voucher_table


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_journal(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            Notes = data['Notes']
            TotalDebit = data['TotalDebit']
            TotalCredit = data['TotalCredit']
            Difference = data['Difference']
            IsActive = data['IsActive']
            Action = "A"

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "JL"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = JournalMaster.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_JournalOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    JournalMaster, BranchID, CompanyID, "JL")
                is_JournalOK = True
            elif is_voucherExist == False:
                is_JournalOK = True
            else:
                is_JournalOK = False

            if is_JournalOK:
                VoucherType = "JL"
                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)
                JournalMasterID = get_auto_idMaster(
                    JournalMaster, BranchID, CompanyID)
                JournalMaster_Log.objects.create(
                    TransactionID=JournalMasterID,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    TotalDebit=TotalDebit,
                    TotalCredit=TotalCredit,
                    Difference=Difference,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                JournalMaster.objects.create(
                    JournalMasterID=JournalMasterID,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    TotalDebit=TotalDebit,
                    TotalCredit=TotalCredit,
                    Difference=Difference,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                journalDetailsLogs = data["JournalDetails"]

                for journalDetailLog in journalDetailsLogs:

                    LedgerID = journalDetailLog['LedgerID']
                    Debit = journalDetailLog['Debit']
                    Credit = journalDetailLog['Credit']
                    Narration = journalDetailLog['Narration']

                    JournalDetailsID = get_auto_id(
                        JournalDetails, BranchID, CompanyID)

                    ledger_instance = JournalDetails_Log.objects.create(
                        TransactionID=JournalDetailsID,
                        BranchID=BranchID,
                        JournalMasterID=JournalMasterID,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Narration=Narration,
                        Action=Action,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    JournalDetails.objects.create(
                        JournalDetailsID=JournalDetailsID,
                        BranchID=BranchID,
                        JournalMasterID=JournalMasterID,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Narration=Narration,
                        Action=Action,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                        LogID=ledger_instance.ID
                    )

                VoucherType = "JL"
                datas = journalDetailsLogs
                # print("=======================")
                # print(datas)
                debit_credit_list = []
                for i in datas:
                    ledger = i.get("LedgerID")
                    debit = i.get("Debit")
                    credit = i.get("Credit")
                    debit_credit_list.append([ledger, debit, credit])
                print("debit_credit_list=============")
                print(debit_credit_list)

                # debit_credit_list = [
                #       [1, 0, 50], [2, 0, 25], [3, 0,25], [4, 100, 0]]

                debit_list = []
                credit_list = []
                final_data = []

                def remove_non_zero_equal_debit_and_credit(data):
                    # function that matches same debit and credit values and remove them from data
                    # global final_data
                    for item in data:
                        if item[1] != 0:
                            to_be_removed = list(
                                filter(lambda x: x[-1] == item[1], data))
                            item_index = data.index(item)
                            if to_be_removed:
                                to_be_removed = to_be_removed[0]
                                final_data.append(
                                    {
                                        'LedgerID': item[0],
                                        'RelativeLedgerID': to_be_removed[0],
                                        'Debit': item[1],
                                        'Credit': to_be_removed[1]
                                    }
                                )
                                final_data.append(
                                    {
                                        'LedgerID': to_be_removed[0],
                                        'RelativeLedgerID': item[0],
                                        'Debit': to_be_removed[1],
                                        'Credit': item[1]
                                    }
                                )
                                del data[item_index]
                                index_of_to_be_removed = data.index(
                                    to_be_removed)
                                del data[index_of_to_be_removed]
                                remove_non_zero_equal_debit_and_credit(data)

                def set_debit_and_credit_list():
                    # global debit_list, credit_list
                    # removes items with both debit and credit being 0
                    non_zero_entries = sorted(
                        filter(lambda x: x[1] != 0 or x[-1] != 0, debit_credit_list))
                    remove_non_zero_equal_debit_and_credit(non_zero_entries)
                    # print(non_zero_entries, final_data)
                    debit_list = list(
                        filter(lambda x: x[1] != 0, non_zero_entries))
                    credit_list = list(
                        filter(lambda x: x[-1] != 0, non_zero_entries))
                    # print(debit_list, credit_list)
                    return debit_list, credit_list

                debit_list, credit_list = set_debit_and_credit_list()
                # final_data, debit_list, credit_list
                while debit_list and credit_list:
                    print(debit_list, credit_list)
                    debit_item = debit_list[0]
                    credit_item = credit_list[0]
                    debit = debit_item[1]
                    credit = credit_item[-1]
                    if converted_float(debit) > converted_float(credit):
                        # update debit in debit list and delete credit from credit list
                        delta = credit
                        del credit_list[0]
                        debit_list[0][1] = converted_float(debit) - converted_float(delta)
                    elif debit < credit:
                        # update credit in credit list and delete debit from debit list
                        delta = debit
                        del debit_list[0]
                        credit_list[0][-1] = converted_float(credit) - converted_float(delta)
                    else:
                        # debit and credit are equal
                        del debit_list[0]
                        del credit_list[0]
                        delta = debit
                    final_data.append(
                        {
                            'LedgerID': debit_item[0],
                            'RelativeLedgerID': credit_item[0],
                            'Debit': delta,
                            'Credit': 0
                        }
                    )
                    final_data.append(
                        {
                            'LedgerID': credit_item[0],
                            'RelativeLedgerID': debit_item[0],
                            'Debit': 0,
                            'Credit': delta
                        }
                    )
                # from pprint import pprint
                # pprint(final_data)
                for f in final_data:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=JournalMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=f['LedgerID'],
                        RelatedLedgerID=f['RelativeLedgerID'],
                        Debit=f['Debit'],
                        Credit=f['Credit'],
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=JournalMasterID,
                        VoucherNo=VoucherNo,
                        VoucherType=VoucherType,
                        LedgerID=f['LedgerID'],
                        RelatedLedgerID=f['RelativeLedgerID'],
                        Debit=f['Debit'],
                        Credit=f['Credit'],
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    debit = f['Debit']
                    credit = f['Credit']
                    DrOCr = "Dr"
                    Amount = 0
                    if not debit == 0:
                        Amount = debit
                        DrOCr = "Dr"
                    elif not credit == 0:
                        Amount = credit
                        DrOCr = "Cr"
                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, f['LedgerID'], JournalMasterID, VoucherType, Amount, DrOCr, "create")

                response_data = {
                    "StatusCode": 6000,
                    "message": "Journal created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Journal',
                             'Create', 'Journal created Failed.', 'VoucherNo already exist')
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist!.Please Change Your Prefix!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Journal',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_journal(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            today = datetime.datetime.now()

            journalMaster_instance = None
            journalDetails = None
            journalMaster_instance = JournalMaster.objects.get(
                pk=pk, CompanyID=CompanyID)
            JournalMasterID = journalMaster_instance.JournalMasterID
            BranchID = journalMaster_instance.BranchID
            VoucherNo = journalMaster_instance.VoucherNo
            # VoucherType = journalMaster_instance.VoucherType

            VoucherType = "JL"

            Date = data['Date']
            Notes = data['Notes']
            TotalDebit = data['TotalDebit']
            TotalCredit = data['TotalCredit']
            Difference = data['Difference']
            IsActive = data['IsActive']

            Action = "M"

            JournalMaster_Log.objects.create(
                TransactionID=JournalMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                TotalDebit=TotalDebit,
                TotalCredit=TotalCredit,
                Difference=Difference,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, JournalMasterID, VoucherType, 0, "Cr", "update")

            if LedgerPosting.objects.filter(VoucherMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID, VoucherType=VoucherType).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    VoucherMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID, VoucherType=VoucherType).delete()
                # for ledgerPostInstance in ledgerPostInstances:
                #     ledgerPostInstance.delete()

            if JournalDetails.objects.filter(JournalMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID).exists():
                journalDetailInstances = JournalDetails.objects.filter(
                    JournalMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID).delete()
                # for journalDetailInstance in journalDetailInstances:
                #     journalDetailInstance.delete()

            journalMaster_instance.Date = Date
            journalMaster_instance.Notes = Notes
            journalMaster_instance.TotalDebit = TotalDebit
            journalMaster_instance.TotalCredit = TotalCredit
            journalMaster_instance.Difference = Difference
            journalMaster_instance.IsActive = IsActive
            journalMaster_instance.UpdatedDate = today
            journalMaster_instance.CreatedUserID = CreatedUserID
            journalMaster_instance.Action = Action

            journalMaster_instance.save()

            journalDetails = data["JournalDetails"]

            for journalDetail in journalDetails:

                detailID = journalDetail['detailID']
                LedgerID = journalDetail['LedgerID']
                Debit = journalDetail['Debit']
                Credit = journalDetail['Credit']
                Narration = journalDetail['Narration']

                if detailID == 0:
                    JournalDetailsID = get_auto_id(
                        JournalDetails, BranchID, CompanyID)

                    log_instance = JournalDetails_Log.objects.create(
                        TransactionID=JournalDetailsID,
                        BranchID=BranchID,
                        JournalMasterID=JournalMasterID,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Narration=Narration,
                        Action=Action,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )
                    JournalDetails.objects.create(
                        JournalDetailsID=JournalDetailsID,
                        BranchID=BranchID,
                        JournalMasterID=JournalMasterID,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Narration=Narration,
                        Action=Action,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                        LogID=log_instance.ID
                    )

                    # VoucherType = "JL"

                    # LedgerPostingID = get_auto_LedgerPostid(
                    #     LedgerPosting, BranchID, CompanyID)

                    # LedgerPosting.objects.create(
                    #     LedgerPostingID=LedgerPostingID,
                    #     BranchID=BranchID,
                    #     Date=Date,
                    #     VoucherMasterID=JournalMasterID,
                    #     VoucherType=VoucherType,
                    #     VoucherNo=VoucherNo,
                    #     LedgerID=LedgerID,
                    #     Debit=Debit,
                    #     Credit=Credit,
                    #     IsActive=IsActive,
                    #     Action=Action,
                    #     CreatedUserID=CreatedUserID,
                    #     CreatedDate=today,
                    #     UpdatedDate=today,
                    #     CompanyID=CompanyID,
                    # )

                    # LedgerPosting_Log.objects.create(
                    #     TransactionID=LedgerPostingID,
                    #     BranchID=BranchID,
                    #     Date=Date,
                    #     VoucherMasterID=JournalMasterID,
                    #     VoucherNo=VoucherNo,
                    #     VoucherType=VoucherType,
                    #     LedgerID=LedgerID,
                    #     Debit=Debit,
                    #     Credit=Credit,
                    #     IsActive=IsActive,
                    #     Action=Action,
                    #     CreatedUserID=CreatedUserID,
                    #     CreatedDate=today,
                    #     UpdatedDate=today,
                    #     CompanyID=CompanyID,
                    # )

                if detailID == 1:
                    Action = "A"
                    JournalDetailsID = get_auto_id(
                        JournalDetails, BranchID, CompanyID)

                    log_instance = JournalDetails_Log.objects.create(
                        TransactionID=JournalDetailsID,
                        BranchID=BranchID,
                        JournalMasterID=JournalMasterID,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Narration=Narration,
                        Action=Action,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    JournalDetails.objects.create(
                        JournalDetailsID=JournalDetailsID,
                        BranchID=BranchID,
                        JournalMasterID=JournalMasterID,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Narration=Narration,
                        Action=Action,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                        LogID=log_instance.ID
                    )

                    # VoucherType = "JL"

                    # LedgerPostingID = get_auto_LedgerPostid(
                    #     LedgerPosting, BranchID, CompanyID)

                    # LedgerPosting.objects.create(
                    #     LedgerPostingID=LedgerPostingID,
                    #     BranchID=BranchID,
                    #     Date=Date,
                    #     VoucherMasterID=JournalMasterID,
                    #     VoucherType=VoucherType,
                    #     VoucherNo=VoucherNo,
                    #     LedgerID=LedgerID,
                    #     Debit=Debit,
                    #     Credit=Credit,
                    #     IsActive=IsActive,
                    #     Action=Action,
                    #     CreatedUserID=CreatedUserID,
                    #     CreatedDate=today,
                    #     UpdatedDate=today,
                    #     CompanyID=CompanyID,
                    # )

                    # LedgerPosting_Log.objects.create(
                    #     TransactionID=LedgerPostingID,
                    #     BranchID=BranchID,
                    #     Date=Date,
                    #     VoucherMasterID=JournalMasterID,
                    #     VoucherNo=VoucherNo,
                    #     VoucherType=VoucherType,
                    #     LedgerID=LedgerID,
                    #     Debit=Debit,
                    #     Credit=Credit,
                    #     IsActive=IsActive,
                    #     Action=Action,
                    #     CreatedUserID=CreatedUserID,
                    #     CreatedDate=today,
                    #     UpdatedDate=today,
                    #     CompanyID=CompanyID,
                    # )

            VoucherType = "JL"
            datas = journalDetails
            # print("=======================")
            # print(datas)
            debit_credit_list = []
            for i in datas:
                ledger = i.get("LedgerID")
                debit = i.get("Debit")
                credit = i.get("Credit")
                debit_credit_list.append([ledger, debit, credit])
            print("debit_credit_list=============")
            print(debit_credit_list)

            # debit_credit_list = [[1, 0, 50], [2, 0, 25], [3, 0,25], [4, 100, 0]]

            debit_list = []
            credit_list = []
            final_data = []

            def remove_non_zero_equal_debit_and_credit(data):
                # function that matches same debit and credit values and remove them from data
                # global final_data
                for item in data:
                    if item[1] != 0:
                        to_be_removed = list(
                            filter(lambda x: x[-1] == item[1], data))
                        item_index = data.index(item)
                        if to_be_removed:
                            to_be_removed = to_be_removed[0]
                            final_data.append(
                                {
                                    'LedgerID': item[0],
                                    'RelativeLedgerID': to_be_removed[0],
                                    'Debit': item[1],
                                    'Credit': to_be_removed[1]
                                }
                            )
                            final_data.append(
                                {
                                    'LedgerID': to_be_removed[0],
                                    'RelativeLedgerID': item[0],
                                    'Debit': to_be_removed[1],
                                    'Credit': item[1]
                                }
                            )
                            del data[item_index]
                            index_of_to_be_removed = data.index(to_be_removed)
                            del data[index_of_to_be_removed]
                            remove_non_zero_equal_debit_and_credit(data)

            def set_debit_and_credit_list():
                # global debit_list, credit_list
                # removes items with both debit and credit being 0
                non_zero_entries = sorted(
                    filter(lambda x: x[1] != 0 or x[-1] != 0, debit_credit_list))
                remove_non_zero_equal_debit_and_credit(non_zero_entries)
                # print(non_zero_entries, final_data)
                debit_list = list(
                    filter(lambda x: x[1] != 0, non_zero_entries))
                credit_list = list(
                    filter(lambda x: x[-1] != 0, non_zero_entries))
                # print(debit_list, credit_list)
                return debit_list, credit_list

            debit_list, credit_list = set_debit_and_credit_list()
            # final_data, debit_list, credit_list
            while debit_list and credit_list:
                print(debit_list, credit_list)
                debit_item = debit_list[0]
                credit_item = credit_list[0]
                debit = debit_item[1]
                credit = credit_item[-1]
                if converted_float(debit) > converted_float(credit):
                    # update debit in debit list and delete credit from credit list
                    delta = credit
                    del credit_list[0]
                    debit_list[0][1] = converted_float(debit) - converted_float(delta)
                elif converted_float(debit) < converted_float(credit):
                    # update credit in credit list and delete debit from debit list
                    delta = debit
                    del debit_list[0]
                    credit_list[0][-1] = converted_float(credit) - converted_float(delta)
                else:
                    # debit and credit are equal
                    del debit_list[0]
                    del credit_list[0]
                    delta = debit
                final_data.append(
                    {
                        'LedgerID': debit_item[0],
                        'RelativeLedgerID': credit_item[0],
                        'Debit': delta,
                        'Credit': 0
                    }
                )
                final_data.append(
                    {
                        'LedgerID': credit_item[0],
                        'RelativeLedgerID': debit_item[0],
                        'Debit': 0,
                        'Credit': delta
                    }
                )
            print("==========================final data")
            print(final_data)
            # from pprint import pprint
            # pprint(final_data)
            for f in final_data:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=JournalMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=f['LedgerID'],
                    RelatedLedgerID=f['RelativeLedgerID'],
                    Debit=f['Debit'],
                    Credit=f['Credit'],
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=JournalMasterID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=f['LedgerID'],
                    RelatedLedgerID=f['RelativeLedgerID'],
                    Debit=f['Debit'],
                    Credit=f['Credit'],
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                debit = f['Debit']
                credit = f['Credit']
                DrOCr = "Dr"
                Amount = 0
                if not debit == 0:
                    Amount = debit
                    DrOCr = "Dr"
                elif not credit == 0:
                    Amount = credit
                    DrOCr = "Cr"

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, f['LedgerID'], JournalMasterID, VoucherType, Amount, DrOCr, "create")

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal',
            #              'Edit', 'Journal Updated successfully.', 'Journal Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Journal Updated Successfully!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Journal',
                     'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def journals(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if JournalMaster.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

            if page_number and items_per_page:
                instances = JournalMaster.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = JournalMaster.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)
                count = len(ledger_sort_pagination)

            serialized = JournalMasterRestSerializer(ledger_sort_pagination, many=True, context={"CompanyID": CompanyID,
                                                                                                 "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal',
            #              'View', 'Journal List Viewed successfully.', 'User Viewed Journal List.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Journal', 'View',
                         'Journal List Viewed Failed.', 'Journal List is Not Foound Under this Branch.')
            response_data = {
                "StatusCode": 6001,
                "message": "Journal Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def journal(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    instance = None
    if JournalMaster.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = JournalMaster.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = JournalMasterRestSerializer(instance, context={"CompanyID": CompanyID,
                                                                    "PriceRounding": PriceRounding})

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal', 'View',
        #              'Journal Single Page Viewed Successfully.', 'Journal Single Page Viewed Successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Journal',
                     'View', 'Journal Single Page Viewed Failed.', 'Journal Not Found')
        response_data = {
            "StatusCode": 6001,
            "message": "Journal Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_journalDetail(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if JournalDetails.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = JournalDetails.objects.get(pk=pk, CompanyID=CompanyID)
        JournalDetailsID = instance.JournalDetailsID
        BranchID = instance.BranchID
        JournalMasterID = instance.JournalMasterID
        LedgerID = instance.LedgerID
        Debit = instance.Debit
        Credit = instance.Credit
        Narration = instance.Narration
        Action = "D"

        instance.delete()

        JournalDetails_Log.objects.create(
            TransactionID=JournalDetailsID,
            BranchID=BranchID,
            JournalMasterID=JournalMasterID,
            LedgerID=LedgerID,
            Debit=Debit,
            Credit=Credit,
            Narration=Narration,
            Action=Action,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Journal Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Journal Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_journal(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instances = None
    if selecte_ids:
        if JournalMaster.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = JournalMaster.objects.filter(pk__in=selecte_ids)
    else:
        if JournalMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = JournalMaster.objects.filter(pk=pk)

    ledgerPostInstances = None

    if instances:
        for instance in instances:
            JournalMasterID = instance.JournalMasterID
            BranchID = instance.BranchID
            VoucherNo = instance.VoucherNo
            Date = instance.Date
            Notes = instance.Notes
            TotalDebit = instance.TotalDebit
            TotalCredit = instance.TotalCredit
            Difference = instance.Difference
            IsActive = instance.IsActive
            Action = "D"

            VoucherType = "JL"

            JournalMaster_Log.objects.create(
                TransactionID=JournalMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                TotalDebit=TotalDebit,
                TotalCredit=TotalCredit,
                Difference=Difference,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            detail_instances = JournalDetails.objects.filter(
                JournalMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID)

            for detail_instance in detail_instances:

                JournalDetailsID = detail_instance.JournalDetailsID
                BranchID = detail_instance.BranchID
                JournalMasterID = detail_instance.JournalMasterID
                LedgerID = detail_instance.LedgerID
                Debit = detail_instance.Debit
                Credit = detail_instance.Credit
                Narration = detail_instance.Narration

                detail_instance.delete()

                JournalDetails_Log.objects.create(
                    TransactionID=JournalDetailsID,
                    BranchID=BranchID,
                    JournalMasterID=JournalMasterID,
                    LedgerID=LedgerID,
                    Debit=Debit,
                    Credit=Credit,
                    Narration=Narration,
                    Action=Action,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

            if LedgerPosting.objects.filter(VoucherMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID, VoucherType=VoucherType).exists():
                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, 0, JournalMasterID, VoucherType, 0, "Cr", "update")
                ledgerPostInstances = LedgerPosting.objects.filter(
                    VoucherMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID, VoucherType=VoucherType)

                for ledgerPostInstance in ledgerPostInstances:
                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive
                    Date = ledgerPostInstance.Date
                    LedgerID = ledgerPostInstance.LedgerID

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=JournalMasterID,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    ledgerPostInstance.delete()

            instance.delete()

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal',
                     'Delete', 'Journal Deleted Successfully', 'Journal Deleted Successfully')
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Journal Deleted Successfully!"
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Journal', 'Delete', 'Journal Deleted Failed', 'Journal Not Found')
        response_data = {
            "StatusCode": 6001,
            "title": "Failed!",
            "message": "Journal Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def search_journals(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    param = data['param']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if JournalMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = JournalMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            if length < 3:
                if param == "VoucherNo":
                    instances = instances.filter(
                        (Q(VoucherNo__icontains=product_name)))[:10]
                else:
                    instances = instances.filter(
                        (Q(Date__icontains=product_name)))[:10]
            else:
                if param == "VoucherNo":
                    instances = instances.filter(
                        (Q(VoucherNo__icontains=product_name)))
                else:
                    instances = instances.filter(
                        (Q(Date__icontains=product_name)))
            serialized = JournalMasterRestSerializer(instances, many=True, context={
                "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "product_name": "product_name"})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
