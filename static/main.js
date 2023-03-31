const ALLOWED_USERNAME = "abcdefghijklmnopqrstuvwxyz1234567890_-"
const ALLOWED_EMAIL = "abcdefghijklmnopqrstuvwxyz1234567890!#$%&'*+-/=?^_`{|}~@."

var flashes = []
var FLASH_TIMEOUT = 3

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

function deleteFlash(button) {
    let flash_message = button.parentElement.querySelector("span").value
    let index = flashes.indexOf(flash_message)
    if (index > -1) {
        flashes.splice(index, 1)
    }
    button.parentElement.remove()
}

function fadeFlashes() {
    let flashes_div = document.getElementById("flashes")
    let flashes = flashes_div.children
    for (let i = 0; i < flashes.length; i++) {
        flashes[i].classList.add("fade")
        let button = flashes[i].querySelector("button")
        setTimeout(function() {deleteFlash(button)}, FLASH_TIMEOUT*1000)
    }
}

function checkFields() {
    let feedback_email = document.getElementById("feedback-email")
    let feedback_username = document.getElementById("feedback-username")
    let feedback_password_confirm = document.getElementById("feedback-password-confirm")
    let email = document.getElementById("email").value
    let username = document.getElementById("username").value
    let password = document.getElementById("password").value
    let password_confirm = document.getElementById("password-confirm").value
    let submit = document.getElementById("submit")

    let fail_email = null
    for (let char_ind in email) {
        char = email[char_ind].toLowerCase()
        if (!ALLOWED_EMAIL.includes(char)) {
            fail_email = "invalid character(s)"
        }
    }

    if (
        email.indexOf("@") > email.lastIndexOf(".") - 2 ||  // last . appears before @ or missing .
        email.indexOf("@") == -1 ||     // missing @
        email[0] == "@" ||              // @ is first character
        email.slice(-1) == "." ||       // . is first character 
        email.split("@").length > 2     // more than one @
    ) {
        fail_email = "invalid format"
    }

    if (fail_email) {
        feedback_email.innerHTML = fail_email
        feedback_email.classList = "neg"
    } else {
        feedback_email.innerHTML = ""
    }

    let fail_username = false
    for (let char_ind in username) {
        char = username[char_ind].toLowerCase()
        if (!ALLOWED_USERNAME.includes(char)) {
            fail_username = true
        }
    }

    if (fail_username) {
        feedback_username.innerHTML = "invalid character(s)"
        feedback_username.classList = "neg"
    } else {
        feedback_username.innerHTML = ""
    }

    let fail_password = false
    if (password == password_confirm && password != "") {
        feedback_password_confirm.innerHTML = "good to go!"
        feedback_password_confirm.classList = "pos"
        fail_password = false
    } else {
        feedback_password_confirm.innerHTML = "does not match"
        feedback_password_confirm.classList = "neg"
        fail_password = true
    }

    if (fail_email || fail_username || fail_password) {
        submit.disabled = true
    } else {
        submit.disabled = false
    }
}

function copyLink() {
    let remoteLink = document.getElementById("remote-link")
    let link = remoteLink.textContent
    navigator.clipboard.writeText(link)
    let message = document.createTextNode(" *copied!*")
    remoteLink.appendChild(message)
}

fadeFlashes()