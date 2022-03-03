function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
     $("#form-avatar").submit(function (e) {
         // 阻止表单的默认行为
         e.preventDefault()
         $(this).ajaxSubmit({
             url: "/api_1/avatar",
             type: "post",
             dataType: "json",
             headers: {
                 "X-CSRFToken": getCookie("csrf_token")
             },
             success: function (resp) {
                 if (resp.errno == '1'){
                     showSuccessMsg()
                 }
             }
         })
     })

    $("#form-name").submit(function (e) {
        e.preventDefault()
        $(this).ajaxSubmit({
            url: "/api_1/name",
            type: "post",
             dataType: "json",
             headers: {
                 "X-CSRFToken": getCookie("csrf_token")
             },
             success: function (resp) {
                 if (resp.errno == '1') {
                     showSuccessMsg()
                 }
             }
        })
    })
})

