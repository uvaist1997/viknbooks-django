
     

SELECT  ROW_NUMBER() Over(Order by CAST("LedgerPostingID" AS int)) AS SlNo    
,"VoucherMasterID"    
,"VoucherType"    
,CASE WHEN "VoucherType" ='SI' THEN (SELECT "VoucherNo" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID" = A."VoucherMasterID" AND "CompanyID_id" = A."CompanyID_id")       
 WHEN "VoucherType" ='SR' THEN (SELECT "VoucherNo" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = A."CompanyID_id")      
WHEN "VoucherType" ='PI' THEN (SELECT "VoucherNo" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = A."CompanyID_id")      
WHEN "VoucherType" ='PR' THEN (SELECT "VoucherNo" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = A."CompanyID_id")      
WHEN "VoucherType" ='CR' THEN (SELECT "VoucherNo" FROM public."receiptMasters_receiptMaster" WHERE "BranchID" = '1' AND "ReceiptMasterID" = A."VoucherMasterID" AND "CompanyID_id" = A."CompanyID_id")      
WHEN "VoucherType" ='CP' THEN (SELECT "VoucherNo" FROM public."paymentMasters_paymentMaster" WHERE "BranchID" = '1' AND "PaymentMasterID" = A."VoucherMasterID" AND "CompanyID_id" = A."CompanyID_id")      
WHEN "VoucherType" ='LOB' THEN (SELECT "VoucherNo" FROM public."accountLedger_accountLedger" WHERE "BranchID" = '1' AND "LedgerID" = "VoucherMasterID" AND "CompanyID_id" = A."CompanyID_id")      
WHEN "VoucherType" ='OS' THEN (SELECT "VoucherNo" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = A."CompanyID_id")      
END AS VoucherNo  
,CASE WHEN "VoucherType" ='SI' THEN 'Sales Invoice'      
WHEN "VoucherType" ='SR' THEN 'Sales Return'      
WHEN "VoucherType" ='PI' THEN 'Purchase Invoice'      
WHEN "VoucherType" ='PR' THEN 'Purchase Return'      
WHEN "VoucherType" ='CR' THEN 'Cash Receipt'      
WHEN "VoucherType" ='CP' THEN 'Cash Payment'      
WHEN "VoucherType" ='LOB' THEN 'Ledger Opening Balance'      
WHEN "VoucherType" ='OS' THEN 'Opening Stock'      
END AS Particulars     
, "Date"    
,A."LedgerID"    
,B."LedgerName" ,       
"Debit",      
"Credit"     
       
FROM public."ledgerPostings_ledgerPosting" AS A      
       
INNER JOIN public."accountLedger_accountLedger" AS B ON A."LedgerID"=B."LedgerID" AND A."CompanyID_id"=B."CompanyID_id"      
       
WHERE A."BranchID"='1' AND "Date"='2022-01-14' AND a."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'  ORDER BY "Date"  

