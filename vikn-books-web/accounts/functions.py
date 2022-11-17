import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from brands.models import AccountGroup, PaymentMaster, ReceiptMaster, PurchaseMaster, JournalMaster
import re


def generate_form_errors(args,formset=False):
    message = ''
    if not formset:
        for field in args:
            if field.errors:
                message += field.errors  + "|"
        for err in args.non_field_errors():
            message += str(err) + "|"

    elif formset:
        for form in args:
            for field in form:
                if field.errors:
                    message +=field.errors + "|"
            for err in form.non_field_errors():
                message += str(err) + "|"
    return message[:-1]


def get_auto_AccountGroupID(model,DataBase):
    AccountGroupID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('AccountGroupID'))
    
    if model.objects.filter().exists():
        max_value =  model.objects.filter().aggregate(Max('AccountGroupID'))
        
        if max_value:
            max_groupID = max_value.get('AccountGroupID__max', 0)
            AccountGroupID = max_groupID + 1
        else:
            AccountGroupID = 1

    return AccountGroupID



def get_auto_id(model,BranchID):
    BrandID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('BrandID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('BrandID'))
        

        if max_value:
            max_brandId = max_value.get('BrandID__max', 0)
            
            BrandID = max_brandId + 1
            
        else:
            BrandID = 1

    return BrandID


def get_auto_Branchid(model):
    BranchID = 1
    latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    if latest_auto_id:
        for auto in latest_auto_id:
            BranchID = auto.BranchID + 1
    return BranchID


def get_auto_LedgerID(model,BranchID,DataBase):
    LedgerID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('LedgerID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('LedgerID'))
        

        if max_value:
            max_ledgeriD = max_value.get('LedgerID__max', 0)
            
            LedgerID = max_ledgeriD + 1
            
        else:
            LedgerID = 1

    return LedgerID


def get_auto_EmployeeID(model,BranchID,DataBase):
    EmployeeID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('EmployeeID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('EmployeeID'))
        

        if max_value:
            max_employeeiD = max_value.get('EmployeeID__max', 0)
            
            EmployeeID = max_employeeiD + 1
            
        else:
            EmployeeID = 1

    return EmployeeID


def check_groupforProfitandLoss(AccountGroupUnder,DataBase):
    if not AccountGroupUnder == 0:
        if AccountGroup.objects.filter(AccountGroupID=AccountGroupUnder).exists():
            group_instance = AccountGroup.objects.get(AccountGroupID=AccountGroupUnder)
            AccountGroupUnder = group_instance.AccountGroupUnder
            AccountGroupName = group_instance.AccountGroupName
            if AccountGroupName == "Direct Expenses":
                return AccountGroupName
            elif AccountGroupName == "Indirect Expenses":
                return AccountGroupName
            elif AccountGroupName == "Direct Income":
                return AccountGroupName
            elif AccountGroupName == "Indirect Income":
                return AccountGroupName
            else:
                return check_groupforProfitandLoss(AccountGroupUnder)
        else:
            return False
    else:
        return False




def get_GroupCode(model,DataBase):
    GroupCode = "GP1"
    if AccountGroup.objects.filter().exists():
        instance = AccountGroup.objects.filter().first()
        OldGroupCode = instance.GroupCode
        res = re.search(r"\d+(\.\d+)?", OldGroupCode)
        num = res.group(0)
        new_num = int(num) + 1
        new_GroupCode = "GP" + str(new_num)
        return new_GroupCode

    else:
    
        return GroupCode



def get_auto_partyID(model,BranchID,DataBase):
    PartyID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('PartyID'))
    
    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('PartyID'))
        
        if max_value:
            max_partyId = max_value.get('PartyID__max', 0)
            
            PartyID = max_partyId + 1
            
        else:
            PartyID = 1


    return PartyID


def get_auto_TransactionTypesID(model,DataBase, BranchID):
    TransactionTypesID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(BranchID=BranchID).aggregate(Max('TransactionTypesID'))
    
    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('TransactionTypesID'))
        
        if max_value:
            max_transactionTypesid = max_value.get('TransactionTypesID__max', 0)
            TransactionTypesID = max_transactionTypesid + 1
        else:
            TransactionTypesID = 1

    return TransactionTypesID


# def get_base64_file(form_img):
#     import base64
#     import json
#     a = base64.b64encode(b'form_img')
#     dataStr = json.dumps(a)
#     base64EncodedStr = base64.b64encode(dataStr.encode('utf-8'))



