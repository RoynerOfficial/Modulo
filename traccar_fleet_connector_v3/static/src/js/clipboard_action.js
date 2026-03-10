odoo.define('traccar_fleet_connector.clipboard_action', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    core.action_registry.add('clipboard_action', AbstractAction.extend({
        init: function (parent, action) {
            this._super(parent, action);
            if (action.params && action.params.text) {
                navigator.clipboard.writeText(action.params.text)
                    .then(() => {
                        alert(action.params.message || "Texto copiado al portapapeles.");
                    });
            }
        },
    }));
});