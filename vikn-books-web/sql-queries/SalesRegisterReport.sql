BranchList = ('1','2')

if WarehouseID == 0 and UserID = 0 AND LedgerID = 0:
    if ProductID > 0:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", 
        SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id" ) AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND Sd."ProductID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif ProductGroupID > 0:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id"  ) AS Temp) AS AVGRate
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID"  AND P."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID"  AND PL."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND P."ProductGroupID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif ProductCategoryID > 0:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date"  AND "CompanyID_id" = S."CompanyID_id") AS Temp) AS AVGRate 
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND PG."CategoryID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif ProductCode:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", 
        SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id" ) AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND P."ProductCode" = 'PC1000' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif Barcode:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date"  AND "CompanyID_id" = S."CompanyID_id") AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND PL."Barcode" = '4568' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'
    
    else:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date"  AND "CompanyID_id" = S."CompanyID_id") AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'




elif WarehouseID > 0 and UserID = 0 AND LedgerID = 0:
    if ProductID > 0:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", 
        SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id" ) AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND Sd."ProductID" = '1' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif ProductGroupID > 0:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id"  ) AS Temp) AS AVGRate
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID"  AND P."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID"  AND PL."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND P."ProductGroupID" = '1' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif ProductCategoryID > 0:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date"  AND "CompanyID_id" = S."CompanyID_id") AS Temp) AS AVGRate 
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND PG."CategoryID" = '1' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif ProductCode:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", 
        SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id" ) AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND P."ProductCode" = 'PC1000' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif Barcode:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date"  AND "CompanyID_id" = S."CompanyID_id") AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND PL."Barcode" = '4568' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'
    
    else:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date"  AND "CompanyID_id" = S."CompanyID_id") AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

elif WarehouseID > 0 and UserID > 0 AND LedgerID = 0:
    if ProductID > 0:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", 
        SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id" ) AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND Sd."ProductID" = '1' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif ProductGroupID > 0:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id"  ) AS Temp) AS AVGRate
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID"  AND P."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID"  AND PL."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND P."ProductGroupID" = '1' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif ProductCategoryID > 0:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date"  AND "CompanyID_id" = S."CompanyID_id") AS Temp) AS AVGRate 
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND PG."CategoryID" = '1' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif ProductCode:
        SELECT 
        "Date", "VoucherNo",P."ProductCode", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", 
        SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id" ) AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND P."ProductCode" = 'PC1000' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif Barcode:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date"  AND "CompanyID_id" = S."CompanyID_id") AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND PL."Barcode" = '4568' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'
    
    else:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date"  AND "CompanyID_id" = S."CompanyID_id") AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id" 
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND S."WarehouseID" = '1' AND
        S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'


elif WarehouseID > 0 AND UserID > 0 AND LedgerID > 0:
    if ProductID > 0:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id" ) AS Temp) AS AVGRate

        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND SD."ProductID" = '1' AND S."WarehouseID" = '1' 
        AND S."CreatedUserID" = '114' AND S."LedgerID" = '1166' AND S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'
    
    elif ProductGroupID > 0:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" ) AS Temp) AS AVGRate
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND p."ProductGroupID" = '1' 
        AND S."WarehouseID" = '1' AND S."CreatedUserID" = '114' AND S."LedgerID" = '1166'  AND S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif ProductCategoryID > 0:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" ) AS Temp) AS AVGRate 
        
        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID"  AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id"
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND PG."CategoryID" = '1' AND S."WarehouseID" = '1' AND S."CreatedUserID" = '114'
         AND S."LedgerID" = '1166' AND S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'
    
    elif ProductCode:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id" ) AS Temp) AS AVGRate

        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND P."ProductCode" = 'PC1000' AND S."WarehouseID" = '1' 
        AND S."CreatedUserID" = '114' AND S."LedgerID" = '1166' AND S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'

    elif Barcode:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id" ) AS Temp) AS AVGRate

        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND PL."Barcode" = '4568' AND S."WarehouseID" = '1' 
        AND S."CreatedUserID" = '114' AND S."LedgerID" = '1166' AND S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'
    else:
        SELECT 
        "Date", "VoucherNo", P."ProductName", PL."Barcode", SD."Qty",
        SD."UnitPrice", SD."GrossAmount", SD."VATAmount", SD."NetAmount", SD."CostPerPrice", 
        (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn) ELSE 0 END AS AvgRate FROM(SELECT coalesce(SUM("Rate"* "QtyIn"), 
        0) AS AvgRate, coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "VoucherType" in('PI', 'OS', 'ES') 
        AND "ProductID" = SD."ProductID" AND "BranchID" in ('1','2') AND "QtyIn" > 0 AND "Date" <= S."Date" AND "CompanyID_id" = S."CompanyID_id" ) AS Temp) AS AVGRate

        FROM public."salesMasters_salesMaster" AS S 
        INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
        INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
        WHERE S."Date" BETWEEN '2022-02-20' AND '2022-02-23' AND S."WarehouseID" = '1' 
        AND S."CreatedUserID" = '114' AND S."LedgerID" = '1166' AND S."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'
    















        