


-- Stock Value Report
   SELECT * from (
            SELECT "ProductCode","AutoBarcode","ProductName",

            "PurchasePrice","SalesPrice",    
                
            CAST((SELECT coalesce(SUM(SP."QtyIn" - SP."QtyOut"), 0) FROM public."stockPosting_stockPosting" AS SP       
            WHERE SP."CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND SP."ProductID" = P."ProductID" AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND "Date" <= '2022-07-21') AS decimal(24, 2)) Stock,       
            --- AVG ----       
            
            (SELECT CASE WHEN AvgRate !=0 THEN((AvgRate) / QtyIn) 

            WHEN AvgRate = 0 THEN (SELECT "PurchasePrice" FROM public.pricelist_pricelist AS PL WHERE PL."ProductID" = P."ProductID" AND PL."DefaultUnit" = 'true' AND "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8') 

            
            ELSE AvgRate END AS AvgRates FROM(SELECT coalesce(SUM("Rate"* "QtyIn"),0) AS AvgRate,       
            coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND "VoucherType" in('PI', 'OS', 'ES') AND "ProductID" =       
            P."ProductID" AND "BranchID" = '1' AND "QtyIn" <> 0 AND "Date" <= '2022-07-21' ) AS Temp)       
            AS Cost       
                
            FROM public.products_product AS P       
            INNER JOIN public.pricelist_pricelist PL ON P."ProductID" = PL."ProductID" 
            AND P."BranchID" = PL."BranchID" AND PL."DefaultUnit" = 'true'   AND P."CompanyID_id" =PL."CompanyID_id"    
            WHERE P."CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND P."BranchID" = '1'
        ) as t where Stock != 0 and Stock is not null



            WHEN AvgRate = 0 THEN (SELECT "PurchasePrice" FROM public.pricelist_pricelist AS PL WHERE PL."ProductID" = P."ProductID" AND PL."DefaultUnit" = 'true' AND "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8') 










  SELECT * from (
        SELECT "ProductCode","AutoBarcode","ProductName"
        


        ,round("PurchasePrice",2),round("SalesPrice",2),    
            
        CAST((SELECT NULLIF(SUM(SP."QtyIn" - SP."QtyOut"), 0) FROM public."stockPosting_stockPosting" AS SP       
        WHERE SP."CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND 

        SP."ProductID" = P."ProductID" 
   
             
        AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND "Date" <= '2022-07-21') AS decimal(24, 2)) Stock,       
        -------Unit-------
        (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID" AND PL."DefaultUnit" = 'true'  ) AS BaseUnitName,

        (SELECT coalesce(round("MultiFactor", '0'),2) FROM public."pricelist_pricelist" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."ProductID" = PL."ProductID" AND UN."UnitInReports" = 'true')AS StockInBaseUnit,
        

        (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN INNER JOIN public.pricelist_pricelist as AA ON  AA."BranchID" = '1' AND 
      
        AA."ProductID" = P."ProductID" AND AA."UnitInReports" = 'true' 
        AND UN."UnitID" = AA."UnitID" AND
        AA."CompanyID_id" = P."CompanyID_id" WHERE UN."CompanyID_id" = P."CompanyID_id")
        AS UnitName,
        -----END----

        --- AVG ----        
        # round((SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn)
        
        # WHEN AvgRate = 0 THEN (SELECT "PurchasePrice" FROM public.pricelist_pricelist AS PL WHERE PL."ProductID" = P."ProductID" AND PL."DefaultUnit" = 'true' AND "CompanyID_id" = PL."CompanyID_id") 

        
        -- ELSE 0 END AS AvgRates FROM(SELECT NULLIF(SUM("Rate"* "QtyIn"),0) AS AvgRate,       
        -- NULLIF(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND "VoucherType" in('PI', 'OS', 'ES') AND "ProductID" =       
        -- P."ProductID" AND "BranchID" = '1' AND "QtyIn" > 0 AND "Date" <= '2022-07-21' ) AS Temp),2)       
        -- AS Cost    

        (SELECT CASE WHEN AvgRate <>0 THEN((AvgRate) / QtyIn) 

            WHEN AvgRate = 0 THEN (SELECT "PurchasePrice" FROM public.pricelist_pricelist AS PL WHERE PL."ProductID" = P."ProductID" AND PL."DefaultUnit" = 'true' AND "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8') 

            
            ELSE AvgRate END AS AvgRates FROM(SELECT coalesce(SUM("Rate"* "QtyIn"),0) AS AvgRate,       
            coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND "VoucherType" in('PI', 'OS', 'ES') AND "ProductID" =       
            P."ProductID" AND "BranchID" = '1' AND "QtyIn" <> 0 AND "Date" <= '2022-07-21' ) AS Temp)       
            AS Cost       
            
        FROM public.products_product AS P       
        INNER JOIN public.pricelist_pricelist PL ON P."ProductID" = PL."ProductID" 
        AND P."BranchID" = PL."BranchID" AND PL."DefaultUnit" = 'true'   AND P."CompanyID_id" =PL."CompanyID_id"    
        WHERE P."CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND 
       
        P."BranchID" = '1'

    ) as t where Stock != 0 and Stock is not null






  SELECT * from (
<<<<<<< HEAD
<<<<<<< HEAD
        SELECT P."ProductID" ,"ProductCode","AutoBarcode","ProductName"
        


        ,    
            
        CAST((SELECT NULLIF(SUM(SP."QtyIn" - SP."QtyOut"), 0) FROM public."stockPosting_stockPosting" AS SP       
        WHERE SP."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a' AND 
=======
=======
>>>>>>> 173051c28510918b68824c2406e6c47c892d38c3
        SELECT "ProductCode","AutoBarcode","ProductName"
        


        ,round("PurchasePrice",2),round("SalesPrice",2),    
            
        CAST((SELECT NULLIF(SUM(SP."QtyIn" - SP."QtyOut"), 0) FROM public."stockPosting_stockPosting" AS SP       
        WHERE SP."CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND 
<<<<<<< HEAD
>>>>>>> 6e26aaa66a6f98a87584afbdc2b35ba0aa103ae0
=======
>>>>>>> 173051c28510918b68824c2406e6c47c892d38c3

        SP."ProductID" = P."ProductID" 
   
             
        AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND "Date" <= '2022-07-21') AS decimal(24, 2)) Stock,       
<<<<<<< HEAD
<<<<<<< HEAD
        -------Unit-------        


        -----END----

        --- AVG ----        
       

            (SELECT CASE WHEN AvgRate <>0 THEN((AvgRate) / QtyIn) WHEN AvgRate = 0 THEN (SELECT 
            
            "PurchasePrice" FROM public.pricelist_pricelist AS PL WHERE PL."ProductID" = P."ProductID" AND PL."DefaultUnit" = 'true' AND "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8') 

            
            ELSE 0 END AS AvgRates FROM(SELECT coalesce(SUM("Rate"* "QtyIn"),0) AS AvgRate,       
            coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a' AND "VoucherType" in('PI', 'OS', 'ES') AND "ProductID" =       
            P."ProductID" AND "BranchID" = '1' AND "QtyIn" <> 0 AND "Date" <= '2022-07-21' ) AS Temp)   
            AS Cost          
=======
=======
>>>>>>> 173051c28510918b68824c2406e6c47c892d38c3
        -------Unit-------
        (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID" AND PL."DefaultUnit" = 'true'  ) AS BaseUnitName,

        (SELECT coalesce(round("MultiFactor", '0'),2) FROM public."pricelist_pricelist" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."ProductID" = PL."ProductID" AND UN."UnitInReports" = 'true')AS StockInBaseUnit,
        

        (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN INNER JOIN public.pricelist_pricelist as AA ON  AA."BranchID" = '1' AND 
      
        AA."ProductID" = P."ProductID" AND AA."UnitInReports" = 'true' 
        AND UN."UnitID" = AA."UnitID" AND
        AA."CompanyID_id" = P."CompanyID_id" WHERE UN."CompanyID_id" = P."CompanyID_id")
        AS UnitName,
        -----END----

        --- AVG ----        
        # round((SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn)
        
        # WHEN AvgRate = 0 THEN (SELECT "PurchasePrice" FROM public.pricelist_pricelist AS PL WHERE PL."ProductID" = P."ProductID" AND PL."DefaultUnit" = 'true' AND "CompanyID_id" = PL."CompanyID_id") 

        (SELECT CASE WHEN AvgRate <>0 THEN((AvgRate) / QtyIn) 

            WHEN AvgRate = 0 THEN (SELECT "PurchasePrice" FROM public.pricelist_pricelist AS PL WHERE PL."ProductID" = P."ProductID" AND PL."DefaultUnit" = 'true' AND "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8') 

            
            ELSE AvgRate END AS AvgRates FROM(SELECT coalesce(SUM("Rate"* "QtyIn"),0) AS AvgRate,       
            coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND "VoucherType" in('PI', 'OS', 'ES') AND "ProductID" =       
            P."ProductID" AND "BranchID" = '1' AND "QtyIn" <> 0 AND "Date" <= '2022-07-21' ) AS Temp)       
            AS Cost       
<<<<<<< HEAD
>>>>>>> 6e26aaa66a6f98a87584afbdc2b35ba0aa103ae0
=======
>>>>>>> 173051c28510918b68824c2406e6c47c892d38c3
            
        FROM public.products_product AS P       
        INNER JOIN public.pricelist_pricelist PL ON P."ProductID" = PL."ProductID" 
        AND P."BranchID" = PL."BranchID" AND PL."DefaultUnit" = 'true'   AND P."CompanyID_id" =PL."CompanyID_id"    
<<<<<<< HEAD
<<<<<<< HEAD
        WHERE P."CompanyID_id" = 'cbba36e8-8cb9-4570-9161-2aecf7cf8e8a' AND 
=======
        WHERE P."CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND 
>>>>>>> 6e26aaa66a6f98a87584afbdc2b35ba0aa103ae0
=======
        WHERE P."CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND 
>>>>>>> 173051c28510918b68824c2406e6c47c892d38c3
       
        P."BranchID" = '1'

    ) as t where Stock != 0 and Stock is not null