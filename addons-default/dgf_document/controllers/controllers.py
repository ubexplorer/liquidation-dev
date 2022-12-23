# -*- coding: utf-8 -*-
# from odoo import http


# class DgfDocuments(http.Controller):
#     @http.route('/dgf_documents/dgf_documents/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dgf_documents/dgf_documents/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dgf_documents.listing', {
#             'root': '/dgf_documents/dgf_documents',
#             'objects': http.request.env['dgf_documents.dgf_documents'].search([]),
#         })

#     @http.route('/dgf_documents/dgf_documents/objects/<model("dgf_documents.dgf_documents"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dgf_documents.object', {
#             'object': obj
#         })
