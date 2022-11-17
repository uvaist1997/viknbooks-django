from brands.models import LoyaltyProgram, LoyaltyProgram_Log,Product,ProductGroup,ProductCategory,TransactionTypes,LoyaltyPoint,LoyaltyCustomer
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.loyaltyProgram.serializers import LoyaltyProgramSerializer, LoyaltyProgramRestSerializer,LoyaltyPointSerializer
from api.v4.loyaltyCustomer.serializers import LoyaltyCustomerRestSerializer
from api.v4.brands.serializers import ListSerializer
from api.v4.loyaltyProgram.functions import generate_serializer_errors
from rest_framework import status
from api.v4.loyaltyProgram.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime
from api.v4.sales.functions import get_actual_point
from api.v4.salesReturns.functions import sales_return_point


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_loyaltyProgram(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LoyaltyProgramSerializer(data=request.data)
    if serialized.is_valid():
        CardTypeID = serialized.data['CardTypeID']

        BranchID = serialized.data['BranchID']

        FromDate = serialized.data['FromDate']
        ToDate = serialized.data['ToDate']
        date_arr = []
        test = LoyaltyProgram.objects.filter(BranchID=BranchID,CompanyID=CompanyID,CardTypeID=CardTypeID)
        for i in test:
            date_form = i.FromDate
            date_to = i.ToDate
            # database date filter
            print('date_form')
            start = datetime.datetime.strptime(str(date_form), "%Y-%m-%d")
            end = datetime.datetime.strptime(str(date_to), "%Y-%m-%d")
            date_array = \
                (start + datetime.timedelta(days=x) for x in range(0, (end-start).days))

            for date_object in date_array:
                date = date_object.strftime("%Y-%m-%d")
                date_arr.append(date)
                print('und')
        print(FromDate,ToDate)
        print(date_arr)

        if str(FromDate) in date_arr or str(ToDate) in date_arr:
            print('und')
            response_data = {
                "StatusCode": 6001,
                "message": "In this Card Type LoyaltyProgram is Exists"
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
        # if not LoyaltyProgram.objects.filter(FromDate__range=[FromDate,ToDate],ToDate__range=[FromDate,ToDate],CardTypeID=CardTypeID).exists():
            Name = serialized.data['Name']
            NoOFDayExpPoint = serialized.data['NoOFDayExpPoint']
            MinimumSalePrice = serialized.data['MinimumSalePrice']
            Amount = serialized.data['Amount']
            Amount_Point = serialized.data['Amount_Point']
            Percentage = serialized.data['Percentage']
            product = serialized.data['product']
            ProductGroupIDs = serialized.data['ProductGroupIDs']
            ProductCategoryIDs = serialized.data['ProductCategoryIDs']
            is_offer = serialized.data['is_offer']
            is_Return_MinimumSalePrice = serialized.data['is_Return_MinimumSalePrice']
            ProductType = serialized.data['ProductType']
            Calculate_with = serialized.data['Calculate_with']

            print(ProductGroupIDs,"ProductGroupIDs")
            print(ProductCategoryIDs,"ProductCategoryIDs")
          

            Action = 'A'
            LoyaltyProgramID = get_auto_id(LoyaltyProgram, BranchID, CompanyID)
            is_nameExist = False
            NameLow = Name.lower()
            loyaltyprograms = LoyaltyProgram.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            for loyaltyprogram in loyaltyprograms:
                name = loyaltyprogram.Name
                A_Name = name.lower()
                if NameLow == A_Name:
                    is_nameExist = True

            print(Name,'Name')
            if not is_nameExist:
                product_instance = None
                if Product.objects.filter(pk=product).exists():
                    product_instance = Product.objects.get(pk=product)

                # productgroup_instance = None
                # if ProductGroup.objects.filter(pk=productgroup).exists():
                #     productgroup_instance = ProductGroup.objects.get(pk=productgroup)

                # productcategory_instance = None
                # if ProductCategory.objects.filter(pk=productcategory).exists():
                #     productcategory_instance = ProductCategory.objects.get(pk=productcategory)


                card_type_instance= None
                if TransactionTypes.objects.filter(pk=CardTypeID).exists():
                    card_type_instance = TransactionTypes.objects.get(pk=CardTypeID)
                # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
                LoyaltyProgram.objects.create(
                    LoyaltyProgramID=LoyaltyProgramID,
                    BranchID=BranchID,

                    Name=Name,
                    FromDate=FromDate,
                    ToDate=ToDate,
                    NoOFDayExpPoint=NoOFDayExpPoint,
                    CardTypeID=card_type_instance,
                    MinimumSalePrice=MinimumSalePrice,
                    Amount=Amount,
                    Amount_Point=Amount_Point,
                    Percentage=Percentage,
                    product=product_instance,
                    ProductGroupIDs=ProductGroupIDs,
                    ProductCategoryIDs=ProductCategoryIDs,
                    is_offer=is_offer,
                    is_Return_MinimumSalePrice=is_Return_MinimumSalePrice,
                    ProductType=ProductType,
                    Calculate_with=Calculate_with,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                LoyaltyProgram_Log.objects.create(
                    BranchID=BranchID,
                    LoyaltyProgramID=LoyaltyProgramID,
                   
                    Name=Name,
                    FromDate=FromDate,
                    ToDate=ToDate,
                    NoOFDayExpPoint=NoOFDayExpPoint,
                    CardTypeID=card_type_instance,
                    MinimumSalePrice=MinimumSalePrice,
                    Amount=Amount,
                    Amount_Point=Amount_Point,
                    Percentage=Percentage,
                    product=product_instance,
                    ProductGroupIDs=ProductGroupIDs,
                    ProductCategoryIDs=ProductCategoryIDs,
                    is_offer=is_offer,
                    is_Return_MinimumSalePrice=is_Return_MinimumSalePrice,
                    ProductType=ProductType,
                    Calculate_with=Calculate_with,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                data = {"LoyaltyProgramID": LoyaltyProgramID}
                data.update(serialized.data)
                response_data = {
                    "StatusCode": 6000,
                    "data": data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Loyalty Program Name Already Exist!!!"
                }

            return Response(response_data, status=status.HTTP_200_OK)
        # else:
        #     response_data = {
        #         "StatusCode": 6001,
        #         "message": "In this Card Type LoyaltyProgram is Exists"
        #     }

        # return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_loyaltyProgram(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LoyaltyProgramSerializer(data=request.data)
    instance = LoyaltyProgram.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    LoyaltyProgramID = instance.LoyaltyProgramID
    instancename = instance.Name
    if serialized.is_valid():
        FromDate = serialized.data['FromDate']
        ToDate = serialized.data['ToDate']
        CardTypeID = serialized.data['CardTypeID']
        if not LoyaltyProgram.objects.filter(FromDate__range=[FromDate,ToDate],ToDate__range=[FromDate,ToDate],CardTypeID=CardTypeID).exclude(pk=pk):
            Name = serialized.data['Name']
            NoOFDayExpPoint = serialized.data['NoOFDayExpPoint']
            MinimumSalePrice = serialized.data['MinimumSalePrice']
            Amount = serialized.data['Amount']
            Amount_Point = serialized.data['Amount_Point']
            Percentage = serialized.data['Percentage']
            product = serialized.data['product']
            ProductGroupIDs = serialized.data['ProductGroupIDs']
            ProductCategoryIDs = serialized.data['ProductCategoryIDs']
            is_offer = serialized.data['is_offer']
            is_Return_MinimumSalePrice = serialized.data['is_Return_MinimumSalePrice']
            ProductType = serialized.data['ProductType']
            Calculate_with = serialized.data['Calculate_with']



            Action = 'M'
            is_nameExist = False
            loyaltyprogram_ok = False

            NameLow = Name.lower()

            loyaltyprograms = LoyaltyProgram.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)

            for loyaltyprogram in loyaltyprograms:
                name = loyaltyprogram.Name

                loyaltyprogramName = name.lower()

                if NameLow == loyaltyprogramName:
                    is_nameExist = True

                if instancename.lower() == NameLow:

                    loyaltyprogram_ok = True

            if loyaltyprogram_ok:
                product_instance = None
                productcategory_instance = None
                productgroup_instance = None
                card_type_instance = None

                instance.Name = Name
                instance.FromDate = FromDate
                instance.ToDate = ToDate
                instance.NoOFDayExpPoint = NoOFDayExpPoint
                if ProductGroupIDs:
                    instance.ProductGroupIDs = ProductGroupIDs
                    instance.ProductCategoryIDs = ""

                if ProductCategoryIDs:
                    instance.ProductCategoryIDs = ProductCategoryIDs
                    instance.ProductGroupIDs = ""

                if CardTypeID:
                    card_type_instance = TransactionTypes.objects.get(pk=CardTypeID)
                    instance.CardTypeID = card_type_instance

                instance.MinimumSalePrice = MinimumSalePrice
                instance.Amount = Amount
                instance.Amount_Point = Amount_Point
                instance.Percentage = Percentage
                if product:
                    product_instance = Product.objects.get(pk=product)
                    instance.product = product_instance
                # if productcategory:
                #     productcategory_instance = ProductCategory.objects.get(pk=productcategory)
                #     instance.productcategory = productcategory_instance
                # if productgroup:
                #     productgroup_instance = ProductGroup.objects.get(pk=productgroup)
                #     instance.productgroup = productgroup_instance
                instance.is_offer = is_offer
                instance.is_Return_MinimumSalePrice = is_Return_MinimumSalePrice
                instance.ProductType = ProductType
                instance.Calculate_with = Calculate_with


                instance.Action = Action
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.save()

                LoyaltyProgram_Log.objects.create(
                    BranchID=BranchID,
                    
                    LoyaltyProgramID=LoyaltyProgramID,
                   
                    Name=Name,
                    FromDate=FromDate,
                    ToDate=ToDate,
                    NoOFDayExpPoint=NoOFDayExpPoint,
                    CardTypeID=card_type_instance,
                    MinimumSalePrice=MinimumSalePrice,
                    Amount=Amount,
                    Amount_Point=Amount_Point,
                    Percentage=Percentage,
                    product=product_instance,
                    ProductGroupIDs=ProductGroupIDs,
                    ProductCategoryIDs=ProductCategoryIDs,
                    is_offer=is_offer,
                    is_Return_MinimumSalePrice=is_Return_MinimumSalePrice,
                    ProductType=ProductType,
                    Calculate_with=Calculate_with,
                
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                data = {"LoyaltyProgramID": LoyaltyProgramID}
                data.update(serialized.data)
                response_data = {
                    "StatusCode": 6000,
                    "data": data
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:

                if is_nameExist:

                    response_data = {
                        "StatusCode": 6001,
                        "message": "Loyalty Program Name Already exist with this Branch ID"
                    }
                    return Response(response_data, status=status.HTTP_200_OK)

                else:
                    instance.Name = Name
                   
                    instance.Action = Action
                    instance.UpdatedDate = today
                    instance.CreatedUserID = CreatedUserID
                    instance.save()

                    LoyaltyProgram_Log.objects.create(
                        BranchID=BranchID,
                        LoyaltyProgramID=LoyaltyProgramID,
                   
                        Name=Name,
                        FromDate=FromDate,
                        ToDate=ToDate,
                        NoOFDayExpPoint=NoOFDayExpPoint,
                        CardTypeID=CardTypeID,
                        MinimumSalePrice=MinimumSalePrice,
                        Amount=Amount,
                        Amount_Point=Amount_Point,
                        Percentage=Percentage,
                        product=product,
                        ProductGroupIDs=ProductGroupIDs,
                        ProductCategoryIDs=ProductCategoryIDs,
                        is_offer=is_offer,
                        is_Return_MinimumSalePrice=is_Return_MinimumSalePrice,
                       
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    data = {"LoyaltyProgramID": LoyaltyProgramID}
                    data.update(serialized.data)
                    response_data = {
                        "StatusCode": 6000,
                        "data": data
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "In this Card Type LoyaltyProgram is Exists"
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
def loyaltyPrograms(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if LoyaltyProgram.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = LoyaltyProgram.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = LoyaltyProgramRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Loyalty Program Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def loyaltyProgram(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if LoyaltyProgram.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LoyaltyProgram.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = LoyaltyProgramRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Loyalty Program Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_loyaltyProgram(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if LoyaltyProgram.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LoyaltyProgram.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        LoyaltyProgramID = instance.LoyaltyProgramID
      

        Action = "D"

        instance.delete()

        LoyaltyProgram_Log.objects.create(
            BranchID=BranchID,

            LoyaltyProgramID=LoyaltyProgramID,
            Name=instance.Name,
            FromDate=instance.FromDate,
            ToDate=instance.ToDate,
            NoOFDayExpPoint=instance.NoOFDayExpPoint,
            CardTypeID=instance.CardTypeID,
            MinimumSalePrice=instance.MinimumSalePrice,
            Amount=instance.Amount,
            Amount_Point=instance.Amount_Point,
            Percentage=instance.Percentage,
            product=instance.product,
            ProductGroupIDs=instance.ProductGroupIDs,
            ProductCategoryIDs=instance.ProductCategoryIDs,
            is_Return_MinimumSalePrice=instance.is_Return_MinimumSalePrice,
            is_offer=instance.is_offer,
            ProductType=instance.ProductType,
            Calculate_with=instance.Calculate_with,
           

            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Loyalty Program Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Loyalty Program Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


from django.db.models import Sum
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_customer_point(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    Loyalty_Point_Expire = data['Loyalty_Point_Expire']
    try:
        VoucherMasterID = data['SalesMasterID']
    except:
        VoucherMasterID = None
    Type = data['Type']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    # today = datetime.datetime.now()
    print(pk,"today.date")
    today = datetime.datetime.now().date()
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        is_edit = False
        if LoyaltyPoint.objects.filter(BranchID=BranchID,CompanyID=CompanyID,VoucherType="SI",LoyaltyCustomerID__id=pk,is_Radeem=True).exists():
            is_edit = True
        if LoyaltyPoint.objects.filter(LoyaltyCustomerID__id=pk,BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = LoyaltyPoint.objects.filter(
                LoyaltyCustomerID__id=pk,BranchID=BranchID, CompanyID=CompanyID)

            tot_Point = 0
            for i in instances:
                print(tot_Point,i.ExpiryDate)
                if i.Point:
                    if Loyalty_Point_Expire:
                        if i.ExpiryDate:
                            # if i.is_Radeem == False:
                            #     print('float(i.Radeemed_Point) and not i.ExpiryDate >= today:')
                            #     if not float(i.Point) == float(i.Radeemed_Point) and i.ExpiryDate >= today:
                            #         print("EEEEEE")
                            if not today >= i.ExpiryDate:
                                if i.is_Radeem == False:
                                    if i.Radeemed_Point:
                                        Radeemed_Point = i.Radeemed_Point
                                    else:
                                        Radeemed_Point = 0 
                                    print('float(i.Radeemed_Point) and not i.ExpiryDate >= today:')
                                    if not float(i.Point) == float(Radeemed_Point) and i.ExpiryDate >= today:
                                        print("EEEEEE")
                                        if Type == "M" and VoucherMasterID:
                                            if not VoucherMasterID == i.VoucherMasterID:
                                                pnt = float(i.Point) - float(Radeemed_Point)
                                                tot_Point = float(tot_Point) + float(pnt) 
                                                print((tot_Point,"1 EDITTTTTTTTTT"))
                                        elif Type == "A":
                                            print(Radeemed_Point,"RADEEEEEEMEDPOINT",i.Point)
                                            # if i.is_Radeem == False:
                                            pnt = float(i.Point) - float(Radeemed_Point)
                                            tot_Point = float(tot_Point) + float(pnt) 
                                            # tot_Point = float(tot_Point) + float(i.Point) 
                                            print(("2 AAAAAAAAAAAAAAAAAAA"))
                    else:
                        print((VoucherMasterID,"3 MMMMMMMMMMMMMMMMMMM"))
                        if Type == "M" and VoucherMasterID:
                            if not VoucherMasterID == i.VoucherMasterID:
                                tot_Point = float(tot_Point) + float(i.Point) 
                        elif Type == "A":
                            tot_Point = float(tot_Point) + float(i.Point) 
                            print(("4 Kayaryyyyyyyyyyyyyy"))
                # tot_Point = tot_Point.map(float, PriceRounding) + i.Point.map(float, PriceRounding)
            # serialized = LoyaltyPointSerializer(instances, many=True)
            if tot_Point == 0:
                StatusCode = 6001
            else:
                StatusCode = 6000
            response_data = {
                "StatusCode": StatusCode,
                "tot_Point": tot_Point
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Loyalty Program Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_sigle_point(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    MasterId = data['id']
    VoucherType = data['VoucherType']
    print(MasterId,'MasterIdMasterIdMasterIdMasterIdMasterIdMasterIdMasterIdMasterIdMasterIdMasterIdMasterIdMasterIdMasterId')

    serialized1 = ListSerializer(data=request.data)
    # today = datetime.datetime.now()
    print("today.date")
    today = datetime.datetime.now().date()
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if LoyaltyPoint.objects.filter(is_Radeem=True,VoucherMasterID=MasterId,VoucherType=VoucherType,BranchID=BranchID, CompanyID=CompanyID).exists():
            instance = LoyaltyPoint.objects.get(is_Radeem=True,VoucherMasterID=MasterId,VoucherType=VoucherType,BranchID=BranchID, CompanyID=CompanyID)

            
            serialized = LoyaltyPointSerializer(instance)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Loyalty Point Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_loyalty_customer(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    customer_id = data['customer_id']
    LedgerCode = data['LedgerCode']

    serialized1 = ListSerializer(data=request.data)
    # today = datetime.datetime.now()
    print(customer_id,"today.date11111111111111")
    today = datetime.datetime.now().date()
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if customer_id:
            if LoyaltyCustomer.objects.filter(AccountLedgerID__pk=customer_id,BranchID=BranchID, CompanyID=CompanyID).exists():
                # instance = LoyaltyCustomer.objects.get(AccountLedgerID__pk=customer_id,BranchID=BranchID, CompanyID=CompanyID)
                try:
                    instance = LoyaltyCustomer.objects.get(AccountLedgerID__pk=customer_id,BranchID=BranchID, CompanyID=CompanyID)
                except :
                    instance = LoyaltyCustomer.objects.filter(AccountLedgerID__pk=customer_id,AccountLedgerID__LedgerCode=LedgerCode,BranchID=BranchID, CompanyID=CompanyID).first()
                # else:
                #     instance = None

                print(instance,"ROOOOOOOOOOOOOOOOO")
                
                serialized = LoyaltyCustomerRestSerializer(instance)
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Loyalty Point Not Found in this BranchID!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Customer ID is is not Valid!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


from django.db.models import Sum
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_return_point(request):
    data = request.data
    CompanyID = data['CompanyID']
    BranchID = data['BranchID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    loyalty_customer_id = data['loyalty_customer_id']
    is_MinimumSalePrice = data["is_Loyalty_SalesReturn_MinimumSalePrice"]
    # product_id = data['product_id']
    taskList = data['taskList']
    Type = data['Type']

    try:
        SalesReturnMasterID = data['SalesReturnMasterID']        
    except:
        SalesReturnMasterID = None
    
    serialized1 = ListSerializer(data=request.data)
    # today = datetime.datetime.now()
    today = datetime.datetime.now().date()
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        
        if LoyaltyProgram.objects.filter(BranchID=BranchID,CompanyID=CompanyID,FromDate__lte=today,ToDate__gte=today).exists():
            instance = LoyaltyProgram.objects.get(BranchID=BranchID,CompanyID=CompanyID,FromDate__lte=today,ToDate__gte=today)
            print(instance.ProductType)
            return_point = 0
            tot_taxable_amnt = 0
            for data in taskList:
                print(data['ProductID'],"uvaissss")
                product_id = data['ProductID']
                TaxableAmount = data['TaxableAmount']
                single_product_point = sales_return_point(instance,product_id,TaxableAmount,BranchID,CompanyID,is_MinimumSalePrice)
                tot_taxable_amnt+=single_product_point
                
            actual_point = get_actual_point(tot_taxable_amnt,instance)
            print(loyalty_customer_id,tot_taxable_amnt,"tot_TaxableAmount actual_point",actual_point)
            CurrentPoint = 0
            if loyalty_customer_id:
                loyalty_instance = LoyaltyCustomer.objects.get(BranchID=BranchID,CompanyID=CompanyID,LoyaltyCustomerID=loyalty_customer_id)
                CurrentPoint = loyalty_instance.CurrentPoint
                if float(CurrentPoint) >= float(actual_point):
                    if Type == "Create":
                        return_point = float(CurrentPoint) - float(actual_point)
                    elif Type == "Edit":
                        if LoyaltyPoint.objects.filter(BranchID=BranchID,CompanyID=CompanyID,LoyaltyCustomerID__pk=loyalty_instance.pk,VoucherMasterID=SalesReturnMasterID,VoucherType="SR").exists():
                            point_instance = LoyaltyPoint.objects.get(BranchID=BranchID,CompanyID=CompanyID,LoyaltyCustomerID__pk=loyalty_instance.pk,VoucherMasterID=SalesReturnMasterID,VoucherType="SR")
                        
                            edited_point = point_instance.Point
                            print(edited_point,"UNIQUE INSTANCE@@@@@",loyalty_instance.pk,"@@@@@@@@@@@@@@@@",point_instance)
                            return_point = float(CurrentPoint) - float(actual_point) 
                            return_point = return_point - float(edited_point)
                                        
            response_data = {
                "StatusCode": 6000,
                'return_point':return_point,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Loyalty Program Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)