/*
 * Detact Mobile Browser
 */
if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
   $('html').addClass('ismobile');
}
$(window).on('load', function(){
    /* --------------------------------------------------------
        Page Loader
     ---------------------------------------------------------*/
    if(!$('html').hasClass('ismobile')) {
        if($('.preloader')[0]) {
            setTimeout (function () {
                $('.preloader').fadeOut();
            }, 400);

        }

    }
});


function openNav() {
  document.getElementById("mySidenav").style.right = "0";
}

function closeNav() {
  document.getElementById("mySidenav").style.right = "-250px";
}

function resize(){
	var $margin = $("section#spot-light div.container").css("margin-left");
    $("section#our-products div.margin-script").css("margin-left", $margin);

    var $height = $("html body header section#specialize div.container.py-5 div.row.text-center div.col-sm img.img-thumbnail.border-0").css("height");
    $("html body header section#specialize div.container.py-5 div.row.text-center div.col-sm div.d-block").css("height", "70");
      // position aware button hover effet  
    (function() {
      const buttons = document.querySelectorAll(".btn-posnawr");

      buttons.forEach(button => {
        ["mouseenter", "mouseout"].forEach(evt => {
          button.addEventListener(evt, e => {
            let parentOffset = button.getBoundingClientRect(),
                relX = e.pageX - parentOffset.left,
                relY = e.pageY - parentOffset.top;

            const span = button.getElementsByTagName("span");

            span[0].style.top = relY + "px";
            span[0].style.left = relX + "px";
          });
        });
      });
    })();
  // position aware button hover effect

if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
   $('html').addClass('ismobile');
}
$(window).on('load', function(){
    /* --------------------------------------------------------
        Page Loader
     ---------------------------------------------------------*/
    if(!$('html').hasClass('ismobile')) {
        if($('.preloader')[0]) {
            setTimeout (function () {
                $('.preloader').fadeOut();
            }, 400);

        }
    }
});

  // equal card
      function equalCard($selector){
        var h = 0;
        $selector.height('auto');
        $selector.each(function(){
            var height = $(this).height();
            if(height > h){
                h = height;
            }
        });
        $selector.height(h);
    }
    equalCard($('section.trust-us.py-5 div.container div.row.text-center div.col-sm.px-3.py-3'));
    equalCard($('section#product-list.py-5 div.container div.row.mb-5 div.col-4 div.card img'));
    equalCard($('section#specialize div.container.py-5 div.row.text-center div.col-sm.bubble-center div.hover-effect-web img.img-thumbnail.img-fluid.border-0.hover-effect-web.w-50'));
    equalCard($('section#product-list.py-5 div.container div.row.row-cols-1.row-cols-md-3 div.col-sm-4.mb-4 div.card.shadow-sm.bg-white.rounded'));
    equalCard($('section#product-list.py-5 div.container div.row.row-cols-1.row-cols-md-3 div.col-xl-4.mb-4 div.card.shadow.bg-white.rounded'));
    equalCard($('section.trust-us.py-5 div.container div.row.row-cols-1.row-cols-md-3 div.col.py-3.border-bottom'));
    
    // equal card

}

