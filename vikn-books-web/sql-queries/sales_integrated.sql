  
CREATE   PROCEDURE[dbo].[Select_SalesIntegrated_Report]    
--declare    
@BranchID BIGINT = 1,    
@FromDate  date = '2021-06-12',      
@ToDate date = '2021-06-12',    
@List VARCHAR(MAX)    
    
    
AS    
    
    
declare @DAILY_DATE date = @FromDate    
if (LEN(@List) > 0)    
begin    
WHILE @DAILY_DATE BETWEEN @FromDate AND @ToDate    
    
BEGIN    
select @DAILY_DATE as Date,    
    
(select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting L inner join SalesMaster S on L.VoucherMasterID = S.SalesMasterID where VoucherType = 'SI' AND L.LedgerID IN    
(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder = 9) AND L.Date = @DAILY_DATE and S.CreatedUserID in     
(SELECT * FROM  SplitList(@List, ',') ))AS CashSale    
    
,(select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting L inner    
                                    join SalesMaster S on L.VoucherMasterID = S.SalesMasterID where VoucherType = 'SI'    
    
AND L.LedgerID IN(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder = 8) AND L.Date = @DAILY_DATE and S.CreatedUserID in    
(SELECT * FROM  SplitList(@List, ',') ))AS BankSale    
,(select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting L inner    
                                    join SalesMaster S on L.VoucherMasterID = s.SalesMasterID where VoucherType = 'SI'    
    
AND L.LedgerID IN(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder IN(10, 29, 69)) AND L.Date = @DAILY_DATE and S.CreatedUserID in    
(SELECT * FROM  SplitList(@List, ',') ))AS CreditSale    
    
,(select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting L inner    
                                    join SalesReturnMaster S on L.VoucherMasterID = S.SalesReturnMasterID where VoucherType = 'SR'    
    
AND L.LedgerID IN(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder = 9) AND Date = @DAILY_DATE and S.CreatedUserID in    
(SELECT * FROM  SplitList(@List, ',') ))AS CashReturn    
    
,(select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting L inner    
                                    join SalesReturnMaster S on L.VoucherMasterID = S.SalesReturnMasterID where VoucherType = 'SR'    
    
AND L.LedgerID IN(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder = 8) AND Date = @DAILY_DATE and S.CreatedUserID in    
(SELECT * FROM  SplitList(@List, ',') ))AS BankReturn    
,(select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting L inner    
                                    join SalesReturnMaster S on L.VoucherMasterID = S.SalesReturnMasterID where VoucherType = 'SR'    
    
AND L.LedgerID IN(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder IN(10, 29, 69)) AND Date = @DAILY_DATE and S.CreatedUserID in    
(SELECT * FROM  SplitList(@List, ',') ))AS DebitReturn    
SET @DAILY_DATE = DATEADD(DAY, 1, @DAILY_DATE);    
    
end    
    
end    
    
else if (LEN(@List) = 0)    
    
begin    
    
WHILE @DAILY_DATE BETWEEN @FromDate AND @ToDate    
    
begin    
select @DAILY_DATE as Date, (select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting where VoucherType = 'SI' AND LedgerID IN(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder = 9) AND Date = @DAILY_DATE )AS CashSale    
,(select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting where VoucherType = 'SI' AND LedgerID IN(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder = 8) AND Date = @DAILY_DATE)AS BankSale    
,(select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting where VoucherType = 'SI' AND LedgerID IN(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder IN(10, 29, 69)) AND Date = @DAILY_DATE )AS CreditSale    
,(select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting where VoucherType = 'SR' AND LedgerID IN(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder = 9) AND Date = @DAILY_DATE )AS CashReturn    
,(select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting where VoucherType = 'SR' AND LedgerID IN(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder = 8) AND Date = @DAILY_DATE )AS BankReturn    
,(select ISNULL(SUM(Debit) - SUM(Credit), 0) from LedgerPosting where VoucherType = 'SR' AND LedgerID IN(SELECT LedgerID FROM AccountLedger WHERE AccountGroupUnder IN(10, 29, 69)) AND Date = @DAILY_DATE  
)AS DebitReturn    
SET @DAILY_DATE = DATEADD(DAY, 1, @DAILY_DATE);    
    
