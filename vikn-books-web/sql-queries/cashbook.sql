SELECT          
        L."VoucherMasterID" AS ID        
    ,CASE WHEN "VoucherType" ='SI' THEN (SELECT "VoucherNo" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")         
    WHEN "VoucherType" ='SR' THEN (SELECT "VoucherNo" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PI' THEN (SELECT "VoucherNo" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PR' THEN (SELECT "VoucherNo" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='CR' THEN (SELECT "VoucherNo" FROM public."receiptMasters_receiptMaster" WHERE "BranchID" = '1' AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType"='CR' AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='BR' THEN (SELECT "VoucherNo" FROM public."receiptMasters_receiptMaster" WHERE "BranchID" = '1' AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType"='BR' AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='CP' THEN (SELECT "VoucherNo" FROM public."paymentMasters_paymentMaster" WHERE "BranchID" = '1' AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType"='CP' AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='BP' THEN (SELECT "VoucherNo" FROM public."paymentMasters_paymentMaster" WHERE "BranchID" = '1' AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType"='BP' AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='LOB' THEN (SELECT "VoucherNo" FROM public."accountLedger_accountLedger" WHERE "BranchID" = '1' AND "LedgerID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='OS' THEN (SELECT "VoucherNo" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")          
    WHEN "VoucherType" ='JE' THEN (SELECT "VoucherNo" FROM public."journalMaster_journalMaster" WHERE "BranchID" = '1' AND "JournalMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
    WHEN "VoucherType" ='EX' THEN (SELECT "VoucherNo" FROM public."expenseMasters_expenseMaster" WHERE "BranchID" = '1' AND "ExpenseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")  
    ELSE ''  
    END AS "Voucher No",        


    CASE WHEN "VoucherType" ='SI' THEN (SELECT "Notes" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")         
    WHEN "VoucherType" ='SR' THEN (SELECT "Notes" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PI' THEN (SELECT "Notes" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PR' THEN (SELECT "Notes" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='EX' THEN (SELECT "Notes" FROM public."expenseMasters_expenseMaster" WHERE "BranchID" = '1' AND "ExpenseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")  
    WHEN "VoucherType" ='CR' THEN            

    (SELECT "Narration" FROM public."receiptDetailses_receiptDetails" AS A        
    INNER JOIN public."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType"='CR'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")        

    WHEN "VoucherType" ='BR' THEN         

    (SELECT "Narration" FROM public."receiptDetailses_receiptDetails" AS A        
    INNER JOIN public."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"          
    WHERE B."BranchID" = '1' AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType"='BR'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")           

    WHEN "VoucherType" ='CP' THEN         

    (SELECT "Narration" FROM public."paymentDetails_paymentDetail" AS A        
    INNER JOIN public."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType"='CP'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")        

    WHEN "VoucherType" ='BP' THEN         

    (SELECT "Narration" FROM public."paymentDetails_paymentDetail" AS A        
    INNER JOIN public."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON B."LedgerID" = B."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND  A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType"='BP'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = C."CompanyID_id")         


    WHEN "VoucherType" ='LOB' THEN (SELECT "Notes" FROM public."accountLedger_accountLedger" WHERE "BranchID" = '1' AND "LedgerID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='OS' THEN (SELECT "Notes" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")          

    WHEN "VoucherType" ='JL' THEN         

    (SELECT "Narration" FROM public."journalDetails_journalDetail" AS A        
    INNER JOIN public."journalMaster_journalMaster" AS B ON A."JournalMasterID" = B."JournalMasterID" AND A."CompanyID_id" = B."CompanyID_id"        
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID"  AND A."CompanyID_id" = C."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."JournalDetailsID" = "VoucherDetailID"         
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = C."CompanyID_id"   )        

    END AS "Narration"      

    ,L."Date" AS Date    
    ,CASE WHEN "VoucherType" ='SI' THEN 'Sales Invoice'        
    WHEN "VoucherType" ='SR' THEN 'Sales Return'        
    WHEN "VoucherType" ='PI' THEN 'Purchase Invoice'        
    WHEN "VoucherType" ='PR' THEN 'Purchase Return'        
    WHEN "VoucherType" ='CR' THEN 'Cash Receipt'        
    WHEN "VoucherType" ='BR' THEN 'Bank Receipt'        
    WHEN "VoucherType" ='CP' THEN 'Cash Payment'        
    WHEN "VoucherType" ='BP' THEN 'Bank Payment'        
    WHEN "VoucherType" ='LOB' THEN 'Ledger Opening Balance'        
    WHEN "VoucherType" ='OS' THEN 'Opening Stock'        
    WHEN "VoucherType" ='JE' THEN 'Journal Entry'    
    WHEN "VoucherType" ='EX' THEN 'Expense'   
    END AS Particulars        
    ,LL."LedgerName"         
    ,L."Debit"        
    ,L."Credit"      
    ,L."VoucherType"        
    FROM public."ledgerPostings_ledgerPosting" L        
    INNER JOIN public."accountLedger_accountLedger" AS LL ON L."LedgerID" = LL."LedgerID" AND L."CompanyID_id" = LL."CompanyID_id"        
    WHERE L."LedgerID" IN ('1')  AND L."Date" between '2022-01-01' AND '2022-02-16' AND L."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'        
    order by "Date" 

    -- GroupWise
    SELECT          
        
    CASE WHEN "VoucherType" ='SI' THEN (SELECT "VoucherNo" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")         
    WHEN "VoucherType" ='SR' THEN (SELECT "VoucherNo" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PI' THEN (SELECT "VoucherNo" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PR' THEN (SELECT "VoucherNo" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='CR' THEN (SELECT "VoucherNo" FROM public."receiptMasters_receiptMaster" WHERE "BranchID" = '1' AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType"='CR' AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='BR' THEN (SELECT "VoucherNo" FROM public."receiptMasters_receiptMaster" WHERE "BranchID" = '1' AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType"='BR' AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='CP' THEN (SELECT "VoucherNo" FROM public."paymentMasters_paymentMaster" WHERE "BranchID" = '1' AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType"='CP' AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='BP' THEN (SELECT "VoucherNo" FROM public."paymentMasters_paymentMaster" WHERE "BranchID" = '1' AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType"='BP' AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='LOB' THEN (SELECT "VoucherNo" FROM public."accountLedger_accountLedger" WHERE "BranchID" = '1' AND "LedgerID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='OS' THEN (SELECT "VoucherNo" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")          
    WHEN "VoucherType" ='JE' THEN (SELECT "VoucherNo" FROM public."journalMaster_journalMaster" WHERE "BranchID" = '1' AND "JournalMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
    WHEN "VoucherType" ='EX' THEN (SELECT "VoucherNo" FROM public."expenseMasters_expenseMaster" WHERE "BranchID" = '1' AND "ExpenseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")  
    ELSE ''  
    END AS "Voucher No",        


        CASE WHEN "VoucherType" ='SI' THEN (SELECT "Notes" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")         
    WHEN "VoucherType" ='SR' THEN (SELECT "Notes" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PI' THEN (SELECT "Notes" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PR' THEN (SELECT "Notes" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='EX' THEN (SELECT "Notes" FROM public."expenseMasters_expenseMaster" WHERE "BranchID" = '1' AND "ExpenseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")  
    WHEN "VoucherType" ='CR' THEN            

    (SELECT "Narration" FROM public."receiptDetailses_receiptDetails" AS A        
    INNER JOIN public."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType"='CR'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")        

    WHEN "VoucherType" ='BR' THEN         

    (SELECT "Narration" FROM public."receiptDetailses_receiptDetails" AS A        
    INNER JOIN public."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"          
    WHERE B."BranchID" = '1' AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType"='BR'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")           

    WHEN "VoucherType" ='CP' THEN         

    (SELECT "Narration" FROM public."paymentDetails_paymentDetail" AS A        
    INNER JOIN public."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType"='CP'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")        

    WHEN "VoucherType" ='BP' THEN         

    (SELECT "Narration" FROM public."paymentDetails_paymentDetail" AS A        
    INNER JOIN public."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON B."LedgerID" = B."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND  A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType"='BP'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = C."CompanyID_id")         


    WHEN "VoucherType" ='LOB' THEN (SELECT "Notes" FROM public."accountLedger_accountLedger" WHERE "BranchID" = '1' AND "LedgerID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='OS' THEN (SELECT "Notes" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")          

    WHEN "VoucherType" ='JL' THEN         

    (SELECT "Narration" FROM public."journalDetails_journalDetail" AS A        
    INNER JOIN public."journalMaster_journalMaster" AS B ON A."JournalMasterID" = B."JournalMasterID" AND A."CompanyID_id" = B."CompanyID_id"        
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID"  AND A."CompanyID_id" = C."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."JournalDetailsID" = "VoucherDetailID"         
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = C."CompanyID_id"   )        

    END AS "Narration"        

    ,L."Date" AS Date    
    ,CASE WHEN "VoucherType" ='SI' THEN 'Sales Invoice'        
    WHEN "VoucherType" ='SR' THEN 'Sales Return'        
    WHEN "VoucherType" ='PI' THEN 'Purchase Invoice'        
    WHEN "VoucherType" ='PR' THEN 'Purchase Return'        
    WHEN "VoucherType" ='CR' THEN 'Cash Receipt'        
    WHEN "VoucherType" ='BR' THEN 'Bank Receipt'        
    WHEN "VoucherType" ='CP' THEN 'Cash Payment'        
    WHEN "VoucherType" ='BP' THEN 'Bank Payment'        
    WHEN "VoucherType" ='LOB' THEN 'Ledger Opening Balance'        
    WHEN "VoucherType" ='OS' THEN 'Opening Stock'        
    WHEN "VoucherType" ='JE' THEN 'Journal Entry'    
    WHEN "VoucherType" ='EX' THEN 'Expense'   
    END AS Particulars        
    ,LL."LedgerName"      
    ,(SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "BranchID" = '1' AND "LedgerID" = L."LedgerID" AND "CompanyID_id" = L."CompanyID_id") AS Demo

    ,L."Debit"        
    ,L."Credit"      
    ,L."VoucherType"        
    FROM public."ledgerPostings_ledgerPosting" AS L        
    INNER JOIN public."accountLedger_accountLedger" AS LL ON L."LedgerID" = LL."LedgerID" AND L."CompanyID_id" = LL."CompanyID_id"        
    WHERE L."LedgerID" IN (SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = 'e4039a97-876c-4261-af47-c4855e69f5c7' AND "AccountGroupUnder" = '9' )  AND L."Date" between '2022-01-01' AND '2022-02-21' AND L."CompanyID_id" = 'e4039a97-876c-4261-af47-c4855e69f5c7'        
    order by "Date" 

-- Opening Balance(All)
SELECT '','','Opening Balance','','','','', COALESCE(SUM("Debit" - "Credit"),0) AS Balance   
FROM "public"."ledgerPostings_ledgerPosting"  
WHERE "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' AND "LedgerID" IN (SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9') AND "Date" < '2022-02-21'

-- Opening Balance(GroupWise)
SELECT '','','Opening Balance','','','','', COALESCE(SUM("Debit" - "Credit"),0) AS Balance   
FROM "public"."ledgerPostings_ledgerPosting"  
WHERE "LedgerID" IN (SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9' ) AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' AND "Date" < '2022-02-21'

-- Opening Balance(LedgerWIse)
SELECT '','','Opening Balance','','','','', COALESCE(SUM("Debit" - "Credit"),0) AS Balance   
FROM "public"."ledgerPostings_ledgerPosting"  
WHERE "LedgerID" IN ('1','107') AND"CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' AND "Date" < '2022-02-21'

-- Indexing Receipt
CREATE INDEX index_ReceiptMaster_Search
ON "receiptMasters_receiptMaster" ("ReceiptMasterID","VoucherType", "BranchID","CompanyID_id")

CREATE INDEX index_ReceiptDetail_Search
ON "receiptDetailses_receiptDetails" ("ReceiptDetailID","LedgerID", "CompanyID_id")
-- Indexing Payment
CREATE INDEX index_PaymentMaster_Search
ON "paymentMasters_paymentMaster" ("PaymentMasterID","VoucherType", "BranchID","CompanyID_id")

CREATE INDEX index_PaymentDetail_Search
ON "paymentDetails_paymentDetail" ("PaymentDetailsID","LedgerID", "CompanyID_id")


