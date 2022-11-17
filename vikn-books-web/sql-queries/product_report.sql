SELECT SP."ProductID",PD."ProductName",      
CASE        
WHEN "VoucherType" = 'SI' THEN 'Sales Invoice'        
WHEN "VoucherType" = 'SR' THEN 'Sales Return'        
WHEN "VoucherType" = 'PI' THEN 'Purchase Invoice'        
WHEN "VoucherType" = 'PR' THEN 'Purchase Return'        
WHEN "VoucherType" = 'OS' THEN 'Opening Stock'        
WHEN "VoucherType" = 'WO' THEN 'Work Order'        
WHEN "VoucherType" = 'ST' THEN 'Stock Transfer'      
WHEN "VoucherType" = 'ES' THEN 'Excess Stock'      
WHEN "VoucherType" = 'SS' THEN 'Shortage Stock'      
WHEN "VoucherType" = 'DS' THEN 'Damage Stock'      
WHEN "VoucherType" = 'US' THEN 'Used Stock'      
END AS VoucherType,          
SUM("QtyIn") AS In ,SUM("QtyOut") AS Out ,SP."Date" as Date, PL."UnitID" ,      


CASE        

WHEN  "VoucherType" = 'SI' AND SUM("QtyIn")> 0 THEN(select SUM(SD."TaxableAmount")  from public."salesDetails_salesDetail" AS SD      
INNER JOIN public."salesMasters_salesMaster" AS SM ON SM."SalesMasterID" = SD."SalesMasterID"       
WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        
WHEN "VoucherType" = 'SR' AND SUM("QtyIn")> 0 THEN(select SUM(SD."TaxableAmount")  from public."salesReturnDetails_salesReturnDetail" AS SD        
INNER JOIN public."salesReturnMasters_salesReturnMaster" AS SM ON SM."SalesReturnMasterID" = SD."SalesReturnMasterID"         
WHERE "ProductID" = SP."ProductID" AND SM."VoucherDate" = '2021-12-01' )      
WHEN "VoucherType" = 'PI' AND SUM("QtyIn")> 0 THEN(select SUM(SD."TaxableAmount")  from public."purchaseDetailses_purchaseDetails" AS SD      
INNER JOIN public."purchaseMasters_purchaseMaster" AS SM ON SM."PurchaseMasterID" = SD."PurchaseMasterID"      
WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')      
WHEN "VoucherType" = 'PR' AND SUM("QtyIn")> 0 THEN(select SUM(SD."TaxableAmount")  from public."purchaseReturnDetails_purchaseReturnDetail" AS SD      
INNER JOIN public."purchaseReturnMasters_purchaseReturnMaster" AS SM ON SM."PurchaseReturnMasterID" = SD."PurchaseReturnMasterID"      
WHERE "ProductID" = SP."ProductID" AND SM."VoucherDate" = '2021-12-01')      
WHEN "VoucherType" = 'OS' AND SUM("QtyIn")> 0 THEN(select SUM("Amount")  from public."openingStockDetailss_openingStockDetails" AS SD      
INNER JOIN public."openingStockMasters_openingStockMaster" AS SM ON SM."OpeningStockMasterID" = SD."OpeningStockMasterID"      
WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        
WHEN "VoucherType" = 'ST' AND SUM("QtyIn")> 0 THEN(select SUM("Amount")  from public."stockTransferDetails_stockTransferDetails" AS SD       
INNER JOIN public."stockTransferMaster_ID_stockTransferMaster_ID" AS SM ON SM."StockTransferMasterID" = SD."StockTransferMasterID"      
WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        


WHEN "VoucherType" = 'ES' AND SUM("QtyIn")> 0 THEN(select SUM("ExcessStock") * SUM("CostPerItem")  from public."excessStockDetails_excessStockDetails" AS SD      
INNER JOIN public."excessStockMaster_excessStockMaster" AS SM ON SM."ExcessStockMasterID" = SD."ExcessStockMasterID"      
WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        
ELSE 0        
END AS Amount_In        

, CASE        
WHEN "VoucherType" = 'SI' AND SUM("QtyOut")> 0 THEN(select SUM(SD."TaxableAmount")  from public."salesDetails_salesDetail" AS SD      
INNER JOIN public."salesMasters_salesMaster" AS SM ON SM."SalesMasterID" = SD."SalesMasterID"      
WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')      
WHEN "VoucherType" = 'SR' AND SUM("QtyOut")> 0 THEN(select SUM(SD."TaxableAmount")  from public."salesReturnDetails_salesReturnDetail" AS SD      
INNER JOIN public."salesReturnMasters_salesReturnMaster" AS SM ON SM."SalesReturnMasterID" = SD."SalesReturnMasterID"      
WHERE "ProductID" = SP."ProductID" AND SM."VoucherDate" = '2021-12-01')      
WHEN "VoucherType" = 'PI' AND SUM("QtyOut")> 0 THEN(select SUM(SD."TaxableAmount")  from public."purchaseDetailses_purchaseDetails" AS SD      
INNER JOIN public."purchaseMasters_purchaseMaster" AS SM ON SM."PurchaseMasterID" = SD."PurchaseMasterID"      
WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')      
WHEN "VoucherType" = 'PR' AND SUM("QtyOut")> 0 THEN(select SUM(SD."TaxableAmount")  from public."purchaseReturnDetails_purchaseReturnDetail" AS SD      
INNER JOIN public."purchaseReturnMasters_purchaseReturnMaster" AS SM ON SM."PurchaseReturnMasterID" = SD."PurchaseReturnMasterID"      
WHERE "ProductID" = SP."ProductID" AND SM."VoucherDate" = '2021-12-01')        
WHEN "VoucherType" = 'OS' AND SUM("QtyOut")> 0 THEN(select SUM("Amount")  from public."openingStockDetailss_openingStockDetails" AS SD      
INNER JOIN public."openingStockMasters_openingStockMaster" AS SM ON SM."OpeningStockMasterID" = SD."OpeningStockMasterID"      
WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')      
WHEN "VoucherType" = 'ST' AND SUM("QtyOut")> 0 THEN(select SUM("Amount")  from public."stockTransferDetails_stockTransferDetails" AS SD      
INNER JOIN public."stockTransferMaster_ID_stockTransferMaster_ID" AS SM ON SM."StockTransferMasterID" = SD."StockTransferMasterID"      
WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')      
WHEN "VoucherType" = 'SS' AND SUM("QtyOut")> 0 THEN(select SUM("ShortageStock") * SUM("CostPerItem")  from public."shortageStockDetails_shortageStockDetails" AS SD        
INNER JOIN public."shortageStockMaster_shortageStockMaster" AS SM ON SM."ShortageStockMasterID" = SD."ShortageStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        



WHEN "VoucherType" = 'DS' AND SUM("QtyOut")> 0 THEN(select SUM("DamageStock") * SUM("CostPerItem")  from public."damageStockDetails_damageStockDetails" AS SD        

INNER JOIN public."damageStockMaster_damageStockMaster" AS SM ON SM."DamageStockMasterID" = SD."DamageStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        



WHEN "VoucherType" = 'US' AND SUM("QtyOut")> 0 THEN(select SUM("UsedStock") * SUM("CostPerItem")  from public."usedStockDetails_usedStockDetails" AS SD        

INNER JOIN public."usedStockMaster_usedStockMaster" AS SM ON SM."UsedStockMasterID" = SD."UsedStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        


ELSE 0        


END AS Amount_Out        

, CASE        
WHEN "VoucherType" = 'SI' AND SUM("QtyIn")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyIn"))  from public."salesDetails_salesDetail" AS SD        

INNER JOIN public."salesMasters_salesMaster" AS SM ON SM."SalesMasterID" = SD."SalesMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')                

WHEN "VoucherType" = 'SR' AND SUM("QtyIn")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyIn"))  from public."salesReturnDetails_salesReturnDetail" AS SD        

INNER JOIN public."salesReturnMasters_salesReturnMaster" AS SM ON SM."SalesReturnMasterID" = SD."SalesReturnMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."VoucherDate" = '2021-12-01')        


WHEN "VoucherType" = 'PI' AND SUM("QtyIn")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyIn"))  from public."purchaseDetailses_purchaseDetails" AS SD        

INNER JOIN public."purchaseMasters_purchaseMaster" AS SM ON SM."PurchaseMasterID" = SD."PurchaseMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        


WHEN "VoucherType" = 'PR' AND SUM("QtyIn")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyIn"))   from public."purchaseReturnDetails_purchaseReturnDetail" AS SD        

INNER JOIN public."purchaseReturnMasters_purchaseReturnMaster" AS SM ON SM."PurchaseReturnMasterID" = SD."PurchaseReturnMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."VoucherDate" = '2021-12-01')        


WHEN "VoucherType" = 'OS' AND SUM("QtyIn")> 0 THEN(select(SUM("Amount") / SUM("QtyIn"))  from public."openingStockDetailss_openingStockDetails" AS SD        

INNER JOIN public."openingStockMasters_openingStockMaster" AS SM ON SM."OpeningStockMasterID" = SD."OpeningStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        


WHEN "VoucherType" = 'ST' AND SUM("QtyIn")> 0 THEN(select(SUM("Amount") / SUM("QtyIn"))  from public."stockTransferDetails_stockTransferDetails" AS SD        

INNER JOIN public."stockTransferMaster_ID_stockTransferMaster_ID" AS SM ON SM."StockTransferMasterID" = SD."StockTransferMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        




WHEN "VoucherType" = 'ES' AND SUM("QtyIn")> 0 THEN(select(SUM("ExcessStock") * SUM("CostPerItem")) / SUM("QtyIn")  from public."excessStockDetails_excessStockDetails" AS SD        

INNER JOIN public."excessStockMaster_excessStockMaster" AS SM ON SM."ExcessStockMasterID" = SD."ExcessStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')       
ELSE 0        


END AS  PurchasePrice        



, CASE        
WHEN  "VoucherType" = 'SI' AND SUM("QtyOut")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyOut"))  from public."salesDetails_salesDetail" AS SD        

INNER JOIN public."salesMasters_salesMaster" AS SM ON SM."SalesMasterID" = SD."SalesMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        


WHEN "VoucherType" = 'SR' AND SUM("QtyIn")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyIn"))  from public."salesReturnDetails_salesReturnDetail" AS SD        

INNER JOIN public."salesReturnMasters_salesReturnMaster" AS SM ON SM."SalesReturnMasterID" = SD."SalesReturnMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."VoucherDate" = '2021-12-01')        


WHEN "VoucherType" = 'PI' AND SUM("QtyIn")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyIn"))  from public."purchaseDetailses_purchaseDetails" AS SD        

INNER JOIN public."purchaseMasters_purchaseMaster" AS SM ON SM."PurchaseMasterID" = SD."PurchaseMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        


WHEN "VoucherType" = 'PR' AND SUM("QtyOut")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyOut"))   from public."purchaseReturnDetails_purchaseReturnDetail" AS SD        

INNER JOIN public."purchaseReturnMasters_purchaseReturnMaster" AS SM ON SM."PurchaseReturnMasterID" = SD."PurchaseReturnMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."VoucherDate" = '2021-12-01')        


WHEN "VoucherType" = 'OS' AND SUM("QtyIn")> 0 THEN(select(SUM("Amount") / SUM("QtyIn"))  from public."openingStockDetailss_openingStockDetails" AS SD        

INNER JOIN public."openingStockMasters_openingStockMaster" AS SM ON SM."OpeningStockMasterID" = SD."OpeningStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        

--WHEN "VoucherType" = 'ST' AND SUM("QtyIn")> 0 THEN(select(SUM("Amount") / SUM("QtyIn"))  from public."stockTransferDetails_stockTransferDetails" AS SD        
--INNER JOIN public."stockTransferMaster_ID_stockTransferMaster_ID" AS SM ON SM."StockTransferMasterID" = SD."StockTransferMasterID"        
--WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        



WHEN "VoucherType" = 'ES' AND SUM("QtyIn")> 0 THEN(select(SUM("ExcessStock") * SUM("CostPerItem")) / SUM("QtyIn")  from public."excessStockDetails_excessStockDetails" AS SD        

INNER JOIN public."excessStockMaster_excessStockMaster" AS SM ON SM."ExcessStockMasterID" = SD."ExcessStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        



WHEN "VoucherType" = 'SS' AND SUM("QtyOut")> 0 THEN(select SUM("ShortageStock") * SUM("CostPerItem")  from public."shortageStockDetails_shortageStockDetails" AS SD        

INNER JOIN public."shortageStockMaster_shortageStockMaster" AS SM ON SM."ShortageStockMasterID" = SD."ShortageStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        



WHEN "VoucherType" = 'DS' AND SUM("QtyOut")> 0 THEN(select SUM("DamageStock") * SUM("CostPerItem")  from public."damageStockDetails_damageStockDetails" AS SD        

INNER JOIN public."damageStockMaster_damageStockMaster" AS SM ON SM."DamageStockMasterID" = SD."DamageStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        



WHEN "VoucherType" = 'US' AND SUM("QtyOut")> 0 THEN(select SUM("UsedStock") * SUM("CostPerItem")  from public."usedStockDetails_usedStockDetails" AS SD        

INNER JOIN public."usedStockMaster_usedStockMaster" AS SM ON SM."UsedStockMasterID" = SD."UsedStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        




ELSE 0        


END AS  Cost        



, CASE        
WHEN  "VoucherType" = 'SI' AND SUM("QtyOut")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyOut"))   from public."salesDetails_salesDetail" AS SD        

INNER JOIN public."salesMasters_salesMaster" AS SM ON SM."SalesMasterID" = SD."SalesMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        


WHEN "VoucherType" = 'SR' AND SUM("QtyOut")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyOut"))   from public."salesReturnDetails_salesReturnDetail" AS SD        

INNER JOIN public."salesReturnMasters_salesReturnMaster" AS SM ON SM."SalesReturnMasterID" = SD."SalesReturnMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."VoucherDate" = '2021-12-01')        


WHEN "VoucherType" = 'PI' AND SUM("QtyOut")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyOut"))   from public."purchaseDetailses_purchaseDetails" AS SD        

INNER JOIN public."purchaseMasters_purchaseMaster" AS SM ON SM."PurchaseMasterID" = SD."PurchaseMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        


WHEN "VoucherType" = 'PR' AND SUM("QtyOut")> 0 THEN(select(SUM(SD."TaxableAmount") / SUM("QtyOut"))  from public."purchaseReturnDetails_purchaseReturnDetail" AS SD        

INNER JOIN public."purchaseReturnMasters_purchaseReturnMaster" AS SM ON SM."PurchaseReturnMasterID" = SD."PurchaseReturnMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."VoucherDate" = '2021-12-01')        


WHEN "VoucherType" = 'OS' AND SUM("QtyOut")> 0 THEN(select(SUM("Amount") / SUM("QtyOut"))  from public."openingStockDetailss_openingStockDetails" AS SD        

INNER JOIN public."openingStockMasters_openingStockMaster" AS SM ON SM."OpeningStockMasterID" = SD."OpeningStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        


WHEN "VoucherType" = 'ST' AND SUM("QtyOut")> 0 THEN(select(SUM("Amount") / SUM("QtyOut"))  from public."stockTransferDetails_stockTransferDetails" AS SD        

INNER JOIN public."stockTransferMaster_ID_stockTransferMaster_ID" AS SM ON SM."StockTransferMasterID" = SD."StockTransferMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        



WHEN "VoucherType" = 'ES' AND SUM("QtyOut")> 0 THEN(select(SUM("ShortageStock") * SUM("CostPerItem")) / SUM("QtyOut")  from public."shortageStockDetails_shortageStockDetails" AS SD        

INNER JOIN public."shortageStockMaster_shortageStockMaster" AS SM ON SM."ShortageStockMasterID" = SD."ShortageStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        



WHEN "VoucherType" = 'DS' AND SUM("QtyOut")> 0 THEN(select(SUM("DamageStock") * SUM("CostPerItem")) / SUM("QtyOut")  from public."damageStockDetails_damageStockDetails" AS SD        

INNER JOIN public."damageStockMaster_damageStockMaster" AS SM ON SM."DamageStockMasterID" = SD."DamageStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        



WHEN "VoucherType" = 'US' AND SUM("QtyOut")> 0 THEN(select(SUM("UsedStock") * SUM("CostPerItem")) / SUM("QtyOut")  from public."usedStockDetails_usedStockDetails" AS SD        

INNER JOIN public."usedStockMaster_usedStockMaster" AS SM ON SM."UsedStockMasterID" = SD."UsedStockMasterID"        

WHERE "ProductID" = SP."ProductID" AND SM."Date" = '2021-12-01')        



ELSE 0        


END AS  SalesPrice        

, CASE        
WHEN  "VoucherType" = 'SI'   THEN (select "VoucherNo" from public."salesMasters_salesMaster"       

WHERE "SalesMasterID"= SP."VoucherMasterID" AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97')        


WHEN "VoucherType" = 'SR'   THEN (select "VoucherNo" from public."salesReturnMasters_salesReturnMaster" WHERE      

"SalesReturnMasterID"= SP."VoucherMasterID" AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97')        


WHEN "VoucherType" = 'PI'   THEN (select "VoucherNo"   from public."purchaseMasters_purchaseMaster" WHERE       

"PurchaseMasterID"= SP."VoucherMasterID" AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97')        


WHEN "VoucherType" = 'PR'   THEN (select "VoucherNo"  from public."purchaseReturnMasters_purchaseReturnMaster"       

WHERE "PurchaseReturnMasterID"= SP."VoucherMasterID" AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' )        


WHEN "VoucherType" = 'OS'   THEN (select "VoucherNo"  from       

public."openingStockMasters_openingStockMaster" WHERE "OpeningStockMasterID"= SP."VoucherMasterID" AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' )        


WHEN "VoucherType" = 'ST'   THEN (select "VoucherNo"  from public."stockTransferMaster_ID_stockTransferMaster_ID"       


WHERE "StockTransferMasterID"= SP."VoucherMasterID" AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' )        


WHEN "VoucherType" = 'ES'   THEN(select "VoucherNo"  from public."shortageStockMaster_shortageStockMaster"       

WHERE "ShortageStockMasterID"= SP."VoucherMasterID" AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' )        


WHEN "VoucherType" = 'DS'   THEN(select "VoucherNo"  from       

public."damageStockMaster_damageStockMaster" WHERE "DamageStockMasterID"= SP."VoucherMasterID" AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' )        


WHEN "VoucherType" = 'US'   THEN(select "VoucherNo" from public."usedStockMaster_usedStockMaster"       

WHERE "UsedStockMasterID"= SP."VoucherMasterID" AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97')        



ELSE '0'        


END AS  VoucherNo     


FROM public."stockPosting_stockPosting" AS SP        
INNER JOIN public."pricelist_pricelist" AS PL ON SP."PriceListID" = PL."PriceListID" AND PL."DefaultUnit" = 'TRUE'        
INNER JOIN public."products_product" AS PD ON PD."ProductID" = SP."ProductID"        
WHERE SP."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' AND "Date" = '2021-12-01' AND SP."BranchID" = '1'        
GROUP BY SP."ProductID","VoucherType" , "Date" ,PD."ProductName",PL."UnitID"  ,SP."VoucherMasterID"      
