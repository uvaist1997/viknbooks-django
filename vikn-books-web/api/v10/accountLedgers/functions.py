import random
import re
from sre_parse import State
import string
from decimal import Decimal

from django.db.models import Max
from django.http import HttpResponse

from brands import models as table
from main.functions import converted_float


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
    LedgerID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(CompanyID=CompanyID).aggregate(
        Max("LedgerID")
    )
    if model.objects.filter(CompanyID=CompanyID).exists():
        max_value = model.objects.filter(CompanyID=CompanyID).aggregate(Max("LedgerID"))
        print(model.objects.filter(CompanyID=CompanyID), "max_value")
        if max_value:
            max_ledgerId = max_value.get("LedgerID__max", 0)

            LedgerID = max_ledgerId + 1
        else:
            LedgerID = 1
    return LedgerID


def get_LedgerCode(model, BranchID, CompanyID):
    LedgerCode = "AL1"
    if model.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
        latest_LedgerCode = model.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID).order_by("LedgerID").last()
        LedgerCode = latest_LedgerCode.LedgerCode
        if not LedgerCode.isdecimal():
            temp = re.compile("([a-zA-Z]+)([0-9]+)")
            if temp.match(LedgerCode):
                res = temp.match(LedgerCode).groups()
                code, number = res
                number = int(number) + 1
                LedgerCode = str(code) + str(number)
            else:
                if LedgerCode == '':
                        LedgerCode = "0"
                if re.findall(r'\d+', LedgerCode):
                    LedgerCodeNumber = re.findall(r'\d+', LedgerCode)[-1]
                    rest = LedgerCode.split(LedgerCodeNumber)[0]
                    LedgerCode = str(int(LedgerCodeNumber) +
                                        1).zfill(len(LedgerCodeNumber))
                    LedgerCode = str(rest) + str(LedgerCode)
                else:
                    LedgerCode = str(LedgerCode) + str(1)
        else:
            code = str(float(LedgerCode) + 1)
            code = code.rstrip('0').rstrip('.') if '.' in code else code
            LedgerCode = code.zfill(len(LedgerCode))
    return LedgerCode


# def get_auto_LedgerPostid(model, BranchID, CompanyID):
#     LedgerPostingID = 1
#     # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
#     # latest_auto_id = model.objects.filter(
#     #     CompanyID=CompanyID).aggregate(Max('LedgerPostingID'))
#     if model.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
#         max_value = model.objects.filter(
#             BranchID=BranchID, CompanyID=CompanyID
#         ).aggregate(Max("LedgerPostingID"))
#         if max_value:
#             max_ledgerPostingId = max_value.get("LedgerPostingID__max", 0)
#             LedgerPostingID = max_ledgerPostingId + 1
#         else:
#             LedgerPostingID = 1
#     return LedgerPostingID

def get_auto_LedgerPostid(model, BranchID, CompanyID):
    LedgerPostingID = 1
    if model.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
        instance = model.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID).order_by('LedgerPostingID').last()
        LedgerPostingID = instance.LedgerPostingID + 1
    return LedgerPostingID


def get_auto_idfor_party(model, BranchID, CompanyID):
    PartyID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(CompanyID=CompanyID).aggregate(Max("PartyID"))
    if model.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
        max_value = model.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID
        ).aggregate(Max("PartyID"))
        if max_value:
            max_partyId = max_value.get("PartyID__max", 0)
            PartyID = max_partyId + 1
        else:
            PartyID = 1
    return PartyID


def UpdateLedgerBalance(
    CompanyID, BranchID, LedgerID, VoucherMasterID, VoucherType, Amount, CrOrDr, action
):
    print(
        CompanyID,
        BranchID,
        LedgerID,
        VoucherMasterID,
        VoucherType,
        Amount,
        CrOrDr,
        action,
    )
    if action == "create":
        if table.AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            instance = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID
            )
            # instance_balance = instance.Balance
            # if not instance_balance:
            #     instance_balance = 0
            updated_balance = 0
            instance_balance = 0
            if instance.Balance:
                instance_balance = instance.Balance
            if not Amount:
                Amount = 0
            if CrOrDr == "Dr":
                updated_balance = converted_float(instance_balance) + converted_float(
                    Amount
                )
            else:
                updated_balance = converted_float(instance_balance) - converted_float(
                    Amount
                )

            instance.Balance = updated_balance
            instance.save()
    else:
        if table.LedgerPosting.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            VoucherMasterID=VoucherMasterID,
            VoucherType=VoucherType,
        ).exists():
            ledger_ins = table.LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                VoucherMasterID=VoucherMasterID,
                VoucherType=VoucherType,
            )
            for l in ledger_ins:
                LedgerID = l.LedgerID
                balance = converted_float(l.Debit) - converted_float(l.Credit)
                instance = table.AccountLedger.objects.get(
                    CompanyID=CompanyID, LedgerID=LedgerID
                )
                instance_balance = instance.Balance
                if not instance_balance:
                    instance_balance = 0
                updated_balance = converted_float(instance_balance) - converted_float(
                    balance
                )
                instance.Balance = updated_balance
                instance.save()

    return ""


