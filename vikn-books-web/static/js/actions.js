function show_loader(){
	$('body').append('<div class="popup-box"><div class="preloader pl-xxl"><svg viewBox="25 25 50 50" class="pl-circular"><circle r="20" cy="50" cx="50" class="plc-path"/></svg></div></div><span class="popup-bg"></span>');
}

function remove_popup(){
	$('.popup-box,.popup-bg').remove();
}


$(document).ready(function () {
	$(document).on('click','.action-button',function(e){
    	e.preventDefault();
    	$this = $(this);
    	var text = $this.attr('data-text');
    	var type = "warning";
    	var confirmButtonText = "Yes";
    	var confirmButtonColor = "#DD6B55";
    	var id = $this.attr('data-id');
		var url = $this.attr('href');
		var title = $this.attr('data-title');
		if(!title){
			title = "Are you sure?";
		}
		var isReload = $this.hasClass('reload');
		var isRedirect = $this.hasClass('redirect');
		var showAlert = $this.hasClass('with_alert');
		var isRemove = $this.hasClass('remove');
		var noResponsePopup = $this.hasClass('no-response-popup');
		var downloadFile = $this.hasClass('download-file');
        swal.fire({
            title: title,
            text: text,
            type: type,
            showCancelButton: true,
            confirmButtonColor: confirmButtonColor,
            confirmButtonText: confirmButtonText,
            closeOnConfirm: false,
			closeOnCancel: false
        }).then((result) => {
			if (result.value) {
				show_loader();
				
				window.setTimeout(function(){
					jQuery.ajax({
						type : 'GET',
						url : url,
						dataType : 'json',
						data : {
							pk : id
						},
						success : function(data) {
							var message = data['message'];
							var status = data['status'];
							var redirect = data['redirect'];
							var redirect_url = data['redirect_url'];
							var stable = data['stable'];
							var title = data['title'];	
							var file_url = data['file_url']
							
							remove_popup();	
							
							if (status == 'true') {
								if (title){
									title = title;
								}else{
									title = "Success";
								}
								if(!noResponsePopup){
									swal.fire({
									  title: title,
									  text: message,
									  type: "success"
									}).then(() => {
										if (isRemove) {
											var row_length = $this.parents('tbody').find('tr').length;
											$this.parents('tr').remove();
											var end = parseInt($('.current_end_status').html());
											var total = parseInt($('.total_count').html());
											$('.total_count').html(total - 1);
											$('.current_end_status').html(end - 1);
											if(row_length <= 1){
												window.location.reload();
											}
										}
										
										if (stable != "true"){					
											if (isRedirect && redirect == 'true') {
												window.location.href = redirect_url;
											}
											if (isReload) {
												window.location.reload();
											}	
										}
									});
								}

								if (downloadFile) {
									window.location.href = file_url;
								}
								
								
							}else{
								if (title){
									title = title;
								}else{
									title = "An Error Occurred";
								}	
								
								swal.fire(title, message, "error");
										
								if (stable != "true"){					
									window.setTimeout(function() {
									}, 2000);	
								}	
							}
						},
						error : function(data) {
							remove_popup();	
							
							var title = "An error occurred";
							var message = "An error occurred. Please try again later."; 
							swal.fire(title, message, "error");
						}
					});
				},100);				
				
		  	}
		  	else if(result.dismiss === Swal.DismissReason.cancel){}
		});
    });
    
    $(document).on('change','.change_select',function(e){
    	e.preventDefault();
    	$this = $(this);
		var isReload = $this.hasClass('reload');
		var isRedirect = $this.hasClass('redirect');
		var showAlert = $this.hasClass('with_alert');
		var id = $this.val();
		var url = $this.attr('data-url');
		
		show_loader();
		jQuery.ajax({
			type : 'GET',
			url : url,
			dataType : 'json',
			data : {
				pk : id
			},
			success : function(data) {
				var message = data['message'];
				var status = data['status'];
				var redirect = data['redirect'];
				var redirect_url = data['redirect_url'];
				var stable = data['stable'];
				var title = data['title'];	
				
				remove_popup();	
				
				if (status == 'true') {
					if (title){
						title = title;
					}else{
						title = "Success";
					}
					
					swal.fire({
					  title: title,
					  text: message,
					  timer: 2000,
					  type: "success"
					}, function () {
						if (stable != "true"){					
							if (isRedirect && redirect == 'true') {
								window.location.href = redirect_url;
							}
							if (isReload) {
								window.location.reload();
							}	
						}
					});
					
					
				}else{
					if (title){
						title = title;
					}else{
						title = "An Error Occurred";
					}	
					
					swal.fire(title, message, "error");
							
					if (stable != "true"){					
						window.setTimeout(function() {
						}, 2000);	
					}	
				}
			},
			error : function(data) {
				remove_popup();	
				
				var title = "An error occurred";
				var message = "An error occurred. Please try again later."; 
				swal.fire(title, message, "error");
			}
		});
    });
	
	var $s = $('.form_set_row .check_empty input');
	var e = $s.val();
	if(e == 0 || e == '0'){
		$s.val('');
	}
	
	$(document).on('submit', 'form.ajax', function(e){	
		e.preventDefault();
		var $this = $(this);

		var skip_empty_row = $this.hasClass('skip_empty_row');
		var not_allowed_without_formset = $this.hasClass('not_allowed_without_formset');
		
		var row_count = $this.find('tr.form_set_row').length;
		
		if(skip_empty_row){
			var er = 0;
			$this.find('tr.form_set_row').each(function(){
				$t = $(this);
				var value = $t.find('.check_empty input').val();
				if(!value){
					if(er == 0){
						$t.addClass('first');
					}
					er++;
					$t.addClass('delete_row');
				}
			});
	
			
			$f = $this.find('tr.form_set_row:first-child');
			if($f.hasClass('first') && not_allowed_without_formset){
				$('tr.form_set_row.delete_row').not($f).find('a.icon-trash').click();
			}else{
				$('tr.form_set_row.delete_row').find('a.icon-trash').click();
			}	
					
		}
		
		$this.validate({
			rules : {
				required_field : "required",
				password1: "required",
			    password2: {
			    	equalTo: "#id_password1"
			    }
			}
		});
		var valid = $this.valid();
		if (valid){

			document.onkeydown = function(evt) {
			    return false;
			};

			var url = $this.attr('action');
			var method = $this.attr('method');
			var isReset = $this.hasClass('reset');
			var isReload = $this.hasClass('reload');
			var isRedirect = $this.hasClass('redirect');
			var noLoader = $this.hasClass('no-loader');
			var noPopup = $this.hasClass('no-popup');
			var isRunFunctionAfter = $this.hasClass('run-function-after');
			var function_name = $this.attr('data-function');
			var selector_class = $this.attr('data-after-function-selector-parent-class');
			var $after_selector = '';
			if(selector_class){
				$after_selector = $('.' + selector_class);
			}

			var data = $this.serialize();
			
			if (!noLoader) {
				show_loader();	
			}
			console.log('dt')
			jQuery.ajax({
				type : method,
				url : url,
				dataType : 'json',
				data : new FormData(this),
				contentType: false,
				cache: false,
				processData: false,
				success : function(data) {

					if (!noLoader) {
						remove_popup();	
					}
					
					var message = data['message'];
					var status = data['status'];
					var title = data['title'];	
					var redirect = data['redirect'];
					var redirect_url = data['redirect_url'];
					var new_redirect_window = data['new_redirect_window'];
					var new_window_url = data['new_window_url']
					var stable = data['stable'];
					var pk = data['pk'];

					if (status == 'true') {
						if (title){
							title = title;
						}else{
							title = "Success";
						}

						function  doAfter() {
							
							if (isReset) {
								$this[0].reset();
								$this.find('.select2-hidden-accessible').val(null).trigger('change').click();
							}
							

							if(isRunFunctionAfter){
								doAfterAction(function_name,data,$this,$after_selector);
							}

							
							if (stable != "true"){	
										
								if (isRedirect && redirect == 'true') {
									window.location.href = redirect_url;
								}
								if (isReload) {
									window.location.reload();
								}	
							}

							
						}
						if (new_redirect_window == 'true'){
							if (new_window_url != "" || new_window_url != null || new_window_url != undefined ){
							window.open(new_window_url);
							}
						}
						

						if(noPopup){
							doAfter();
						}else{
							swal.fire({
							  title: title,
							  text: message,
							  type: "success"
							}).then((res) => {
								doAfter();
							}) 
						}
						document.onkeydown = function(evt) {
						    return true;
						};
												
					}else{			
						if (title){
							title = title;
						}else{
							title = "An Error Occurred";
						}	
						
						swal.fire(title, message, "error");
								
						if (stable != "true"){					
							window.setTimeout(function() {
							}, 2000);	
						}
						document.onkeydown = function(evt) {
						    return true;
						};	
					}					
					
				},
				error : function(data) {
					remove_popup();	
							
					var title = "An error occurred";
					var message = "An error occurred. Please try again later."; 
					document.onkeydown = function(evt) {
					    return true;
					};
					swal.fire(title, message, "error");
				}
			});		
		}

	});	

	$(document).on('click', 'a.ajax', function(e){	
		e.preventDefault();
		var $this = $(this);

		var url = $this.attr('href');
		var method = $this.attr('method');
		var isReset = $this.hasClass('reset');
		var isReload = $this.hasClass('reload');
		var isRedirect = $this.hasClass('redirect');
		var noLoader = $this.hasClass('no-loader');
		var noPopup = $this.hasClass('no-popup');
		var isRunFunctionAfter = $this.hasClass('run-function-after');
		var function_name = $this.attr('data-function');
		var selector_class = $this.attr('data-after-function-selector-parent-class');
		var $after_selector = '';
		if(selector_class){
			$after_selector = $('.' + selector_class);
		}

		var data = $this.serialize();
		
		if (!noLoader) {
			show_loader();	
		}
		
		jQuery.ajax({
			type : method,
			url : url,
			dataType : 'json',
			data : new FormData(this),
			contentType: false,
			cache: false,
			processData: false,
			success : function(data) {

				if (!noLoader) {
					remove_popup();	
				}
				
				var message = data['message'];
				var status = data['status'];
				var title = data['title'];	
				var redirect = data['redirect'];
				var redirect_url = data['redirect_url'];
				var new_redirect_window = data['new_redirect_window'];
				var new_window_url = data['new_window_url']
				var stable = data['stable'];
				var pk = data['pk'];

				if (status == 'true') {
					if (title){
						title = title;
					}else{
						title = "Success";
					}

					function  doAfter() {
						
						if (isReset) {
							$this[0].reset();
							$this.find('.select2-hidden-accessible').val(null).trigger('change').click();
						}
						

						if(isRunFunctionAfter){
							doAfterAction(function_name,data,$this,$after_selector);
						}

						
						if (stable != "true"){	
									
							if (isRedirect && redirect == 'true') {
								window.location.href = redirect_url;
							}
							if (isReload) {
								window.location.reload();
							}	
						}

						
					}
					if (new_redirect_window == 'true'){
						if (new_window_url != "" || new_window_url != null || new_window_url != undefined ){
						window.open(new_window_url);
						}
					}
					

					if(noPopup){
						doAfter();
					}else{
						swal.fire({
						  title: title,
						  text: message,
						  type: "success"
						}).then((res) => {
							doAfter();
						}) 
					}
					document.onkeydown = function(evt) {
					    return true;
					};
											
				}else{			
					if (title){
						title = title;
					}else{
						title = "An Error Occurred";
					}	
					
					swal.fire(title, message, "error");
							
					if (stable != "true"){					
						window.setTimeout(function() {
						}, 2000);	
					}
					document.onkeydown = function(evt) {
					    return true;
					};	
				}					
				
			},
			error : function(data) {
				remove_popup();	
						
				var title = "An error occurred";
				var message = "An error occurred. Please try again later."; 
				document.onkeydown = function(evt) {
				    return true;
				};
				swal.fire(title, message, "error");
			}
		});		
	});


	$('body').on("focus","input.datepickerold", function(){
	    $(this).datepicker({
	    	dateFormat : 'mm/dd/yy',
	    	inline: true,  
            showOtherMonths: true, 
            changeMonth : true,
			changeYear : true,  
            dayNamesMin: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], 
	    });
	});

    $('body').on('click', '[data-ma-action]', function (e) {
        e.preventDefault();
        
        var action = $(this).data('ma-action');
        var $this = $(this);
        
        switch (action) {
            
            /*-------------------------------------------
                Mainmenu and Notifications open/close
            ---------------------------------------------*/
            
            /* Open Sidebar */
            case 'sidebar-open':
                
                var target = $(this).data('ma-target');

                $this.addClass('toggled');
                $('#main').append('<div data-ma-action="sidebar-close" class="sidebar-backdrop animated fadeIn" />')
                
                if (target == 'main-menu') {
                    $('#s-main-menu').addClass('toggled');
                }
                if (target == 'user-alerts') {
                    $('#s-user-alerts').addClass('toggled');
                }

                $('body').addClass('o-hidden');
                
                break;
            
            /* Close Sidebar */
            case 'sidebar-close':
                
                $('[data-ma-action="sidebar-open"]').removeClass('toggled');
                $('.sidebar').removeClass('toggled');
                $('.sidebar-backdrop').remove();
                $('body').removeClass('o-hidden');
                
                break;
            

            
            /*----------------------------------
                Header Search
            -----------------------------------*/
            
            /* Clear Search */
            case 'search-clear':
                
                /* For mobile only */
                $('.h-search').removeClass('toggled');
        
                /* For all */
                $('.hs-input').val('');
                $('.h-search').removeClass('focused');
                
                break;
            
            /* Open search */
            case 'search-open':
                
                $('.h-search').addClass('toggled');
                $('.hs-input').focus();
        
                break;
            

            
            /*----------------------------------
                Main menu
            -----------------------------------*/
            
            /* Toggle Sub menu */
            case 'submenu-toggle':

                $this.next().slideToggle(200);
                $this.parent().toggleClass('toggled');
                
                break;



            /*----------------------------------
                 Messages
            -----------------------------------*/
            case 'message-toggle':

                $('.ms-menu').toggleClass('toggled');
                $this.toggleClass('toggled');

                break;



            /*-------------------------------------------------
                Action Header Search (used in listview.html)
             -------------------------------------------------*/

            //Open action header search
            case 'ah-search-open':
                x = $(this).closest('.action-header').find('.ah-search');

                x.fadeIn(300);
                x.find('.ahs-input').focus();

                break;

            //Close action header search
            case 'ah-search-close':
                    x.fadeOut(300);
                    setTimeout(function(){
                        x.find('.ahs-input').val('');
                    }, 350);

                break;

        }
    }); 
});