end  
end


select ('2022-02-16','2022-02-12','2022-01-20','2022-01-19') as Date, 
(select SUM("Debit") - SUM("Credit") from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SI' AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9')
 AND "Date" in ('2022-02-16','2022-02-12','2022-01-20','2022-01-19') )AS CashSale    
,(select SUM("Debit") - SUM("Credit") from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SI' AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8') AND "Date" in ('2022-02-16','2022-02-12','2022-01-20','2022-01-19'))AS BankSale    
,(select SUM("Debit") - SUM("Credit") from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SI' AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN('10', '29', '69')) AND "Date" in ('2022-02-16','2022-02-12','2022-01-20','2022-01-19'))AS CreditSale    
,(select SUM("Debit") - SUM("Credit") from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SR' AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9') AND "Date" in ('2022-02-16','2022-02-12','2022-01-20','2022-01-19'))AS CashReturn    
,(select SUM("Debit") - SUM("Credit") from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SR' AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8') AND "Date" in ('2022-02-16','2022-02-12','2022-01-20','2022-01-19'))AS BankReturn    
,(select SUM("Debit") - SUM("Credit") from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SR' AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN('10', '29', '69')) AND "Date" in ('2022-02-16','2022-02-12','2022-01-20','2022-01-19') 
)AS DebitReturn    

SET ('2022-02-16','2022-02-12','2022-01-20','2022-01-19') = DATEADD(DAY, 1, ('2022-02-16','2022-02-12','2022-02-10','2022-02-07','2022-02-02','2022-02-01','2022-01-31','2022-01-24','2022-01-20','2022-01-19'));


(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" L inner join public."salesMasters_salesMaster" S on L."VoucherMasterID" = S."SalesMasterID" where "VoucherType" = 'SI' AND L."LedgerID" IN    
(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9') AND L."Date" = %(DAILY_DATE)s and S."CreatedUserID" in     
(1,2))AS CashSale    
    
,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" L inner    
                                    join public."salesMasters_salesMaster" S on L."VoucherMasterID" = S."SalesMasterID" where "VoucherType" = 'SI'    
    
AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8') AND L."Date" = %(DAILY_DATE)s and S."CreatedUserID" in    
(1,2))AS BankSale    
,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" L inner    
                                    join public."salesMasters_salesMaster" S on L."VoucherMasterID" = s."SalesMasterID" where "VoucherType" = 'SI'    
    
AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN(10, 29, 69)) AND L."Date" = %(DAILY_DATE)s and S."CreatedUserID" in    
(1,2))AS CreditSale    
    
,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" L inner    
                                    join public."salesReturnMasters_salesReturnMaster" S on L."VoucherMasterID" = S."SalesReturnMasterID" where "VoucherType" = 'SR'    
    
AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9') AND "Date" = %(DAILY_DATE)s and S."CreatedUserID" in    
(1,2))AS CashReturn    
    
,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" L inner    
                                    join public."salesReturnMasters_salesReturnMaster" S on L."VoucherMasterID" = S."SalesReturnMasterID" where "VoucherType" = 'SR'    
    
AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8') AND "Date" = %(DAILY_DATE)s and S."CreatedUserID" in    
(1,2))AS BankReturn    
,(select ISNULL(SUM(Debit) - SUM(Credit), 0) from public."ledgerPostings_ledgerPosting" L inner    
                                    join public."salesReturnMasters_salesReturnMaster" S on L."VoucherMasterID" = S."SalesReturnMasterID" where "VoucherType" = 'SR'    
    
AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN('10', '29', '69')) AND "Date" = %(DAILY_DATE)s and S."CreatedUserID" in    
(1,2))AS DebitReturn    