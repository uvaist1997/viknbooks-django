import datetime
import json
import os
import sys

import pandas as pd
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import IntegrityError, transaction
from django.db.models import Prefetch, Q, Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v9.bankReconciliationStatement import serializers
from api.v9.bankReconciliationStatement.functions import (
    get_auto_idDetail,
    get_auto_idMaster,
)
from api.v9.banks.serializers import BankRestSerializer
from api.v9.reportQuerys.functions import (
    query_closingBalance_data,
    query_openingBalance_data,
)
from brands import models
from main.functions import (
    activity_log,
    generateVoucherNoFunction,
    get_company,
    get_GeneralSettings,
    update_voucher_table,
)


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def reconsiliation_create(request):
    # try:
    #     with transaction.atomic():
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    CreatedUserID = data["CreatedUserID"]
    today = datetime.datetime.now()
    VoucherNo = data["VoucherNo"]
    Date = data["Date"]
    ClosingBalance = data["ClosingBalance"]
    BankID = data["BankID"]
    BankName = data["BankName"]
    ClosingDate = data["ClosingDate"]
    StartingDate = data["StartingDate"]

    VoucherType = data["VoucherType"]
    Differences = data["Differences"]
    ClearedAmt = data["ClearedAmt"]
    BankStatement = data["BankStatement"]
    Type = data["Type"]
    InvoiceNo = data["InvoiceNo"]
    PreFix = data["PreFix"]
    Seperator = data["Seperator"]

    Action = "A"
    # checking voucher number already exist
    is_voucherExist = False
    check_VoucherNoAutoGenerate = get_GeneralSettings(
        CompanyID, BranchID, "VoucherNoAutoGenerate"
    )
    if models.BankReconciliationMaster.objects.filter(
        CompanyID=CompanyID, BranchID=BranchID, VoucherNo__iexact=VoucherNo
    ).exists():
        is_voucherExist = True

    if is_voucherExist == True and check_VoucherNoAutoGenerate == True:
        VoucherNo, InvoiceNo, PreFix, seperator = generateVoucherNoFunction(
            CompanyID, CreatedUserID, VoucherType, BranchID
        )
        is_voucherExist = False
    update_voucher_table(
        CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo
    )
    BankReconciliationMasterID = get_auto_idMaster(
        models.BankReconciliationMaster, BranchID, CompanyID
    )

    models.BankReconciliationMaster.objects.create(
        BankReconciliationMasterID=BankReconciliationMasterID,
        BranchID=BranchID,
        Action=Action,
        VoucherNo=VoucherNo,
        Date=Date,
        VoucherType=VoucherType,
        ClosingBalance=ClosingBalance,
        StartingDate=StartingDate,
        BankName=BankName,
        BankID=BankID,
        ClosingDate=ClosingDate,
        ClearedAmt=ClearedAmt,
        Differences=Differences,
        BankStatement=BankStatement,
        Type=Type,
        CreatedDate=today,
        LastUDate=today,
        CreatedUserID=CreatedUserID,
        CompanyID=CompanyID,
    )
    models.BankReconciliationMaster_Log.objects.create(
        TransactionID=BankReconciliationMasterID,
        BranchID=BranchID,
        Action=Action,
        VoucherNo=VoucherNo,
        Date=Date,
        VoucherType=VoucherType,
        ClosingBalance=ClosingBalance,
        StartingDate=StartingDate,
        BankName=BankName,
        BankID=BankID,
        ClosingDate=ClosingDate,
        ClearedAmt=ClearedAmt,
        Differences=Differences,
        BankStatement=BankStatement,
        Type=Type,
        CreatedDate=today,
        LastUDate=today,
        CreatedUserID=CreatedUserID,
        CompanyID=CompanyID,
    )

    try:
        reconciliation_details = json.loads(data["reconciliation_datas"])
    except:
        reconciliation_details = data["reconciliation_datas"]

    # reconciliation_details = data["reconciliation_datas"]
    for detail in reconciliation_details:
        try:
            is_opening = detail["is_opening"]
        except:
            is_opening = False

        if not is_opening:
            id = detail["id"]
            Date = detail["Date"]
            TransactionType = detail["TransactionType"]
            Debit = detail["Debit"]
            Credit = detail["Credit"]
            VoucherMasterID = detail["VoucherMasterID"]
            PaymentGateway = detail["PaymentGateway"]
            PaymentStatus = True
            RelativeLedgerName = detail["RelativeLedgerName"]
            RelativeLedgerID = detail["RelatedLedgerID"]
            IsReconciliate = detail["IsReconciliate"]

            ledger_post_inst = None
            if (
                IsReconciliate == True
                and models.LedgerPosting.objects.filter(id=id).exists()
            ):
                ledger_post_inst = models.LedgerPosting.objects.get(id=id)
                if Type == "reconciliate":
                    ledger_post_inst.IsReconciliated = True
                    ledger_post_inst.save()
            BankReconciliationDetailsID = get_auto_idDetail(
                models.BankReconciliationDetails, BranchID, CompanyID
            )
            models.BankReconciliationDetails.objects.create(
                CompanyID=CompanyID,
                BankReconciliationDetailsID=BankReconciliationDetailsID,
                BranchID=BranchID,
                Date=Date,
                TransactionType=TransactionType,
                Debit=Debit,
                Credit=Credit,
                BankReconciliationMasterID=BankReconciliationMasterID,
                VoucherMasterID=VoucherMasterID,
                PaymentGateway=PaymentGateway,
                PaymentStatus=PaymentStatus,
                LedgerPostid=ledger_post_inst,
                RelativeLedgerName=RelativeLedgerName,
                RelativeLedgerID=RelativeLedgerID,
                IsReconciliate=IsReconciliate,
            )

            models.BankReconciliationDetails_Log.objects.create(
                CompanyID=CompanyID,
                TransactionID=BankReconciliationDetailsID,
                BranchID=BranchID,
                Date=Date,
                TransactionType=TransactionType,
                Debit=Debit,
                Credit=Credit,
                BankReconciliationMasterID=BankReconciliationMasterID,
                VoucherMasterID=VoucherMasterID,
                PaymentGateway=PaymentGateway,
                PaymentStatus=PaymentStatus,
                LedgerPostid=ledger_post_inst,
                RelativeLedgerName=RelativeLedgerName,
                RelativeLedgerID=RelativeLedgerID,
                IsReconciliate=IsReconciliate,
            )

    response_data = {
        "StatusCode": 6000,
        "message": "Bank Reconciliation created Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)
    # except Exception as e:
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
    #     response_data = {
    #         "StatusCode": 6001,
    #         "message": "some error occured..please try again"
    #     }

    #     activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, "Bank Reconciliation",
    #                  'Create', str(e), err_descrb)
    #     body_params = str(request.data)
    #     models.Activity_Log.objects.filter(id=activity_id).update(body_params=body_params)
    #     return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def reconsiliation_details(request):
    CompanyID = request.data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BankID = request.data["BankID"]
    BranchID = request.data["BranchID"]
    ClosingDate = request.data["ClosingDate"]

    if models.LedgerPosting.objects.filter(
        CompanyID=CompanyID,
        BranchID=BranchID,
        LedgerID=BankID,
        VoucherType__in=["BR", "BP", "SI", "SR", "PI", "PR", "CP", "CR"],
        Date__lte=ClosingDate,
        IsReconciliated=False,
    ).exists():
        instance = models.LedgerPosting.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            LedgerID=BankID,
            VoucherType__in=["BR", "BP", "SI", "SR", "PI", "PR", "CP", "CR"],
            Date__lte=ClosingDate,
            IsReconciliated=False,
        )
        serialized = serializers.BankReconciliationSerializer(
            instance, many=True, context={"request": request, "CompanyID": CompanyID}
        )

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "datas not found!"}
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def reconsiliation_list(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]
    page_number = data["page_no"]
    items_per_page = data["items_per_page"]

    if models.BankReconciliationMaster.objects.filter(
        BranchID=BranchID, CompanyID=CompanyID
    ).exists():
        instances = models.BankReconciliationMaster.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID
        ).order_by("-BankReconciliationMasterID")
        reconciliation_sort_pagination = list_pagination(
            instances, items_per_page, page_number
        )
        serialized = serializers.BankReconciliationListSerializer(
            reconciliation_sort_pagination,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
            "count": len(instances),
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Bank Not Found in this BranchID!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def bank_list(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]

    if models.Bank.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
        instances = models.Bank.objects.filter(BranchID=BranchID, CompanyID=CompanyID)
        serialized = BankRestSerializer(
            instances,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Bank Not Found in this BranchID!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_reconsiliation(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]
    try:
        selecte_ids = data["selecte_ids"]
    except:
        selecte_ids = []
    Action = "D"
    today = datetime.datetime.now()

    if selecte_ids:
        if models.BankReconciliationMaster.objects.filter(pk__in=selecte_ids).exists():
            instances = models.BankReconciliationMaster.objects.filter(
                pk__in=selecte_ids
            )
    else:
        if models.BankReconciliationMaster.objects.filter(pk=pk).exists():
            instances = models.BankReconciliationMaster.objects.filter(pk=pk)

    if instances:
        for i in instances:
            BankReconciliationMasterID = i.BankReconciliationMasterID
            VoucherNo = i.VoucherNo
            Date = i.Date
            ClosingBalance = i.ClosingBalance
            BankName = i.BankName
            ClosingDate = i.ClosingDate
            VoucherType = i.VoucherType
            BankID = i.BankID
            Differences = i.Differences
            ClearedAmt = i.ClearedAmt
            BankStatement = i.BankStatement
            Type = i.Type

            models.BankReconciliationMaster_Log.objects.create(
                TransactionID=BankReconciliationMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                Date=Date,
                VoucherType=VoucherType,
                ClosingBalance=ClosingBalance,
                BankName=BankName,
                BankID=BankID,
                ClosingDate=ClosingDate,
                ClearedAmt=ClearedAmt,
                Differences=Differences,
                BankStatement=BankStatement,
                Type=Type,
                CreatedDate=today,
                LastUDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            detail_instances = models.BankReconciliationDetails.objects.filter(
                CompanyID=CompanyID,
                BankReconciliationMasterID=BankReconciliationMasterID,
                BranchID=BranchID,
            )
            for detail_instance in detail_instances:
                BankReconciliationDetailsID = (
                    detail_instance.BankReconciliationDetailsID
                )
                Date = detail_instance.Date
                RelativeLedgerName = detail_instance.RelativeLedgerName
                TransactionType = detail_instance.TransactionType
                BankDate = detail_instance.BankDate
                Debit = detail_instance.Debit
                Credit = detail_instance.Credit
                BankReconciliationMasterID = detail_instance.BankReconciliationMasterID
                VoucherMasterID = detail_instance.VoucherMasterID
                RelativeLedgerID = detail_instance.RelativeLedgerID
                PaymentGateway = detail_instance.PaymentGateway
                PaymentStatus = detail_instance.PaymentStatus
                IsReconciliate = detail_instance.IsReconciliate
                LedgerPostid = detail_instance.LedgerPostid
                if IsReconciliate == True:
                    LedgerPostid.IsReconciliated = False
                    LedgerPostid.save()
                models.BankReconciliationDetails_Log.objects.create(
                    CompanyID=CompanyID,
                    TransactionID=BankReconciliationDetailsID,
                    BranchID=BranchID,
                    Date=Date,
                    TransactionType=TransactionType,
                    Debit=Debit,
                    Credit=Credit,
                    BankReconciliationMasterID=BankReconciliationMasterID,
                    VoucherMasterID=VoucherMasterID,
                    PaymentGateway=PaymentGateway,
                    PaymentStatus=PaymentStatus,
                    LedgerPostid=LedgerPostid,
                    RelativeLedgerName=RelativeLedgerName,
                    RelativeLedgerID=RelativeLedgerID,
                    IsReconciliate=IsReconciliate,
                )
                detail_instance.delete()
            i.delete()

        response_data = {
            "StatusCode": 6000,
            "message": "Successfully deleted",
            "title": "Success",
        }

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Reconciliation not found",
            "title": "Failed",
        }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def view_reconsiliation(request, pk):
    CompanyID = request.data["CompanyID"]
    CompanyID = get_company(CompanyID)
    PriceRounding = request.data["PriceRounding"]
    BranchID = request.data["BranchID"]

    if models.BankReconciliationMaster.objects.filter(pk=pk).exists():
        instance = models.BankReconciliationMaster.objects.get(pk=pk)
        serialized = serializers.BankReconciliationSingleSerializer(
            instance,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "datas not found!"}
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_reconsiliation(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            BranchID = data["BranchID"]
            CreatedUserID = data["CreatedUserID"]
            today = datetime.datetime.now()
            VoucherNo = data["VoucherNo"]
            Date = data["Date"]
            ClosingBalance = data["ClosingBalance"]
            BankID = data["BankID"]
            BankName = data["BankName"]
            ClosingDate = data["ClosingDate"]
            VoucherType = data["VoucherType"]
            Differences = data["Differences"]
            ClearedAmt = data["ClearedAmt"]
            BankStatement = data["BankStatement"]
            Type = data["Type"]
            InvoiceNo = data["InvoiceNo"]
            PreFix = data["PreFix"]
            Seperator = data["Seperator"]
            Action = "M"

            if models.BankReconciliationMaster.objects.filter(pk=pk).exists():
                instance = models.BankReconciliationMaster.objects.get(pk=pk)
                BankReconciliationMasterID = instance.BankReconciliationMasterID
                VoucherNo = instance.VoucherNo
                ClosingBalance = instance.ClosingBalance
                BankName = instance.BankName
                BankID = instance.BankID
                ClosingDate = instance.ClosingDate
                instance.Date = Date
                instance.ClearedAmt = ClearedAmt
                instance.Differences = Differences
                instance.BankStatement = BankStatement
                instance.Type = Type
                instance.LastUDate = today
                instance.save()

                models.BankReconciliationMaster_Log.objects.create(
                    TransactionID=BankReconciliationMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    VoucherType=VoucherType,
                    ClosingBalance=ClosingBalance,
                    BankName=BankName,
                    BankID=BankID,
                    ClosingDate=ClosingDate,
                    ClearedAmt=ClearedAmt,
                    Differences=Differences,
                    BankStatement=BankStatement,
                    Type=Type,
                    CreatedDate=today,
                    LastUDate=today,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                models.BankReconciliationDetails.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    BankReconciliationMasterID=BankReconciliationMasterID,
                ).delete()

                try:
                    reconciliation_details = json.loads(data["reconciliation_datas"])
                except:
                    reconciliation_details = data["reconciliation_datas"]

                # reconciliation_details = data["reconciliation_datas"]
                for detail in reconciliation_details:
                    id = detail["id"]
                    Date = detail["Date"]
                    TransactionType = detail["TransactionType"]
                    Debit = detail["Debit"]
                    Credit = detail["Credit"]
                    VoucherMasterID = detail["VoucherMasterID"]
                    PaymentGateway = detail["PaymentGateway"]
                    PaymentStatus = True
                    RelativeLedgerName = detail["RelativeLedgerName"]
                    RelativeLedgerID = detail["RelatedLedgerID"]
                    LedgerPostingUnqid = detail["LedgerPostingUnqid"]
                    IsReconciliate = detail["IsReconciliate"]

                    ledger_post_inst = None
                    if (
                        IsReconciliate == True
                        and models.LedgerPosting.objects.filter(
                            id=LedgerPostingUnqid
                        ).exists()
                    ):
                        ledger_post_inst = models.LedgerPosting.objects.get(
                            id=LedgerPostingUnqid
                        )
                        if Type == "reconciliate":
                            ledger_post_inst.IsReconciliated = True
                            ledger_post_inst.save()
                    BankReconciliationDetailsID = get_auto_idDetail(
                        models.BankReconciliationDetails, BranchID, CompanyID
                    )
                    models.BankReconciliationDetails.objects.create(
                        CompanyID=CompanyID,
                        BankReconciliationDetailsID=BankReconciliationDetailsID,
                        BranchID=BranchID,
                        Date=Date,
                        TransactionType=TransactionType,
                        Debit=Debit,
                        Credit=Credit,
                        BankReconciliationMasterID=BankReconciliationMasterID,
                        VoucherMasterID=VoucherMasterID,
                        PaymentGateway=PaymentGateway,
                        PaymentStatus=PaymentStatus,
                        LedgerPostid=ledger_post_inst,
                        RelativeLedgerName=RelativeLedgerName,
                        RelativeLedgerID=RelativeLedgerID,
                        IsReconciliate=IsReconciliate,
                    )

                    models.BankReconciliationDetails_Log.objects.create(
                        CompanyID=CompanyID,
                        TransactionID=BankReconciliationDetailsID,
                        BranchID=BranchID,
                        Date=Date,
                        TransactionType=TransactionType,
                        Debit=Debit,
                        Credit=Credit,
                        BankReconciliationMasterID=BankReconciliationMasterID,
                        VoucherMasterID=VoucherMasterID,
                        PaymentGateway=PaymentGateway,
                        PaymentStatus=PaymentStatus,
                        LedgerPostid=ledger_post_inst,
                        RelativeLedgerName=RelativeLedgerName,
                        RelativeLedgerID=RelativeLedgerID,
                        IsReconciliate=IsReconciliate,
                    )

                response_data = {
                    "StatusCode": 6000,
                    "message": "Bank Reconciliation Updated Successfully!!!",
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "not found!",
                }
            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
        }

        activity_id = activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Bank Reconciliation",
            "Create",
            str(e),
            err_descrb,
        )
        body_params = str(request.data)
        models.Activity_Log.objects.filter(id=activity_id).update(
            body_params=body_params
        )
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def undo_reconsiliation(request, pk):
    CompanyID = request.data["CompanyID"]
    CompanyID = get_company(CompanyID)
    PriceRounding = request.data["PriceRounding"]
    BranchID = request.data["BranchID"]

    if models.BankReconciliationMaster.objects.filter(pk=pk).exists():
        instance = models.BankReconciliationMaster.objects.get(pk=pk)
        instance.Type = "draft"
        instance.save()
        BankReconciliationMasterID = instance.BankReconciliationMasterID
        if models.BankReconciliationDetails.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            BankReconciliationMasterID=BankReconciliationMasterID,
        ).exists():
            details = models.BankReconciliationDetails.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                BankReconciliationMasterID=BankReconciliationMasterID,
            )
            for i in details:
                if i.IsReconciliate == True:
                    LedgerPostid = i.LedgerPostid
                    LedgerPostid.IsReconciliated = False
                    LedgerPostid.save()

        response_data = {
            "StatusCode": 6000,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "datas not found!"}
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_reconsiliation_list(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]
    search_value = data["search_value"]
    length = data["length"]

    if models.BankReconciliationMaster.objects.filter(
        CompanyID=CompanyID, BranchID=BranchID
    ).exists():
        instances = models.BankReconciliationMaster.objects.filter(
            (Q(VoucherNo__icontains=search_value))
            | (Q(Date__icontains=search_value))
            | (Q(BankName__in=search_value))
        )
        if length < 3:
            instances = instances[:10]

        serialized = serializers.BankReconciliationListSerializer(
            instances,
            many=True,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )

        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {
            "StatusCode": 6001,
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def bank_reconsiliation_report(request):
    CompanyID = request.data["CompanyID"]
    CompanyID = get_company(CompanyID)
    LedgerID = request.data["BankID"]
    BranchID = request.data["BranchID"]
    FromDate = request.data["FromDate"]
    ToDate = request.data["ToDate"]
    PriceRounding = request.data["PriceRounding"]

    print(CompanyID, LedgerID, BranchID, FromDate, ToDate, PriceRounding)
    if models.LedgerPosting.objects.filter(
        CompanyID=CompanyID,
        BranchID=BranchID,
        LedgerID=LedgerID,
        VoucherType__in=["BR", "BP", "SI", "SR", "PI", "PR", "CP", "CR"],
        Date__lte=ToDate,
    ).exists():
        instance = models.LedgerPosting.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            LedgerID=LedgerID,
            VoucherType__in=["BR", "BP", "SI", "SR", "PI", "PR", "CP", "CR"],
            Date__gte=FromDate,
            Date__lte=ToDate,
        )
        unmatched_instance = instance.filter(IsReconciliated=False)
        matched_instance = instance.filter(IsReconciliated=True)
        total_matched_values = 0
        total_unmatched_values = 0
        print(unmatched_instance, "unmatched_instance")
        print(matched_instance, "matched_instance")
        if matched_instance:
            # Matched Transactions
            total_matched_debit = matched_instance.aggregate(Sum("Debit"))
            total_matched_credit = matched_instance.aggregate(Sum("Credit"))
            if total_matched_debit:
                total_matched_debit = total_matched_debit["Debit__sum"]
            if total_matched_credit:
                total_matched_credit = total_matched_credit["Credit__sum"]
            total_matched_values = total_matched_debit - total_matched_credit
        matched_serialized = serializers.BankReconciliationReportSerializer(
            matched_instance,
            many=True,
            context={"request": request, "CompanyID": CompanyID},
        )
        if unmatched_instance:
            # UnMatched Transactions
            total_unmatched_debit = unmatched_instance.aggregate(Sum("Debit"))
            total_unmatched_credit = unmatched_instance.aggregate(Sum("Credit"))
            if total_unmatched_debit:
                total_unmatched_debit = total_unmatched_debit["Debit__sum"]
            if total_unmatched_credit:
                total_unmatched_credit = total_unmatched_credit["Credit__sum"]
            total_unmatched_values = total_unmatched_debit - total_unmatched_credit
        unmatched_serialized = serializers.BankReconciliationReportSerializer(
            unmatched_instance,
            many=True,
            context={"request": request, "CompanyID": CompanyID},
        )
        # OpeningBalance===========
        opening_stock_balance = query_openingBalance_data(
            request.data["CompanyID"],
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            LedgerID,
            "",
        )
        op_balance_row = pd.DataFrame(opening_stock_balance, index=[0])
        # calculating Debit and Credit with opening balance
        op_balance = 0
        if op_balance_row.at[0, 7]:
            op_balance = round(op_balance_row.at[0, 7], PriceRounding)
        # closingBalance===========
        closing_balance = query_closingBalance_data(
            request.data["CompanyID"],
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            LedgerID,
            "",
        )
        clos_balance_row = pd.DataFrame(closing_balance, index=[0])
        # calculating Debit and Credit with closing balance
        clos_balance = 0
        if clos_balance_row.at[0, 7]:
            clos_balance = round(clos_balance_row.at[0, 7], PriceRounding)
        # Reconsiliation status summary
        reconsiliation_status_summary = {
            "OpeningBalance": op_balance,
            "ClosingBalance": clos_balance,
            "total_value_of_matched_transactions_for_this_period": total_matched_values,
            "total_value_of_unmatched_statements": total_unmatched_values,
            "total_value_of_unmatched_statements_in_viknbooks": 0,
        }
        response_data = {
            "StatusCode": 6000,
            "reconsiliation_status_summary": reconsiliation_status_summary,
            "matched_transactions": matched_serialized.data,
            "unmatched_transactions": unmatched_serialized.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "datas not found!"}
        return Response(response_data, status=status.HTTP_200_OK)
