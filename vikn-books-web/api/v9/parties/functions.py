import json
import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
import re
import pandas as pd
from django.db import connection
from django.utils.translation import ugettext_lazy as _

def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def get_auto_id(model, BranchID, CompanyID):
    PartyID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('PartyID'))
    if model.objects.filter(CompanyID=CompanyID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID).aggregate(Max('PartyID'))
        if max_value:
            max_partyId = max_value.get('PartyID__max', 0)
            PartyID = max_partyId + 1
        else:
            PartyID = 1
    return PartyID

def get_auto_idLedger(AccountLedger, BranchID, CompanyID):
    LedgerID = 1
    if AccountLedger.objects.filter(CompanyID=CompanyID).exists():
        last_ins = AccountLedger.objects.filter(CompanyID=CompanyID).order_by('LedgerID').last()
        current_LedgerID = last_ins.LedgerID
        LedgerID = int(current_LedgerID) + 1
    return LedgerID


# def get_auto_idLedger(model, BranchID, CompanyID):
#     LedgerID = 1
#     if model.objects.filter(CompanyID=CompanyID).exists():
#         max_value = model.objects.filter(
#             CompanyID=CompanyID).aggregate(Max('LedgerID'))
#         if max_value:
#             max_ledgerId = max_value.get('LedgerID__max', 0)
#             LedgerID = max_ledgerId + 1
#     return LedgerID


def get_PartyCode(model, BranchID, CompanyID, PartyType):
    if PartyType == "customer":
        if model.objects.filter(CompanyID=CompanyID, PartyType=PartyType).exists():
            latest_PartyCode = model.objects.filter(
                CompanyID=CompanyID, PartyType=PartyType).order_by("PartyID").last()

            PartyCode = latest_PartyCode.PartyCode
            temp = re.compile("([a-zA-Z]+)([0-9]+)")
            if temp.match(PartyCode):
                res = temp.match(PartyCode).groups()
                code, number = res
                number = int(number) + 1
                PartyCode = str(code) + str(number)
        else:
            PartyCode = "CMR1"
        return PartyCode
    elif PartyType == "supplier":
        if model.objects.filter(CompanyID=CompanyID, PartyType=PartyType).exists():
            latest_PartyCode = model.objects.filter(
                CompanyID=CompanyID, PartyType=PartyType).order_by("PartyID").last()
            PartyCode = latest_PartyCode.PartyCode
            temp = re.compile("([a-zA-Z]+)([0-9]+)")
            if temp.match(PartyCode):
                res = temp.match(PartyCode).groups()
                code, number = res
                number = int(number) + 1
                PartyCode = str(code) + str(number)
        else:
            PartyCode = "SLR1"
        return PartyCode


def get_Allparties(CompanyID, UserID, PriceRounding, BranchID,PartyType):
    cursor = connection.cursor()
   
    # CashLedgers = tuple(CashLedgers,"OOOOOOOOOOOOOOOIIIIIIUUUUYYYy")
    dic = { 'CompanyID': CompanyID, 'UserID': UserID, 'PriceRounding': PriceRounding,
           'BranchID': BranchID, "PartyType": PartyType}

    cursor.execute('''
        select PT."PartyCode",PT."PartyName",PT."DisplayName",PT."OpeningBalance",AL."CrOrDr",PT."Attention",PT."Address1",PT."Address2",PT."City",

        CASE WHEN PT."State" = '' THEN
        ''
        ELSE
        (SELECT "Name" FROM public."state_state" WHERE "id" = (PT."State"::uuid) AND PT."BranchID" = %(BranchID)s AND PT."CompanyID_id" = %(CompanyID)s ) 
        END AS State,

        CASE WHEN PT."Country" = '' THEN
        ''
        ELSE
        (SELECT "Country_Name" FROM public."country_country" WHERE "id" = (PT."Country"::uuid) AND PT."BranchID" = %(BranchID)s AND PT."CompanyID_id" = %(CompanyID)s ) 
        END AS Country,
        
        PT."PostalCode",
        PT."OfficePhone",PT."WorkPhone",PT."Mobile",PT."WebURL",PT."Email",PT."IsBillwiseApplicable",PT."CreditPeriod",PT."CreditLimit",
        (SELECT "RouteName" FROM public."route_route" WHERE "RouteID" = PT."RouteID" AND "BranchID" = PT."BranchID" AND "CompanyID_id" = PT."CompanyID_id") AS RouteName,
        PT."VATNumber",PT."GSTNumber",PT."Tax1Number",PT."Tax2Number",PT."Tax3Number",PT."PanNumber",PT."BankName1",PT."AccountName1",PT."AccountNo1",PT."IBANOrIFSCCode1",PT."BankName2",PT."AccountName2",PT."AccountNo2",PT."IBANOrIFSCCode2",PT."CRNo"
     
        from  public."parties_parties" AS PT      
        INNER JOIN public."accountLedger_accountLedger" AS AL ON AL."LedgerID" = PT."LedgerID" AND AL."CompanyID_id" = PT."CompanyID_id"      
        WHERE PT."LedgerID" = AL."LedgerID"  AND PT."PartyType" = %(PartyType)s  AND PT."CompanyID_id" = %(CompanyID)s     

        ''', dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', '', 'NO DATA', '', '','', '','', '','', '','', '','', '','', '','', '','', '','', '','', '','', '','', '','','', '','', '','', '',)]

    df = pd.DataFrame(data)

    # adding Heading to frame
    df.columns = [
        str(('PartyCode')), str(('PartyName')), str(('DisplayName')), str(('OpeningBalance')), str(('CrOrDr')), str(('Attention')),str(('Address1')),str(('Address2'))
        ,str(('City')),str(('State')),str(('Country')),str(('PostalCode')),str(('OfficePhone')),str(('WorkPhone')),str(('Mobile')),str(('WebURL')),str(('Email')),
        str(('IsBillwiseApplicable')),str(('CreditPeriod')),str(('CreditLimit')),str(('RouteName')),str(('VATNumber')),str(('GSTNumber')),str(('Tax1Number')),str(('Tax2Number')),str(('Tax3Number')),str(('PanNumber')),str(('BankName1')),str(('AccountName1')),str(('AccountNo1')),str(('IBANOrIFSCCode1')),str(('BankName2')),str(('AccountName2')),str(('AccountNo2')),str(('IBANOrIFSCCode2')),str(('CRNumber'))]

    return df
