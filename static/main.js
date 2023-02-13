var flashes = []

function flash(message, category) {
    let flashes_div = document.getElementById("flashes")
    let flash_div = document.createElement("div")
    let flash_span = document.createElement("span")
    let flash_text = document.createTextNode(message)
    flash_div.append(flash_span)
    flash_span.append(flash_text)
    flash_div.classList.add("flash", category)
    flashes.push(message)
    flashes_div.append(flash_div)
}

function password_check() {
    let check = document.getElementById("check-match")
    let submit = document.getElementById("submit")
    let password_box = document.getElementById("password")
    let password_confirm_box = document.getElementById("password-confirm")

    if (password_box.value == password_confirm_box.value && password_box.value != "") {
        check.innerHTML = "good to go!"
        check.classList = "success"
        submit.disabled = false
    } else {
        check.innerHTML = "does not match"
        check.classList = "error"
        submit.disabled = true
    }
}