from brands.models import Employee, Employee_Log, AccountLedger, Country, AccountLedger_Log, LedgerPosting, Category
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v5.employees.serializers import EmployeeSerializer, EmployeeRestSerializer, CountrySerializer
from api.v5.brands.serializers import ListSerializer
from api.v5.employees.functions import generate_serializer_errors, get_auto_id
from rest_framework import status
from api.v5.employees.functions import get_auto_id, get_EmployeeCode
from web.functions import get_auto_LedgerID
from django.shortcuts import render, get_object_or_404
from brands.models import CompanySettings
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_employee(request):
    data = request.data
    # CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = EmployeeSerializer(data=request.data)
    if serialized.is_valid():
        CompanyID = serialized.data['CompanyID']
        CompanyID = get_company(CompanyID)
        FirstName = serialized.data['FirstName']
        LastName = serialized.data['LastName']
        DesignationID = serialized.data['DesignationID']
        CategoryID = serialized.data['Category']
        DepartmentID = serialized.data['DepartmentID']
        DateOfBirth = serialized.data['DateOfBirth']
        Gender = serialized.data['Gender']
        BloodGroup = serialized.data['BloodGroup']
        Nationality = data['Nationality']
        State = data['State']
        Address1 = serialized.data['Address1']
        Address2 = serialized.data['Address2']
        Address3 = serialized.data['Address3']
        Post = data['Post']
        Phone = serialized.data['Phone']
        Mobile = serialized.data['Mobile']
        Email = data['Email']
        PassportNo = serialized.data['PassportNo']
        PassportExpiryDate = data['PassportExpiryDate']
        VisaDetails = serialized.data['VisaDetails']
        VisaExpiryDate = serialized.data['VisaExpiryDate']
        ProbationPeriod = serialized.data['ProbationPeriod']
        periodType = serialized.data['periodType']
        DateOfJoining = serialized.data['DateOfJoining']
        Salary = serialized.data['Salary']
        AccountNumber = serialized.data['AccountNumber']
        AccountHolderName = serialized.data['AccountHolderName']
        # AccountName = serialized.data['AccountName']
        AccountBranch = serialized.data['AccountBranch']
        AccountIFSC = serialized.data['AccountIFSC']
        NoCasualLeave = serialized.data['NoCasualLeave']
        Qualification = serialized.data['Qualification']
        EmergencyContactNumber = serialized.data['EmergencyContactNumber']
        EmergencyEmail = serialized.data['EmergencyEmail']
        EmergencyAddress = serialized.data['EmergencyAddress']
        BranchID = serialized.data['BranchID']
        Notes = serialized.data['Notes']

        LedgerName = data['LedgerName']

        Action = 'A'

        EmployeeID = get_auto_id(Employee, BranchID, CompanyID)
        LedgerCode = get_EmployeeCode(Employee, BranchID, CompanyID)
        LedgerID = get_auto_LedgerID(AccountLedger, BranchID, CompanyID)

        category_instance = None
        if Category.objects.filter(pk=CategoryID).exists():
            category_instance = Category.objects.get(pk=CategoryID)

        is_nameExist = False
        LedgerNameLow = LedgerName.lower()
        account_ledgers = AccountLedger.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)
        for account_ledger in account_ledgers:
            ledger_name = account_ledger.LedgerName
            ledgerName = ledger_name.lower()
            if LedgerNameLow == ledgerName:
                is_nameExist = True

        if not is_nameExist:

            Employee.objects.create(
                CompanyID=CompanyID,
                Category=category_instance,
                EmployeeID=EmployeeID,
                BranchID=BranchID,
                FirstName=FirstName,
                LastName=LastName,
                DesignationID=DesignationID,
                DepartmentID=DepartmentID,
                DateOfBirth=DateOfBirth,
                Gender=Gender,
                BloodGroup=BloodGroup,
                Nationality=Nationality,
                State=State,
                Address1=Address1,
                Address2=Address2,
                Address3=Address3,
                Post=Post,
                Phone=Phone,
                Mobile=Mobile,
                Email=Email,
                PassportNo=PassportNo,
                PassportExpiryDate=PassportExpiryDate,
                VisaDetails=VisaDetails,
                VisaExpiryDate=VisaExpiryDate,
                ProbationPeriod=ProbationPeriod,
                periodType=periodType,
                DateOfJoining=DateOfJoining,
                Salary=Salary,
                AccountNumber=AccountNumber,
                AccountHolderName=AccountHolderName,
                # AccountName=AccountName,
                AccountBranch=AccountBranch,
                AccountIFSC=AccountIFSC,
                NoCasualLeave=NoCasualLeave,
                Notes=Notes,
                Qualification=Qualification,
                EmergencyContactNumber=EmergencyContactNumber,
                EmergencyEmail=EmergencyEmail,
                EmergencyAddress=EmergencyAddress,
                EmployeeCode=LedgerCode,
                LedgerID=LedgerID,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
            )

            Employee_Log.objects.create(
                CompanyID=CompanyID,
                TransactionID=EmployeeID,
                Category=category_instance,
                BranchID=BranchID,
                FirstName=FirstName,
                LastName=LastName,
                DesignationID=DesignationID,
                DepartmentID=DepartmentID,
                DateOfBirth=DateOfBirth,
                Gender=Gender,
                BloodGroup=BloodGroup,
                Nationality=Nationality,
                State=State,
                Address1=Address1,
                Address2=Address2,
                Address3=Address3,
                Post=Post,
                Phone=Phone,
                Mobile=Mobile,
                Email=Email,
                PassportNo=PassportNo,
                PassportExpiryDate=PassportExpiryDate,
                VisaDetails=VisaDetails,
                VisaExpiryDate=VisaExpiryDate,
                ProbationPeriod=ProbationPeriod,
                periodType=periodType,
                DateOfJoining=DateOfJoining,
                Salary=Salary,
                AccountNumber=AccountNumber,
                AccountHolderName=AccountHolderName,
                # AccountName=AccountName,
                AccountBranch=AccountBranch,
                AccountIFSC=AccountIFSC,
                NoCasualLeave=NoCasualLeave,
                Notes=Notes,
                Qualification=Qualification,
                EmergencyContactNumber=EmergencyContactNumber,
                EmergencyEmail=EmergencyEmail,
                EmergencyAddress=EmergencyAddress,
                EmployeeCode=LedgerCode,
                LedgerID=LedgerID,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
            )

            AccountLedger.objects.create(
                CompanyID=CompanyID,
                LedgerID=LedgerID,
                BranchID=BranchID,
                LedgerName=LedgerName,
                LedgerCode=LedgerCode,
                AccountGroupUnder=32,
                OpeningBalance=0,
                CrOrDr="Dr",
                Notes=Notes,
                IsActive=True,
                IsDefault=False,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
            )

            AccountLedger_Log.objects.create(
                CompanyID=CompanyID,
                BranchID=BranchID,
                TransactionID=LedgerID,
                LedgerName=LedgerName,
                LedgerCode=LedgerCode,
                AccountGroupUnder=32,
                OpeningBalance=0,
                CrOrDr="Dr",
                Notes=Notes,
                IsActive=True,
                IsDefault=False,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
            )

            data = {"EmployeeID": EmployeeID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Employee Name Already Exist!!!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_employee(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = EmployeeSerializer(data=request.data)
    instance = Employee.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID
    EmployeeID = instance.EmployeeID
    LedgerID = instance.LedgerID
    EmployeeCode = instance.EmployeeCode
    ledgerInstance = AccountLedger.objects.get(
        BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID)
    instanceLedgerName = ledgerInstance.LedgerName
    LedgerName = data['LedgerName']

    if serialized.is_valid():

        FirstName = serialized.data['FirstName']
        LastName = serialized.data['LastName']
        DesignationID = serialized.data['DesignationID']
        DepartmentID = serialized.data['DepartmentID']

        DateOfBirth = serialized.data['DateOfBirth']
        Gender = serialized.data['Gender']
        BloodGroup = serialized.data['BloodGroup']
        Nationality = data['Nationality']
        State = data['State']
        Address1 = serialized.data['Address1']
        Address2 = serialized.data['Address2']
        Address3 = serialized.data['Address3']
        Post = data['Post']
        Phone = serialized.data['Phone']
        Mobile = serialized.data['Mobile']
        Email = data['Email']
        PassportNo = serialized.data['PassportNo']
        PassportExpiryDate = data['PassportExpiryDate']
        VisaDetails = serialized.data['VisaDetails']
        VisaExpiryDate = serialized.data['VisaExpiryDate']
        ProbationPeriod = serialized.data['ProbationPeriod']
        periodType = serialized.data['periodType']
        DateOfJoining = serialized.data['DateOfJoining']
        Salary = serialized.data['Salary']
        AccountNumber = serialized.data['AccountNumber']
        AccountHolderName = serialized.data['AccountHolderName']
        # AccountName = serialized.data['AccountName']
        AccountBranch = serialized.data['AccountBranch']
        AccountIFSC = serialized.data['AccountIFSC']
        NoCasualLeave = serialized.data['NoCasualLeave']
        Qualification = serialized.data['Qualification']
        EmergencyContactNumber = serialized.data['EmergencyContactNumber']
        EmergencyEmail = serialized.data['EmergencyEmail']
        EmergencyAddress = serialized.data['EmergencyAddress']
        Notes = serialized.data['Notes']

        try:
            CategoryID = serialized.data['Category']
        except:
            CategoryID = None

        category_instance = None
        if Category.objects.filter(pk=CategoryID).exists():
            category_instance = Category.objects.get(pk=CategoryID)

        Action = 'M'

        is_nameExist = False
        employee_ok = False

        LedgerNameLow = LedgerName.lower()

        account_ledgers = AccountLedger.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for account_ledger in account_ledgers:

            ledger_name = account_ledger.LedgerName
            ledgerName = ledger_name.lower()

            if LedgerNameLow == ledgerName:
                is_nameExist = True

            if instanceLedgerName.lower() == LedgerNameLow:

                employee_ok = True

        if employee_ok:
            if category_instance:
                instance.Category = category_instance
            instance.FirstName = FirstName
            instance.LastName = LastName
            instance.DesignationID = DesignationID
            instance.DepartmentID = DepartmentID
            instance.DateOfBirth = DateOfBirth
            instance.Gender = Gender
            instance.BloodGroup = BloodGroup
            instance.Nationality = Nationality
            instance.State = State
            instance.Address1 = Address1
            instance.Address2 = Address2
            instance.Address3 = Address3
            instance.Post = Post
            instance.Phone = Phone
            instance.Mobile = Mobile
            instance.Email = Email
            instance.PassportNo = PassportNo
            instance.PassportExpiryDate = PassportExpiryDate
            instance.VisaDetails = VisaDetails
            instance.VisaExpiryDate = VisaExpiryDate
            instance.ProbationPeriod = ProbationPeriod
            instance.periodType = periodType
            instance.DateOfJoining = DateOfJoining
            instance.Salary = Salary
            instance.AccountNumber = AccountNumber
            instance.AccountHolderName = AccountHolderName
            # instance.AccountName = AccountName
            instance.AccountBranch = AccountBranch
            instance.AccountIFSC = AccountIFSC
            instance.NoCasualLeave = NoCasualLeave
            instance.Qualification = Qualification
            instance.EmergencyContactNumber = EmergencyContactNumber
            instance.EmergencyEmail = EmergencyEmail
            instance.EmergencyAddress = EmergencyAddress
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            Employee_Log.objects.create(
                Category=category_instance,
                TransactionID=EmployeeID,
                BranchID=BranchID,
                FirstName=FirstName,
                LastName=LastName,
                DesignationID=DesignationID,
                DepartmentID=DepartmentID,
                DateOfBirth=DateOfBirth,
                Gender=Gender,
                BloodGroup=BloodGroup,
                Nationality=Nationality,
                State=State,
                Address1=Address1,
                Address2=Address2,
                Address3=Address3,
                Post=Post,
                Phone=Phone,
                Mobile=Mobile,
                Email=Email,
                PassportNo=PassportNo,
                PassportExpiryDate=PassportExpiryDate,
                VisaDetails=VisaDetails,
                VisaExpiryDate=VisaExpiryDate,
                ProbationPeriod=ProbationPeriod,
                periodType=periodType,
                DateOfJoining=DateOfJoining,
                Salary=Salary,
                AccountNumber=AccountNumber,
                AccountHolderName=AccountHolderName,
                # AccountName=AccountName,
                AccountBranch=AccountBranch,
                AccountIFSC=AccountIFSC,
                NoCasualLeave=NoCasualLeave,
                Notes=Notes,
                Qualification=Qualification,
                EmergencyContactNumber=EmergencyContactNumber,
                EmergencyEmail=EmergencyEmail,
                EmergencyAddress=EmergencyAddress,
                EmployeeCode=EmployeeCode,
                LedgerID=LedgerID,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID,
            )

            if AccountLedger.objects.filter(BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).exists():
                accountLedgerInstance = AccountLedger.objects.get(
                    BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID)
                accountLedgerInstance.LedgerName = LedgerName
                accountLedgerInstance.Notes = Notes
                accountLedgerInstance.UpdatedDate = today
                accountLedgerInstance.CreatedUserID = CreatedUserID
                accountLedgerInstance.Action = "M"
                accountLedgerInstance.save()

                AccountLedger_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=LedgerName,
                    LedgerCode=accountLedgerInstance.LedgerCode,
                    AccountGroupUnder=accountLedgerInstance.AccountGroupUnder,
                    OpeningBalance=accountLedgerInstance.OpeningBalance,
                    CrOrDr=accountLedgerInstance.CrOrDr,
                    Notes=Notes,
                    IsActive=accountLedgerInstance.IsActive,
                    IsDefault=accountLedgerInstance.IsDefault,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action="M",
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "Employee Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                if category_instance:
                    instance.Category = category_instance
                instance.FirstName = FirstName
                instance.LastName = LastName
                instance.DesignationID = DesignationID
                instance.DepartmentID = DepartmentID
                instance.DateOfBirth = DateOfBirth
                instance.Gender = Gender
                instance.BloodGroup = BloodGroup
                instance.Nationality = Nationality
                instance.State = State
                instance.Address1 = Address1
                instance.Address2 = Address2
                instance.Address3 = Address3
                instance.Post = Post
                instance.Phone = Phone
                instance.Mobile = Mobile
                instance.Email = Email
                instance.PassportNo = PassportNo
                instance.PassportExpiryDate = PassportExpiryDate
                instance.VisaDetails = VisaDetails
                instance.VisaExpiryDate = VisaExpiryDate
                instance.ProbationPeriod = ProbationPeriod
                instance.periodType = periodType
                instance.DateOfJoining = DateOfJoining
                instance.Salary = Salary
                AccountNumber = AccountNumber
                instance.AccountHolderName = AccountHolderName
                # instance.AccountName = AccountName
                instance.AccountBranch = AccountBranch
                instance.AccountIFSC = AccountIFSC
                instance.NoCasualLeave = NoCasualLeave
                instance.Qualification = Qualification
                instance.EmergencyContactNumber = EmergencyContactNumber
                instance.EmergencyEmail = EmergencyEmail
                instance.EmergencyAddress = EmergencyAddress
                instance.Action = Action
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = today
                instance.save()

                Employee_Log.objects.create(
                    TransactionID=EmployeeID,
                    BranchID=BranchID,
                    FirstName=FirstName,
                    LastName=LastName,
                    DesignationID=DesignationID,
                    DepartmentID=DepartmentID,
                    DateOfBirth=DateOfBirth,
                    Gender=Gender,
                    BloodGroup=BloodGroup,
                    Nationality=Nationality,
                    State=State,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Post=Post,
                    Phone=Phone,
                    Mobile=Mobile,
                    Email=Email,
                    PassportNo=PassportNo,
                    PassportExpiryDate=PassportExpiryDate,
                    VisaDetails=VisaDetails,
                    VisaExpiryDate=VisaExpiryDate,
                    ProbationPeriod=ProbationPeriod,
                    periodType=periodType,
                    DateOfJoining=DateOfJoining,
                    Salary=Salary,
                    AccountNumber=AccountNumber,
                    AccountHolderName=AccountHolderName,
                    # AccountName=AccountName,
                    AccountBranch=AccountBranch,
                    AccountIFSC=AccountIFSC,
                    NoCasualLeave=NoCasualLeave,
                    Notes=Notes,
                    Qualification=Qualification,
                    EmergencyContactNumber=EmergencyContactNumber,
                    EmergencyEmail=EmergencyEmail,
                    EmergencyAddress=EmergencyAddress,
                    EmployeeCode=EmployeeCode,
                    LedgerID=LedgerID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    CompanyID=CompanyID,
                )

                if AccountLedger.objects.filter(BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).exists():
                    accountLedgerInstance = AccountLedger.objects.get(
                        BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID)
                    accountLedgerInstance.LedgerName = LedgerName
                    accountLedgerInstance.Notes = Notes
                    accountLedgerInstance.UpdatedDate = today
                    accountLedgerInstance.CreatedUserID = CreatedUserID
                    accountLedgerInstance.Action = "M"
                    accountLedgerInstance.save()

                    AccountLedger_Log.objects.create(
                        BranchID=BranchID,
                        TransactionID=LedgerID,
                        LedgerName=LedgerName,
                        LedgerCode=accountLedgerInstance.LedgerCode,
                        AccountGroupUnder=accountLedgerInstance.AccountGroupUnder,
                        OpeningBalance=accountLedgerInstance.OpeningBalance,
                        CrOrDr=accountLedgerInstance.CrOrDr,
                        Notes=Notes,
                        IsActive=accountLedgerInstance.IsActive,
                        IsDefault=accountLedgerInstance.IsDefault,
                        Action="M",
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def employees(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    print(PriceRounding)
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Employee.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = Employee.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = EmployeeRestSerializer(instances, many=True, context={
                                                "CompanyID": CompanyID, "PriceRounding": PriceRounding})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Employee not found in this branch.",
                "data": []
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not valid.",
            "data": [],
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def employee(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    if Employee.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Employee.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = EmployeeRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": int(PriceRounding)})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Employee Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_employee(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if Employee.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Employee.objects.get(pk=pk, CompanyID=CompanyID)
        Category = instance.Category
        EmployeeID = instance.EmployeeID
        BranchID = instance.BranchID
        FirstName = instance.FirstName
        LastName = instance.LastName
        DesignationID = instance.DesignationID
        DepartmentID = instance.DepartmentID
        DateOfBirth = instance.DateOfBirth
        Gender = instance.Gender
        BloodGroup = instance.BloodGroup
        Nationality = instance.Nationality
        State = instance.State
        Address1 = instance.Address1
        Address2 = instance.Address2
        Address3 = instance.Address3
        Post = instance.Post
        Phone = instance.Phone
        Mobile = instance.Mobile
        Email = instance.Email
        PassportNo = instance.PassportNo
        PassportExpiryDate = instance.PassportExpiryDate
        VisaDetails = instance.VisaDetails
        VisaExpiryDate = instance.VisaExpiryDate
        ProbationPeriod = instance.ProbationPeriod
        periodType = instance.periodType
        DateOfJoining = instance.DateOfJoining
        Salary = instance.Salary
        AccountNumber = instance.AccountNumber
        AccountHolderName = instance.AccountHolderName
        # AccountName = instance.AccountName
        AccountBranch = instance.AccountBranch
        AccountIFSC = instance.AccountIFSC
        NoCasualLeave = instance.NoCasualLeave
        Notes = instance.Notes
        Qualification = instance.Qualification
        EmergencyContactNumber = instance.EmergencyContactNumber
        EmergencyEmail = instance.EmergencyEmail
        EmergencyAddress = instance.EmergencyAddress
        EmployeeCode = instance.EmployeeCode
        LedgerID = instance.LedgerID
        Action = "D"

        instance.delete()

        Employee_Log.objects.create(
            Category=Category,
            TransactionID=EmployeeID,
            BranchID=BranchID,
            FirstName=FirstName,
            LastName=LastName,
            DesignationID=DesignationID,
            DepartmentID=DepartmentID,
            DateOfBirth=DateOfBirth,
            Gender=Gender,
            BloodGroup=BloodGroup,
            Nationality=Nationality,
            State=State,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            Post=Post,
            Phone=Phone,
            Mobile=Mobile,
            Email=Email,
            PassportNo=PassportNo,
            PassportExpiryDate=PassportExpiryDate,
            VisaDetails=VisaDetails,
            VisaExpiryDate=VisaExpiryDate,
            ProbationPeriod=ProbationPeriod,
            periodType=periodType,
            DateOfJoining=DateOfJoining,
            Salary=Salary,
            AccountNumber=AccountNumber,
            AccountHolderName=AccountHolderName,
            # AccountName=AccountName,
            AccountBranch=AccountBranch,
            AccountIFSC=AccountIFSC,
            NoCasualLeave=NoCasualLeave,
            Notes=Notes,
            Qualification=Qualification,
            EmergencyContactNumber=EmergencyContactNumber,
            EmergencyEmail=EmergencyEmail,
            EmergencyAddress=EmergencyAddress,
            EmployeeCode=EmployeeCode,
            LedgerID=LedgerID,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
            CompanyID=CompanyID,
        )

        if not LedgerPosting.objects.filter(BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).exists():

            if AccountLedger.objects.filter(BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).exists():
                accountLedgerInstance = AccountLedger.objects.get(
                    BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID)

                accountLedgerInstance.delete()

                AccountLedger_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=accountLedgerInstance.LedgerName,
                    LedgerCode=accountLedgerInstance.LedgerCode,
                    AccountGroupUnder=accountLedgerInstance.AccountGroupUnder,
                    OpeningBalance=accountLedgerInstance.OpeningBalance,
                    CrOrDr=accountLedgerInstance.CrOrDr,
                    Notes=accountLedgerInstance.Notes,
                    IsActive=accountLedgerInstance.IsActive,
                    IsDefault=accountLedgerInstance.IsDefault,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action="D",
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

        response_data = {
            "StatusCode": 6000,
            "message": "Employee Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Employee Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def countries(request):
    data = request.data
    # CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instances = Country.objects.all()
    serialized = CountrySerializer(instances, many=True)
    response_data = {
        "StatusCode": 6000,
        "data": serialized.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_employee(request):
    data = request.data
    # CompanyID = data['CompanyID']
    EmployeeCode = data['EmployeeCode']
    print(EmployeeCode, "EmployeeCode")
    instance = None
    if Employee.objects.filter(EmployeeCode=EmployeeCode).exists():
        instance = Employee.objects.get(EmployeeCode=EmployeeCode)
        print(instance, "instance")

        serialized = EmployeeSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "In valid Code"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_categoryEmployeeList(request):
    data = request.data
    # CompanyID = data['CompanyID']
    pk = data['id']
    instances = None
    if Employee.objects.filter(Category=pk).exists():
        instances = Employee.objects.filter(Category=pk)
        print(instances, "instances")

        serialized = EmployeeRestSerializer(instances, many=True)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "In valid Code"
        }

        return Response(response_data, status=status.HTTP_200_OK)
