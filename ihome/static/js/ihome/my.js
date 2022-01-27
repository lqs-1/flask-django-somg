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
})