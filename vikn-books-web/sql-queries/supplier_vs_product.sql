-- Supplier filter
SELECT  
  -- P."ProductID",
  P."ProductName",
  (SELECT  round("UnitPrice",2) FROM public."purchaseDetailses_purchaseDetails"  WHERE "BranchID" = '1'  
AND "ProductID" = SP."ProductID" AND "CompanyID_id" = SP."CompanyID_id"    ORDER BY "PurchaseDetailsID" DESC LIMIT 1 ) AS LastPurchasePrice,
(SELECT  coalesce(round("Qty",2),0)  FROM public."purchaseDetailses_purchaseDetails"  WHERE "BranchID" = '1'  
AND "ProductID" = SP."ProductID" AND "CompanyID_id" = SP."CompanyID_id"  ORDER BY "PurchaseDetailsID" DESC LIMIT 1 ) as LastPurchaseQty ,
 (SELECT coalesce(round(SUM("QtyOut"),2),0) FROM public."stockPosting_stockPosting" WHERE  
  "VoucherType" = 'SI' AND "BranchID" = '1'  
  AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID" 
  AND "CompanyID_id" = SP."CompanyID_id" 
  ) AS TotalSales 
  ,( SELECT coalesce(round((SUM("QtyOut") * SUM("Rate")),2),0) FROM public."stockPosting_stockPosting" WHERE  
  "VoucherType" = 'SI' AND "BranchID" = '1'  
  AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"  
  AND "CompanyID_id" = SP."CompanyID_id"
  ) AS TotalSalesAmount 

    ,( SELECT coalesce(round(SUM("Rate") / (SUM("QtyOut")),2),0) FROM public."stockPosting_stockPosting" WHERE  
  "VoucherType" = 'SI' AND "BranchID" = '1'  
  AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"  
  AND "CompanyID_id" = SP."CompanyID_id"
  ) AS AvgSalesRate ,

     
  coalesce(round(SUM(SP."QtyIn"),2),0) AS TotalPurchase,  
  coalesce(round((SUM(SP."QtyIn") * SUM(SP."Rate")),2),0) AS TotalPurchaseAmount,  
    coalesce(round(SUM(SP."Rate") / (SUM(SP."QtyIn")),2),0) AS AvgPurchaseRate,  
    ( SELECT coalesce(round(SUM("QtyIn"),2),0) FROM public."stockPosting_stockPosting" WHERE  
  "VoucherType" = 'SR' AND "BranchID" = '1'  
  AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID" 
  AND "CompanyID_id" = SP."CompanyID_id" 
  ) AS TotalSalesReturn,
    ( SELECT coalesce(round((SUM("QtyIn") * SUM("Rate")),2),0) FROM public."stockPosting_stockPosting" WHERE  
  "VoucherType" = 'SR' AND "BranchID" = '1'  
  AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"  
  AND "CompanyID_id" = SP."CompanyID_id"
  ) AS TotalSalesReturnAmount  
  
  ,( SELECT coalesce(round(SUM("Rate") / (SUM("QtyIn")),2),0) FROM public."stockPosting_stockPosting" WHERE  
  "VoucherType" = 'SR' AND "BranchID" = '1'  
  AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"  
  AND "CompanyID_id" = SP."CompanyID_id"
  ) AS AvgSalesReturnRate  ,

  ( SELECT coalesce(round(SUM("QtyOut"),2),0) FROM public."stockPosting_stockPosting" WHERE  
  "VoucherType" = 'PR' AND "BranchID" = '1'  
  AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID" 
  AND "CompanyID_id" = SP."CompanyID_id" 
  ) AS TotalPurchaseReturn  
  
  ,( SELECT coalesce(round((SUM("QtyOut") * SUM("Rate")),2),0) FROM public."stockPosting_stockPosting" WHERE  
  "VoucherType" = 'PR' AND "BranchID" = '1'  
  AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"  
  AND "CompanyID_id" = SP."CompanyID_id"
  ) AS TotalPurchaseReturnAmount  
  
 ,( SELECT coalesce(round(SUM("Rate") / (SUM("QtyOut")),2),0) FROM public."stockPosting_stockPosting" WHERE  
  "VoucherType" = 'PR' AND "BranchID" = '1'  
  AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID" 
  AND "CompanyID_id" = SP."CompanyID_id" 
  ) AS AvgPurchaseReturnRate  

  ,( SELECT coalesce(round(SUM("QtyIn") - SUM("QtyOut"),2),0) FROM public."stockPosting_stockPosting" WHERE  
   "BranchID" = '1' 
  AND "ProductID" = SP."ProductID"  
  AND "CompanyID_id" = SP."CompanyID_id"
  ) AS CurrentStock ,

   (SELECT "UnitName" FROM public."units_unit" WHERE  
  "UnitID" = PL."UnitID" AND "BranchID" = '1' AND "CompanyID_id" = SP."CompanyID_id") AS Unit 

  
   

