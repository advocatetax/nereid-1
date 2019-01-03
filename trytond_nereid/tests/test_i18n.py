#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

    Test the Internationalisation

    :copyright: (c) 2012-2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details.
"""
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import activate_module, USER, with_transaction
from trytond.pool import Pool
from nereid.testing import NereidTestCase
from nereid import render_template
from trytond.transaction import Transaction
from nereid.contrib.locale import make_lazy_gettext, make_lazy_ngettext

_ = make_lazy_gettext('nereid')
ngettext = make_lazy_ngettext('nereid')


class TestI18N(NereidTestCase):
    """
    Test the internationalisation
    """

    def setUp(self):
        activate_module('nereid_test')

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

        usd, eur = self.currency_obj.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }, {
            'name': 'Euro',
            'code': 'EUR',
            'symbol': '€',
        }])
        self.party, = self.party_obj.create([{
            'name': 'Openlabs',
        }])
        self.company, = self.company_obj.create([{
            'party': self.party,
            'currency': usd,
        }])
        en_us, = self.language_obj.search([('code', '=', 'en')])
        fr_fr, = self.language_obj.search([('code', '=', 'fr')])
        usd, = self.currency_obj.search([('code', '=', 'USD')])
        locale, = self.nereid_website_locale_obj.create([{
            'code': 'en_US',
            'language': en_us,
            'currency': usd,
        }])
        locale_fr_FR, = self.nereid_website_locale_obj.create([{
            'code': 'fr_FR',
            'language': fr_fr,
            'currency': eur,
        }])
        self.nereid_website_obj.create([{
            'name': 'localhost',
            'company': self.company.id,
            'application_user': USER,
            'default_locale': locale,
            'locales': [('add', [locale.id, locale_fr_FR.id])],
        }])

    def set_translations(self):
        """
        Sets the translations
        """
        TranslationSet = Pool().get('ir.translation.set', type='wizard')

        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)
        set_wizard.transition_set_()

    def update_translations(self, language_code):
        """
        Update the translations for the language
        """
        TranslationUpdate = Pool().get('ir.translation.update', type='wizard')
        IRLanguage = Pool().get('ir.lang')

        session_id, _, _ = TranslationUpdate.create()
        update_wizard = TranslationUpdate(session_id)

        # set fr_FR  as translatable
        language, = IRLanguage.search([
            ('code', '=', language_code)
        ], limit=1)
        language.translatable = True
        language.save()

        update_wizard.start.language = language
        update_wizard.do_update(update_wizard.update.get_action())

    def get_template_source(self, name):
        """
        Return templates
        """
        templates = {
            'home.jinja': '{{get_flashed_messages()}}',
        }
        return templates.get(name)

    @with_transaction()
    def test_0010_simple_txn(self):
        """
        Test if the translations work in a simple env
        """
        IRTranslation = Pool().get('ir.translation')

        s = _("en_US")
        self.assertEqual(s, 'en_US')

        # install translations
        self.set_translations()
        self.update_translations('fr')

        # without setting a tranlsation looking for it gives en_US
        with Transaction().set_context(language="fr"):
            self.assertEqual(s, 'en_US')

        # write a translation for it
        translation, = IRTranslation.search([
            ('module', '=', 'nereid'),
            ('src', '=', 'en_US'),
            ('lang', '=', 'fr')
        ])
        translation.value = 'fr'
        translation.save()

        with Transaction().set_context(language="fr"):
            self.assertEqual(s, 'fr')

    @with_transaction()
    def test_0020_kwargs(self):
        """
        Test if kwargs work
        """
        IRTranslation = Pool().get('ir.translation')

        s = _("Hi %(name)s", name="Sharoon")
        self.assertEqual(s, "Hi Sharoon")

        # install translations
        self.set_translations()
        self.update_translations('fr')

        # without setting a tranlsation looking for it gives en_US
        with Transaction().set_context(language="fr"):
            self.assertEqual(s, 'Hi Sharoon')

        # write a translation for it
        translation, = IRTranslation.search([
            ('module', '=', 'nereid'),
            ('src', '=', 'Hi %(name)s'),
            ('lang', '=', 'fr')
        ])
        translation.value = 'Bonjour %(name)s'
        translation.save()

        with Transaction().set_context(language="fr"):
            self.assertEqual(s, 'Bonjour Sharoon')

    @with_transaction()
    def test_0030_ngettext(self):
        """
        Test if ngettext work
        """
        IRTranslation = Pool().get('ir.translation')

        singular = ngettext("%(num)d apple", "%(num)d apples", 1)
        plural = ngettext("%(num)d apple", "%(num)d apples", 2)

        self.assertEqual(singular, "1 apple")
        self.assertEqual(plural, "2 apples")

        # install translations
        self.set_translations()
        self.update_translations('fr')

        # without setting a tranlsation looking for it gives en_US
        with Transaction().set_context(language="fr"):
            self.assertEqual(singular, "1 apple")
            self.assertEqual(plural, "2 apples")

        # write a translation for singular
        translations = IRTranslation.search([
            ('module', '=', 'nereid'),
            ('src', '=', '%(num)d apple'),
            ('lang', '=', 'fr')
        ])
        for translation in translations:
            translation.value = '%(num)d pomme'
            translation.save()

        # write a translation for it
        translations = IRTranslation.search([
            ('module', '=', 'nereid'),
            ('src', '=', '%(num)d apples'),
            ('lang', '=', 'fr')
        ])
        for translation in translations:
            translation.value = '%(num)d pommes'
            translation.save()

        with Transaction().set_context(language="fr"):
            self.assertEqual(singular, "1 pomme")
            self.assertEqual(plural, "2 pommes")

    @with_transaction()
    def test_0110_template(self):
        """
        Test the working of translations in templates
        """
        IRTranslation = Pool().get('ir.translation')

        self.setup_defaults()
        app = self.get_app()

        class User(object):
            def __init__(self, username):
                self.username = username

            def __html__(self):
                return self.username

        user = User('Sharoon')

        template_context = {
            'user': user,
            'username': user.username,
            'list': [1],
            'objname': _('name'),
            'apples': [1, 2],
        }

        def check_en_us(rv):
            self.assertTrue('There is 1 name object.' in rv)
            self.assertTrue('2 apples' in rv)
            self.assertTrue('<p>Hello Sharoon!</p>' in rv)

        def check_fr_fr(rv):
            self.assertTrue('There is 1 name in fr object.' in rv)
            self.assertTrue('2 pommes' in rv)
            self.assertTrue('<p>Bonjour Sharoon!</p>' in rv)

        with app.test_request_context('/en_US/'):
            rv = str(render_template(
                'tests/translation-test.html',
                **template_context
            ))
            check_en_us(rv)

            with Transaction().set_context(language="fr"):
                # No translations set yet, so same thing
                rv = str(render_template(
                    'tests/translation-test.html',
                    **template_context
                ))
                check_en_us(rv)

        # install translations
        self.set_translations()
        self.update_translations('fr')

        # write french translations
        translation, = IRTranslation.search([
            ('module', '=', 'nereid_test'),
            ('type', '=', 'nereid_template'),
            ('src', '=', 'Hello %(username)s!'),
            ('lang', '=', 'fr')
        ])
        translation.value = 'Bonjour %(username)s!'
        translation.save()

        translation, = IRTranslation.search([
            ('module', '=', 'nereid_test'),
            ('type', '=', 'nereid_template'),
            ('src', '=', '%(num)d apples'),
            ('lang', '=', 'fr')
        ])
        translation.value = '%(num)d pommes'
        translation.save()

        translation, = IRTranslation.search([
            ('module', '=', 'nereid_test'),
            ('type', '=', 'nereid_template'),
            ('src', '=', 'Hello %(name)s!'),
            ('lang', '=', 'fr')
        ])
        translation.value = 'Bonjour %(name)s!'
        translation.save()

        translation, = IRTranslation.search([
            ('module', '=', 'nereid'),
            ('name', '=', 'tests/test_i18n.py'),
            ('src', '=', 'name'),
            ('lang', '=', 'fr')
        ])
        translation.value = 'name in fr'
        translation.save()

        with app.test_request_context('/fr/'):
            with Transaction().set_context(language="fr"):
                rv = str(render_template(
                    'tests/translation-test.html',
                    **template_context
                ))
                check_fr_fr(rv)


def suite():
    "Nereid test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestI18N)
    )
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
