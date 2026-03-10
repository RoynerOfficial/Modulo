from odoo import models, fields, api
from odoo.exceptions import UserError
import urllib.parse
from dateutil import parser

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    x_location_latitude = fields.Float(string="Latitud")
    x_location_longitude = fields.Float(string="Longitud")
    x_ultimafecha = fields.Datetime(string="Última actualización")
    x_uniqueid = fields.Char(string="ID del Dispositivo GPS")

    # --- Sobrescribir create ---
    @api.model
    def create(self, vals):
        vehicle = super().create(vals)
        if vehicle.x_uniqueid:
            vehicle._update_position_immediately()
        return vehicle

    # --- Sobrescribir write ---
    def write(self, vals):
        res = super().write(vals)
        if 'x_uniqueid' in vals:
            for veh in self:
                if veh.x_uniqueid:
                    veh._update_position_immediately()
        return res

    # --- Internal function to update position from Traccar ---
    def _update_position_immediately(self):
        if hasattr(self, '_fetch_position_from_traccar_by_uniqueid'):
            pos = self._fetch_position_from_traccar_by_uniqueid(self.x_uniqueid)
            if not pos:
                return
            vals = {}
            if 'latitude' in pos:
                vals['x_location_latitude'] = pos.get('latitude')
            if 'longitude' in pos:
                vals['x_location_longitude'] = pos.get('longitude')
            if 'fixTime' in pos:
                try:
                    dt = parser.isoparse(pos.get('fixTime'))
                    vals['x_ultimafecha'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
            if vals:
                self.sudo().write(vals)

    # Button: View location on Google Maps
    def action_open_google_maps(self):
        self.ensure_one()
        if not self.x_location_latitude or not self.x_location_longitude:
            raise UserError("Este vehículo no tiene coordenadas GPS.")
        url = f"https://www.google.com/maps?q={self.x_location_latitude},{self.x_location_longitude}"
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

    # Button: Copy link to clipboard
    def action_copy_link(self):
        self.ensure_one()
        if not self.x_location_latitude or not self.x_location_longitude:
            raise UserError("Este vehículo no tiene coordenadas GPS.")
        url = f"https://www.google.com/maps?q={self.x_location_latitude},{self.x_location_longitude}"
        return {
            "type": "ir.actions.client",
            "tag": "clipboard_action",
            "params": {
                "text": url,
                "message": f"Link copiado al portapapeles: {url}",
            },
        }

    # Button: Share via WhatsApp
    def action_share_location_whatsapp(self):
        self.ensure_one()
        if not self.x_location_latitude or not self.x_location_longitude:
            raise UserError("Este vehículo no tiene coordenadas GPS.")
        url = f"https://www.google.com/maps?q={self.x_location_latitude},{self.x_location_longitude}"
        message = f"Ubicación del vehículo {self.name}: {url}"
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/?text={encoded_message}"
        return {
            "type": "ir.actions.act_url",
            "url": whatsapp_url,
            "target": "new",
        }

    # Button: Update position now (production)
    def action_update_position_now(self):
        self.ensure_one()
        if not self.x_uniqueid:
            raise UserError("Este vehículo no tiene un ID de dispositivo GPS asignado.")
        self._update_position_immediately()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Sincronización completada",
                "message": f"Ubicación del vehículo {self.name} actualizada correctamente.",
                "type": "success",
                "sticky": False,
            },
        }
