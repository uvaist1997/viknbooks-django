
-- warehouse

   SELECT "OpeningStockMasterID","VoucherNo","Date",OS."WarehouseID",W."WarehouseName",
   OS."Notes","TotalQty","GrandTotal",OS."CreatedUserID",U."username"  
   FROM public."openingStockMasters_openingStockMaster" AS OS  
   INNER JOIN public."warehouse_warehouse" AS W ON W."WarehouseID" = OS."WarehouseID"  AND 
   W."CompanyID_id" = OS."CompanyID_id"
   INNER JOIN public."auth_user" AS U ON U."id" = OS."CreatedUserID"  
 WHERE OS."BranchID" = '1' AND "Date" BETWEEN '2022-01-01' AND '2022-02-23'  
 AND OS."WarehouseID" = '1' AND OS."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'    
  
  
--  all warehouse
  
   SELECT "OpeningStockMasterID","VoucherNo","Date",OS."WarehouseID",W."WarehouseName",
   OS."Notes","TotalQty","GrandTotal",OS."CreatedUserID",U."username"  
   FROM public."openingStockMasters_openingStockMaster" AS OS  
   INNER JOIN public."warehouse_warehouse" AS W ON W."WarehouseID" = OS."WarehouseID" AND 
   W."CompanyID_id" = OS."CompanyID_id" 
   INNER JOIN public."auth_user" AS U ON U."id" = OS."CreatedUserID"  
 WHERE OS."BranchID" = '1' AND "Date" BETWEEN '2022-01-01' AND '2022-02-23' 
 AND OS."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'   