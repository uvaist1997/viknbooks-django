-- SELECT * from (
--             SELECT   
--             P."StockReOrder" AS StockReOrder,
--             P."StockMaximum" AS StockMaximum,
--             P."StockMinimum" AS StockMinimum,
--             P."ProductCode",
--             PL."AutoBarcode" AS Barcode,
--             P."ProductName",
        
--           (SELECT NULLIF(SUM(SP."QtyIn") - SUM(SP."QtyOut"),0)
--             FROM public."stockPosting_stockPosting" AS SP WHERE SP."CompanyID_id" = P."CompanyID_id" AND SP."ProductID" = P."ProductID" AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND SP."Date" <= '2022-03-16')
--             AS CurrentStock,  

--             (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID" AND PL."UnitInReports" = 'true'  )
--             AS UnitName,
--             PG."GroupName",
--             (SELECT NULLIF("CategoryName", '') FROM public."productcategory_productcategory" AS C WHERE C."CompanyID_id" = P."CompanyID_id" AND C."ProductCategoryID" = PG."CategoryID" )
--             AS CategoryName,
--             (SELECT NULLIF("BrandName", '') FROM public."brands_brand" AS B WHERE B."CompanyID_id" = P."CompanyID_id" AND B."BrandID" = P."BrandID" )
--             AS BrandName,


--             (SELECT coalesce("MultiFactor", '0') FROM public."pricelist_pricelist" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."ProductID" = PL."ProductID" AND UN."DefaultUnit" = 'true')AS StockInBaseUnit,
            
--             PL."PurchasePrice",
--             PL."SalesPrice"
        
--             FROM public.products_product as P  
--             INNER JOIN public.pricelist_pricelist as PL ON P."ProductID" = PL."ProductID" AND P."BranchID" = '1' AND
--             PL."DefaultUnit" = 'true' AND P."CompanyID_id" = PL."CompanyID_id"
--             INNER JOIN  public.productgroup_productgroup as PG on PG."ProductGroupID" = P."ProductGroupID" AND P."CompanyID_id" = PG."CompanyID_id"

  
--             WHERE P."CompanyID_id" = '4f684660-13b2-4823-bc13-d2edea17dbb7' AND
--             P."ProductGroupID" IN(SELECT "ProductGroupID" FROM public."productgroup_productgroup" WHERE "CategoryID" = '2' and 
--                                                                  "CompanyID_id" = '4f684660-13b2-4823-bc13-d2edea17dbb7') AND P."ProductID" = PL."ProductID"

         
--             ) as t where 
            
--             CurrentStock != 0 and CurrentStock is not null



SELECT "ProductCode",
AutoBarcode,
Barcode,
"ProductName",(MultiFactorInReports * CurrentStock) as CurrentStock,UnitName,"GroupName",CategoryName,BrandName,"PurchasePrice","SalesPrice",CurrentStock as StockInBaseUnit  from (
            SELECT   
            P."StockReOrder" AS StockReOrder,
            P."StockMaximum" AS StockMaximum,
            P."StockMinimum" AS StockMinimum,
            P."ProductCode",
            PL."AutoBarcode" AS AutoBarcode,
            PL."Barcode" AS Barcode,
            P."ProductName",
        
          (SELECT NULLIF(SUM(SP."QtyIn") - SUM(SP."QtyOut"),0)
            FROM public."stockPosting_stockPosting" AS SP WHERE SP."CompanyID_id" = P."CompanyID_id" AND SP."ProductID" = P."ProductID" AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND SP."Date" <= '2022-09-22')
            AS CurrentStock,  

            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID" AND PL."UnitInReports" = 'true'  )
            AS UnitName,
            PG."GroupName",
            (SELECT NULLIF("CategoryName", '') FROM public."productcategory_productcategory" AS C WHERE C."CompanyID_id" = P."CompanyID_id" AND C."ProductCategoryID" = PG."CategoryID" )
            AS CategoryName,
            (SELECT NULLIF("BrandName", '') FROM public."brands_brand" AS B WHERE B."CompanyID_id" = P."CompanyID_id" AND B."BrandID" = P."BrandID" )
            AS BrandName,
            
            PL."PurchasePrice",
            PL."SalesPrice",
            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID" AND PL."DefaultUnit" = 'true'  ) AS BaseUnit,
         (SELECT NULLIF("MultiFactor", 0) FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID" AND PL."UnitInReports" = 'true'  ) as MultiFactorInReports
            FROM public.products_product as P  
            INNER JOIN public.pricelist_pricelist as PL ON P."ProductID" = PL."ProductID" AND P."BranchID" = '1' AND
            PL."DefaultUnit" = 'true' AND P."CompanyID_id" = PL."CompanyID_id"
            INNER JOIN  public.productgroup_productgroup as PG on PG."ProductGroupID" = P."ProductGroupID" AND P."CompanyID_id" = PG."CompanyID_id"

  
            WHERE P."CompanyID_id" = '4f684660-13b2-4823-bc13-d2edea17dbb7' AND
             P."ProductID" = PL."ProductID"

         
            ) as t where 
            
            CurrentStock != 0 and CurrentStock is not null


-- P."ProductGroupID" IN(SELECT "ProductGroupID" FROM public."productgroup_productgroup" WHERE "CategoryID" = '2' and 
--                                                                  "CompanyID_id" = '4f684660-13b2-4823-bc13-d2edea17dbb7') AND