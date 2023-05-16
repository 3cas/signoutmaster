const ALLOWED_EMAIL = "abcdefghijklmnopqrstuvwxyz1234567890!#$%&'*+-/=?^_`{|}~@."

const tooltips = {
    "test": "Hello world!",
    "notlocked": "This button locks the signout panel to only this screen, so that students cannot view the monitor page or change settings on this device. When locked, this device can be used as a signout panel in the classroom. To unlock the panel, the password must be re-entered.",
    "allowother": "This option controls whether you want to display the 'other' option on the student signout screen. This option allows students to enter anything as their reason for leaving class.",
    "allowdismiss": "This option controls whether or not students can sign out for the day. This would be useful for going to the nurse and going home, although it is an optional feature.",
    
}

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
    let feedback_password_confirm = document.getElementById("feedback-password-confirm")
    let email = document.getElementById("email").value
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
        email.slice(-1) == "." ||       // . is last character 
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

    if (fail_email || fail_password) {
        submit.disabled = true
    } else {
        submit.disabled = false
    }
}

function copyLink() {
    let remoteLink = document.getElementById("remote-link")
    let link = remoteLink.textContent
    navigator.clipboard.writeText(link)
    let button = document.getElementById("copier")
    button.textContent = "Copied!"
    setTimeout(function () { button.textContent = "Copy Link" }, 1000)
}

function showInfo(key) {
    let info = tooltips[key]
    if (info) {
        alert(info)
    } else {
        alert("Error: Tooltip not found")
    }
}

fadeFlashes()