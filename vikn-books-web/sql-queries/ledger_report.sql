select "Credit" from public."ledgerPostings_ledgerPosting" where "VoucherNo" = 'CP-0139' AND"LedgerID"='92'  and "CompanyID_id" = 'cc8a95b9-0e63-479e-8475-f3bc4663718f' 
-- LedgerWIse
SELECT   
            CASE 
            WHEN "VoucherType" = 'SI' THEN(SELECT "VoucherNo" FROM public."salesMasters_salesMaster" WHERE "BranchID" = L."BranchID" AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'SR' THEN(SELECT "VoucherNo" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = L."BranchID" AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'PI' THEN(SELECT "VoucherNo" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = L."BranchID" AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'PR' THEN(SELECT "VoucherNo" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = L."BranchID" AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'CR' THEN(SELECT "VoucherNo" FROM "public"."receiptMasters_receiptMaster" WHERE "BranchID" = L."BranchID" AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType" = 'CR' AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'BR' THEN(SELECT "VoucherNo" FROM "public"."receiptMasters_receiptMaster" WHERE "BranchID" = L."BranchID" AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType" = 'BR' AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'CP' THEN(SELECT "VoucherNo" FROM "public"."paymentMasters_paymentMaster" WHERE "BranchID" = L."BranchID" AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType" = 'CP' AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'BP' THEN(SELECT "VoucherNo" FROM "public"."paymentMasters_paymentMaster" WHERE "BranchID" = L."BranchID" AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType" = 'BP' AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'LOB' THEN cast( L."LedgerID" as varchar(50))
            WHEN "VoucherType" = 'OS' THEN(SELECT "VoucherNo" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = L."BranchID" AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'JL' THEN(SELECT "VoucherNo" FROM "public"."journalMaster_journalMaster" WHERE "BranchID" = L."BranchID" AND "JournalMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'EX' THEN(SELECT "VoucherNo" FROM "public"."expenseMasters_expenseMaster" WHERE "BranchID" = L."BranchID" AND "ExpenseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id") END AS VoucherNo,   

            CASE WHEN "VoucherType" = 'SI' THEN(SELECT "Notes" FROM public."salesMasters_salesMaster" WHERE "BranchID" = L."BranchID" AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'SR' THEN(SELECT "Notes" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = L."BranchID" AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'PI' THEN(SELECT "Notes" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = L."BranchID" AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'PR' THEN(SELECT "Notes" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = L."BranchID" AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")

            WHEN "VoucherType" = 'CR' THEN (SELECT "Narration" FROM "public"."receiptDetailses_receiptDetails" AS A   
            INNER JOIN "public"."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND B."CompanyID_id" = A."CompanyID_id"  
            WHERE B."BranchID" = L."BranchID" AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType" = 'CR'    
            AND A."LedgerID" = L."LedgerID" AND B."CompanyID_id" = L."CompanyID_id")   

            WHEN "VoucherType" = 'BR' THEN (SELECT "Narration" FROM "public"."receiptDetailses_receiptDetails" AS A 
                                            INNER JOIN "public"."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND A."CompanyID_id" = B."CompanyID_id"
                                            WHERE B."BranchID" = L."BranchID" AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType" = 'BR'   
            AND A."LedgerID" = L."LedgerID"  AND A."CompanyID_id" = L."CompanyID_id")   

            WHEN "VoucherType" = 'CP' THEN (SELECT "Narration" FROM "public"."paymentDetails_paymentDetail" AS A 
                                            INNER JOIN "public"."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID" AND B."CompanyID_id" = A."CompanyID_id"   
            WHERE B."BranchID" = L."BranchID" AND A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType" = 'CP'   
            AND A."LedgerID" = L."LedgerID" AND A."CompanyID_id" = L."CompanyID_id")   

            WHEN "VoucherType" = 'BP' THEN (SELECT "Narration" FROM "public"."paymentDetails_paymentDetail" AS A INNER JOIN "public"."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID"
            WHERE B."BranchID" = L."BranchID" AND A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType" = 'BP' AND B."CompanyID_id" = A."CompanyID_id" 
            AND A."LedgerID" = L."LedgerID" AND A."CompanyID_id" = L."CompanyID_id")   

            WHEN "VoucherType" = 'LOB' THEN(SELECT "Notes" FROM public."accountLedger_accountLedger" WHERE "BranchID" = L."BranchID" AND "LedgerID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'OS' THEN(SELECT "Notes" FROM "public"."openingStockMasters_openingStockMaster" WHERE "BranchID" = L."BranchID" AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'JL' THEN   
            (SELECT "Narration" FROM "public"."journalDetails_journalDetail" AS A 
            INNER JOIN "public"."journalMaster_journalMaster" AS B ON A."JournalMasterID" = B."JournalMasterID" AND B."CompanyID_id" = A."CompanyID_id"
            WHERE B."BranchID" = L."BranchID" AND A."JournalDetailsID" = "VoucherDetailID"   
            AND A."LedgerID" = L."LedgerID" AND A."CompanyID_id" =L."CompanyID_id")   

            WHEN "VoucherType" = 'EX' THEN   
            (SELECT "Notes" FROM "public"."expenseDetails_expenseDetail" AS A 
            INNER JOIN "public"."expenseMasters_expenseMaster" AS B ON A."ExpenseMasterID" = B."ExpenseMasterID" AND B."CompanyID_id" = A."CompanyID_id"    
            WHERE B."BranchID" = L."BranchID" AND A."ExpenseDetailsID" = "VoucherDetailID" AND B."CompanyID_id" = L."CompanyID_id" 
            AND A."Ledger_id" = LL.id )   
            END AS Narration,   
            L."Date" AS VoucherDate   
            , CASE WHEN "VoucherType" = 'SI' THEN 'Sales Invoice'   
            WHEN "VoucherType" = 'SR' THEN 'Sales Return'   
            WHEN "VoucherType" = 'PI' THEN 'Purchase Invoice'   
            WHEN "VoucherType" = 'PR' THEN 'Purchase Return'   
            WHEN "VoucherType" = 'CR' THEN 'Cash Receipt'   
            WHEN "VoucherType" = 'BR' THEN 'Bank Receipt'   
            WHEN "VoucherType" = 'CP' THEN 'Cash Payment'   
            WHEN "VoucherType" = 'BP' THEN 'Bank Payment'   
            WHEN "VoucherType" = 'LOB' THEN 'Ledger Opening Balance'   
            WHEN "VoucherType" = 'OS' THEN 'Opening Stock'   
            WHEN "VoucherType" = 'EX' THEN 'Expense'   
            WHEN "VoucherType" = 'JL' THEN 'Journal Entry'   
            END AS Particulars,

            (SELECT COALESCE("LedgerName", '') FROM public."accountLedger_accountLedger" AS RL WHERE RL."CompanyID_id" = L."CompanyID_id" AND RL."LedgerID" = L."RelatedLedgerID")
            AS LedgerName

            ,L."VoucherType"   
            ,round(L."Debit",2)   
            ,round(L."Credit",2)   

            FROM "public"."ledgerPostings_ledgerPosting" AS L   
            INNER JOIN public."accountLedger_accountLedger" AS LL ON L."LedgerID" = LL."LedgerID" AND L."CompanyID_id" = LL."CompanyID_id" 
            WHERE L."CompanyID_id" = 'cc8a95b9-0e63-479e-8475-f3bc4663718f' AND L."VoucherNo" = 'CP-0139' AND L."LedgerID" = '92' AND L."Date" between '2021-01-01' AND '2022-10-04' AND L."BranchID" = '1'  
            order by "Date"

-- GROUP WISE
SELECT* FROM(   
SELECT   
A."LedgerName",   
round(NULLIF(SUM(L."Debit"), 0),2 ) as Debit,   
round(NULLIF(SUM(L."Credit"), 0),2) as Credit,   
round(NULLIF(SUM(L."Debit"), 0) - NULLIF(SUM(L."Credit"), 0),2) AS Balance   
FROM public."accountLedger_accountLedger" A   
INNER JOIN "public"."ledgerPostings_ledgerPosting" AS L ON L."LedgerID" = A."LedgerID" AND L."BranchID" = A."BranchID" AND L."Date" <= '2022-08-16'   
WHERE A."CompanyID_id" ='cbba36e8-8cb9-4570-9161-2aecf7cf8e8a' AND A."BranchID" = '1' AND A."AccountGroupUnder" = '10' GROUP BY L."LedgerID",A."LedgerName" ) AS TEMP WHERE Balance != 0 ORDER BY "LedgerName"   
==================
SELECT* FROM(   
            SELECT   
            A."LedgerName",   
            round(NULLIF(SUM(L."Debit"), 0),2 ) as Debit,   
            round(NULLIF(SUM(L."Credit"), 0),2) as Credit,   
            round(NULLIF(SUM(L."Debit"), 0) - NULLIF(SUM(L."Credit"), 0),2) AS Balance   
            FROM public."accountLedger_accountLedger" A   
            INNER JOIN "public"."ledgerPostings_ledgerPosting" AS L ON L."CompanyID_id" = A."CompanyID_id" AND L."LedgerID" = A."LedgerID" AND L."BranchID" = A."BranchID" AND L."Date" <= '2022-07-23'   
            WHERE A."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a' AND A."BranchID" = '1' AND A."AccountGroupUnder" = '10' GROUP BY L."LedgerID",A."LedgerName" ) AS TEMP WHERE Balance != 0 ORDER BY "LedgerName"   


            SELECT   
           A."LedgerName",  
            round(NULLIF(SUM(L."Debit"), 0),2 ) as Debit
            
            FROM public."accountLedger_accountLedger" A   
            INNER JOIN "public"."ledgerPostings_ledgerPosting" AS L ON L."CompanyID_id" = A."CompanyID_id" AND L."LedgerID" = A."LedgerID" AND L."BranchID" = A."BranchID" AND L."Date" <= '2022-07-23'   
            WHERE A."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a' AND A."BranchID" = '1' AND A."AccountGroupUnder" = '10' GROUP BY L."LedgerID",A."LedgerName" 


======= countineution=====
SELECT   
           A."LedgerName",  
            round(NULLIF(SUM(L."Debit"), 0),2 ) as Debit
            
            FROM public."accountLedger_accountLedger" A   
            INNER JOIN "public"."ledgerPostings_ledgerPosting" AS L ON L."CompanyID_id" = A."CompanyID_id" AND L."LedgerID" = A."LedgerID" AND L."BranchID" = A."BranchID" AND L."Date" <= '2022-07-23'   
            WHERE A."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a' AND A."BranchID" = '1' AND A."AccountGroupUnder" = '10' GROUP BY L."LedgerID",A."LedgerName" ORDER BY "LedgerName" 
===================
-- TESTING
SELECT SUM("Debit") FROM "public"."ledgerPostings_ledgerPosting" where "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' and "LedgerID" = '96'
SELECT * FROM "public"."ledgerPostings_ledgerPosting" where "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' and "LedgerID" = '4359' and "VoucherNo"='CP705' order by "Date"

SELECT * FROM "public"."ledgerPostings_ledgerPosting" where "VoucherType"='LOB' and "Date" is null
update "public"."ledgerPostings_ledgerPosting" set "Date" = "CreatedDate" where "VoucherType"='LOB' and "Date" is null



SELECT * FROM "public"."accountLedger_accountLedger" where "LedgerID"='1600' and "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
SELECT * FROM "public"."accountLedger_accountLedger" where "LedgerID"='4359' and "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'

SELECT * FROM "public"."ledgerPostings_ledgerPosting" where "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' and "VoucherNo"='CP705' order by "Date"





SELECT* FROM(   
SELECT   
A."LedgerName",   
round(NULLIF(SUM(L."Debit"), 0),2 ) as Debit,   
round(NULLIF(SUM(L."Credit"), 0),2) as Credit,   
round(NULLIF(SUM(L."Debit"), 0) - NULLIF(SUM(L."Credit"), 0),2) AS Balance   
FROM public."accountLedger_accountLedger" A   
LEFT OUTER JOIN "public"."ledgerPostings_ledgerPosting" AS L ON L."LedgerID" = A."LedgerID" AND L."BranchID" = A."BranchID" AND L."Date" <= '2022-08-16'   
WHERE A."CompanyID_id" ='cbba36e8-8cb9-4570-9161-2aecf7cf8e8a' AND A."BranchID" = '1' AND A."AccountGroupUnder" = '10' GROUP BY L."LedgerID",A."LedgerName" ) AS TEMP WHERE Balance != 0 ORDER BY "LedgerName"   




SELECT* FROM(   
SELECT   
A."LedgerName",   
round(NULLIF(SUM(L."Debit"), 0),2 ) as Debit,   
round(NULLIF(SUM(L."Credit"), 0),2) as Credit,   
round(NULLIF(SUM(L."Debit"), 0) - NULLIF(SUM(L."Credit"), 0),2) AS Balance   
FROM public."accountLedger_accountLedger" A   
INNER JOIN "public"."ledgerPostings_ledgerPosting" AS L ON L."CompanyID_id" = A."CompanyID_id" AND L."LedgerID" = A."LedgerID" AND L."BranchID" = A."BranchID" AND L."Date" <= '2022-08-16'   
WHERE A."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a' AND A."BranchID" = '1' AND A."AccountGroupUnder" = '10' AND A."LedgerID" = '1899' GROUP BY L."LedgerID",A."LedgerName" ) AS TEMP WHERE Balance != 0 ORDER BY "LedgerName"   



SELECT* FROM(   
SELECT   
A."LedgerName",   
round(COALESCE(SUM(L."Debit"), 0),2 ) as Debit,   
round(COALESCE(SUM(L."Credit"), 0),2) as Credit,   
round(COALESCE(SUM(L."Debit"), 0) - COALESCE(SUM(L."Credit"), 0),2) AS Balance   
FROM public."accountLedger_accountLedger" A   
INNER JOIN "public"."ledgerPostings_ledgerPosting" AS L ON L."CompanyID_id" = A."CompanyID_id" AND L."LedgerID" = A."LedgerID" AND L."BranchID" = A."BranchID" AND L."Date" <= '2022-08-16'   
WHERE A."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a' AND A."BranchID" = '1' AND A."AccountGroupUnder" = '10' AND L."LedgerID" = '1899' GROUP BY L."LedgerID",A."LedgerName" ) AS TEMP WHERE Balance != 0 ORDER BY "LedgerName"   


SELECT * FROM "public"."ledgerPostings_ledgerPosting" where "CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a' and "LedgerID" = '1899' 


-- ledgerwise latest
SELECT   
L."Date"   
L."VoucherNo"   
,L."VoucherType"   
,round(L."Debit",2)   
,round(L."Credit",2)   
,L."LedgerID"

FROM "public"."ledgerPostings_ledgerPosting" AS L   
INNER JOIN public."accountLedger_accountLedger" AS LL ON L."LedgerID" = LL."LedgerID" AND L."CompanyID_id" = LL."CompanyID_id" 
WHERE L."CompanyID_id" = 'cc8a95b9-0e63-479e-8475-f3bc4663718f'AND L."VoucherNo" = 'CP-0139' AND L."VoucherType" = 'BP' AND L."LedgerID" = '92' AND L."Date" between '2021-01-01' AND '2022-10-04' AND L."BranchID" = '1'  
order by "Date"
