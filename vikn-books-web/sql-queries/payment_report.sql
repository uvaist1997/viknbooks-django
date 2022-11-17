select PM."VoucherNo", PM."Date",     
AL."LedgerName", PD."Amount", PD."Discount", PD."NetAmount",
CASE WHEN
PM."VoucherType" = 'CP'  THEN 'Cash Payment'   
WHEN PM."VoucherType" = 'BP' THEN 'Bank Payment'      
END AS VoucherType, 
PD."Narration"           
from public."paymentMasters_paymentMaster" AS PM      
INNER JOIN public."paymentDetails_paymentDetail" AS PD ON PD."PaymentMasterID" = PM."PaymentMasterID"    AND PD."CompanyID_id" = PM."CompanyID_id"     
INNER JOIN public."accountLedger_accountLedger" AS AL ON AL."LedgerID" = PD."LedgerID" AND AL."CompanyID_id" = PM."CompanyID_id"           
WHERE PD."LedgerID" in %(CashLedgers)s AND PM."VoucherType" IN %(VoucherType)s  AND PM."Date" between %(FromDate)s AND %(ToDate)s  AND PM."CompanyID_id" = %(CompanyID)s          
order by "Date" DESC  