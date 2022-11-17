def edit_purchases(request,pk):
    instance = get_object_or_404(transaction_models.Purchase.objects.filter(pk=pk,is_deleted=False))
    PurchaseDetailsFormset = formset_factory(transaction_froms.PurchaseDetailsForm)
    if transaction_models.PurchaseDetails.objects.filter(PurchaseId=instance).exists():
        extra = 0
    else:
        extra= 1
    PurchaseDetailsFormset = inlineformset_factory(
        transaction_models.Purchase,
        transaction_models.PurchaseDetails,
        can_delete=True,
        extra=extra,
        form=transaction_froms.PurchaseDetailsForm,
    )

    if request.method == 'POST':      
        form = transaction_froms.PurchaseForm(request.POST,request.FILES,instance=instance)
        purchase_details_formset = PurchaseDetailsFormset(request.POST,prefix="purchase_details_formset",instance=instance)

         # taiking current financial year
        if master_models.FinancialYear.objects.filter(is_deleted=False,IsClosed=False).exists():
            financial_year = get_object_or_404(master_models.FinancialYear.objects.filter(is_deleted=False,IsClosed=False))
            if form.is_valid() and purchase_details_formset.is_valid():
                data = form.save(commit=False)
                data.updater = request.user
                data.date_updated = datetime.datetime.now()
                data.FinancialYearId = financial_year
                data.Action = 'M'
                data.save()

                if master_models.LedgerPosting.objects.filter(MasterID=instance.auto_id).exists():
                    ledger_post = master_models.LedgerPosting.objects.filter(MasterID=instance.auto_id)
                    for i in ledger_post:  
                        i.delete()    

                # taiking currency instance
                sar = None
                inr = None
                if master_models.Currency.objects.filter().exists():
                    sar = get_object_or_404(master_models.Currency.objects.filter(Name="SAR"))
                    inr = get_object_or_404(master_models.Currency.objects.filter(Name="INR"))

                purchase_items = purchase_details_formset.save(commit=False)  
                print(purchase_items)          
                print('purchase_items')          
                for item in purchase_items:            
                    item.PurchaseId = data                  
                    item.Action = "M"    
                    LedgerID = item.LedgerID
                    INRAmount = item.INRAmount
                    CurrencyRate = item.CurrencyRate
                    Amount = item.Amount        
                    item.save()

                    print(item.pk)
                    print("++++++++++")                    

                for item in purchase_details_formset:
                    LedgerID = item.cleaned_data['LedgerID']
                    INRAmount = item.cleaned_data['INRAmount']
                    CurrencyRate = item.cleaned_data['CurrencyRate']
                    Amount = item.cleaned_data['Amount']
                    Notes = item.cleaned_data['Notes']

                    # purchase details log
                    transaction_models.PurchaseDetailsLog.objects.create(      
                        LedgerID = LedgerID,
                        INRAmount = INRAmount,
                        CurrencyRate = CurrencyRate,
                        Notes = Notes,
                        Amount = Amount,
                        Action = "M",
                        PurchaseId = data,
                    )


                for obj in purchase_details_formset.deleted_objects:
                    print('======++++')
                    LedgerID = item.cleaned_data['LedgerID']
                    INRAmount = item.cleaned_data['INRAmount']
                    CurrencyRate = item.cleaned_data['CurrencyRate']
                    Amount = item.cleaned_data['Amount']
                    obj.delete()

                

                purch_formsets = transaction_models.PurchaseDetails.objects.filter(PurchaseId=data)
                for i in purch_formsets:
                    print("'''''''''''''purch'''''''''''''")
                    LedgerID = i.LedgerID
                    INRAmount = i.INRAmount
                    CurrencyRate = i.CurrencyRate
                    Amount = i.Amount
                    # ledger post sundry creaditer
                    master_models.LedgerPosting.objects.create(
                        auto_id = get_auto_id(master_models.LedgerPosting),
                        creator = request.user,
                        updater = request.user,
                        MasterID = data.auto_id,
                        LedgerID = LedgerID.pk,
                        Action = 'M',
                        VoucharType = "Purchase",
                        DetailID = i.pk,
                        IsActive = True,
                        Date = data.Date,
                        Debit = 0,
                        Credit = Amount,
                        CurrencyId = sar,                
                    )
                    # ledger post log sundry creaditer
                    master_models.LedgerPostingLog.objects.create(
                        auto_id = get_auto_id(master_models.LedgerPostingLog),
                        creator = request.user,
                        updater = request.user,
                        MasterID = data.auto_id,
                        LedgerID = LedgerID.pk,
                        Action = 'M',
                        VoucharType = "Purchase",
                        DetailID = i.pk,
                        IsActive = True,
                        Date = data.Date,
                        Debit = 0,
                        Credit = Amount,
                        CurrencyId = sar,                
                    )
                    # <<<<<<<<<<<<<<<<<<<<<<
                    # ledger post Agent
                    master_models.LedgerPosting.objects.create(
                        auto_id = get_auto_id(master_models.LedgerPosting),
                        creator = request.user,
                        updater = request.user,
                        MasterID = data.auto_id,
                        LedgerID = data.AgentID.pk,
                        Action = 'M',
                        VoucharType = "Purchase",
                        IsActive = True,
                        DetailID = i.pk,
                        Date = data.Date,
                        Debit = 0,
                        Credit = Amount,
                        CurrencyId = inr,                
                    )
                    # ledger post log Agent
                    master_models.LedgerPostingLog.objects.create(
                        auto_id = get_auto_id(master_models.LedgerPostingLog),
                        creator = request.user,
                        updater = request.user,
                        MasterID = data.auto_id,
                        LedgerID = data.AgentID.pk,
                        Action = 'M',
                        VoucharType = "Purchase",
                        IsActive = True,
                        DetailID = i.pk,
                        Date = data.Date,
                        Debit = 0,
                        Credit = Amount,
                        CurrencyId = inr,                
                    )


                # purchase log
                transaction_models.PurchaseLog.objects.create(
                    auto_id = get_auto_id(transaction_models.PurchaseLog),
                    creator = data.creator,
                    updater = data.updater,    
                    Action = "M",
                    PurchaseId = data.pk,
                    Notes = data.Notes,
                    VoucherNo = data.VoucherNo,
                    Date = data.Date,
                    AgentID = data.AgentID,
                    TotalINRAmount = data.TotalINRAmount,
                    CurrencyRate = data.CurrencyRate,
                    Amount = data.Amount,
                    FinancialYearId = data.FinancialYearId,
                )                

                if master_models.AccountLedger.objects.filter().exists():
                    ledger_purchase_id = get_object_or_404(master_models.AccountLedger.objects.filter(LedgerName="Purchase"))

                # ledger post INR
                master_models.LedgerPosting.objects.create(
                    auto_id = get_auto_id(master_models.LedgerPosting),
                    creator = request.user,
                    updater = request.user,
                    MasterID = data.auto_id,
                    LedgerID = ledger_purchase_id.id,
                    Action = 'M',
                    VoucharType = "Purchase",
                    IsActive = True,
                    Date = data.Date,
                    Debit = data.TotalINRAmount,
                    Credit = 0,
                    CurrencyId = inr,                
                )
                # ledger post log INR
                master_models.LedgerPostingLog.objects.create(
                    auto_id = get_auto_id(master_models.LedgerPostingLog),
                    creator = request.user,
                    updater = request.user,
                    MasterID = data.auto_id,
                    LedgerID = ledger_purchase_id.id,
                    Action = 'M',
                    VoucharType = "Purchase",
                    IsActive = True,
                    Date = data.Date,
                    Debit = data.TotalINRAmount,
                    Credit = 0,
                    CurrencyId = inr,                
                )
                 # ledger post SAR
                master_models.LedgerPosting.objects.create(
                    auto_id = get_auto_id(master_models.LedgerPosting),
                    creator = request.user,
                    updater = request.user,
                    MasterID = data.auto_id,
                    LedgerID = ledger_purchase_id.id,
                    Action = 'M',
                    VoucharType = "Purchase",
                    IsActive = True,
                    Date = data.Date,
                    Debit = data.TotalINRAmount,
                    Credit = 0,
                    CurrencyId = sar,                
                )
                # ledger post log SAR
                master_models.LedgerPostingLog.objects.create(
                    auto_id = get_auto_id(master_models.LedgerPostingLog),
                    creator = request.user,
                    updater = request.user,
                    MasterID = data.auto_id,
                    LedgerID = ledger_purchase_id.id,
                    Action = 'M',
                    VoucharType = "Purchase",
                    IsActive = True,
                    Date = data.Date,
                    Debit = data.TotalINRAmount,
                    Credit = 0,
                    CurrencyId = sar,                
                )                

                response_data = {
                    "status" : "true",
                    "title" : "Successfully Updated",
                    "message" : "Purchase Successfully Updated.",
                    "redirect" : "true",
                    "redirect_url" : reverse('transactions:purchases')
                }  
               
            else:
                message = generate_form_errors_new(form,formset=False)    
                message = generate_form_errors_new(purchase_details_formset,formset=True)
                print(form.errors)
                print(purchase_details_formset.errors)
               
                response_data = {
                    "status" : "false",
                    "stable" : "true",
                    "title" : "Form validation error",
                    "message" : str(message)
                }  
               
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        else:
            message = "Please Create a Financial Year"
            response_data = {
                "status" : "false",
                "stable" : "true",
                "title" : str(_("Financial Year is not exists")),
                "message" : str(message)
            }  
       
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')    
    else:
        sundry_creaditer = master_models.AccountLedger.objects.filter(MasterGroup__GroupName="Sundry Creditors")
        form = transaction_froms.PurchaseForm(instance=instance)
        form.fields['AgentID'].queryset = master_models.AccountLedger.objects.filter(MasterGroup__GroupName="Agent")
        purchase_details_formset = PurchaseDetailsFormset(prefix='purchase_details_formset',instance=instance)
        for forms in purchase_details_formset:
            forms.fields['LedgerID'].queryset = sundry_creaditer
        context = {
            "form" : form,
            "title" : str(_("Edit Purchase :")) + str(instance.AgentID),
            "purchase_details_formset" : purchase_details_formset,
            "url" : reverse('transactions:edit_purchases',kwargs={'pk':instance.pk}),
            "redirect" : True,
         
        }
        return render(request,"transactions/create_purchase.html",context)