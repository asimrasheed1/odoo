from odoo import http
from odoo.http import request

class BajFbrPosConnectController(http.Controller):
    @http.route('/asmite_fbr_pos_connect/hello', type='http', auth='public', website=True)
    def hello_view(self, **kwargs):
        return request.render('asmite_fbr_pos_connect.hello_template', {})
