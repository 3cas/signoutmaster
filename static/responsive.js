document.onkeydown = (e) => {
    e=e || window.event

    if (["ArrowUp", "ArrowDown"].includes(e.key)) {
        let selectedIndex = 100
        let options = document.signout.destination

        for (key in options) {
            if (options[key].checked) {
                selectedIndex = key
            }
        }

        if (e.key == "ArrowUp") {
            selectedIndex --
            console.log(selectedIndex)
        } else if (e.key == "ArrowDown") {
            selectedIndex ++
            console.log(selectedIndex)
        }

        if (selectedIndex < 0) {
            selectedIndex = options.length - 1
        } else if (selectedIndex >= options.length) {
            selectedIndex = 0
        }

        let selectedValue = "hamburger"
        for (key in options) {
            if (key == selectedIndex) {
                options[key].checked = true
                selectedValue = options[key].value
            } else {
                options[key].checked = false
            }
        }

        if (selectedValue == "other") {
            document.getElementById("otherval").focus()
        }
    } 
    // else if (e.key == "h") {
    //     let dismiss = document.getElementById("dismiss")
    //     if (dismiss.checked) {
    //         dismiss.checked = false
    //     } else {
    //         dismiss.checked = true
    //     }
    // }
}