From public."stockPosting_stockPosting" AS SP  
INNER JOIN public."products_product" AS P ON P."ProductID" = SP."ProductID" AND P."CompanyID_id" = SP."CompanyID_id" 
INNER JOIN public."pricelist_pricelist" AS PL ON PL."PriceListID" = SP."PriceListID"  AND PL."CompanyID_id" = SP."CompanyID_id"
INNER JOIN public."purchaseMasters_purchaseMaster" AS PM ON PM."PurchaseMasterID" = SP."VoucherMasterID"  AND PM."CompanyID_id" = SP."CompanyID_id"
INNER JOIN public."accountLedger_accountLedger" AS AL ON PM."LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = SP."CompanyID_id" 
WHERE AL."AccountGroupUnder" = '29' AND SP."VoucherType" = 'PI' AND SP."BranchID" = '1'  AND PM."LedgerID" = '103'  
AND SP."Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND SP."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'
  GROUP BY SP."ProductID",              
P."ProductName",             
PL."UnitID",        
P."ProductCode",        
PM."LedgerID",              
AL."LedgerName"  ,       
P."ProductID",      
SP."Date",      
SP."BranchID",  
SP."CompanyID_id" 



----------------------------------------------------------------------
-- product filter

SELECT DISTINCT  
SP."ProductID",    
P."ProductName",    
(SELECT "UnitName" FROM public."units_unit" WHERE  
  "UnitID" = PL."UnitID" AND "BranchID" = '1' AND "CompanyID_id" = SP."CompanyID_id") AS Unit,
P."ProductCode",    
PM."LedgerID",    
AL."LedgerName" AS Supplier  
        
        
,(SELECT SUM("QtyIn") FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'PI' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"
  AND "CompanyID_id" = SP."CompanyID_id" 
) AS TotalPurchase  
  
,(SELECT (SUM("QtyIn") * SUM("Rate")) FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'PI' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"  
AND "CompanyID_id" = SP."CompanyID_id" 
) AS TotalPurchaseAmount  
  
,(SELECT SUM("Rate") / (SUM("QtyIn")) FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'PI' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"  
AND "CompanyID_id" = SP."CompanyID_id" 
) AS AvgPurchaseRate  
  
  
,( SELECT SUM("QtyOut") FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'SI' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID" 
AND "CompanyID_id" = SP."CompanyID_id"  
) AS TotalSales  
  
,( SELECT (SUM("QtyOut") * SUM("Rate")) FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'SI' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"
AND "CompanyID_id" = SP."CompanyID_id"   
) AS TotalSalesAmount  
  
,( SELECT SUM("Rate") / (SUM("QtyOut")) FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'SI' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"  
AND "CompanyID_id" = SP."CompanyID_id" 
) AS AvgSalesRate  
  
,( SELECT SUM("QtyIn") FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'SR' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID" 
AND "CompanyID_id" = SP."CompanyID_id"  
) AS TotalSalesReturn  
  
