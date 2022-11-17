--------------AVARAGE--------------
-- ==Opening===
select AverageValueOfAllProductBeforeDate('2022-03-01','2022-01-01','ded7822a-1355-40c1-aa0d-2335153d4d08',1)
-- ===Closing===
<<<<<<< HEAD
<<<<<<< HEAD
select AverageValueOfAllProduct('2022-03-01','cbba36e8-8cb9-4570-9161-2aecf7cf8e8a',1)
=======
select AverageValueOfAllProduct('2022-03-01','ded7822a-1355-40c1-aa0d-2335153d4d08',1)
>>>>>>> 6e26aaa66a6f98a87584afbdc2b35ba0aa103ae0
=======
select AverageValueOfAllProduct('2022-03-01','ded7822a-1355-40c1-aa0d-2335153d4d08',1)
>>>>>>> 173051c28510918b68824c2406e6c47c892d38c3
--------------FIFO--------------
-- ==Opening===
SELECT SUM(FIFOValueOfAProductBeforeDate('2022-01-01',P."ProductID",'ded7822a-1355-40c1-aa0d-2335153d4d08')) FROM public.products_product AS P 
WHERE "CompanyID_id"='ded7822a-1355-40c1-aa0d-2335153d4d08' AND "InventoryType" = 'StockItem'
-- ===Closing===
SELECT SUM(FIFOValueOfAProduct('2022-03-01',P."ProductID",'ded7822a-1355-40c1-aa0d-2335153d4d08')) FROM public.products_product AS P 
WHERE "CompanyID_id"='ded7822a-1355-40c1-aa0d-2335153d4d08' AND "InventoryType" = 'StockItem'
--------------LIFO--------------
-- ==Opening===
SELECT SUM(LIFOValueOfAProductBeforeDate('2022-01-01',P."ProductID",'ded7822a-1355-40c1-aa0d-2335153d4d08')) FROM public.products_product AS P 
WHERE "CompanyID_id"='ded7822a-1355-40c1-aa0d-2335153d4d08' AND "InventoryType" = 'StockItem'
-- ===Closing===
SELECT SUM(LIFOValueOfAProduct('2022-03-01',P."ProductID",'ded7822a-1355-40c1-aa0d-2335153d4d08')) FROM public.products_product AS P 
WHERE "CompanyID_id"='ded7822a-1355-40c1-aa0d-2335153d4d08' AND "InventoryType" = 'StockItem'


-- Consolidated
--DIRECT EXPENSES
WITH RECURSIVE GroupInMainGroup42 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 42 AND "CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup42 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
)  
SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
FROM(  
SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
(SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2022-01-01' AND '2022-03-09' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup42) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";

--INDIRECT EXPENSE
-- =====CHECKING===========
WITH RECURSIVE GroupInMainGroup43 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 43 AND "CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup43 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
)       
SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
FROM(  
SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
(SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2022-08-01' AND '2022-09-22' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup43) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";

--DIRECT INCOME
WITH RECURSIVE GroupInMainGroup70 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 70 AND "CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup70 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
)       
SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
FROM(  
SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
(SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2021-02-01' AND '2022-01-01' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup70) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";
--INDIRECT INCOME  
WITH RECURSIVE GroupInMainGroup71 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 71 AND "CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup71 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
)       
SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
FROM(  
SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
(SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2022-08-01' AND '2022-09-22' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup71) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";

-- =============================================================CONSOLIDATE END===========================

--OPENING STOCK Average
SELECT       
(SELECT ( (ROUND(coalesce(SUM(AvgValue),0),@2)) ) AS OpeningStockValue FROM       
(       
SELECT "ProductID",QtyIn,QtyOut,Stock,AvgRate,(Stock * AvgRate) AS AvgValue FROM       
(SELECT "ProductID",QtyIn,QtyOut,(QtyIn - QtyOut) AS Stock,       
CASE       
WHEN QtyInTotal != 0 AND QtyInRate != 0 THEN (       
(QtyInRate) / QtyInTotal)       
WHEN QtyInRate = 0 THEN (SELECT "PurchasePrice" FROM public.pricelist_pricelist PL WHERE PL."ProductID" = temp."ProductID" AND PL."DefaultUnit" = 'true' AND "CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08')       
ELSE 0       
END AS AvgRate       
from       
(Select S."ProductID", SUM("QtyIn") AS QtyIn,SUM("QtyOut") AS QtyOut       
,(SELECT coalesce(SUM("QtyIn"),0) from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS','ES') AND S."ProductID" = "ProductID" 
  and "QtyIn" != 0 AND "Date" < '2022-01-01' AND "CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08') AS QtyInTotal
,(SELECT coalesce(SUM("QtyIn" * "Rate"),0) from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS','ES') AND S."ProductID" = "ProductID" and "QtyIn" != 0 AND "Date" < '2022-03-01'
 AND "CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08') AS QtyInRate  
from public."stockPosting_stockPosting" AS S inner join public.products_product P ON S."CompanyID_id"=P."CompanyID_id" AND S."ProductID" = P."ProductID" WHERE S."Date" < '2022-03-01' AND P."InventoryType" = 'StockItem'       
AND S."BranchID" = 1 AND S."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08' Group By S."ProductID" ) as temp       
where "ProductID" = "ProductID" ) AS temp1) AS Temp2 ) + (       
SELECT coalesce(SUM(stock),0) FROM (       
SELECT coalesce(SUM("QtyIn" * "Rate"),0) - coalesce(SUM("QtyOut" * "Rate"),0) as stock       
from public."stockPosting_stockPosting" AS S inner join public.products_product P ON S."ProductID" = P."ProductID" AND S."CompanyID_id"=P."CompanyID_id"
        WHERE S."Date" BETWEEN '2022-01-01' AND '2022-03-01' AND S."VoucherType"='OS' AND S."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'    
AND P."InventoryType" = 'StockItem' AND S."BranchID" = 1 Group By S."ProductID") temp       
)
AS OpeningStockValue

-- ===================DETAILED START ============
--DIRECT EXPENSES
WITH RECURSIVE GroupInMainGroup42 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 42 AND "CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup42 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
)  
SELECT *  
FROM(  
SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
(SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2022-01-01' AND '2022-03-09' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup42) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
) AS TEMP WHERE Total != 0;

--INDIRECT EXPENSE
-- ============ CHECking===============
WITH RECURSIVE GroupInMainGroup43 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 43 AND "CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup43 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
)       
SELECT *
FROM(  
SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
(SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2022-08-01' AND '2022-09-22' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup43) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
) AS TEMP WHERE Total != 0;


--DIRECT INCOME  
WITH RECURSIVE GroupInMainGroup70 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 70 AND "CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup70 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
)       
SELECT *
FROM(  
SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
(SELECT (coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0))) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2021-08-01' AND '2022-09-22' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup70) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
) AS TEMP WHERE Total != 0;

--INDIRECT INCOME  
WITH RECURSIVE GroupInMainGroup71 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 71 AND "CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup71 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
)       
SELECT *
FROM(  
SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
(SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2022-08-01' AND '2022-09-22' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup71) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = 'ded7822a-1355-40c1-aa0d-2335153d4d08'
) AS TEMP WHERE Total != 0;
