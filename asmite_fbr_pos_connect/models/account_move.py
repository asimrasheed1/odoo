from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    x_fbr_inv = fields.Char(string="FBR Invoice")