,( SELECT (SUM("QtyIn") * SUM("Rate")) FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'SR' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"  
AND "CompanyID_id" = SP."CompanyID_id" 
) AS TotalSalesReturnAmount  
  
,( SELECT SUM("Rate") / (SUM("QtyIn")) FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'SR' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID" 
AND "CompanyID_id" = SP."CompanyID_id"  
) AS AvgSalesReturnRate  
  
  
,( SELECT SUM("QtyOut") FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'PR' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID"
AND "CompanyID_id" = SP."CompanyID_id"   
) AS TotalPurchaseReturn  
  
,( SELECT (SUM("QtyOut") * SUM("Rate")) FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'PR' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID" 
AND "CompanyID_id" = SP."CompanyID_id"  
) AS TotalPurchaseReturnAmount  
  
,( SELECT SUM("Rate") / (SUM("QtyOut")) FROM public."stockPosting_stockPosting" WHERE  
"VoucherType" = 'PR' AND "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID" 
AND "CompanyID_id" = SP."CompanyID_id"  
) AS AvgPurchaseReturnRate  
  
,( SELECT SUM("QtyIn") - SUM("QtyOut") FROM public."stockPosting_stockPosting" WHERE  
 "BranchID" = '1'  
AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND "ProductID" = SP."ProductID" 
AND "CompanyID_id" = SP."CompanyID_id"  
) AS CurrentStock  
  
 ,( SELECT SUM("QtyIn") - SUM("QtyOut") FROM public."stockPosting_stockPosting" WHERE  
   "BranchID" = '1'  
  AND "ProductID" = SP."ProductID"  
  AND "CompanyID_id" = SP."CompanyID_id" 
  ) AS CurrentPrimaryStock  
  
  ,( SELECT SUM("QtyOut") FROM public."stockPosting_stockPosting" WHERE  
   "BranchID" = '1'  AND "VoucherType" = 'ST'  
  AND "ProductID" = SP."ProductID" AND "Date" BETWEEN '2022-01-01' AND '2022-02-21'
  AND "CompanyID_id" = SP."CompanyID_id"   
  ) AS PrimaryStockTranferedOut,  
  
(SELECT  "UnitPrice" FROM public."purchaseDetailses_purchaseDetails"  WHERE "BranchID" = '1'  
AND "ProductID" = SP."ProductID" AND "CompanyID_id" = SP."CompanyID_id"    ORDER BY "PurchaseDetailsID" DESC LIMIT 1 ) AS LastPurchasePrice, 
(SELECT  "Qty"  FROM public."purchaseDetailses_purchaseDetails"  WHERE "BranchID" = '1'  
AND "ProductID" = SP."ProductID" AND "CompanyID_id" = SP."CompanyID_id"  ORDER BY "PurchaseDetailsID" DESC LIMIT 1 ) as LastPurchaseQty  
  
  
From public."stockPosting_stockPosting" AS SP  
INNER JOIN public."products_product" AS P ON P."ProductID" = SP."ProductID"   AND P."CompanyID_id" = SP."CompanyID_id" 
INNER JOIN public."pricelist_pricelist" AS PL ON PL."PriceListID" = SP."PriceListID"   AND PL."CompanyID_id" = SP."CompanyID_id"
INNER JOIN public."purchaseMasters_purchaseMaster" AS PM ON PM."PurchaseMasterID" = SP."VoucherMasterID"  AND PM."CompanyID_id" = SP."CompanyID_id"
INNER JOIN public."accountLedger_accountLedger" AS AL ON PM."LedgerID" = AL."LedgerID"  AND AL."CompanyID_id" = SP."CompanyID_id" 
  
  
WHERE AL."AccountGroupUnder" = '29'  AND SP."BranchID" = '1'  AND SP."ProductID" = '1'  
AND SP."Date" BETWEEN '2022-01-01' AND '2022-02-21'  AND SP."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'