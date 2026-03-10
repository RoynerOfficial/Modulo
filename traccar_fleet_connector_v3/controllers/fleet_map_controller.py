from odoo import http
from odoo.http import request
import json

class FleetMapController(http.Controller):

    @http.route('/fleet/map_data', type='http', auth='user', csrf=False)
    def get_vehicle_locations(self, **kwargs):
        """Devuelve la ubicación de todos los vehículos en JSON"""
        vehicles = request.env['fleet.vehicle'].sudo().search([])
        data = []

        for v in vehicles:
            if v.x_location_latitude and v.x_location_longitude:
                try:
                    lat = float(v.x_location_latitude)
                    lon = float(v.x_location_longitude)
                except (ValueError, TypeError):
                    continue
                data.append({
                    'name': v.name or 'Sin nombre',
                    'lat': lat,
                    'lon': lon,
                })

        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )
