# -*- coding: utf-8 -*-
"""
    Test User

    :copyright: (c) 2015 by Fulfil.IO Inc.
    :license: BSD, see LICENSE for more details.
"""
from decimal import Decimal
import unittest

import trytond.tests.test_tryton
from nereid.testing import NereidTestCase
from trytond.tests.test_tryton import activate_module, USER, with_transaction
from trytond.pool import Pool
from trytond.exceptions import UserError


class TestUser(NereidTestCase):
    """
    Test User
    """

    def setUp(self):
        activate_module('nereid')

    def setup_defaults(self):
        """
        Setup the defaults
        """
        self.nereid_website_obj = Pool().get('nereid.website')
        self.nereid_website_locale_obj = Pool().get('nereid.website.locale')
        self.nereid_permission_obj = Pool().get('nereid.permission')
        self.nereid_user_obj = Pool().get('nereid.user')
        self.company_obj = Pool().get('company.company')
        self.currency_obj = Pool().get('currency.currency')
        self.language_obj = Pool().get('ir.lang')
        self.party_obj = Pool().get('party.party')
        self.Country = Pool().get('country.country')
        self.Subdivision = Pool().get('country.subdivision')

        usd, = self.currency_obj.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
            'rates': [('create', [{'rate': Decimal('1')}])],
        }])
        eur, = self.currency_obj.create([{
            'name': 'Euro',
            'code': 'EUR',
            'symbol': 'E',
            'rates': [('create', [{'rate': Decimal('2')}])],
        }])
        self.party, = self.party_obj.create([{
            'name': 'Openlabs',
        }])
        self.company, = self.company_obj.create([{
            'currency': usd,
            'party': self.party,
        }])
        c1, = self.currency_obj.create([{
            'code': 'C1',
            'symbol': 'C1',
            'name': 'Currency 1',
            'rates': [('create', [{'rate': Decimal('10')}])],

        }])
        c2, = self.currency_obj.create([{
            'code': 'C2',
            'symbol': 'C2',
            'name': 'Currency 2',
            'rates': [('create', [{'rate': Decimal('20')}])],
        }])
        self.lang_currency, = self.currency_obj.create([{
            'code': 'C3',
            'symbol': 'C3',
            'name': 'Currency 3',
            'rates': [('create', [{'rate': Decimal('30')}])],
        }])
        self.currency_obj.create([{
            'code': 'C4',
            'symbol': 'C4',
            'name': 'Currency 4',
            'rates': [('create', [{'rate': Decimal('40')}])],
        }])
        self.website_currencies = [c1, c2]
        self.en_us, = self.language_obj.search([('code', '=', 'en')])
        self.es_es, = self.language_obj.search([('code', '=', 'es')])
        self.usd, = self.currency_obj.search([('code', '=', 'USD')])
        self.eur, = self.currency_obj.search([('code', '=', 'EUR')])
        locale_en_us, locale_es_es = self.nereid_website_locale_obj.create([{
            'code': 'en_US',
            'language': self.en_us,
            'currency': self.usd,
        }, {
            'code': 'es_ES',
            'language': self.es_es,
            'currency': self.eur,
        }])
        self.nereid_website_obj.create([{
            'name': 'localhost',
            'company': self.company,
            'application_user': USER,
            'default_locale': locale_en_us.id,
            'currencies': [('add', self.website_currencies)],
        }])
        self.templates = {
            'home.jinja': '{{ "hell" }}',
        }

    @with_transaction()
    def test_0010_user(self):
        "Test for User display_name deprecated field"
        self.setup_defaults()

        user, = self.nereid_user_obj.create([{
            "display_name": "Fulfil.io",
            "party": self.party.id,
            "company": self.company.id,
        }])
        assert user.name == "Fulfil.io"
        assert user.display_name == "Fulfil.io"

        search_result, = self.nereid_user_obj.search([
            ('display_name', '=', 'Fulfil.io'),
        ])
        assert search_result == user

    @with_transaction()
    def test_0020_user_email_case_sensitive(self):
        """Backend user should not be allowed to create user with case
        sensitive emails
        """
        self.setup_defaults()

        user, = self.nereid_user_obj.create([{
            "display_name": "Fulfil.io",
            "email": "pp@fulfil.io",
            "party": self.party.id,
            "company": self.company.id,
        }])

        # Try create a new user with same email but in upper case
        with self.assertRaises(UserError):
            user, = self.nereid_user_obj.create([{
                "display_name": "Fulfil.io",
                "email": "PP@FULFIL.IO",
                "party": self.party.id,
                "company": self.company.id,
            }])


def suite():
    "Nereid test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestUser)
    )
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
