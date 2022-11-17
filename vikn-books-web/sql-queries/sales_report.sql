SELECT *,round(GrandTotal-CashSales-BankSales,2) AS CreditSales FROM(
        SELECT     
        S."VoucherNo" AS VoucherNo,          
        S."Date",
        AL."LedgerName" AS LedgerName,          
        S."CustomerName" AS Name,                  
        CASE WHEN  
        S."EmployeeID" >0  THEN(SELECT NULLIF("LastName", '') FROM public.employees_employees WHERE "EmployeeID" = S."EmployeeID" AND "CompanyID_id" = S."CompanyID_id")      
        WHEN S."EmployeeID" =0 THEN ''
        END AS SalesMan,
        round(S."TotalGrossAmt",2) AS NetAmount,          
        round(S."TotalTax",2) AS TotalTax,          
        round(S."TotalDiscount",2) AS BillDiscount,
        round(S."GrandTotal",2) AS GrandTotal,          

            round(
        (Select COALESCE(SUM("Debit" - "Credit"),0) FROM public."ledgerPostings_ledgerPosting" where "VoucherType"='SI'      
                        AND "VoucherMasterID"=s."SalesMasterID" AND "BranchID" = S."BranchID"
                AND "CompanyID_id" = S."CompanyID_id"
                AND "LedgerID" IN       
                    (Select "LedgerID" FROM public."accountLedger_accountLedger" where "AccountGroupUnder"=9 AND "CompanyID_id" = S."CompanyID_id")),2) AS CashSales,
            
            round(
            (Select COALESCE(SUM("Debit" - "Credit"),0) FROM public."ledgerPostings_ledgerPosting" where "VoucherType"='SI'      
                        AND "VoucherMasterID"=s."SalesMasterID" AND "BranchID" = S."BranchID"
                AND "CompanyID_id" = S."CompanyID_id"
                AND "LedgerID" IN       
                    (Select "LedgerID" FROM public."accountLedger_accountLedger" where "AccountGroupUnder"=8 AND "CompanyID_id" = S."CompanyID_id")),2) AS BankSales,
        (select COALESCE (SUM("Debit"),0) from public."ledgerPostings_ledgerPosting" where "VoucherType"='SI'      
        AND "VoucherMasterID"=s."SalesMasterID"  
        AND "LedgerID" IN (Select "LedgerID" from public."accountLedger_accountLedger" where "AccountGroupUnder" IN (8,9))) AS Cash
                        
                FROM public."salesMasters_salesMaster" AS S LEFT OUTER JOIN public."accountLedger_accountLedger" AS AL ON S."LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = S."CompanyID_id"     
                WHERE S."BranchID" = '1' AND S."Status" != 'Cancelled' AND         
                S."Date" BETWEEN '2021-12-28' AND '2022-04-22' AND S."CompanyID_id" = '22aa64dd-7b7e-4b49-9bea-1c3fd55c5b32'         
                ORDER BY "SalesMasterID"
        ) as t 



-- indexing
CREATE INDEX index_Ledgerposting_Search
ON "ledgerPostings_ledgerPosting" ("LedgerID","VoucherMasterID", "BranchID","CompanyID_id","VoucherType")

DROP INDEX index_Search

CREATE INDEX index_ledger
ON "accountLedger_accountLedger" ("LedgerID", "BranchID","CompanyID_id");

CREATE INDEX index_ledger_withoutbranch
ON "accountLedger_accountLedger" ("LedgerID","CompanyID_id");

CREATE INDEX index_salesmasterfilter
ON "salesMasters_salesMaster" ("Date", "BranchID","Status","CompanyID_id");


-- SALESRETURN
(select COALESCE (SUM("Credit"),0) from public."ledgerPostings_ledgerPosting" where "CompanyID_id" = S."CompanyID_id" AND "VoucherType"='SR'      
AND "VoucherMasterID"=s."SalesReturnMasterID"  
AND "LedgerID" IN (Select "LedgerID" from public."accountLedger_accountLedger" where "CompanyID_id" = S."CompanyID_id" AND "AccountGroupUnder" IN (8,9))) AS Cash


-- SALES
(select COALESCE (SUM("Debit"),0) from public."ledgerPostings_ledgerPosting" where "CompanyID_id" = S."CompanyID_id" AND "VoucherType"='SI'      
AND "VoucherMasterID"=s."SalesMasterID"  
AND "LedgerID" IN (Select "LedgerID" from public."accountLedger_accountLedger" where "CompanyID_id" = S."CompanyID_id" AND "AccountGroupUnder" IN (8,9))) AS Cash