/* form validation*/
(function(e){e.extend(e.fn,{validate:function(t){if(!this.length){if(t&&t.debug&&window.console){console.warn("Nothing selected, can't validate, returning nothing.")}return}var n=e.data(this[0],"validator");if(n){return n}this.attr("novalidate","novalidate");n=new e.validator(t,this[0]);e.data(this[0],"validator",n);if(n.settings.onsubmit){this.validateDelegate(":submit","click",function(t){if(n.settings.submitHandler){n.submitButton=t.target}if(e(t.target).hasClass("cancel")){n.cancelSubmit=true}if(e(t.target).attr("formnovalidate")!==undefined){n.cancelSubmit=true}});this.submit(function(t){function r(){var r;if(n.settings.submitHandler){if(n.submitButton){r=e("<input type='hidden'/>").attr("name",n.submitButton.name).val(e(n.submitButton).val()).appendTo(n.currentForm)}n.settings.submitHandler.call(n,n.currentForm,t);if(n.submitButton){r.remove()}return false}return true}if(n.settings.debug){t.preventDefault()}if(n.cancelSubmit){n.cancelSubmit=false;return r()}if(n.form()){if(n.pendingRequest){n.formSubmitted=true;return false}return r()}else{n.focusInvalid();return false}})}return n},valid:function(){if(e(this[0]).is("form")){return this.validate().form()}else{var t=true;var n=e(this[0].form).validate();this.each(function(){t=t&&n.element(this)});return t}},removeAttrs:function(t){var n={},r=this;e.each(t.split(/\s/),function(e,t){n[t]=r.attr(t);r.removeAttr(t)});return n},rules:function(t,n){var r=this[0];if(t){var i=e.data(r.form,"validator").settings;var s=i.rules;var o=e.validator.staticRules(r);switch(t){case"add":e.extend(o,e.validator.normalizeRule(n));delete o.messages;s[r.name]=o;if(n.messages){i.messages[r.name]=e.extend(i.messages[r.name],n.messages)}break;case"remove":if(!n){delete s[r.name];return o}var u={};e.each(n.split(/\s/),function(e,t){u[t]=o[t];delete o[t]});return u}}var a=e.validator.normalizeRules(e.extend({},e.validator.classRules(r),e.validator.attributeRules(r),e.validator.dataRules(r),e.validator.staticRules(r)),r);if(a.required){var f=a.required;delete a.required;a=e.extend({required:f},a)}return a}});e.extend(e.expr[":"],{blank:function(t){return!e.trim(""+e(t).val())},filled:function(t){return!!e.trim(""+e(t).val())},unchecked:function(t){return!e(t).prop("checked")}});e.validator=function(t,n){this.settings=e.extend(true,{},e.validator.defaults,t);this.currentForm=n;this.init()};e.validator.format=function(t,n){if(arguments.length===1){return function(){var n=e.makeArray(arguments);n.unshift(t);return e.validator.format.apply(this,n)}}if(arguments.length>2&&n.constructor!==Array){n=e.makeArray(arguments).slice(1)}if(n.constructor!==Array){n=[n]}e.each(n,function(e,n){t=t.replace(new RegExp("\\{"+e+"\\}","g"),function(){return n})});return t};e.extend(e.validator,{defaults:{messages:{},groups:{},rules:{},errorClass:"error",validClass:"valid",errorElement:"label",focusInvalid:true,errorContainer:e([]),errorLabelContainer:e([]),onsubmit:true,ignore:":hidden",ignoreTitle:false,onfocusin:function(e,t){this.lastActive=e;if(this.settings.focusCleanup&&!this.blockFocusCleanup){if(this.settings.unhighlight){this.settings.unhighlight.call(this,e,this.settings.errorClass,this.settings.validClass)}this.addWrapper(this.errorsFor(e)).hide()}},onfocusout:function(e,t){if(!this.checkable(e)&&(e.name in this.submitted||!this.optional(e))){this.element(e)}},onkeyup:function(e,t){if(t.which===9&&this.elementValue(e)===""){return}else if(e.name in this.submitted||e===this.lastElement){this.element(e)}},onclick:function(e,t){if(e.name in this.submitted){this.element(e)}else if(e.parentNode.name in this.submitted){this.element(e.parentNode)}},highlight:function(t,n,r){if(t.type==="radio"){this.findByName(t.name).addClass(n).removeClass(r)}else{e(t).addClass(n).removeClass(r)}},unhighlight:function(t,n,r){if(t.type==="radio"){this.findByName(t.name).removeClass(n).addClass(r)}else{e(t).removeClass(n).addClass(r)}}},setDefaults:function(t){e.extend(e.validator.defaults,t)},messages:{required:"This field is required.",remote:"Please fix this field.",email:"Please enter a valid email address.",url:"Please enter a valid URL.",date:"Please enter a valid date.",dateISO:"Please enter a valid date (ISO).",number:"Please enter a valid number.",digits:"Please enter only digits.",creditcard:"Please enter a valid credit card number.",equalTo:"Please enter the same value again.",maxlength:e.validator.format("Please enter no more than {0} characters."),minlength:e.validator.format("Please enter at least {0} characters."),rangelength:e.validator.format("Please enter a value between {0} and {1} characters long."),range:e.validator.format("Please enter a value between {0} and {1}."),max:e.validator.format("Please enter a value less than or equal to {0}."),min:e.validator.format("Please enter a value greater than or equal to {0}.")},autoCreateRanges:false,prototype:{init:function(){function r(t){var n=e.data(this[0].form,"validator"),r="on"+t.type.replace(/^validate/,"");if(n.settings[r]){n.settings[r].call(n,this[0],t)}}this.labelContainer=e(this.settings.errorLabelContainer);this.errorContext=this.labelContainer.length&&this.labelContainer||e(this.currentForm);this.containers=e(this.settings.errorContainer).add(this.settings.errorLabelContainer);this.submitted={};this.valueCache={};this.pendingRequest=0;this.pending={};this.invalid={};this.reset();var t=this.groups={};e.each(this.settings.groups,function(n,r){if(typeof r==="string"){r=r.split(/\s/)}e.each(r,function(e,r){t[r]=n})});var n=this.settings.rules;e.each(n,function(t,r){n[t]=e.validator.normalizeRule(r)});e(this.currentForm).validateDelegate(":text, [type='password'], [type='file'], select, textarea, "+"[type='number'], [type='search'] ,[type='tel'], [type='url'], "+"[type='email'], [type='datetime'], [type='date'], [type='month'], "+"[type='week'], [type='time'], [type='datetime-local'], "+"[type='range'], [type='color'] ","focusin focusout keyup",r).validateDelegate("[type='radio'], [type='checkbox'], select, option","click",r);if(this.settings.invalidHandler){e(this.currentForm).bind("invalid-form.validate",this.settings.invalidHandler)}},form:function(){this.checkForm();e.extend(this.submitted,this.errorMap);this.invalid=e.extend({},this.errorMap);if(!this.valid()){e(this.currentForm).triggerHandler("invalid-form",[this])}this.showErrors();return this.valid()},checkForm:function(){this.prepareForm();for(var e=0,t=this.currentElements=this.elements();t[e];e++){if(this.findByName(t[e].name).length!=undefined&&this.findByName(t[e].name).length>1){for(var n=0;n<this.findByName(t[e].name).length;n++){this.check(this.findByName(t[e].name)[n])}}else{this.check(t[e])}}return this.valid()},element:function(t){t=this.validationTargetFor(this.clean(t));this.lastElement=t;this.prepareElement(t);this.currentElements=e(t);var n=this.check(t)!==false;if(n){delete this.invalid[t.name]}else{this.invalid[t.name]=true}if(!this.numberOfInvalids()){this.toHide=this.toHide.add(this.containers)}this.showErrors();return n},showErrors:function(t){if(t){e.extend(this.errorMap,t);this.errorList=[];for(var n in t){this.errorList.push({message:t[n],element:this.findByName(n)[0]})}this.successList=e.grep(this.successList,function(e){return!(e.name in t)})}if(this.settings.showErrors){this.settings.showErrors.call(this,this.errorMap,this.errorList)}else{this.defaultShowErrors()}},resetForm:function(){if(e.fn.resetForm){e(this.currentForm).resetForm()}this.submitted={};this.lastElement=null;this.prepareForm();this.hideErrors();this.elements().removeClass(this.settings.errorClass).removeData("previousValue")},numberOfInvalids:function(){return this.objectLength(this.invalid)},objectLength:function(e){var t=0;for(var n in e){t++}return t},hideErrors:function(){this.addWrapper(this.toHide).hide()},valid:function(){return this.size()===0},size:function(){return this.errorList.length},focusInvalid:function(){if(this.settings.focusInvalid){try{e(this.findLastActive()||this.errorList.length&&this.errorList[0].element||[]).filter(":visible").focus().trigger("focusin")}catch(t){}}},findLastActive:function(){var t=this.lastActive;return t&&e.grep(this.errorList,function(e){return e.element.name===t.name}).length===1&&t},elements:function(){var t=this,n={};return e(this.currentForm).find("input, select, textarea").not(":submit, :reset, :image, [disabled]").not(this.settings.ignore).filter(function(){if(!this.name&&t.settings.debug&&window.console){console.error("%o has no name assigned",this)}if(this.name in n||!t.objectLength(e(this).rules())){return false}n[this.name]=true;return true})},clean:function(t){return e(t)[0]},errors:function(){var t=this.settings.errorClass.replace(" ",".");return e(this.settings.errorElement+"."+t,this.errorContext)},reset:function(){this.successList=[];this.errorList=[];this.errorMap={};this.toShow=e([]);this.toHide=e([]);this.currentElements=e([])},prepareForm:function(){this.reset();this.toHide=this.errors().add(this.containers)},prepareElement:function(e){this.reset();this.toHide=this.errorsFor(e)},elementValue:function(t){var n=e(t).attr("type"),r=e(t).val();if(n==="radio"||n==="checkbox"){return e("input[name='"+e(t).attr("name")+"']:checked").val()}if(typeof r==="string"){return r.replace(/\r/g,"")}return r},check:function(t){t=this.validationTargetFor(this.clean(t));var n=e(t).rules();var r=false;var i=this.elementValue(t);var s;for(var o in n){var u={method:o,parameters:n[o]};try{s=e.validator.methods[o].call(this,i,t,u.parameters);if(s==="dependency-mismatch"){r=true;continue}r=false;if(s==="pending"){this.toHide=this.toHide.not(this.errorsFor(t));return}if(!s){this.formatAndAdd(t,u);return false}}catch(a){if(this.settings.debug&&window.console){console.log("Exception occurred when checking element "+t.id+", check the '"+u.method+"' method.",a)}throw a}}if(r){return}if(this.objectLength(n)){this.successList.push(t)}return true},customDataMessage:function(t,n){return e(t).data("msg-"+n.toLowerCase())||t.attributes&&e(t).attr("data-msg-"+n.toLowerCase())},customMessage:function(e,t){var n=this.settings.messages[e];return n&&(n.constructor===String?n:n[t])},findDefined:function(){for(var e=0;e<arguments.length;e++){if(arguments[e]!==undefined){return arguments[e]}}return undefined},defaultMessage:function(t,n){return this.findDefined(this.customMessage(t.name,n),this.customDataMessage(t,n),!this.settings.ignoreTitle&&t.title||undefined,e.validator.messages[n],"<strong>Warning: No message defined for "+t.name+"</strong>")},formatAndAdd:function(t,n){var r=this.defaultMessage(t,n.method),i=/\$?\{(\d+)\}/g;if(typeof r==="function"){r=r.call(this,n.parameters,t)}else if(i.test(r)){r=e.validator.format(r.replace(i,"{$1}"),n.parameters)}this.errorList.push({message:r,element:t});this.errorMap[t.name]=r;this.submitted[t.name]=r},addWrapper:function(e){if(this.settings.wrapper){e=e.add(e.parent(this.settings.wrapper))}return e},defaultShowErrors:function(){var e,t;for(e=0;this.errorList[e];e++){var n=this.errorList[e];if(this.settings.highlight){this.settings.highlight.call(this,n.element,this.settings.errorClass,this.settings.validClass)}this.showLabel(n.element,n.message)}if(this.errorList.length){this.toShow=this.toShow.add(this.containers)}if(this.settings.success){for(e=0;this.successList[e];e++){this.showLabel(this.successList[e])}}if(this.settings.unhighlight){for(e=0,t=this.validElements();t[e];e++){this.settings.unhighlight.call(this,t[e],this.settings.errorClass,this.settings.validClass)}}this.toHide=this.toHide.not(this.toShow);this.hideErrors();this.addWrapper(this.toShow).show()},validElements:function(){return this.currentElements.not(this.invalidElements())},invalidElements:function(){return e(this.errorList).map(function(){return this.element})},showLabel:function(t,n){var r=this.errorsFor(t);if(r.length){r.removeClass(this.settings.validClass).addClass(this.settings.errorClass);r.html(n)}else{r=e("<"+this.settings.errorElement+">").attr("for",this.idOrName(t)).addClass(this.settings.errorClass).html(n||"");if(this.settings.wrapper){r=r.hide().show().wrap("<"+this.settings.wrapper+"/>").parent()}if(!this.labelContainer.append(r).length){if(this.settings.errorPlacement){this.settings.errorPlacement(r,e(t))}else{r.insertAfter(t)}}}if(!n&&this.settings.success){r.text("");if(typeof this.settings.success==="string"){r.addClass(this.settings.success)}else{this.settings.success(r,t)}}this.toShow=this.toShow.add(r)},errorsFor:function(t){var n=this.idOrName(t);return this.errors().filter(function(){return e(this).attr("for")===n})},idOrName:function(e){return this.groups[e.name]||(this.checkable(e)?e.name:e.id||e.name)},validationTargetFor:function(e){if(this.checkable(e)){e=this.findByName(e.name).not(this.settings.ignore)[0]}return e},checkable:function(e){return/radio|checkbox/i.test(e.type)},findByName:function(t){return e(this.currentForm).find("[name='"+t+"']")},getLength:function(t,n){switch(n.nodeName.toLowerCase()){case"select":return e("option:selected",n).length;case"input":if(this.checkable(n)){return this.findByName(n.name).filter(":checked").length}}return t.length},depend:function(e,t){return this.dependTypes[typeof e]?this.dependTypes[typeof e](e,t):true},dependTypes:{"boolean":function(e,t){return e},string:function(t,n){return!!e(t,n.form).length},"function":function(e,t){return e(t)}},optional:function(t){var n=this.elementValue(t);return!e.validator.methods.required.call(this,n,t)&&"dependency-mismatch"},startRequest:function(e){if(!this.pending[e.name]){this.pendingRequest++;this.pending[e.name]=true}},stopRequest:function(t,n){this.pendingRequest--;if(this.pendingRequest<0){this.pendingRequest=0}delete this.pending[t.name];if(n&&this.pendingRequest===0&&this.formSubmitted&&this.form()){e(this.currentForm).submit();this.formSubmitted=false}else if(!n&&this.pendingRequest===0&&this.formSubmitted){e(this.currentForm).triggerHandler("invalid-form",[this]);this.formSubmitted=false}},previousValue:function(t){return e.data(t,"previousValue")||e.data(t,"previousValue",{old:null,valid:true,message:this.defaultMessage(t,"remote")})}},classRuleSettings:{required:{required:true},email:{email:true},url:{url:true},date:{date:true},dateISO:{dateISO:true},number:{number:true},digits:{digits:true},creditcard:{creditcard:true}},addClassRules:function(t,n){if(t.constructor===String){this.classRuleSettings[t]=n}else{e.extend(this.classRuleSettings,t)}},classRules:function(t){var n={};var r=e(t).attr("class");if(r){e.each(r.split(" "),function(){if(this in e.validator.classRuleSettings){e.extend(n,e.validator.classRuleSettings[this])}})}return n},attributeRules:function(t){var n={};var r=e(t);var i=r[0].getAttribute("type");for(var s in e.validator.methods){var o;if(s==="required"){o=r.get(0).getAttribute(s);if(o===""){o=true}o=!!o}else{o=r.attr(s)}if(/min|max/.test(s)&&(i===null||/number|range|text/.test(i))){o=Number(o)}if(o){n[s]=o}else if(i===s&&i!=="range"){n[s]=true}}if(n.maxlength&&/-1|2147483647|524288/.test(n.maxlength)){delete n.maxlength}return n},dataRules:function(t){var n,r,i={},s=e(t);for(n in e.validator.methods){r=s.data("rule-"+n.toLowerCase());if(r!==undefined){i[n]=r}}return i},staticRules:function(t){var n={};var r=e.data(t.form,"validator");if(r.settings.rules){n=e.validator.normalizeRule(r.settings.rules[t.name])||{}}return n},normalizeRules:function(t,n){e.each(t,function(r,i){if(i===false){delete t[r];return}if(i.param||i.depends){var s=true;switch(typeof i.depends){case"string":s=!!e(i.depends,n.form).length;break;case"function":s=i.depends.call(n,n);break}if(s){t[r]=i.param!==undefined?i.param:true}else{delete t[r]}}});e.each(t,function(r,i){t[r]=e.isFunction(i)?i(n):i});e.each(["minlength","maxlength"],function(){if(t[this]){t[this]=Number(t[this])}});e.each(["rangelength","range"],function(){var n;if(t[this]){if(e.isArray(t[this])){t[this]=[Number(t[this][0]),Number(t[this][1])]}else if(typeof t[this]==="string"){n=t[this].split(/[\s,]+/);t[this]=[Number(n[0]),Number(n[1])]}}});if(e.validator.autoCreateRanges){if(t.min&&t.max){t.range=[t.min,t.max];delete t.min;delete t.max}if(t.minlength&&t.maxlength){t.rangelength=[t.minlength,t.maxlength];delete t.minlength;delete t.maxlength}}return t},normalizeRule:function(t){if(typeof t==="string"){var n={};e.each(t.split(/\s/),function(){n[this]=true});t=n}return t},addMethod:function(t,n,r){e.validator.methods[t]=n;e.validator.messages[t]=r!==undefined?r:e.validator.messages[t];if(n.length<3){e.validator.addClassRules(t,e.validator.normalizeRule(t))}},methods:{required:function(t,n,r){if(!this.depend(r,n)){return"dependency-mismatch"}if(n.nodeName.toLowerCase()==="select"){var i=e(n).val();return i&&i.length>0}if(this.checkable(n)){return this.getLength(t,n)>0}return e.trim(t).length>0},email:function(e,t){return this.optional(t)||/^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))$/i.test(e)},url:function(e,t){return this.optional(t)||/^(https?|s?ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(e)},date:function(e,t){return this.optional(t)||!/Invalid|NaN/.test((new Date(e)).toString())},dateISO:function(e,t){return this.optional(t)||/^\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}$/.test(e)},number:function(e,t){return this.optional(t)||/^-?(?:\d+|\d{1,3}(?:,\d{3})+)?(?:\.\d+)?$/.test(e)},digits:function(e,t){return this.optional(t)||/^\d+$/.test(e)},creditcard:function(e,t){if(this.optional(t)){return"dependency-mismatch"}if(/[^0-9 \-]+/.test(e)){return false}var n=0,r=0,i=false;e=e.replace(/\D/g,"");for(var s=e.length-1;s>=0;s--){var o=e.charAt(s);r=parseInt(o,10);if(i){if((r*=2)>9){r-=9}}n+=r;i=!i}return n%10===0},minlength:function(t,n,r){var i=e.isArray(t)?t.length:this.getLength(e.trim(t),n);return this.optional(n)||i>=r},maxlength:function(t,n,r){var i=e.isArray(t)?t.length:this.getLength(e.trim(t),n);return this.optional(n)||i<=r},rangelength:function(t,n,r){var i=e.isArray(t)?t.length:this.getLength(e.trim(t),n);return this.optional(n)||i>=r[0]&&i<=r[1]},min:function(e,t,n){return this.optional(t)||e>=n},max:function(e,t,n){return this.optional(t)||e<=n},range:function(e,t,n){return this.optional(t)||e>=n[0]&&e<=n[1]},equalTo:function(t,n,r){var i=e(r);if(this.settings.onfocusout){i.unbind(".validate-equalTo").bind("blur.validate-equalTo",function(){e(n).valid()})}return t===i.val()},remote:function(t,n,r){if(this.optional(n)){return"dependency-mismatch"}var i=this.previousValue(n);if(!this.settings.messages[n.name]){this.settings.messages[n.name]={}}i.originalMessage=this.settings.messages[n.name].remote;this.settings.messages[n.name].remote=i.message;r=typeof r==="string"&&{url:r}||r;if(i.old===t){return i.valid}i.old=t;var s=this;this.startRequest(n);var o={};o[n.name]=t;e.ajax(e.extend(true,{url:r,mode:"abort",port:"validate"+n.name,dataType:"json",data:o,success:function(r){s.settings.messages[n.name].remote=i.originalMessage;var o=r===true||r==="true";if(o){var u=s.formSubmitted;s.prepareElement(n);s.formSubmitted=u;s.successList.push(n);delete s.invalid[n.name];s.showErrors()}else{var a={};var f=r||s.defaultMessage(n,"remote");a[n.name]=i.message=e.isFunction(f)?f(t):f;s.invalid[n.name]=true;s.showErrors(a)}i.valid=o;s.stopRequest(n,o)}},r));return"pending"}}});e.format=e.validator.format})(jQuery);(function(e){var t={};if(e.ajaxPrefilter){e.ajaxPrefilter(function(e,n,r){var i=e.port;if(e.mode==="abort"){if(t[i]){t[i].abort()}t[i]=r}})}else{var n=e.ajax;e.ajax=function(r){var i=("mode"in r?r:e.ajaxSettings).mode,s=("port"in r?r:e.ajaxSettings).port;if(i==="abort"){if(t[s]){t[s].abort()}t[s]=n.apply(this,arguments);return t[s]}return n.apply(this,arguments)}}})(jQuery);(function(e){e.extend(e.fn,{validateDelegate:function(t,n,r){return this.bind(n,function(n){var i=e(n.target);if(i.is(t)){return r.apply(i,arguments)}})}})})(jQuery)
/* form validation*/
