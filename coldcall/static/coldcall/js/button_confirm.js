// Confirms the action of a button before proceeding
function buttonConfirm(buttonId, formId, confirmMessage) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.addEventListener('click', function() {
            if (confirm(confirmMessage)) {
                document.getElementById(formId).submit();
            }
        });
    }
}