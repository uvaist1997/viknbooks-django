select RM."VoucherNo",RM."Date",      
AL."LedgerName",RD."Amount",RD."Discount",RD."NetAmount",
CASE WHEN
RM."VoucherType" = 'CR'  THEN 'Cash Receipt'   
WHEN RM."VoucherType" = 'BR' THEN 'Bank Receipt'      
END AS VoucherType, 
RD."Narration"      
from  public."receiptMasters_receiptMaster" AS RM      
INNER JOIN public."receiptDetailses_receiptDetails" AS RD ON RD."ReceiptMasterID" = RM."ReceiptMasterID"   AND RD."CompanyID_id" = RM."CompanyID_id"   
INNER JOIN public."accountLedger_accountLedger" AS AL ON AL."LedgerID" = RD."LedgerID" AND AL."CompanyID_id" = RM."CompanyID_id"      
WHERE RD."LedgerID" in %(CashLedgers)s  AND RM."VoucherType" IN %(VoucherType)s  AND RM."Date" between %(FromDate)s AND %(ToDate)s  AND RM."CompanyID_id" = %(CompanyID)s     
order by "Date" DESC