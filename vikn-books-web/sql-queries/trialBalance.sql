SELECT * FROM               
(              
SELECT               
l."LedgerID"  ,    
--aL.LedgerName    
aG."AccountGroupName"   
,(SELECT "LedgerName" FROM public."accountLedger_accountLedger"  WHERE     
"LedgerID" = L."LedgerID" AND "BranchID" = 1 AND "CompanyID_id" = 'e4039a97-876c-4261-af47-c4855e69f5c7') AS LedgerName     

--,ROUND(NULLIF(SUM(Debit),0) - NULLIF(SUM(Credit),0),2) AS Total              
,NULLIF(SUM("Debit"),0) - NULLIF(SUM("Credit"),0) AS Total              
FROM public."ledgerPostings_ledgerPosting" AS L     
iNNER jOIN public."accountLedger_accountLedger" AS AL ON l."LedgerID" =aL."LedgerID" AND al."CompanyID_id" = l."CompanyID_id"
iNNER jOIN public.accountgroup_accountgroup AS AG on ag."AccountGroupID" =aL."AccountGroupUnder"   
AND ag."CompanyID_id" = aL."CompanyID_id"
WHERE l."BranchID" = 1 AND l."CompanyID_id" = 'e4039a97-876c-4261-af47-c4855e69f5c7' AND "Date" < '2022-02-15'            
Group BY l."LedgerID","LedgerName"    
,aG."AccountGroupName"   

) AS Temp              
WHERE Total != 0 



select * from public."accountLedger_accountLedger" WHERE "LedgerName" = 'VAT on Purchase(Outside State)' AND "CompanyID_id" = 'e4039a97-876c-4261-af47-c4855e69f5c7'

select * from public."ledgerPostings_ledgerPosting" WHERE "LedgerID" = '56' AND "CompanyID_id" = 'e4039a97-876c-4261-af47-c4855e69f5c7' AND "Date" < '2022-02-15'    