$(document).ready(function(){
    resize();
    var $margin = $("section#spot-light div.container").css("margin-left");
    $("section#our-products div.margin-script").css("margin-left", $margin);

    var $height = $("html body header section#specialize div.container.py-5 div.row.text-center div.col-sm.bubble-center div.hover-effect-web img.img-thumbnail.img-fluid.border-0.hover-effect-web").css("height");
    $("html body header section#specialize div.container.py-5 div.row.text-center div.col-sm div.d-block").css("height", $height);
  
  // position aware button hover effet  
    (function() {
      const buttons = document.querySelectorAll(".btn-posnawr");

      buttons.forEach(button => {
        ["mouseenter", "mouseout"].forEach(evt => {
          button.addEventListener(evt, e => {
            let parentOffset = button.getBoundingClientRect(),
                relX = e.pageX - parentOffset.left,
                relY = e.pageY - parentOffset.top;

            const span = button.getElementsByTagName("span");

            span[0].style.top = relY + "px";
            span[0].style.left = relX + "px";
          });
        });
      });
    })();
  // position aware button hover effect

  // hover bubble

    $('div.hover-effect-app, section#product-list.py-5 div.container div.app').hover(function () {
      $("div.hover-effect-app img.img-thumbnail.border-0.hover-effect-app, section#product-list.py-5 div.container div.app img").css({"background" : "transparent","filter" : "brightness(0) invert(1)"});
    }, function () {
      $("div.hover-effect-app img.img-thumbnail.border-0.hover-effect-app, section#product-list.py-5 div.container div.app img").css({"background" : "#fff", "filter" : "invert(0)"});
    });

    $('div.hover-effect-web, section#product-list.py-5 div.container div.web').hover(function () {
      $("div.hover-effect-web img.img-thumbnail.border-0.hover-effect-web, section#product-list.py-5 div.container div.web img").css({"background" : "transparent","filter" : "brightness(0) invert(1)"});
    }, function () {
      $("div.hover-effect-web img.img-thumbnail.border-0.hover-effect-web, section#product-list.py-5 div.container div.web img").css({"background" : "#fff", "filter" : "invert(0)"});
    });

    $('div.hover-effect-digital, section#product-list.py-5 div.container div.digital').hover(function () {
      $("div.hover-effect-digital img.img-thumbnail.border-0.hover-effect-digital, section#product-list.py-5 div.container div.digital img").css({"background" : "transparent","filter" : "brightness(0) invert(1)"});
    }, function () {
      $("div.hover-effect-digital img.img-thumbnail.border-0.hover-effect-digital, section#product-list.py-5 div.container div.digital img").css({"background" : "#fff", "filter" : "invert(0)"});
    });

    $('div.hover-effect-erp, section#product-list.py-5 div.container div.erp').hover(function () {
      $("div.hover-effect-erp img.img-thumbnail.border-0.hover-effect-erp, section#product-list.py-5 div.container div.erp img").css({"background" : "transparent","filter" : "brightness(0) invert(1)"});
    }, function () {
      $("div.hover-effect-erp img.img-thumbnail.border-0.hover-effect-erp, section#product-list.py-5 div.container div.erp img").css({"background" : "#fff", "filter" : "invert(0)"});
    });

    $('div.hover-effect-tax, section#product-list.py-5 div.container div.tax').hover(function () {
      $("div.hover-effect-tax img.img-thumbnail.border-0.hover-effect-tax, section#product-list.py-5 div.container div.tax img").css({"background" : "transparent","filter" : "brightness(0) invert(1)"});
    }, function () {
      $("div.hover-effect-tax img.img-thumbnail.border-0.hover-effect-tax, section#product-list.py-5 div.container div.tax img").css({"background" : "#fff", "filter" : "invert(0)"});
    });

    $('div.hover-effect-data, section#product-list.py-5 div.container div.data').hover(function () {
      $("div.hover-effect-data img.img-thumbnail.border-0.hover-effect-data, section#product-list.py-5 div.container div.data img").css({"background" : "transparent","filter" : "brightness(0) invert(1)"});
    }, function () {
      $("div.hover-effect-data img.img-thumbnail.border-0.hover-effect-data, section#product-list.py-5 div.container div.data img").css({"background" : "#fff", "filter" : "invert(0)"});
    });

  // hover bubble ends here
  // font hover
    // $('section#specialize div.container.py-5 div.row.text-center div.col-sm.bubble-center div.hover-effect-app').hover(function () {
    //   $("section#specialize div.container.py-5 div.row.text-center div.col-sm.bubble-center h4.app-text").css({"font-size" : "30  px", "transition" : "1s"});
    // }, function () {
    //   $("section#specialize div.container.py-5 div.row.text-center div.col-sm.bubble-center h4.app-text").css({"font-size" : "28px", "transition" : "font-size 1s"});
    // });
    // font hover

});
$(window).resize(function(){
    resize();
});




// originally forked from https://codepen.io/kkick/pen/oWZMov



// $("section#spot-light div.container").css("margin-left")
