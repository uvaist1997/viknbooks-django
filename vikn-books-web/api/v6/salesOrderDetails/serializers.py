from rest_framework import serializers
from brands.models import SalesOrderDetails, SalesOrderDetailsDummy, Product


class SalesOrderDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesOrderDetails
        fields = ('id','BranchID','SalesOrderMasterID','DeliveryDetailsID','OrederDetailsID','ProductID',
        	'Qty','FreeQty','UnitPrice',
        	'RateWithTax','CostPerPrice','PriceListID','TaxID','TaxType','DiscountPerc',
            'DiscountAmount','GrossAmount','TaxableAmount','VATPerc','VATAmount',
            'SGSTPerc','SGSTAmount','CGSTPerc','CGSTAmount','IGSTPerc','IGSTAmount',
            'NetAmount','Sauceoption')


class SalesOrderDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesOrderDetails
        fields = ('id','SalesOrderDetailsID','BranchID','Action','SalesOrderMasterID','DeliveryDetailsID','OrederDetailsID','ProductID',
        	'Qty','FreeQty','UnitPrice',
        	'RateWithTax','CostPerPrice','PriceListID','TaxID','TaxType','DiscountPerc','DiscountAmount',
            'GrossAmount','TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount','CGSTPerc',
            'CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','Sauceoption')



class SalesOrderDetailsDummySerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerPrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    TaxableAmount = serializers.SerializerMethodField()
    VATPerc = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTPerc = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTPerc = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTPerc = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderDetailsDummy
        fields = ('id','BranchID','SalesOrderMasterID','DeliveryDetailsID','OrderDetailsID','ProductID','ProductName','Qty','FreeQty','UnitPrice','RateWithTax',
            'CostPerPrice','PriceListID','TaxID',
            'TaxType','DiscountPerc','DiscountAmount','GrossAmount','TaxableAmount','VATPerc','VATAmount',
            'SGSTPerc','SGSTAmount','CGSTPerc','CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','Flavour','CreatedUserID',
            'detailID')


    def get_ProductName(self, instances):

        DataBase = self.context.get("DataBase")

        ProductID = instances.ProductID
        BranchID = instances.BranchID

        product = Product.objects.get(ProductID=ProductID,BranchID=BranchID)

        ProductName = product.ProductName

        return ProductName


    def get_Qty(self, instances):


        Qty = instances.Qty

        Qty = round(Qty,2)

        return str(Qty)


    def get_FreeQty(self, instances):


        FreeQty = instances.FreeQty

        FreeQty = round(FreeQty,2)

        return str(FreeQty)


    def get_UnitPrice(self, instances):


        UnitPrice = instances.UnitPrice

        UnitPrice = round(UnitPrice,2)

        return str(UnitPrice)


    def get_RateWithTax(self, instances):


        RateWithTax = instances.RateWithTax

        RateWithTax = round(RateWithTax,2)

        return str(RateWithTax)


    def get_CostPerPrice(self, instances):


        CostPerPrice = instances.CostPerPrice

        CostPerPrice = round(CostPerPrice,2)

        return str(CostPerPrice)
        

    def get_DiscountPerc(self, instances):


        DiscountPerc = instances.DiscountPerc

        DiscountPerc = round(DiscountPerc,2)

        return str(DiscountPerc)


    def get_DiscountAmount(self, instances):


        DiscountAmount = instances.DiscountAmount

        DiscountAmount = round(DiscountAmount,2)

        return str(DiscountAmount)


    def get_GrossAmount(self, instances):


        GrossAmount = instances.GrossAmount

        GrossAmount = round(GrossAmount,2)

        return str(GrossAmount)


    def get_TaxableAmount(self, instances):


        TaxableAmount = instances.TaxableAmount

        TaxableAmount = round(TaxableAmount,2)

        return str(TaxableAmount)


    def get_VATPerc(self, instances):


        VATPerc = instances.VATPerc

        VATPerc = round(VATPerc,2)

        return str(VATPerc)


    def get_VATAmount(self, instances):


        VATAmount = instances.VATAmount

        VATAmount = round(VATAmount,2)

        return str(VATAmount)


    def get_SGSTPerc(self, instances):


        SGSTPerc = instances.SGSTPerc

        SGSTPerc = round(SGSTPerc,2)

        return str(SGSTPerc)


    def get_SGSTAmount(self, instances):


        SGSTAmount = instances.SGSTAmount

        SGSTAmount = round(SGSTAmount,2)

        return str(SGSTAmount)


    def get_CGSTPerc(self, instances):


        CGSTPerc = instances.CGSTPerc

        CGSTPerc = round(CGSTPerc,2)

        return str(CGSTPerc)



    def get_CGSTAmount(self, instances):


        CGSTAmount = instances.CGSTAmount

        CGSTAmount = round(CGSTAmount,2)

        return str(CGSTAmount)


    def get_IGSTPerc(self, instances):


        IGSTPerc = instances.IGSTPerc

        IGSTPerc = round(IGSTPerc,2)

        return str(IGSTPerc)


    def get_IGSTAmount(self, instances):


        IGSTAmount = instances.IGSTAmount

        IGSTAmount = round(IGSTAmount,2)

        return str(IGSTAmount)


    def get_NetAmount(self, instances):


        NetAmount = instances.NetAmount

        NetAmount = round(NetAmount,2)

        return str(NetAmount)
