function set_cookies() {
    const elements = document.getElementsByClassName("dropdown_ioc");
    let cookiestring = "";
    for (const element of elements) {
        if (element.checked) {
            cookiestring += element.value + ",";
        }
    }
    document.cookie = "indicator_pattern=" + cookiestring;
}

function init() {
    const cookie = document.cookie;
    const cookie_split = cookie.split(";");

    let cookie_value = null;
    for (const split of cookie_split) {
        if (split.startsWith("indicator_pattern=")) {
            cookie_value = split.split("indicator_pattern=")[1];
        }
    }

    if (cookie_value == null) {
        const elements = document.getElementsByClassName("dropdown_ioc");
        for (const element of elements) {
            element.checked = true;
        }
        set_cookies();
    } else {
        const values = cookie_value.split(",");
        for (const element of document.getElementsByClassName("dropdown_ioc")) {
            if (values.includes(element.value)) {
                element.checked = true;
            }
        }
    }
}

init()