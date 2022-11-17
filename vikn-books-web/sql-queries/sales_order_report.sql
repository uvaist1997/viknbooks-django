   
Select           
S."VoucherNo" AS VoucherNo,      
S."Date",
AL."LedgerName" AS LedgerName,      
(SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE  
  "LedgerID" = S."LedgerID" AND "AccountGroupUnder" in ('10','29') AND "BranchID" = '1'
   AND "CompanyID_id" = S."CompanyID_id") AS CustomerName,     
S."NetTotal" AS NetAmount,      
S."TotalTax" AS TotalTax,      
S."GrandTotal" AS GrandTotal,
case 
when S."IsInvoiced" = 'N'then 'Pending'
when  S."IsInvoiced" = 'I' then 'Invoiced'
when S."IsInvoiced" = 'C' then 'Cancelled'
end AS Status     
FROM public."salesOrderMasters_salesOrderMaster" AS S      
INNER JOIN public."accountLedger_accountLedger" AS AL ON S."LedgerID" = AL."LedgerID"  
AND AL."CompanyID_id" = S."CompanyID_id"     
WHERE S."BranchID" = '1' AND S."IsActive" = 'true' AND "IsInvoiced" in ('I') AND S."Date" BETWEEN '2022-01-01' AND '2022-02-23'
AND S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'      
ORDER BY "SalesOrderMasterID"      
      
                                         