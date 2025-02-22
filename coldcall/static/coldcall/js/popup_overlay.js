window.onload = function() {
    // user onboarding popups
    const close_init = document.getElementById("close-init");
    const init = document.getElementById("init-popup");

    close_init.addEventListener("click", () => {
        init.classList.remove("visible");
        console.log("a")
    });
}