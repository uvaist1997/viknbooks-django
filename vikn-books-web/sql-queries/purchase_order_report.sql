Select           
P."VoucherNo" AS VoucherNo,      
P."Date",      
AL."LedgerName" AS LedgerName,   
(SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE  
  "LedgerID" = P."LedgerID" AND "AccountGroupUnder" in ('10','29') AND "BranchID" = '1'
   AND "CompanyID_id" = P."CompanyID_id") AS SupplierName,   
P."NetTotal" AS NetAmount,      
P."TotalTax" AS TotalTax,        
P."GrandTotal" AS GrandTotal,
case 
when P."IsInvoiced" = 'N'then 'Pending'
when  P."IsInvoiced" = 'I' then 'Invoiced'
when P."IsInvoiced" = 'C' then 'Cancelled'
end AS Status           
FROM public."purchaseOrderMasters_purchaseOrderMaster" AS P       
INNER JOIN public."accountLedger_accountLedger" AS AL ON P."LedgerID" = AL."LedgerID"
AND AL."CompanyID_id" = P."CompanyID_id"      
WHERE P."BranchID" = '1' AND P."IsActive" = 'true' AND "IsInvoiced" in ('N') AND P."Date" BETWEEN '2022-01-01' AND '2022-02-23' 
AND P."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'     
ORDER BY "PurchaseOrderMasterID"       
      