def get_shippingAddress(CompanyID, BranchID, LedgerID, types="ShippingAddress"):
    addresses = []
    # types = ["ShippingAddressAdded", "ShippingAddress"]
    if table.UserAdrress.objects.filter(
        CompanyID=CompanyID, Party__LedgerID=LedgerID, Type=types
    ).exists():
        address_instances = table.UserAdrress.objects.filter(
            CompanyID=CompanyID, Party__LedgerID=LedgerID, Type=types
        )
        for a in address_instances:
            Attention = a.Attention
            Address1 = a.Address1
            Address2 = a.Address2
            City = a.City
            District = a.District
            state = a.state
            country = a.country
            PostalCode = a.PostalCode
            Mobile = a.Mobile
            state_name = ""
            Country_Name = ""
            CustomerStateName = ""
            state_id = None
            country_id = None
            if state:
                state_name = state.Name
                state_id = state.id
            if country:
                Country_Name = country.Country_Name
                country_id = country.id
            if table.Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
                pary_ins = table.Parties.objects.filter(
                    CompanyID=CompanyID, LedgerID=LedgerID
                ).first()

                if pary_ins.PlaceOfSupply and not pary_ins.PlaceOfSupply == "null":
                    CustomerState = pary_ins.PlaceOfSupply
                else:
                    CustomerState = pary_ins.State

                if CustomerState:
                    if table.State.objects.filter(id=CustomerState).exists():
                        CustomerStateName = table.State.objects.get(
                            id=CustomerState).Name
            BillingAddress = ""
            if Attention or Address1 or City or CustomerStateName or PostalCode:
                BillingAddress = (
                    str(Address1)
                    + str(", ")
                    + str(City)
                    + str(", ")
                    + str(CustomerStateName)
                    + str(", ")
                    + str(PostalCode)
                )
            addresses.append(
                {
                    "id": a.id,
                    "Attention": Attention,
                    "Address1": BillingAddress,
                    "Address2": Address2,
                    "City": City,
                    "state": state_id,
                    "country": country_id,
                    "Mobile": Mobile,
                    "CompanyID": CompanyID.id,
                    "BranchID": BranchID,
                    "LedgerID": LedgerID,
                    "PostalCode": PostalCode,
                    "District": District,
                }
            )
    else:
        if table.Parties.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            party = table.Parties.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)
            Attention_Shipping = party.Attention_Shipping
            Address1_Shipping = party.Address1_Shipping
            Address2_Shipping = party.Address2_Shipping
            State_Shipping = party.State_Shipping
            Country_Shipping = party.Country_Shipping
            City_Shipping = party.City_Shipping
            Phone_Shipping = party.Phone_Shipping
            state_Shipping = None
            country_Shipping = None
            if State_Shipping:
                state_Shipping = table.State.objects.get(id=State_Shipping)
            if Country_Shipping:
                country_Shipping = table.Country.objects.get(id=Country_Shipping)

            if (
                Attention_Shipping
                or Address1_Shipping
                or Address2_Shipping
                or State_Shipping
                or Country_Shipping
                or City_Shipping
                or Phone_Shipping
            ):
                stateName = ""
                countryName = ""
                state = None
                country = None
                if state_Shipping:
                    stateName = state_Shipping.Name
                    state = state_Shipping.id
                if country_Shipping:
                    countryName = country_Shipping.Country_Name
                    country = state_Shipping.id
                addresses.append(
                    {
                        "id": party.id,
                        "Attention": Attention_Shipping,
                        "Address1": Address1_Shipping,
                        "Address2": Address2_Shipping,
                        "City": City_Shipping,
                        "state": state,
                        "country": country,
                        "Mobile": Phone_Shipping,
                        "CompanyID": CompanyID.id,
                        "BranchID": BranchID,
                        "LedgerID": LedgerID,
                    }
                )

    return addresses
