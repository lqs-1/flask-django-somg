// html:页面
// css:美化
// javascript:动作行为

// js读取cookie的方法
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 保存imageID
var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    // 形成图片验证码的链接的后段地址,设置到页面中,让浏览器请求验证码图片
    // 1:生成验证码编号(两种方式:时间戳uuid全局唯一标识符)
    imageCodeId = generateUUID();
    // 设置图片url
    var url = "api/V1.0/image_code/" + imageCodeId
    $(".image-code img").attr("src", url)
}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    var req_date = {
        image_code: imageCode, // 图片验证码的值
        image_code_id: imageCodeId// 图片验证码id
    }
    // 向后端发送请求
    $.get("api/V1.0/sms_code/" + mobile, req_date, function (resp) {
        // resp是后端返回的响应值,把后端的json字符串,转换为js对象
        if (resp.errno == "0") {
            var num = 60;
            // 表示发送成功
            var timer = setInterval(function () {
                if (num > 1) {
                    // 修改倒计时文本
                    $(".phonecode-a").html(num + "秒");
                    num -= 1;
                } else {
                    $(".phonecode-a").html("获取验证码");
                    $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    clearInterval(timer)
                }
            }, 1000, 60)
        } else {
            alert(resp.errmsg);
            $(".phonecode-a").attr("onclick", "sendSMSCode();");
        }
    })





    // $.get("/api/smscode", {mobile:mobile, code:imageCode, codeId:imageCodeId}, 
    //     function(data){
    //         if (0 != data.errno) {
    //             $("#image-code-err span").html(data.errmsg); 
    //             $("#image-code-err").show();
    //             if (2 == data.errno || 3 == data.errno) {
    //                 generateImageCode();
    //             }
    //             $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //         }   
    //         else {
    //             var $time = $(".phonecode-a");
    //             var duration = 60;
    //             var intervalid = setInterval(function(){
    //                 $time.html(duration + "秒"); 
    //                 if(duration === 1){
    //                     clearInterval(intervalid);
    //                     $time.html('获取验证码'); 
    //                     $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //                 }
    //                 duration = duration - 1;
    //             }, 1000, 60); 
    //         }
    // }, 'json'); 
}

$(document).ready(function () {
    generateImageCode();
    $("#mobile").focus(function () {
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function () {
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function () {
        $("#phone-code-err").hide();
    });
    $("#password").focus(function () {
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function () {
        $("#password2-err").hide();
    });

    // 为表单的提交补充自定义的函数行为(事件)
    $(".form-register").submit(function (e) {
        // 阻止浏览器对于表单的默认自动提交
        e.preventDefault();
        //
        var mobile = $("#mobile").val();
        var phoneCode = $("#phonecode").val();
        var passwd = $("#password").val();
        var passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }

        // 调用ajax向后端发送注册请求
        var req_data = {
            mobile: mobile,
            sms_code: phoneCode,
            password: passwd,
            password2: passwd2,
        }

        var req_json = JSON.stringify((req_data))
        $.ajax({
            url: "/api/V1.0/user",
            type: "post",
            data: req_json,
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },  // 请求头,将csrf_token存入
            success: function (resp) {
                if (resp.errno == "0") {
                    // 注册成功,跳转页面
                    location.href = "/login.html"
                } else {
                    alert(resp.errmsg)
                }
            }
        })
    });
})
