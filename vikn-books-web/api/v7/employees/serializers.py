from rest_framework import serializers
from brands.models import Employee, Country, Designation, AccountLedger, Department


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('CompanyID','id','CompanyID','FirstName','LastName','Category','DesignationID','DepartmentID','DateOfBirth','Gender','BloodGroup','Nationality',
            'State','Address1','Address2','Address3','Post','Phone','Mobile','Email',
            'PassportNo','PassportExpiryDate','VisaDetails','VisaExpiryDate','ProbationPeriod','periodType','DateOfJoining','Salary',
            'AccountHolderName','AccountNumber','AccountName','AccountBranch','AccountIFSC','NoCasualLeave','Notes','Qualification','EmergencyContactNumber','EmergencyEmail','EmergencyAddress',
            'BranchID',)


class EmployeeRestSerializer(serializers.ModelSerializer):

    DepartmentName = serializers.SerializerMethodField()
    DesignationName = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    Salary = serializers.SerializerMethodField()
    Nationality_Name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ('id','FirstName','LastName','Category','DesignationID','DepartmentID','DateOfBirth','Gender','BloodGroup','Nationality',
        	'State','Address1','Address2','Address3','Post','Phone','Mobile','Email','Nationality_Name',
        	'PassportNo','PassportExpiryDate','VisaDetails','VisaExpiryDate','ProbationPeriod','periodType','DateOfJoining','Salary',
        	'AccountHolderName','AccountNumber','AccountName','AccountBranch','AccountIFSC','NoCasualLeave','Notes','Qualification','EmergencyContactNumber','EmergencyEmail','EmergencyAddress',
        	'EmployeeCode','EmployeeID','BranchID','LedgerID','LedgerName','CreatedDate','UpdatedDate','CreatedUserID','Action','DesignationName','DepartmentName',
            'EmployeeCardID','WorkLocation','JobType','WorkEmail','OfficialEmail','City')

    # def get_Nationality(self, instance):
    #     CompanyID = self.context.get("CompanyID")
    #     Nationality = ""
    #     if instance.Nationality:
    #         id = instance.Nationality
    #         if Country.objects.filter(id=id).exists():
    #             Nationality = Country.objects.get(id=id).Country_Name
            
    #     return Nationality

    def get_Nationality_Name(self, instance):
        CompanyID = self.context.get("CompanyID")
        Nationality = instance.Nationality
        BranchID = instance.BranchID

        Nationality_Name = ""
        if Country.objects.filter(id=Nationality).exists():
            NationalityInstances = Country.objects.get(id=Nationality)
            Nationality_Name = NationalityInstances.Country_Name
        return Nationality_Name
        

    def get_DesignationName(self, instance):
        CompanyID = self.context.get("CompanyID")

        DesignationID = instance.DesignationID
        BranchID = instance.BranchID
        if Designation.objects.filter(DesignationID=DesignationID,BranchID=BranchID,CompanyID=CompanyID).exists():
            DesignationInstances = Designation.objects.filter(DesignationID=DesignationID,BranchID=BranchID,CompanyID=CompanyID)
            for instance in DesignationInstances:
                DesignationName = instance.DesignationName
            return DesignationName
        else:
            return ""

    def get_DepartmentName(self, instance):
        CompanyID = self.context.get("CompanyID")

        DepartmentID = instance.DepartmentID
        BranchID = instance.BranchID
        if Department.objects.filter(DepartmentID=DepartmentID,BranchID=BranchID,CompanyID=CompanyID).exists():
            DepartmentInstances = Department.objects.filter(DepartmentID=DepartmentID,BranchID=BranchID,CompanyID=CompanyID)
            for instance in DepartmentInstances:
                DepartmentName = instance.DepartmentName
            return DepartmentName
        else:
            return ""

    def get_LedgerName(self, instance):
        CompanyID = self.context.get("CompanyID")
        
        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        if AccountLedger.objects.filter(LedgerID=LedgerID,BranchID=BranchID,CompanyID=CompanyID).exists():
            AccountLedgerInstances = AccountLedger.objects.filter(LedgerID=LedgerID,BranchID=BranchID,CompanyID=CompanyID)
            for instance in AccountLedgerInstances:
                LedgerName = instance.LedgerName
            return LedgerName
        else:
            return ""


    def get_Salary(self, instance):
        PriceRounding = self.context.get("PriceRounding")
        print("###########")
        print(PriceRounding)
        Salary = instance.Salary
        Salary = round(Salary,PriceRounding)
        return Salary


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ('id','CountryID','CountryCode','Currency_Name','Currency_Description','Change',
            'Symbol','FractionalUnits','CurrencySymbolUnicode','Country_Name','Country_Description','ISD_Code'
            )