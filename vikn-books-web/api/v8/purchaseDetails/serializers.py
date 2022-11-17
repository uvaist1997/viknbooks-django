from rest_framework import serializers
from brands.models import PurchaseDetails, PurchaseDetailsDummy, Product


class PurchaseDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseDetails
        fields = ('id','BranchID','PurchaseMasterID','DeliveryDetailsID','OrederDetailsID','ProductID',
        	'Qty','FreeQty','UnitPrice',
        	'RateWithTax','CostPerPrice','PriceListID','DiscountPerc',
            'DiscountAmount','GrossAmount','TaxableAmount','VATPerc','VATAmount',
            'SGSTPerc','SGSTAmount','CGSTPerc','CGSTAmount','IGSTPerc','IGSTAmount',
            'NetAmount','TAX1Perc','TAX1Amount','TAX2Perc','TAX2Amount','TAX3Perc','TAX3Amount')


class PurchaseDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseDetails
        fields = ('id','PurchaseDetailsID','BranchID','Action','PurchaseMasterID','DeliveryDetailsID','OrederDetailsID','ProductID',
        	'Qty','FreeQty','UnitPrice',
        	'RateWithTax','CostPerPrice','PriceListID','DiscountPerc','DiscountAmount',
            'GrossAmount','TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount','CGSTPerc',
            'CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','TAX1Perc','TAX1Amount','TAX2Perc','TAX2Amount','TAX3Perc','TAX3Amount')


class PurchaseDetailsDummySerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerItem = serializers.SerializerMethodField()
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
    TAX1Perc = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Perc = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Perc = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseDetailsDummy
        fields = ('id','unq_id','PurchaseDetailsID','BranchID','ProductID','ProductName','Qty','FreeQty','UnitPrice','RateWithTax','CostPerItem','PriceListID',
        'DiscountPerc','DiscountAmount',
            'AddlDiscPerc','AddlDiscAmt','GrossAmount','TaxableAmount','VATPerc','VATAmount','SGSTPerc',
            'SGSTAmount','CGSTPerc','CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','CreatedUserID','detailID',
            'TAX1Perc','TAX1Amount','TAX2Perc','TAX2Amount','TAX3Perc','TAX3Amount')


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


    def get_CostPerItem(self, instances):

        CostPerItem = instances.CostPerItem

        CostPerItem = round(CostPerItem,2)

        return str(CostPerItem)
        

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


    def get_TAX1Perc(self, instances):

        TAX1Perc = instances.TAX1Perc

        TAX1Perc = round(TAX1Perc,2)

        return str(TAX1Perc)


    def get_TAX1Amount(self, instances):

        TAX1Amount = instances.TAX1Amount

        TAX1Amount = round(TAX1Amount,2)

        return str(TAX1Amount)


    def get_TAX2Perc(self, instances):

        TAX2Perc = instances.TAX2Perc

        TAX2Perc = round(TAX2Perc,2)

        return str(TAX2Perc)


    def get_TAX2Amount(self, instances):

        TAX2Amount = instances.TAX2Amount

        TAX2Amount = round(TAX2Amount,2)

        return str(TAX2Amount)


    def get_TAX3Perc(self, instances):

        TAX3Perc = instances.TAX3Perc

        TAX3Perc = round(TAX3Perc,2)

        return str(TAX3Perc)


    def get_TAX3Amount(self, instances):

        TAX3Amount = instances.TAX3Amount

        TAX3Amount = round(TAX3Amount,2)

        return str(TAX3Amount)



class PurchaseDetailsDeletedDummySerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseDetailsDummy
        fields = ('id','PurchaseDetailsID','unq_id')