--  IF(@UserID > 0 AND @WarehouseFromID > 0 AND @WarehouseToID > 0)  
    SELECT 
    "VoucherNo"  
    ,"Date"  
    ,UC."username" AS User
    ,WF."WarehouseName" AS WarehouseFrom  
    , WT."WarehouseName" AS WarehouseTo
    , "TotalQty"  
    , "GrandTotal"  
    ,"MaxGrandTotal"  
    FROM public."stockTransferMaster_ID_stockTransferMaster_ID" AS S  
    INNER JOIN public."warehouse_warehouse" WT ON WT."BranchID" = S."BranchID" AND WT."WarehouseID" = S."WarehouseToID" AND WT."CompanyID_id" = S."CompanyID_id"  
    INNER JOIN public."warehouse_warehouse" WF ON WF."BranchID" = S."BranchID" AND WF."WarehouseID" = S."WarehouseFromID" AND WF."CompanyID_id" = S."CompanyID_id"  
    INNER JOIN public."auth_user" UC ON UC."id" = S."CreatedUserID"  
    INNER JOIN public."auth_user" UU ON UU."id" = S."CreatedUserID"  
    WHERE S."CreatedUserID" = '35' AND S."Date" BETWEEN '2021-02-21' AND  '2022-02-21' AND S."BranchID" = '1' AND S."CompanyID_id" = '54ba4163-584f-4d3f-bb02-120b9800ba97'; 
--  IF(@UserID > 0 AND @WarehouseFromID > 0 AND @WarehouseToID > 0)  
 SELECT "StockTransferMasterID"  
      ,S."Action"  
      ,"VoucherNo"  
      ,"Date"  
      ,S."Notes"  
      ,"WarehouseFromID"  
      ,WF."WarehouseName" AS WarehouseFrom 
      , "WarehouseToID"  
      , WT."WarehouseName" AS WarehouseTo
       , "TotalQty"  
       , "GrandTotal"  
       , S."CreatedDate"  
      ,S."CreatedUserID"  
      ,"MaxGrandTotal"  
      ,S."UpdatedDate"  
      ,S."UpdatedUserID"  
      ,UC."UserName" AS CreatedUser
      , UU."UserName" AS UpdatedUser
      FROM public."stockTransferMaster_ID_stockTransferMaster_ID" AS S  
      INNER JOIN public."warehouse_warehouse" AS WT ON WT."BranchID" = S."BranchID" AND WT."WarehouseID" = S."WarehouseToID"  
      INNER JOIN public."warehouse_warehouse" AS WF ON WF."BranchID" = S."BranchID" AND WF."WarehouseID" = S."WarehouseFromID"  
      INNER JOIN public."auth_user" AS UC ON UC."BranchID" = S."BranchID" AND UC."UserID" = S."CreatedUserID"  
      INNER JOIN public."auth_user" AS UU ON UU."BranchID" = S."BranchID" AND UU."UserID" = S."CreatedUserID"  
      WHERE S.CreatedUserID = @UserID AND "WarehouseFromID" = '1' AND S.VoucherType = @Type AND S."BranchID" = '1'  
      AND WarehouseToID = @WarehouseToID AND S.CreatedUserID = @UserID AND S.Date BETWEEN @DateFrom AND @DateTo; 