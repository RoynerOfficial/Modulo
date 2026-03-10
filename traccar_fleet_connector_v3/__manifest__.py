{
    "name": "Traccar GPS Connector for Fleet",
    "version": "16.0.1.0.0",
    "license": "OPL-1",
    "summary": "Connect Traccar GPS server with Odoo Fleet vehicles",
    "description": """
Integrates Traccar GPS tracking server with Odoo Fleet.

Main Features:
- Synchronize GPS coordinates from Traccar
- Store latitude and longitude in Fleet vehicles
- Open vehicle location directly in Google Maps
- Copy GPS tracking link
- Share vehicle location via WhatsApp
""",
    "author": "Royner Perez, Reynaldo Perez Cuantico SURL",
    "website": "https://github.com/RoynerOfficial/OdooTraccar",
    "category": "Fleet",
    "license": "OPL-1",
    "price": 49.00,
    "currency": "USD",
    "depends": ["fleet"],

    "data": [
        "security/ir.model.access.csv",
        "views/traccar_config_views.xml",
        "views/cron_data.xml",
        "views/website_fleet_map.xml",
        "views/fleet_vehicle_traccar_views.xml",
    ],

    "assets": {
        "web.assets_backend": [
            "traccar_fleet_connector_v3/static/src/js/clipboard_action.js"
        ]
    },

    "images": [
        "static/description/banner.png"
    ],

    "installable": True,
    "application": False,

}
