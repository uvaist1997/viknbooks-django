SELECT CASE  
            WHEN "VoucherType" = 'SI' THEN 'Sales Invoice'  
            WHEN "VoucherType" = 'SR' THEN 'Sales Return'  
            WHEN "VoucherType" = 'PI' THEN 'Purchase Invoice'  
            WHEN "VoucherType" = 'PR' THEN 'Purchase Return'  
            WHEN "VoucherType" = 'OS' THEN 'Opening Stock'  
            WHEN "VoucherType" = 'WO' THEN 'Work Order'  
            WHEN "VoucherType" = 'ST' THEN 'Stock Transfer'  
            WHEN "VoucherType" = 'SA' THEN 'Stock Adjustment'  
            WHEN "VoucherType" = 'ES' THEN 'Excess Stock'  
            WHEN "VoucherType" = 'SS' THEN 'Shortage Stock'  
            WHEN "VoucherType" = 'DS' THEN 'Damage Stock'  
            WHEN "VoucherType" = 'US' THEN 'Used Stock'  
            END AS VoucherType,  
            CASE
			WHEN "VoucherType" = 'SI' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))  
            WHEN "VoucherType" = 'SR' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))
            WHEN "VoucherType" = 'PI' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))
            WHEN "VoucherType" = 'PR' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))
            -- WHEN "VoucherType" = 'ST' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."stockTransferMaster_ID_stockTransferMaster_ID" WHERE "BranchID" = '1' AND "StockTransferMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))
			ELSE '' END AS LedgerName,
            CASE  
            WHEN "VoucherType" = 'SI' THEN (SELECT "VoucherNo" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id" )  
            WHEN "VoucherType" = 'SR' THEN (SELECT "VoucherNo" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'PI' THEN (SELECT "VoucherNo" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'PR' THEN (SELECT "VoucherNo" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'OS' THEN (SELECT "VoucherNo" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'WO' THEN (SELECT "VoucherNo" FROM public."WorkOrderMasters_WorkOrderMaster" WHERE "BranchID" = '1' AND "WorkOrderMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'ST' THEN (SELECT "VoucherNo" FROM public."stockTransferMaster_ID_stockTransferMaster_ID" WHERE "BranchID" = '1' AND "StockTransferMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'ES' THEN (SELECT "VoucherNo" FROM public."excessStockMaster_excessStockMaster" WHERE "BranchID" = '1' AND "ExcessStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'SS' THEN (SELECT "VoucherNo" FROM public."shortageStockMaster_shortageStockMaster" WHERE "BranchID" = '1' AND "ShortageStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'DS' THEN (SELECT "VoucherNo" FROM public."damageStockMaster_damageStockMaster" WHERE "BranchID" = '1' AND "DamageStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'US' THEN (SELECT "VoucherNo" FROM public."usedStockMaster_usedStockMaster" WHERE "BranchID" = '1' AND "UsedStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id" )  
            WHEN "VoucherType" = 'SA' THEN (SELECT "VoucherNo" FROM public."stock_management_master" WHERE "BranchID" = '1' AND "StockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id" )  
            END AS VoucherNo, 

            "Date",W."WarehouseName",  
            round("QtyIn",2),round("QtyOut",2),  
            round((S."QtyIn"* S."Rate"),2) as QtyInRate,round((S."QtyOut"* S."Rate"),2) as QtyOutRate,  
            
            ---------START------------
            CASE 
			WHEN "VoucherType" = 'SI' THEN (SELECT "Qty" FROM public."salesDetails_salesDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SR' THEN (SELECT "Qty" FROM public."salesReturnDetails_salesReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PI' THEN (SELECT "Qty" FROM public."purchaseDetailses_purchaseDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PR' THEN (SELECT "Qty" FROM public."purchaseReturnDetails_purchaseReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'OS' THEN (SELECT "Qty" FROM public."openingStockDetailss_openingStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'WO' THEN (SELECT "Qty" FROM public."workOrderDetails_workOrderDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'ST' THEN (SELECT "Qty" FROM public."stockTransferDetails_stockTransferDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'ES' THEN (SELECT "Stock" FROM public."excessStockDetails_excessStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SS' THEN (SELECT "Stock" FROM public."shortageStockDetails_shortageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'DS' THEN (SELECT "Stock" FROM public."damageStockDetails_damageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'US' THEN (SELECT "Stock" FROM public."usedStockDetails_usedStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SA' THEN (SELECT "Qty" FROM public."stock_management_details" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID")
			ELSE 0 END AS Qty,
            --------------------
			CASE 
            WHEN "VoucherType" = 'SI' THEN (SELECT "FreeQty" FROM public."salesDetails_salesDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SR' THEN (SELECT "FreeQty" FROM public."salesReturnDetails_salesReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PI' THEN (SELECT "FreeQty" FROM public."purchaseDetailses_purchaseDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PR' THEN (SELECT "FreeQty" FROM public."purchaseReturnDetails_purchaseReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'OS' THEN (SELECT "FreeQty" FROM public."openingStockDetailss_openingStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'WO' THEN (SELECT "FreeQty" FROM public."workOrderDetails_workOrderDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'ST' THEN (SELECT "FreeQty" FROM public."stockTransferDetails_stockTransferDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'ES' THEN (SELECT "FreeQty" FROM public."excessStockDetails_excessStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SS' THEN (SELECT "FreeQty" FROM public."shortageStockDetails_shortageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'DS' THEN (SELECT "FreeQty" FROM public."damageStockDetails_damageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'US' THEN (SELECT "FreeQty" FROM public."usedStockDetails_usedStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SA' THEN (SELECT "FreeQty" FROM public."stock_management_details" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID")
			ELSE 0 END AS FreeQty,

            -----------------
			CASE 
			WHEN "VoucherType" = 'SI' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."salesDetails_salesDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID"))
			WHEN "VoucherType" = 'SR' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."salesReturnDetails_salesReturnDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'PI' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."purchaseDetailses_purchaseDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'PR' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."purchaseReturnDetails_purchaseReturnDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'OS' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."openingStockDetailss_openingStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'WO' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."workOrderDetails_workOrderDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'ST' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."stockTransferDetails_stockTransferDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'ES' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."excessStockDetails_excessStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'SS' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."shortageStockDetails_shortageStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'DS' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."damageStockDetails_damageStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'US' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."usedStockDetails_usedStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'SA' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."stock_management_details" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID"))
			ELSE '' END AS Unit,

            ----------------
			CASE 
			WHEN "VoucherType" = 'SI' THEN (SELECT "UnitPrice" FROM public."salesDetails_salesDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SR' THEN (SELECT "UnitPrice" FROM public."salesReturnDetails_salesReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PI' THEN (SELECT "UnitPrice" FROM public."purchaseDetailses_purchaseDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PR' THEN (SELECT "UnitPrice" FROM public."purchaseReturnDetails_purchaseReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'OS' THEN (SELECT "Rate" FROM public."openingStockDetailss_openingStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'WO' THEN (SELECT "UnitPrice" FROM public."workOrderDetails_workOrderDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'ST' THEN (SELECT "Rate" FROM public."stockTransferDetails_stockTransferDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'ES' THEN (SELECT "UnitPrice" FROM public."excessStockDetails_excessStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SS' THEN (SELECT "UnitPrice" FROM public."shortageStockDetails_shortageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'DS' THEN (SELECT "UnitPrice" FROM public."damageStockDetails_damageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'US' THEN (SELECT "UnitPrice" FROM public."usedStockDetails_usedStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SA' THEN (SELECT "UnitPrice" FROM public."stock_management_details" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID")
			ELSE 0 END AS UnitPrice,
            --------END-----------

            U."username"  
            FROM public."stockPosting_stockPosting" AS S  
            INNER JOIN public.products_product AS P ON P."ProductID" = S."ProductID" AND P."CompanyID_id" = S."CompanyID_id"  
            INNER JOIN public.pricelist_pricelist AS PR ON PR."PriceListID" = S."PriceListID" AND PR."CompanyID_id" = S."CompanyID_id"  
            INNER JOIN public.warehouse_warehouse AS W ON W."WarehouseID" = S."WareHouseID" AND W."CompanyID_id" = S."CompanyID_id"  
            INNER JOIN public.auth_user AS U ON U."id" = S."CreatedUserID"  
            WHERE S."CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND S."WareHouseID" = '1' AND S."ProductID" = '2164' AND S."Date" BETWEEN '2022-06-01' AND '2022-06-01'  
            ORDER BY "Date"  



SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8' AND "LedgerID" = (SELECT "LedgerID" FROM public."stockTransferMaster_ID_stockTransferMaster_ID" WHERE "BranchID" = '1' AND "VoucherNo"="ST125" AND "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8')

SELECT * FROM public."stockTransferMaster_ID_stockTransferMaster_ID" WHERE "VoucherNo"='ST125' AND "BranchID" = '1' AND "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8'


