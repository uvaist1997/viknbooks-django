from brands.models import AccountGroup, AccountGroup_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.dashboard import serializers
from api.v3.ledgerPosting.serializers import ListSerializerforProfitAndLoss, ProfitAndLossSerializer
from api.v3.dashboard.functions import generate_serializer_errors
from rest_framework import status
from api.v3.dashboard.functions import get_auto_id
from django.shortcuts import get_object_or_404
from main.functions import get_company, activity_log
from api.v3.ledgerPosting.functions import convertOrderdDict
from brands import models
import datetime
from itertools import chain


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def customer(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instances = None
    if models.Parties.objects.filter(CompanyID=CompanyID, PartyType="customer").exists():
        instances = models.Parties.objects.filter(
            CompanyID=CompanyID, PartyType="customer")
    serialized = serializers.CustomerSerializer(
        instances, many=True, context={"CompanyID": CompanyID})
    data = []
    count = 0
    for i in serialized.data:
        if count <= 9:
            id = i['id']
            PartyName = i['PartyName']
            LedgerID = i['LedgerID']
            OpeningBalance = i['OpeningBalance']
            Balance = i['Balance']
            PartyImage = i['PartyImage']
            PartyImage = i['PartyImage']
            dic = {
                'id': id,
                'PartyName': PartyName,
                'LedgerID': LedgerID,
                'OpeningBalance': OpeningBalance,
                'Balance': Balance,
                'PartyImage': PartyImage,
            }
            data.append(dic)
            count += 1
    sorted_data = sorted(data, key=lambda i: i['Balance'], reverse=True)
    # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountGroup', 'View', 'AccountGroup List', 'The user viewed AccountGroups')
    response_data = {
        "StatusCode": 6000,
        # "data": str(combined_results),
        # "type" : str(type(combined_results)),
        "data": sorted_data
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def supplier(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']

    instances = None
    if models.Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PartyType="supplier").exists():
        instances = models.Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, PartyType="supplier")
    serialized = serializers.CustomerSerializer(instances, many=True, context={
                                                "CompanyID": CompanyID, "BranchID": BranchID})
    data = []
    count = 0
    for i in serialized.data:
        if count <= 9:
            id = i['id']
            PartyName = i['PartyName']
            LedgerID = i['LedgerID']
            OpeningBalance = i['OpeningBalance']
            Balance = i['Balance']
            PartyImage = i['PartyImage']
            PartyImage = i['PartyImage']
            dic = {
                'id': id,
                'PartyName': PartyName,
                'LedgerID': LedgerID,
                'OpeningBalance': OpeningBalance,
                'Balance': Balance,
                'PartyImage': PartyImage,
            }
            data.append(dic)
            count += 1
    sorted_data = sorted(data, key=lambda i: i['Balance'], reverse=True)
    # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountGroup', 'View', 'AccountGroup List', 'The user viewed AccountGroups')
    response_data = {
        "StatusCode": 6000,
        # "data": str(combined_results),
        # "type" : str(type(combined_results)),
        "data": sorted_data
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def accounts(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']

    instances = None
    if models.Bank.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        # instances = models.Bank.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
        instances = models.AccountLedger.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder__in=[8, 9])
    serialized = serializers.BankSerializer(instances, many=True, context={
                                            "CompanyID": CompanyID, "BranchID": BranchID})
    data = []
    count = 0
    for i in serialized.data:
        if count <= 9:
            id = i['id']
            LedgerName = i['LedgerName']
            OpeningBalance = i['OpeningBalance']
            Balance = i['Balance']
            dic = {
                'id': id,
                'LedgerName': LedgerName,
                'OpeningBalance': OpeningBalance,
                'Balance': Balance,
            }
            data.append(dic)
            count += 1
    sorted_data = sorted(data, key=lambda i: i['Balance'], reverse=True)
    # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountGroup', 'View', 'AccountGroup List', 'The user viewed AccountGroups')
    response_data = {
        "StatusCode": 6000,
        "data": sorted_data,
        # "type" : str(type(combined_results)),
        # "data" : serialized.data
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def profit_and_loss(request):
    data = request.data
    CompanyID = data['CompanyID']
    PriceRounding = data['PriceRounding']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = int(PriceRounding)
    serialized1 = ListSerializerforProfitAndLoss(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']
        start_month = int(FromDate.split("-")[1])
        end_month = int(ToDate.split("-")[1])
        start_day = int(FromDate.split("-")[2])
        end_day = int(ToDate.split("-")[2])
        start_year = int(FromDate.split("-")[0])
        end_year = int(ToDate.split("-")[0])
        print(start_month)
        print(end_month)
        print("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
        Direct_Expenses_Array = []
        Indirect_Expenses_Array = []
        Direct_Income_Array = []
        Indirect_Income_Array = []

        dirExArr = []

        name_exist_dirExp = {}
        name_exist_detailed_dirExp = {}
        dic_exGrp_dirExp = {}
        final_direct_expence_arr = []

        name_exist_indirExp = {}
        name_exist_detailed_indirExp = {}
        dic_exGrp_indirExp = {}
        final_indirect_expence_arr = []

        name_exist_dirInc = {}
        name_exist_detailed_dirInc = {}
        dic_exGrp_dirInc = {}
        final_direct_income_arr = []

        name_exist_indirInc = {}
        name_exist_detailed_indirInc = {}
        dic_exGrp_indirInc = {}
        final_indirect_income_arr = []
        Direct_difference = 0
        # DirExPCons = []
        # inDirIncCons = []
        # inDirExpCons = []
        # DirIncCons = []
        TotalAvgValueOpening = 0
        TotalAvgValueClosing = 0
        dashboard_array = []
        month_list = []
        purchase_list = []
        profit_list = []
        sales_list = []
        # my_date = datetime.datetime.strptime(my_string, "%Y-%m-%d").date()
        from_date = datetime.datetime.strptime(FromDate, "%Y-%m-%d").date()
        to_date = datetime.datetime.strptime(
            FromDate, "%Y-%m-%d").date()+datetime.timedelta(31)
        for month in range(12):
            # from_date = f'{start_year}-{month}-{start_day}'
            # to_date = f'{start_year}-{month+1}-{start_day}'
            # if start_month <= month:
            if models.LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=from_date, Date__lte=to_date).exists():

                TotalCoast = 0
                TotalDirectExpense = 0
                TotalDirectIncome = 0
                TotalIndirectExpense = 0
                TotalInDirectIncome = 0
                test_arr = []
                instances = models.LedgerPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=from_date, Date__lte=to_date)
                ledger_ids = instances.values_list('LedgerID')
                for ledger_id in ledger_ids:
                    if ledger_id[0] not in test_arr:
                        test_arr.append(ledger_id[0])

                account_ledger = models.AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerID__in=test_arr)
                serialized = ProfitAndLossSerializer(
                    account_ledger, many=True, context={"CompanyID": CompanyID})

                orderdDict = serialized.data
                jsnDatas = convertOrderdDict(orderdDict)

                # TotalAvgValueOpening = 0
                if models.Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
                    product_instances_OS = models.Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")

                    for pi in product_instances_OS:
                        ProductID = pi.ProductID
                        if models.StockPosting.objects.filter(ProductID=ProductID, Date__lt=from_date, CompanyID=CompanyID).exists():
                            stock_instance_OS = models.StockPosting.objects.filter(
                                ProductID=ProductID, Date__lt=from_date, CompanyID=CompanyID)
                            QtyInRate = 0
                            QtyOutTot = 0
                            QtyInTot = 0
                            for si in stock_instance_OS:
                                QtyInRate += (float(si.QtyIn) * float(si.Rate))
                                QtyInTot += float(si.QtyIn)
                                QtyOutTot += float(si.QtyOut)

                            stock = float(QtyInTot) - float(QtyOutTot)

                            AvgRate = 0
                            if QtyInTot > 0:
                                AvgRate = float(QtyInRate) / float(QtyInTot)

                            TotalAvgValueOpening += float(stock) * \
                                float(AvgRate)

                        if models.StockPosting.objects.filter(ProductID=ProductID, Date__gte=from_date, Date__lte=to_date, CompanyID=CompanyID, VoucherType="OS").exists():
                            stock_instance_OS = models.StockPosting.objects.filter(
                                ProductID=ProductID, Date__gte=from_date, Date__lte=to_date, CompanyID=CompanyID, VoucherType="OS")
                            QtyInRate = 0
                            QtyOutTot = 0
                            QtyInTot = 0
                            for si in stock_instance_OS:
                                QtyInRate += (float(si.QtyIn) * float(si.Rate))
                                QtyInTot += float(si.QtyIn)
                                QtyOutTot += float(si.QtyOut)

                            stock = float(QtyInTot) - float(QtyOutTot)

                            AvgRate = 0
                            if QtyInTot > 0:
                                AvgRate = float(QtyInRate) / float(QtyInTot)

                            TotalAvgValueOpening += float(stock) * \
                                float(AvgRate)

                name_exist_dirExp['Opening Stock'] = {
                    'Balance': float(TotalAvgValueOpening)
                }

                # TotalAvgValueClosing = 0

                if models.Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
                    product_instances_CS = models.Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")

                    for pi in product_instances_CS:
                        ProductID = pi.ProductID

                        if models.StockPosting.objects.filter(ProductID=ProductID, Date__lte=to_date, CompanyID=CompanyID).exists():
                            stock_instance_CS = models.StockPosting.objects.filter(
                                ProductID=ProductID, Date__lte=to_date, CompanyID=CompanyID)
                            QtyInRate = 0
                            QtyOutTot = 0
                            QtyInTot = 0
                            for si in stock_instance_CS:
                                QtyInRate += (float(si.QtyIn) * float(si.Rate))
                                QtyInTot += float(si.QtyIn)
                                QtyOutTot += float(si.QtyOut)

                            stock = float(QtyInTot) - float(QtyOutTot)

                            AvgRate = 0
                            if QtyInTot > 0:
                                AvgRate = float(QtyInRate) / float(QtyInTot)

                            TotalAvgValueClosing += float(stock) * \
                                float(AvgRate)

                test_dicT = {}

                for i in jsnDatas:
                    LedgerName = i['LedgerName']
                    LedgerID = i['LedgerID']
                    GroupUnder = i['GroupUnder']
                    Balance = i['Balance']
                    if GroupUnder == 'Direct Expenses':
                        Group_Under = models.AccountLedger.objects.get(
                            BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                        Group_name = models.AccountGroup.objects.get(
                            AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                        ledgerpost_ins = models.LedgerPosting.objects.filter(
                            LedgerID=LedgerID, Date__range=(from_date, to_date), CompanyID=CompanyID)

                        dir_exp_Tot_Credit = 0
                        dir_exp_Tot_Debit = 0
                        for lpi in ledgerpost_ins:
                            dir_exp_Tot_Debit = + float(lpi.Debit)
                            dir_exp_Tot_Credit = + float(lpi.Credit)
                            dir_exp_balance = float(
                                dir_exp_Tot_Debit) - float(dir_exp_Tot_Credit)

                            dic_exGrp_dirExp = {"GroupName": str(
                                Group_name), "Balance": float(dir_exp_balance)}

                        if not Group_name in name_exist_dirExp:
                            dic_exGrp_dirExp = {
                                "Balance": float(Balance)
                            }
                            name_exist_dirExp[Group_name] = dic_exGrp_dirExp
                        else:
                            b = name_exist_dirExp[Group_name]["Balance"]
                            name_exist_dirExp[Group_name]["Balance"] = b + \
                                float(Balance)
                        TotalDirectExpense += Balance
                        Direct_Expenses_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                      "Balance": Balance, "GroupUnder": GroupUnder, }

                        if not Group_name in name_exist_detailed_dirExp:
                            name_exist_detailed_dirExp[Group_name] = []
                        name_exist_detailed_dirExp[Group_name].append(
                            Direct_Expenses_dictionary)
                    elif GroupUnder == 'Indirect Expenses':

                        Group_Under = models.AccountLedger.objects.get(
                            BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                        Group_name = models.AccountGroup.objects.get(
                            AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                        ledgerpost_ins = models.LedgerPosting.objects.filter(
                            LedgerID=LedgerID, Date__range=(from_date, to_date), CompanyID=CompanyID)

                        indir_exp_Tot_Credit = 0
                        indir_exp_Tot_Debit = 0
                        for lpi in ledgerpost_ins:
                            indir_exp_Tot_Debit = + lpi.Debit
                            dir_exp_Tot_Credit = + lpi.Credit
                            dir_exp_balance = indir_exp_Tot_Debit - indir_exp_Tot_Credit

                            dic_exGrp_indirExp = {"GroupName": str(
                                Group_name), "Balance": float(dir_exp_balance)}

                        if not Group_name in name_exist_indirExp:
                            dic_exGrp_indirExp = {
                                "Balance": float(Balance),
                            }
                            name_exist_indirExp[Group_name] = dic_exGrp_indirExp
                        else:
                            b = name_exist_indirExp[Group_name]["Balance"]
                            name_exist_indirExp[Group_name]["Balance"] = b + \
                                float(Balance)

                        TotalIndirectExpense += Balance
                        Indirect_Expenses_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                        "Balance": Balance, "GroupUnder": GroupUnder, }

                        if not Group_name in name_exist_detailed_indirExp:
                            name_exist_detailed_indirExp[Group_name] = []
                        name_exist_detailed_indirExp[Group_name].append(
                            Indirect_Expenses_dictionary)

                    elif GroupUnder == 'Direct Income':
                        if LedgerID == 86:
                            Balance = -(Balance)
                        if LedgerID == 85:
                            Balance = abs(Balance)
                        if LedgerID == 83:
                            Balance = abs(Balance)

                        Group_Under = models.AccountLedger.objects.get(
                            BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                        Group_name = models.AccountGroup.objects.get(
                            AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                        ledgerpost_ins = models.LedgerPosting.objects.filter(
                            LedgerID=LedgerID, Date__range=(from_date, to_date), CompanyID=CompanyID)

                        dir_inc_Tot_Credit = 0
                        dir_inc_Tot_Debit = 0
                        for lpi in ledgerpost_ins:

                            dir_inc_Tot_Debit = + lpi.Debit
                            dir_inc_Tot_Credit = + lpi.Credit

                            dir_inc_balance = dir_inc_Tot_Debit - dir_inc_Tot_Credit

                            dir_inc_balance = dir_inc_balance

                            dic_exGrp_dirInc = {"GroupName": str(
                                Group_name), "Balance": float(dir_inc_balance)}
                        if not Group_name in name_exist_dirInc:
                            dic_exGrp_dirInc = {
                                "Balance": float(Balance),
                            }
                            name_exist_dirInc[Group_name] = dic_exGrp_dirInc
                        else:
                            b = name_exist_dirInc[Group_name]["Balance"]
                            name_exist_dirInc[Group_name]["Balance"] = b + \
                                float(Balance)

                        name_exist_dirInc['Closing Stock'] = {
                            'Balance': TotalAvgValueClosing
                        }

                        TotalDirectIncome += Balance

                        Direct_Income_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                    "Balance": Balance, "GroupUnder": GroupUnder, }

                        if not Group_name in name_exist_detailed_dirInc:
                            name_exist_detailed_dirInc[Group_name] = []
                        name_exist_detailed_dirInc[Group_name].append(
                            Direct_Income_dictionary)

                    elif GroupUnder == 'Indirect Income':

                        Group_Under = models.AccountLedger.objects.get(
                            BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                        Group_name = models.AccountGroup.objects.get(
                            AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                        ledgerpost_ins = models.LedgerPosting.objects.filter(
                            LedgerID=LedgerID, Date__range=(from_date, to_date), CompanyID=CompanyID)

                        indir_inc_Tot_Credit = 0
                        indir_inc_Tot_Debit = 0
                        for lpi in ledgerpost_ins:
                            indir_inc_Tot_Debit = + lpi.Debit
                            indir_inc_Tot_Credit = + lpi.Credit
                            indir_inc_balance = indir_inc_Tot_Debit - indir_inc_Tot_Credit

                            dic_exGrp_indirInc = {"GroupName": str(
                                Group_name), "Balance": float(abs(indir_inc_balance))}

                        if not Group_name in name_exist_indirInc:
                            dic_exGrp_indirInc = {
                                "Balance": float(Balance),
                            }
                            name_exist_indirInc[Group_name] = dic_exGrp_indirInc
                        else:
                            b = name_exist_indirInc[Group_name]["Balance"]
                            name_exist_indirInc[Group_name]["Balance"] = b + \
                                float(Balance)

                        TotalInDirectIncome += abs(Balance)
                        Indirect_Income_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                      "Balance": abs(Balance), "GroupUnder": GroupUnder, }

                        if not Group_name in name_exist_detailed_indirInc:
                            name_exist_detailed_indirInc[Group_name] = []
                        name_exist_detailed_indirInc[Group_name].append(
                            Indirect_Income_dictionary)

                final_direct_expence_arr.append(name_exist_dirExp)

                final_direct_income_arr.append(name_exist_dirInc)

                final_indirect_expence_arr.append(name_exist_indirExp)

                final_indirect_income_arr.append(name_exist_indirInc)

                Direct_Expenses_Array.append(name_exist_detailed_dirExp)
                Indirect_Expenses_Array.append(name_exist_detailed_indirExp)
                Direct_Income_Array.append(name_exist_detailed_dirInc)
                Indirect_Income_Array.append(name_exist_detailed_indirInc)

                if models.StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=from_date, Date__lte=to_date).exists():
                    stock_instances = models.StockRate.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Date__gte=from_date, Date__lte=to_date)
                    for stock_instance in stock_instances:
                        TotalCoast += stock_instance.Cost

                is_DirectexpenseGreater = False
                is_IndirectexpenseGreater = False
                is_DirectincomeGreater = False
                is_IndirectincomeGreater = False

                TotalDirectIncome = float(
                    TotalDirectIncome) + float(TotalAvgValueClosing)
                TotalDirectExpense = float(
                    TotalDirectExpense) + float(TotalAvgValueOpening)

                if TotalDirectIncome > TotalDirectExpense:
                    is_DirectincomeGreater = True
                    TotalDirect = TotalDirectIncome
                    Direct_difference = float(
                        TotalDirectIncome) - float(TotalDirectExpense)
                elif TotalDirectExpense > TotalDirectIncome:
                    is_DirectexpenseGreater = True
                    TotalDirect = TotalDirectExpense
                    Direct_difference = float(
                        TotalDirectExpense) - float(TotalDirectIncome)
                else:
                    TotalDirect = TotalDirectExpense
                    Direct_difference = 0

                if is_DirectincomeGreater == True:
                    TotalInDirectIncome = TotalInDirectIncome + Direct_difference

                if is_DirectexpenseGreater == True:
                    TotalIndirectExpense = TotalIndirectExpense + Direct_difference

                if TotalIndirectExpense > TotalInDirectIncome:
                    is_IndirectexpenseGreater = True
                    TotalIndirect = TotalIndirectExpense
                    Indirectdifference = float(
                        TotalIndirectExpense) - float(TotalInDirectIncome)
                elif TotalIndirectExpense < TotalInDirectIncome:

                    is_IndirectincomeGreater = True
                    TotalIndirect = TotalInDirectIncome
                    Indirectdifference = float(
                        TotalInDirectIncome) - float(TotalIndirectExpense)
                else:
                    Indirectdifference = 0
                    TotalIndirect = TotalIndirectExpense

                DirExPCons = []
                for i in final_direct_expence_arr[0]:
                    if i == "Purchase":
                        myDic = {
                            'GroupName': i,
                            'Balance': float(round(final_direct_expence_arr[0][i]['Balance'], PriceRounding))
                        }
                        DirExPCons.append(myDic)
                    # else:
                    #     myDic = {
                    #         'GroupName': "Purchase",
                    #         'Balance': 0
                    #     }
                    #     DirExPCons.append(myDic)

                print("===========================")
                print(final_direct_income_arr[0])
                DirIncCons = []
                if final_direct_income_arr[0]:
                    for i in final_direct_income_arr[0]:
                        print("----------------------")
                        print(i)
                        if i == "Sales":
                            myDic = {
                                'GroupName': i,
                                'Balance': float(round(final_direct_income_arr[0][i]['Balance'], PriceRounding))
                            }
                            DirIncCons.append(myDic)
                        # else:
                        #     myDic = {
                        #         'GroupName': i,
                        #         'Balance': float(round(final_direct_income_arr[0][i]['Balance'], PriceRounding))
                        #     }
                        #     DirIncCons.append(myDic)
                else:
                    myDic = {
                        'GroupName': "Closing Stock",
                        'Balance': float(round(TotalAvgValueClosing, PriceRounding))
                    }
                    DirIncCons.append(myDic)

                inDirIncCons = []
                inDirExpCons = []
                for i in final_indirect_income_arr[0]:
                    myDic = {
                        'GroupName': i,
                        'Balance': float(round(final_indirect_income_arr[0][i]['Balance'], PriceRounding))
                    }
                    inDirIncCons.append(myDic)

                for i in final_indirect_expence_arr[0]:
                    myDic = {
                        'GroupName': i,
                        'Balance': float(round(final_indirect_expence_arr[0][i]['Balance'], PriceRounding))
                    }
                    inDirExpCons.append(myDic)
                # month_parse = datetime.datetime(int(start_year),int(month),int(start_day))
                # month_parse = datetime.datetime(from_date)
                month_list.append(from_date.strftime("%b"))
                profit_list.append(Indirectdifference)
                dash_dict = {
                    "DirExPCons": DirExPCons,
                    "DirIncCons": DirIncCons,
                    "Profit": Indirectdifference,
                    "month": from_date.strftime("%b"),
                }
                dashboard_array.append(dash_dict)
                from_date += datetime.timedelta(31)
                to_date += datetime.timedelta(62)
        for direxp in dashboard_array:
            month = direxp["month"]
            if direxp["DirExPCons"]:
                for purchase in direxp["DirExPCons"]:
                    purchase_balance = purchase["Balance"]
                    purchase_list.append(purchase_balance)
                    # purchase_list.append(month)
            else:
                purchase_list.append(0)

        for direxp in dashboard_array:
            if direxp["DirIncCons"]:
                for sales in direxp["DirIncCons"]:
                    if sales["GroupName"] == "Sales":
                        sales_balance = sales["Balance"]
                        sales_list.append(sales_balance)
            else:
                sales_list.append(0)

        response_data = {
            "StatusCode": 6000,
            # "dashboard_array": dashboard_array,
            "month_list": month_list,
            "purchase_list": purchase_list,
            "profit_list": profit_list,
            "sales_list": sales_list,
        }
        return Response(response_data, status=status.HTTP_200_OK)
        # else:
        #     response_data = {
        #         "StatusCode": 6001,
        #         "message": "No Datas During this Time Periods!"
        #     }
        #     return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid Dates!!!"
        }
        return Response(response_data, status=status.HTTP_200_OK)
