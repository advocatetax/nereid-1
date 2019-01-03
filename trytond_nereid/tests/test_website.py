# This file is part of Tryton & Nereid. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import unittest
import json

import trytond.tests.test_tryton
from trytond.tests.test_tryton import activate_module, USER, with_transaction
from trytond.pool import Pool
from nereid.testing import NereidTestCase


class TestWebsite(NereidTestCase):
    'Test Website'

    def setUp(self):
        activate_module('nereid')

    def setup_defaults(self):
        """
        Setup the defaults
        """
        self.NereidWebsite = Pool().get('nereid.website')
        self.NereidWebsiteLocale = Pool().get('nereid.website.locale')
        self.NereidPermission = Pool().get('nereid.permission')
        self.NereidUser = Pool().get('nereid.user')
        self.Company = Pool().get('company.company')
        self.Currency = Pool().get('currency.currency')
        self.Language = Pool().get('ir.lang')
        self.Party = Pool().get('party.party')

        usd, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])
        self.party, = self.Party.create([{
            'name': 'Openlabs',
        }])
        self.company, = self.Company.create([{
            'party': self.party,
            'currency': usd,
        }])

        en_us, = self.Language.search([('code', '=', 'en')])
        currency, = self.Currency.search([('code', '=', 'USD')])
        locale, = self.NereidWebsiteLocale.create([{
            'code': 'en_US',
            'language': en_us,
            'currency': currency,
        }])
        self.NereidWebsite.create([{
            'name': 'localhost',
            'company': self.company,
            'application_user': USER,
            'default_locale': locale,
        }])

    @with_transaction()
    def test_0010_user_status(self):
        """
        Test that user status returns jsonified object on POST
        request.
        """
        self.setup_defaults()
        app = self.get_app()

        with app.test_client() as c:
            rv = c.get('/user_status')
            self.assertEqual(rv.status_code, 200)

            rv = c.post('/user_status')
            data = json.loads(rv.data)

            self.assertEqual(data['status']['logged_id'], False)
            self.assertEqual(data['status']['messages'], [])


def suite():
    "Nereid test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestWebsite)
    )
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
