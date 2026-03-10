import logging
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil import parser  

_logger = logging.getLogger(__name__)

class TraccarConfig(models.Model):
    _name = 'traccar.config'
    _description = 'Configuración Traccar'
    _rec_name = 'traccar_url'

    traccar_url = fields.Char(string='URL del servidor Traccar', required=True)
    traccar_token = fields.Char(string='API Token de Traccar', required=True)
    active = fields.Boolean(string='Activo', default=True)

    @api.model
    def get_active_config(self):
        """Devuelve la configuración activa de Traccar"""
        return self.search([('active', '=', True)], limit=1)


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def _get_traccar_headers_from_config(self):
        config = self.env['traccar.config'].sudo().get_active_config()
        if not config:
            raise UserError(_('No existe una configuración activa de Traccar.'))
        return config.traccar_url.rstrip('/'), {'Authorization': f'Bearer {config.traccar_token}'}

    def _fetch_position_from_traccar_by_uniqueid(self, uniqueid):
        if not uniqueid:
            return None
        base_url, headers = self._get_traccar_headers_from_config()
        try:
            r = requests.get(f"{base_url}/api/devices?uniqueId={uniqueid}", headers=headers, timeout=10)
            if r.status_code != 200:
                return None
            devices = r.json()
            if not devices:
                return None
            device_id = devices[0].get('id')
            r2 = requests.get(f"{base_url}/api/positions?deviceId={device_id}", headers=headers, timeout=10)
            if r2.status_code == 200 and r2.json():
                return r2.json()[-1]
            return None
        except Exception as e:
            _logger.exception('Error consultando Traccar: %s', e)
            return None

    def update_positions_from_traccar(self):
        """Actualiza las coordenadas en vehículos con x_uniqueid"""
        vehicles = self.search([('x_uniqueid', '!=', False)])
        for veh in vehicles:
            pos = veh._fetch_position_from_traccar_by_uniqueid(veh.x_uniqueid)
            if not pos:
                continue
            vals = {}
            if 'latitude' in pos and hasattr(veh, 'x_location_latitude'):
                vals['x_location_latitude'] = pos.get('latitude')
            if 'longitude' in pos and hasattr(veh, 'x_location_longitude'):
                vals['x_location_longitude'] = pos.get('longitude')
            if 'fixTime' in pos and hasattr(veh, 'x_ultimafecha'):
                try:
                    dt = parser.isoparse(pos.get('fixTime'))
                    vals['x_ultimafecha'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    _logger.exception("Error parseando fixTime: %s", e)
            if vals:
                veh.sudo().write(vals)
