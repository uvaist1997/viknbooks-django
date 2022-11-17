create      procedure Select_BillwiseList_Report        
   
   
 @BranchID BIGINT=1,            
 @FromDate DATETIME='2021-4-29',            
 @ToDate DATETIME='2021-5-20',            
 @Warehouse_List nvarchar(100)='1,3',            
 @Customer_List nvarchar(100)='93',            
 @User_List nvarchar(100)  ='1'  
           
   as  

   IF(len( @Warehouse_List  )>0) AND (len(  @RouteList  )>0) AND (len(  @User_List )>0)          
            
  begin            
                      
  SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"="SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID"   AND AL."CompanyID_id" = A."CompanyID_id"          
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15'  AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'  
 AND A."CreatedUserID" = '114'
 AND A."WarehouseID" = '1'
 AND A."LedgerID" in (SELECT "LedgerID" from public."parties_parties" as p where p."CompanyID_id" = A."CompanyID_id"
 And p."BranchID" = A."BranchID" AND p."RouteID" = '1')           
            
              
              
  end          
        
           
  ELSE IF(len( @Warehouse_List  )>0) AND (len(  @Customer_List  )>0) AND (len(  @User_List )>0)          
            
 begin            
                     
 SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"="SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"        
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15' AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b' 
 AND A."CreatedUserID" = '114'           
 AND A."WarehouseID" = '1'           
  AND A."LedgerID" = '111'           
           
            
            
end   
 ELSE  IF(len(  @RouteList  )>0) AND (len(  @Warehouse_List )>0)          
            
 begin            
                     
  SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"="SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID"   AND AL."CompanyID_id" = A."CompanyID_id"          
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15'  AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'  
 AND A."WarehouseID" = '1'
 AND A."LedgerID" in (SELECT "LedgerID" from public."parties_parties" as p where p."CompanyID_id" = A."CompanyID_id"
 And p."BranchID" = A."BranchID" AND p."RouteID" = '1')        
       
            
            
end  
 ELSE  IF(len(  @RouteList  )>0) AND (len(  @User_List )>0)          
            
 begin            
                     
SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"="SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID"   AND AL."CompanyID_id" = A."CompanyID_id"          
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15'  AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'  
 AND A."CreatedUserID" = '114'
 AND A."LedgerID" in (SELECT "LedgerID" from public."parties_parties" as p where p."CompanyID_id" = A."CompanyID_id"
 And p."BranchID" = A."BranchID" AND p."RouteID" = '1')          
       
            
            
end          
            
            
  ELSE IF(len( @Warehouse_List  )>0) AND (len(  @Customer_List  )>0)          
            
 begin            
                     
 SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"="SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"        
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15' AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b' 
 AND A."WarehouseID" = '1'           
  AND A."LedgerID" = '111'         
         
       
            
            
end    

   ELSE  IF(len(  @Customer_List  )>0) AND (len(  @User_List )>0)          
            
 begin            
                     
 SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"="SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID"   AND AL."CompanyID_id" = A."CompanyID_id"          
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15'  AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'  
 AND A."CreatedUserID" = '114'
 AND A."LedgerID" = '111'          
       
            
            
end  
            
            
  ELSE IF(len( @Warehouse_List  )>0)  AND (len(  @User_List )>0)          
            
 begin            
                     
 SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"="SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"        
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15' AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b' 
 AND A."WarehouseID" = '1'          
 AND A."CreatedUserID" = '114'          
    
       
            
            
end           
            


ELSE  IF(len( @RouteList  )>0)          
            
 begin            
                     
SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"="SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"         
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15' AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'    
 AND A."LedgerID" in (SELECT "LedgerID" from public."parties_parties" as p where p."CompanyID_id" = A."CompanyID_id"
 And p."BranchID" = A."BranchID" AND p."RouteID" = '1')        
        
            
            
end   
           
      
      
 ELSE  IF(len( @Warehouse_List  )>0)          
            
 begin            
                     
SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"        
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15' AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b' 
 AND A."WarehouseID" ='1'         
        
            
            
end           
           
     
      
 ELSE  IF(len(  @Customer_List  )>0)          
            
 begin            
                     
SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"="SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"         
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15' AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b'    
 AND A."LedgerID" = '111'       
       
            
            
end           
       
    
     
 ELSE  IF(len(  @User_List )>0)          
            
 begin            
                     
 SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"         
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15' AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b' 

AND A."CreatedUserID" = '114'       
            
            
end           
       
    
    
            
ELSE            
            
BEGIN            
            
             
 SELECT  ROW_NUMBER() Over(Order by CAST("SalesMasterID" AS BIGINT)) AS SlNo ,             
 A."Date",          
 "VoucherNo",       
  AL."LedgerName",      
    "GrandTotal" as GrandTotal,       
 "TotalGrossAmt" as GrossAmount,          
 "NetTotal"   as NetAmount,      
 A."TotalDiscount" as TotalDiscount,      
 A."VATAmount" as VATAmount ,        
 (SELECT sum("CostPerPrice"*"Qty") FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND "BranchID" = '1' AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
        
 FROM public."salesMasters_salesMaster" as A     
   INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"         
    where A."BranchID"='1' and   "Date" BETWEEN '2022-01-01' AND '2022-02-15' AND A."CompanyID_id" = '134e49f5-2390-4284-a6c5-eb205543a21b' 
END   