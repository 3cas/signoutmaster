const ALLOWED_USERNAME = "abcdefghijklmnopqrstuvwxyz1234567890_-"
const ALLOWED_EMAIL = "abcdefghijklmnopqrstuvwxyz1234567890_-@+~."

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

function check_email() {
    let check = document.getElementById("check-email")
    let submit = document.getElementById("submit")
    let email_box = document.getElementById("email")
    
    let errors = 0
    for (let char in email_box.value) {
        char = char.toLowerCase()
        console.log("debug: char in email")
        if (!ALLOWED_EMAIL.includes(char)) {
            errors ++
            console.log(errors)
        }
    }

    if (errors > 0) {
        check.innerHTML = "invalid format"
        check.classList = "error"
        submit.disabled = true
    } else {
        check.innerHTML = ""
        submit.disabled = false
    }
}

function check_username() {
    let check = document.getElementById("check-username")
    let submit = document.getElementById("submit")
    let username_box = document.getElementById("username")

    let errors = 0
    for (let char in username_box.value) {
        char = char.toLowerCase()
        console.log("debug: char in username")
        if (!ALLOWED_USERNAME.includes(char)) {
            errors++
            console.log(errors)
        }
    }

    if (errors > 0) {
        check.innerHTML = "invalid format"
        check.classList = "error"
        submit.disabled = true
    } else {
        check.innerHTML = ""
        submit.disabled = false
    }
}

function check_password() {
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