#     # b = base64.b64encode(b'a').decode()
#     # print(a)
#     # print(type(b))
#     return base64EncodedStr

    # import base64
    # from django.core.files.base import ContentFile
    # from io import BytesIO
    # from PIL import Image
    # from subprocess import Popen, PIPE
    # decodedbytes = base64.decodebytes(str.encode(filename))
    # image_stream = io.BytesIO(decodedbytes)
    # image = Image.open(image_stream)
    # filetype = image.format

    # a = base64.b64decode(b'filename.file')
    # lines = filename.readlines()
    # for i in lines:
        # print(i)
    #     data = Popen.communicate(Popen([lines], stdout=PIPE))[0]
    #     scr = Image.open(BytesIO(data))

    #     with open(scr, 'rb') as file: 
    #         binaryData = file.read()
        # format, imgstr = i.split(';base64,') 
        # ext = format.split('/')[-1] 
        # data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        # with open(i, "wb") as fh:
        #     c = fh.write(base64.decodebytes(a))

# def conver_to_file(filename):
#     print(type(str(filename)))
#     for x in filename:

#         if x.line.startswith(b'>'):
#             print('')
#     return cutFile(x)

def get_base64_file(filename):
    print(type(filename))
    import base64
    from PIL import Image
    # dd = conver_to_file(filename)
    dd = str(filename)

    with open(dd, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')



def generateVoucherNo(VoucherType, BranchID):
    if VoucherType == "SI":
        if SalesMaster.objects.filter(BranchID=BranchID).exists():
            instance = SalesMaster.objects.filter(BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "SI" + str(new_num)


        else:
            new_VoucherNo = "SI1"

        return new_VoucherNo

    elif VoucherType == "PI":
        if PurchaseMaster.objects.filter(BranchID=BranchID).exists():
            instance = PurchaseMaster.objects.filter(BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "PI" + str(new_num)


        else:
            new_VoucherNo = "PI1"

        return new_VoucherNo

    elif VoucherType == "SO":
        if SalesOrderMaster.objects.filter(BranchID=BranchID).exists():
            instance = SalesOrderMaster.objects.filter(BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "SO" + str(new_num)


        else:
            new_VoucherNo = "SO1"

        return new_VoucherNo

    elif VoucherType == "PO":
        if PurchaseOrderMaster.objects.filter(BranchID=BranchID).exists():
            instance = PurchaseOrderMaster.objects.filter(BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "PO" + str(new_num)


        else:
            new_VoucherNo = "PO1"

        return new_VoucherNo

    elif VoucherType == "SR":
        if PurchaseOrderMaster.objects.filter(BranchID=BranchID).exists():
            instance = PurchaseOrderMaster.objects.filter(BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "SR" + str(new_num)


        else:
            new_VoucherNo = "SR1"

        return new_VoucherNo

    elif VoucherType == "PR":
        if PurchaseOrderMaster.objects.filter(BranchID=BranchID).exists():
            instance = PurchaseOrderMaster.objects.filter(BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "PR" + str(new_num)


        else:
            new_VoucherNo = "PR1"

        return new_VoucherNo

    elif VoucherType == "OS":
        if OpeningStockMaster.objects.filter(BranchID=BranchID).exists():
            instance = OpeningStockMaster.objects.filter(BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "OS" + str(new_num)


        else:
            new_VoucherNo = "OS1"

        return new_VoucherNo

    elif VoucherType == "JL":
        if JournalMaster.objects.filter(BranchID=BranchID).exists():
            instance = JournalMaster.objects.filter(BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "JL" + str(new_num)


        else:
            new_VoucherNo = "JL1"

        return new_VoucherNo

    elif VoucherType == "CP":
        if PaymentMaster.objects.filter(BranchID=BranchID,VoucherType="CP").exists():
            instance = PaymentMaster.objects.filter(BranchID=BranchID,VoucherType="CP").first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "CP" + str(new_num)


        else:
            new_VoucherNo = "CP1"

        return new_VoucherNo

    elif VoucherType == "BP":
        if PaymentMaster.objects.filter(BranchID=BranchID,VoucherType="BP").exists():
            instance = PaymentMaster.objects.filter(BranchID=BranchID,VoucherType="BP").first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "BP" + str(new_num)


        else:
            new_VoucherNo = "BP1"

        return new_VoucherNo

    elif VoucherType == "CR":
        if ReceiptMaster.objects.filter(BranchID=BranchID,VoucherType="CR").exists():
            instance = ReceiptMaster.objects.filter(BranchID=BranchID,VoucherType="CR").first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "CR" + str(new_num)


        else:
            new_VoucherNo = "CR1"

        return new_VoucherNo

    elif VoucherType == "BR":
        if ReceiptMaster.objects.filter(BranchID=BranchID,VoucherType="BR").exists():
            instance = ReceiptMaster.objects.filter(BranchID=BranchID,VoucherType="BR").first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "BR" + str(new_num)


        else:
            new_VoucherNo = "BR1"

        return new_VoucherNo

    else:
        
        new_VoucherNo: None

        return new_VoucherNo
