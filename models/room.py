from odoo import fields, models

class SchoolRoom(models.Model):
    _name = 'school.room'
    _description = 'School Room'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Room Name')
    floor = fields.Integer(string='Floor')
    building = fields.Char(string='Building')
    capacity = fields.Integer(string='Capacity')
    room_type_id = fields.Many2one("school.room.type",string='Room Type')
    status = fields.Selection([
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
        ('inactive', 'Inactive')
    ], default='available', string="Status")
    description = fields.Char(string='Description')

    def action_open_room_type_modal(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Room Type',
            'res_model': 'school.room.type',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_available(self):
        self.write({'status': 'available'})

    def action_reserved(self):
        self.write({'status': 'reserved'})

    def action_occupied(self):
        self.write({'status': 'occupied'})

    def action_maintenance(self):
        self.write({'status': 'maintenance'})

    def action_inactive(self):
        self.write({'status': 'inactive'})

    def action_reset(self):
        self.write({'status': 'available'})

class RoomType(models.Model):
    _name = 'school.room.type'
    _description = 'School Room Type'

    name = fields.Char(required=True)
    description = fields.Char(string='Description')

    room_ids = fields.One2many(
        'school.room',
        'room_type_id',
        string="Rooms"
    )