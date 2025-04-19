import datetime
import email.utils
from odoo import http, fields
from odoo.http import request


class Main(http.Controller):
    @http.route('/my_library/books', type='http', auth='none')
    def books(self):
        books = request.env['library.book'].sudo().search([])
        html_result = '<html><body><ul>'
        for book in books:
            html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        # return html_result
        return request.make_response(
            html_result, headers=[
                ('Last-modified', email.utils.formatdate(
                    (
                        fields.Datetime.from_string(
                            request.env['library.book'].sudo()
                            .search([], order='write_date desc', limit=1)
                            .write_date) - datetime.datetime(1970, 1, 1)
                    ).total_seconds(),
                    usegmt=True)),
            ])

    @http.route('/my_library/books/json', type='json', auth='none')
    def books_json(self):
        records = request.env['library.book'].sudo().search([])
        return records.read(['name'])
