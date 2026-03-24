jQuery(document).ready(function() {
    if (jQuery("#bTouchUi").length) {
        return;
    }

    const button = jQuery(
        '<button id="bTouchUi" class="plugins" title="Touch UI">Touch UI</button>'
    );

    button.on("click", function() {
        window.location = "/touch-ui";
    });

    if (jQuery("#bRunOnce").length) {
        jQuery("#bRunOnce").after(button);
        return;
    }

    if (jQuery("#nav").length) {
        jQuery("#nav").append(button);
    }
});
