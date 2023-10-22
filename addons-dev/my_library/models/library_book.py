# -*- coding: utf-8 -*-
# SOAP Client
import zeep
# SOAP Client

import logging
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
# from odoo.exceptions import UserError
from odoo.tools.translate import _
logger = logging.getLogger(__name__)


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'
    _sql_constraints = [('positive_page', 'CHECK(pages>0)', 'Number of pages must be positive')]
    # ('name_uniq', 'UNIQUE (name)', 'Book title must be unique.'),

    name = fields.Char('Title', required=True)
    short_name = fields.Char('Short Title', required=True)
    category_id = fields.Many2one('library.book.category')
    isbn = fields.Char('ISBN')
    # user_type_id = fields.Many2one('account.account.type', string='Type', required=False)
    author_ids = fields.Many2many('res.partner', string='Authors')
    publisher_id = fields.Many2one(
        'res.partner', string='Publisher',
        ondelete='restrict',  # 'set null',
        context={},
        domain=[],)
    notes = fields.Text('Internal Notes', index=True)
    state = fields.Selection(
        [("draft", "Not Available"), ("available", "Available"), ("borrowed", "Borrowed"), ("lost", "Lost")],
        string="Status",
        required=True,
        copy=False,
        default="draft",
    )
    description = fields.Html('Description')
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date', groups='my_library.group_release_dates')
    # __last_update = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages')
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4))
    cost_price = fields.Float('Book Cost', digits='Book Price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    retail_price = fields.Monetary('Retail Price', currency_field='currency_id')
    pages = fields.Integer('Number of Pages',
                           groups='base.group_user',
                           states={'lost': [('readonly', True)]},
                           help='Total book page count', company_dependent=False)
    active = fields.Boolean(default=True)
    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=True,  # optional
        compute_sudo=True)   # optional
    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        store=False,  # optional
        related_sudo=True,  # optional
        readonly=True)
    publisher_country_code = fields.Char(
        'Publisher Country',
        related='publisher_id.country_id.code',
        store=False,  # optional
        related_sudo=True,  # optional
        readonly=True)
    ref_doc_id = fields.Reference(
        # selection='_referencable_models',
        selection=[("res.users", "User"), ("library.book.category", "Book Category"), ("library.member", "Library Member")],
        string='Reference Document')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')  # total in tree view

    is_public = fields.Boolean(groups='my_library.group_library_librarian')
    private_notes = fields.Text(groups='my_library.group_library_librarian')
    manager_remarks = fields.Text('Manager Remarks')

    old_edition = fields.Many2one('library.book', string='Old Edition')

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                # raise models.ValidationError('Release date must be in the past')
                raise ValidationError('Release date must be in the past')

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([
            ('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    @api.depends('retail_price')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for record in self:
            record.amount_total = record.retail_price * 0.1

    # Override default implementation of name_get(), which uses the _rec_name attribute to find which field holds the data, which is used to generate the display name.
    def name_get(self):
        result = []
        for record in self:
            authors = record.author_ids.mapped('name')
            # rec_name = "{0} ({1})".format(record.name, record.date_release)
            # rec_name = "{0} ({1})".format(record.name, authors)
            rec_name = '%s (%s)' % (record.name, ', '.join(authors))
            result.append((record.id, rec_name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not(name == '' and operator == 'ilike'):
            args += ['|', '|', '|',
                     ('name', operator, name),
                     ('isbn', operator, name),
                     ('author_ids.name', operator, name)]
        return super(LibraryBook, self)._name_search(
            name=name, args=args, operator=operator,
            limit=limit, name_get_uid=name_get_uid)

    def grouped_data(self):
        data = self._get_average_cost()
        logger.info("Groupped Data %s" % data)

    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group([('cost_price', "!=", False)],  # Domain
                                         ['category_id', 'cost_price:avg'],  # Fields to access
                                         ['category_id']  # group_by
                                         )
        return grouped_result

    @api.model
    def _update_book_price(self):
        all_books = self.search([])
        for book in all_books:
            book.cost_price += 10

    @api.model
    def update_book_price(self, category, amount_to_increase):
        category_books = self.search([('category_id', '=', category)])
        for book in category_books:
            book.cost_price += amount_to_increase

###
# Methods
###

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'borrowed'),
                   ('borrowed', 'available'),
                   ('available', 'lost'),
                   ('borrowed', 'lost'),
                   ('lost', 'available')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                # continue
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)

    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

    def log_all_library_members(self):  # Empty  Recordset
        # This is an empty recordset of model library.member
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members)
        for member in all_members:
            print("MEMBER NAME: {0}".format(member.name))
        return True

    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()

    def change_update(self):
        self.ensure_one()
        self.update({
            'date_release': fields.Datetime.now(),
            'notes': 'Updated on {0}'.format(fields.Datetime.now())
        })

    def change_write(self):
        self.ensure_one()
        for record in self:
            record.write({
                'date_release': fields.Datetime.now(),
                'notes': 'Updated by write() method on {0}'.format(fields.Datetime.now())
            })

    def find_book(self):
        domain = ['|', '&',
                  ('name', 'ilike', 'Book Name'),
                  ('category_id.name', 'ilike', 'Category Name'),
                  '&', ('name', 'ilike', 'Book Name 2'),
                  ('category_id.name', 'ilike', 'Category Name 2')]
        books = self.search(domain)
        print(books)

    def find_partner(self):
        PartnerObj = self.env['res.partner']
        domain = ['&',
                  ('name', 'ilike', 'Parth Gajjar'),
                  ('company_id.name', '=', 'Odoo')]
        partner = PartnerObj.search(domain)
        print(partner)

    # Filter recordset
    def filter_books(self):
        all_books = self.search([])
        filtered_books = self.books_with_multiple_authors(all_books)
        logger.info('Filtered Books: %s', filtered_books.mapped('name'))

    # @api.model
    # def books_with_multiple_authors(self, all_books):
    #     def predicate(book):
    #         if len(book.author_ids) > 1:
    #             return True
    #     return all_books.filtered(predicate)

    @api.model
    def books_with_multiple_authors(self, all_books):
        return all_books.filtered(lambda b: len(b.author_ids) > 1)

    # Traversing recordset
    def mapped_books(self):
        all_books = self.search([])
        books_authors = self.get_author_names(all_books)
        logger.info('Books Authors: %s', books_authors)

    @api.model
    def get_author_names(self, all_books):
        return all_books.mapped('author_ids.name')

    # Sorting recordset
    def sort_books(self):
        all_books = self.search([])
        books_sorted = self.sort_books_by_date(all_books)
        books_sorted_reverse = self.sort_books_reverse(all_books)
        logger.info('Books before sorting: %s', all_books)
        logger.info('Books after sorting: %s', books_sorted)
        logger.info('Books after sorting reverse: %s', books_sorted_reverse)

    @api.model
    def sort_books_by_date(self, all_books):
        return all_books.sorted(key='date_release')

    @api.model
    def sort_books_reverse(self, all_books):
        return all_books.sorted(key='date_release', reverse=True)

    @api.model
    def create(self, values):
        if not self.user_has_groups('my_library.group_library_librarian'):
            if 'manager_remarks' in values:
                raise UserError('You are not allowed to modify manager_remarks')
        return super(LibraryBook, self).create(values)

    def write(self, values):
        if not self.user_has_groups('my_library.group_library_librarian'):
            if 'manager_remarks' in values:
                raise UserError('You are not allowed to modify manager_remarks')
        return super(LibraryBook, self).write(values)

    # ---------------------------------------------------------------------#
    #  SOAP Client methods
    def CountriesUsingCurrency(self, currency):
        # CountriesUsingCurrency
        result = None
        if currency is not None:
            wsdl = 'http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL'
            # settings = zeep.Settings(xsd_ignore_sequence_order=True, strict=True)
            client = zeep.Client(wsdl=wsdl)
            result = client.service.CountriesUsingCurrency(sISOCurrencyCode=currency)
            return result

    def ListOfCurrenciesByCode(self):
        wsdl = 'http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL'
        # settings = zeep.Settings(xsd_ignore_sequence_order=True, strict=True)
        client = zeep.Client(wsdl=wsdl)
        result = client.service.ListOfCurrenciesByCode()
        print('Total items of Currencies: {0}'.format(len(result)))
        for item in result:
            print('Currency: {0} ({1})'.format(item.sISOCode, item.sName))
            CountriesCurrency = self.CountriesUsingCurrency(item.sISOCode)
            if CountriesCurrency is not None:
                print('Total items of CountriesUsingCurrency {0}: {1}'.format(item.sISOCode, len(CountriesCurrency)))
                for elem in CountriesCurrency:
                    print('\tCode: {0}, Name: {1}'.format(elem.sISOCode, elem.sName))
    # ---------------------------------------------------------------------#
