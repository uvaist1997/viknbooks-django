-- ASSET&LIABILITY
WITH RECURSIVE GroupInMainGroup AS (
        SELECT
        "AccountGroupID",
        "AccountGroupUnder",
        "AccountGroupName"
        FROM public.accountgroup_accountgroup
        WHERE
        "AccountGroupID" in (3,4) AND "CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
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
        SELECT "AccountGroupName","LedgerName" ,  
        (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" < '2022-07-10' )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Opening,
  (SELECT ROUND(coalesce(SUM("Debit"), 0),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" between '2022-07-10' and '2022-07-28' )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Debit,
(SELECT ROUND(coalesce(SUM("Credit"), 0),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" between '2022-07-10' and '2022-07-28' )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Credit,
  (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" <= '2022-07-28' )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Closing
FROM public."accountLedger_accountLedger" AL  
        INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
        WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = '1'
        AND AL."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
) AS TEMP WHERE (Credit + Debit + Closing + Opening) != 0;




-- Income/Expence
WITH RECURSIVE GroupInMainGroup42 AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID" in (42,43,70,71) AND "CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup42 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            )  
            SELECT *  
            FROM(  
            SELECT "AccountGroupName","LedgerName" ,  
            
            (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
                    FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" < '2022-07-10' )
                    AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
                    AS Opening,
            (SELECT ROUND(coalesce(SUM("Debit"), 0),2) 
                    FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" between '2022-07-10' and '2022-07-28' )
                    AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
                    AS Debit,
            (SELECT ROUND(coalesce(SUM("Credit"), 0),2) 
                    FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" between '2022-07-10' and '2022-07-28' )
                    AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
                    AS Credit,
            (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
                    FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" <= '2022-07-28' )
                    AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
                    AS Closing
             FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup42) AND AL."BranchID" = '1'
            AND AL."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
) AS TEMP WHERE (Credit + Debit + Closing + Opening) != 0;


