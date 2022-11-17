
-- Consolidated
=======================================Latest========================
Liability
WITH RECURSIVE GroupInMainGroup AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= 4 AND "CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            )  
            SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" <= '2022-08-16' )
            AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = '1'
            AND AL."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            ) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";

		====Assets====
			WITH RECURSIVE GroupInMainGroup AS (
		SELECT
		"AccountGroupID",
		"AccountGroupUnder",
		"AccountGroupName"
		FROM public.accountgroup_accountgroup
		WHERE
		"AccountGroupID"= 3 AND "CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
		UNION
		SELECT
		e."AccountGroupID",
		e."AccountGroupUnder",
		e."AccountGroupName"
		FROM
		public.accountgroup_accountgroup e
		INNER JOIN GroupInMainGroup s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
		)  
		SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
		FROM(  
		SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
		(SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
		FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" <= '2022-08-16' )
		AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
		AS Total FROM public."accountLedger_accountLedger" AL  
		INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
		WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = '1'
		AND AL."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
		) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";

		-- Detailed
		-- ======================================Assets
		WITH RECURSIVE GroupInMainGroup AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= '3' AND "CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            )  
            SELECT *  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" <= '2022-08-16' )
            AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = '1'
            AND AL."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            ) AS TEMP WHERE Total != 0;

-- =============================Liability

 WITH RECURSIVE GroupInMainGroup AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= '4' AND "CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            )  
            SELECT *  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" <= '2022-08-16' )
            AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = '1'
            AND AL."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            ) AS TEMP WHERE Total != 0;