SELECT * FROM               
   (              
    SELECT               
      l."LedgerID"  ,    
   --aL.LedgerName    
   aG."AccountGroupName"    
     ,(SELECT "LedgerName" FROM public."accountLedger_accountLedger"  WHERE     
  "LedgerID" = L."LedgerID" AND "BranchID" = '1' ) AS LedgerName     
    
     ,NULLIF(SUM("Debit"),0) - NULLIF(SUM("Credit"),0) AS Total              
    FROM public."ledgerPostings_ledgerPosting" AS L     
 iNNER jOIN  public."accountLedger_accountLedger" AS AL ON l."LedgerID" =aL."LedgerID"    
 iNNER jOIN public.accountgroup_accountgroup AS AG on ag."AccountGroupID" =aL."AccountGroupUnder"    
     
 WHERE l."BranchID" = '1' AND "Date" < '2022-02-15'          
    Group BY l."LedgerID"     ,"LedgerName"    
   ,aG."AccountGroupName"    
     
    ) AS Temp              
    WHERE Total != 0 Order by "AccountGroupName"            
              
              
    SELECT NULLIF(SUM("Debit"),0) - NULLIF(SUM("Credit"),0) AS OpeningDifference               
 from public."ledgerPostings_ledgerPosting" WHERE "CompanyID_id" = 'e4039a97-876c-4261-af47-c4855e69f5c7' AND "VoucherType" = 'LOB' AND "BranchID" = '1' AND "Date" < '2022-02-15'




  SELECT            
 (SELECT ( (ROUND(NULLIF(SUM(AvgValue),0),2)) ) AS OpeningStockValue FROM                
  (                
  SELECT "ProductID","QtyIn","QtyOut","Stock","AvgRate",("Stock" * "AvgRate") AS AvgValue FROM                 
   (SELECT "ProductID","QtyIn","QtyOut",("QtyIn" - "QtyOut") AS Stock,                
   CASE               
   WHEN  QtyInTotal <> 0 AND QtyInRate>0 THEN  ((QtyInRate) / QtyInTotal)                
   WHEN  QtyInRate = 0 THEN  (SELECT "PurchasePrice" FROM public."pricelist_pricelist" AS PL WHERE  PL."ProductID" = temp."ProductID" AND PL."DefaultUnit" = 'true')                
   ELSE 0                
   END AS AvgRate                
  from                 
   (Select S."ProductID", SUM("QtyIn") AS "QtyIn",SUM("QtyOut") AS QtyOut          
   ,(SELECT SUM("QtyIn") from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS','ES') AND S."ProductID" = "ProductID" and "QtyIn" > 0 AND "Date" < '2022-02-15') AS QtyInTotal          
 ,(SELECT SUM("QtyIn" * "Rate") from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS','ES') AND S."ProductID" = "ProductID" and "QtyIn" > 0 AND "Date" < '2022-02-15') AS QtyInRate               
   from public."stockPosting_stockPosting" AS S inner join public."products_product" AS P ON S."ProductID" = P."ProductID" WHERE S."Date" < '2022-02-15' AND P."InventoryType" = 'StockItem'             
   AND S."BranchID" = '1' Group By S."ProductID" ) as temp                
   where "ProductID" = "ProductID" ) AS temp1                
  )                
  AS Temp2 )               
  +            
(          
SELECT  NULLIF(SUM("stock"),0) FROM (        
SELECT  NULLIF(SUM("QtyIn" * "Rate"),0) - NULLIF(SUM("QtyOut" * "Rate"),0) as stock        
from public."stockPosting_stockPosting" AS S inner join public."products_product" AS P ON S."ProductID" = P."ProductID" WHERE S."Date"  BETWEEN '2021-02-15' AND  '2022-02-15' AND S."VoucherType"='OS'            
   AND P."InventoryType" = 'StockItem' AND S."BranchID" = '1' Group By S."ProductID") temp         
   )        
   AS OpeningStockValue ;

-- Opening Stock Deff
select 'Opening Stock' AS VoucherType,'' AS VoucherNo,'' AS Date,'' AS ProductName,'' AS WarehouseName,'' AS UnitName,'' AS Username, NULLIF(round(SUM("QtyIn"),2)-round(SUM("QtyOut"),2),0) AS OPBalance,'' AS QtyIn,'' AS QtyOut,'' FROM public."stockPosting_stockPosting" where  "Date" < '2022-02-18' AND "CompanyID_id" = 'e4039a97-876c-4261-af47-c4855e69f5c7'
-- Opening Balane OpeningDifference
SELECT NULLIF(SUM("Debit"),0) - NULLIF(SUM("Credit"),0) AS OpeningDifference               
            from public."ledgerPostings_ledgerPosting" WHERE "CompanyID_id" = '8debe3dc-c708-4527-bba9-cb5fad7a2b6a' AND "VoucherType" = 'LOB' AND "BranchID" = '1' AND "Date" < '2022-03-03'


-- Opening Stock Value
SELECT            
 (SELECT ( (ROUND(NULLIF(SUM(AvgValue),0),2))) AS OpeningStockValue FROM                
  (                
  SELECT "ProductID","QtyIn",QtyOut,Stock,AvgRate,(Stock * AvgRate) AS AvgValue FROM                 
   (SELECT "ProductID","QtyIn",QtyOut,("QtyIn" - QtyOut) AS Stock,                
   CASE               
   WHEN  QtyInTotal <> 0 AND QtyInRate>0 THEN  ((QtyInRate) / QtyInTotal)                
   WHEN  QtyInRate = 0 THEN  (SELECT "PurchasePrice" FROM public."pricelist_pricelist" AS PL WHERE  PL."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' AND PL."ProductID" = temp."ProductID" AND PL."DefaultUnit" = 'true')                
   ELSE 0                
   END AS AvgRate                
  from                 
   (Select S."ProductID", SUM("QtyIn") AS "QtyIn",SUM("QtyOut") AS QtyOut          
   ,(SELECT SUM("QtyIn") from public."stockPosting_stockPosting" where "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' AND "VoucherType" in('PI', 'OS','ES') AND S."ProductID" = "ProductID" and "QtyIn" > 0 AND "Date" < '2022-03-03') AS QtyInTotal          
 ,(SELECT SUM("QtyIn" * "Rate") from public."stockPosting_stockPosting" where "CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' AND "VoucherType" in('PI', 'OS','ES') AND S."ProductID" = "ProductID" and "QtyIn" > 0 AND "Date" < '2022-03-03') AS QtyInRate               
   from public."stockPosting_stockPosting" AS S inner join public."products_product" AS P ON S."ProductID" = P."ProductID" AND S."CompanyID_id" = P."CompanyID_id" WHERE P."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97' AND S."Date" < '2022-03-03' AND P."InventoryType" = 'StockItem'             
   AND S."BranchID" = '1' Group By S."ProductID" ) as temp                
   where "ProductID" = "ProductID" ) AS temp1                
  )                
  AS Temp2 )                     
   AS OpeningStockValue;


-- TRAILBALANCE
        SELECT * FROM               
        (              
        SELECT              
        aG."AccountGroupName"   
        ,(SELECT "LedgerName" FROM public."accountLedger_accountLedger"  WHERE     
        "LedgerID" = L."LedgerID" AND "BranchID" = 1 AND "CompanyID_id" = '8debe3dc-c708-4527-bba9-cb5fad7a2b6a') AS LedgerName     

        --,ROUND(ISNULL(SUM(Debit),0) - ISNULL(SUM(Credit),0),2) AS Total              
        ,NULLIF(SUM("Debit" - "Credit"),0) AS Total              
        FROM public."ledgerPostings_ledgerPosting" AS L     
        iNNER jOIN public."accountLedger_accountLedger" AS AL ON l."LedgerID" =aL."LedgerID" AND al."CompanyID_id" = l."CompanyID_id"
        iNNER jOIN public.accountgroup_accountgroup AS AG on ag."AccountGroupID" =aL."AccountGroupUnder"   
        AND ag."CompanyID_id" = aL."CompanyID_id"
        WHERE l."BranchID" = 1 AND l."CompanyID_id" = '8debe3dc-c708-4527-bba9-cb5fad7a2b6a' AND "Date" < '2022-03-03'            
        Group BY l."LedgerID","LedgerName"    
        ,aG."AccountGroupName"   
          

        ) AS Temp              
        WHERE Total != 0 

<<<<<<< HEAD
<<<<<<< HEAD
-- =================================

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
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2022-06-01' AND '2022-06-05' )
            AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup42) AND AL."BranchID" = '1'
            AND AL."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a'
            ) AS TEMP WHERE Total != 0;


Latest============
# Income/Expence
WITH RECURSIVE GroupInMainGroup42 AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID" in (42,43,70,71) AND "CompanyID_id" = 'fde91453-0151-4500-9a84-877aef89283a'
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup42 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'fde91453-0151-4500-9a84-877aef89283a'
            )  
            SELECT *  
            FROM(  
            SELECT "AccountGroupName","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2022-07-01' AND '2022-07-28' )
            AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup42) AND AL."BranchID" = '1'
            AND AL."CompanyID_id" = 'fde91453-0151-4500-9a84-877aef89283a'
            ) AS TEMP WHERE Total != 0;


# Asset/Liability

        WITH RECURSIVE GroupInMainGroup AS (
        SELECT
        "AccountGroupID",
        "AccountGroupUnder",
        "AccountGroupName"
        FROM public.accountgroup_accountgroup
        WHERE
        "AccountGroupID" in (3,4) AND "CompanyID_id" = 'cafb2501-ae79-46a0-a81f-ad22298c31b3'
        UNION
        SELECT
        e."AccountGroupID",
        e."AccountGroupUnder",
        e."AccountGroupName"
        FROM
        public.accountgroup_accountgroup e
        INNER JOIN GroupInMainGroup s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'cafb2501-ae79-46a0-a81f-ad22298c31b3'
        )  
        SELECT *  
        FROM(  
        SELECT "AccountGroupName","LedgerName" ,  
        (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" <= '2022-10-28' )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Total FROM public."accountLedger_accountLedger" AL  
        INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
        WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = '1'
        AND AL."CompanyID_id" = 'cafb2501-ae79-46a0-a81f-ad22298c31b3'
        ) AS TEMP WHERE Total != 0;

-- ==================CURENT=====
         WITH RECURSIVE GroupInMainGroup AS (
        SELECT
        "AccountGroupID",
        "AccountGroupUnder",
        "AccountGroupName"
        FROM public.accountgroup_accountgroup
        WHERE
        "AccountGroupID" in (3,4) AND "CompanyID_id" = 'cafb2501-ae79-46a0-a81f-ad22298c31b3'
        UNION
        SELECT
        e."AccountGroupID",
        e."AccountGroupUnder",
        e."AccountGroupName"
        FROM
        public.accountgroup_accountgroup e
        INNER JOIN GroupInMainGroup s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = 'cafb2501-ae79-46a0-a81f-ad22298c31b3'
        )  
        SELECT *  
        FROM(  
        SELECT "AccountGroupName","LedgerName" ,  

        (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" < '2021-05-28' )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Opening,

  (SELECT ROUND(coalesce(SUM("Debit"), 0),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" between '2021-05-28' and '2022-10-28' )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Debit,

(SELECT ROUND(coalesce(SUM("Credit"), 0),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" between '2021-05-28' and '2022-10-28' )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Credit,

  (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" <= '2022-10-28' )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Closing,

(SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN '2021-05-28' AND '2022-10-28' )
            AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total

FROM public."accountLedger_accountLedger" AL  
        INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
        WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = '1'
        AND AL."CompanyID_id" = 'cafb2501-ae79-46a0-a81f-ad22298c31b3'
) AS TEMP WHERE (Credit + Debit + Closing + Opening) != 0;