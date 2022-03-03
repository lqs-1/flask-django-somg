function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
function logout() {
   $.ajax({
        url: "/api_1/session",
        type: "delete",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        dataType: "json",
        success: function (resp) {
            if ("1" == resp.errno) {
                location.href = "/index.html";
            }
        }
    });
}

$(document).ready(function(){
    $.get('/api_1/user', function (resp) {
        if (resp.errno == '1'){
            $("#user-name").html(resp.data.name);
            $("#user-mobile").html(resp.data.mobile);
            if (resp.data.avatar) {
                $("#user-avatar").attr("src", resp.data.avatar);
            }
        }

    })



})