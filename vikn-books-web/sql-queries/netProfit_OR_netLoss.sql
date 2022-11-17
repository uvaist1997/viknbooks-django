-- ===============DIRECTEXPENCES================
  WITH RECURSIVE GroupInMainGroup42 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 42 AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup42 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
)  
SELECT SUM(Total) as DIRECTEXPENCES 
FROM(  
SELECT   
(SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2021-02-01' AND '2022-01-01' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup42) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
) AS TEMP;
-- ===========================DIRECTINCOME=================================
   WITH RECURSIVE GroupInMainGroup70 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 70 AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup70 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
)  
SELECT SUM(Total) as DIRECTINCOME 
FROM(  
SELECT 
(SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2021-02-01' AND '2022-01-01' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup70) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
) AS TEMP ;
-- ===============INDIRECTEXPENCES================
  WITH RECURSIVE GroupInMainGroup43 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 43 AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup43 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
)  
SELECT SUM(Total) as INDIRECTEXPENCES 
FROM(  
SELECT 
(SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2021-02-01' AND '2022-01-01' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup43) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
) AS TEMP ;

-- ===========================INDIRECTINCOME=================================
   WITH RECURSIVE GroupInMainGroup71 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 71 AND "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup71 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
)  
SELECT SUM(Total) as INDIRECTINCOME 
FROM(  
SELECT 
(SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2021-02-01' AND '2022-01-01' )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup71) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'
) AS TEMP;

-- ===========================
create or replace FUNCTION Profit(ToDate Date,FromDate Date, BranchID bigint, CompanyID uuid,OPENINGSTOCK int,CLOSINGSTOCK int)
RETURNS numeric(24, 8)
language plpgsql
as
$$
DECLARE DIRECTEXPENCES numeric(24, 8) = 0;
 INDIRECTEXPENCES numeric(24, 8) = 0;
--  OPENINGSTOCK numeric(24, 8) = 0;
 DIRECTINCOME numeric(24, 8) = 0;
 INDIRECTINCOME numeric(24, 8) = 0;
--  CLOSINGSTOCK numeric(24, 8) = 0;
 GrossProfit numeric(24, 8) = 0;
 GrossLoss numeric(24, 8) = 0;
 NetProfit numeric(24, 8) = 0;
 NetLoss numeric(24, 8) = 0;  
 begin
 
   WITH RECURSIVE GroupInMainGroup42 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 42 AND "CompanyID_id" = CompanyID
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup42 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = CompanyID
)  
SELECT SUM(Total) into DIRECTEXPENCES 
FROM(  
SELECT   
(SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN FromDate AND ToDate )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup42) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = CompanyID
) AS TEMP ;


--   select AverageValueOfAllProductBeforeDate(FromDate,ToDate,CompanyID,1) into OPENINGSTOCK;
  

   WITH RECURSIVE GroupInMainGroup70 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 70 AND "CompanyID_id" = CompanyID
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup70 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = CompanyID
)  
SELECT SUM(Total) into DIRECTINCOME 
FROM(  
SELECT   
(SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN FromDate AND ToDate )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup70) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = CompanyID
) AS TEMP ;

  
--    SELECT AverageValueOfAllProduct(ToDate,CompanyID,1) into CLOSINGSTOCK;
   
    WITH RECURSIVE GroupInMainGroup43 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 43 AND "CompanyID_id" = CompanyID
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup43 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = CompanyID
)  
SELECT SUM(Total) into INDIRECTEXPENCES 
FROM(  
SELECT   
(SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN FromDate AND ToDate )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup43) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = CompanyID
) AS TEMP ;
  
  
  
  
  
 
   WITH RECURSIVE GroupInMainGroup71 AS (
	SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
	FROM public.accountgroup_accountgroup
	WHERE
		 "AccountGroupID"= 71 AND "CompanyID_id" = CompanyID
	UNION
		SELECT
			e."AccountGroupID",
			e."AccountGroupUnder",
			e."AccountGroupName"
		FROM
			public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup71 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = CompanyID
)  
SELECT SUM(Total) into INDIRECTINCOME 
FROM(  
SELECT   
(SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
 FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN FromDate AND ToDate )
 AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
AS Total FROM public."accountLedger_accountLedger" AL  
INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup71) AND AL."BranchID" = '1'
AND AL."CompanyID_id" = CompanyID
) AS TEMP ;

 SELECT DIRECTEXPENCES + OPENINGSTOCK into DIRECTEXPENCES; 
 SELECT DIRECTINCOME + CLOSINGSTOCK into DIRECTINCOME;
  
  
  
 IF(DIRECTEXPENCES > DIRECTINCOME)  
 THEN  
 SELECT DIRECTEXPENCES - DIRECTINCOME into GrossLoss;  
   SELECT GrossProfit + DIRECTINCOME into DIRECTINCOME;  
 elsif(DIRECTEXPENCES < DIRECTINCOME)  
 THEN  
 SELECT DIRECTINCOME - DIRECTEXPENCES into GrossProfit;
 SELECT GrossProfit + DIRECTEXPENCES into DIRECTEXPENCES;
 end if;
 
 SELECT GrossLoss + INDIRECTEXPENCES into INDIRECTEXPENCES;
 SELECT GrossProfit + INDIRECTINCOME into INDIRECTINCOME;
 IF(INDIRECTEXPENCES <= INDIRECTINCOME)  
 THEN  
 SELECT INDIRECTINCOME - INDIRECTEXPENCES into NetProfit;  
   RETURN NetProfit;
 SELECT NetProfit + INDIRECTINCOME into INDIRECTINCOME;
   
 elsif(INDIRECTEXPENCES > INDIRECTINCOME)  
 THEN  
 SELECT INDIRECTEXPENCES - INDIRECTINCOME into NetLoss;
 RETURN NetLoss * -1;
 SELECT NetLoss + INDIRECTEXPENCES into INDIRECTEXPENCES;
 
end if;


 END $$;