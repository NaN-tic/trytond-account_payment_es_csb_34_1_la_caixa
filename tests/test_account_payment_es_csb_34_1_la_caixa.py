# This file is part of the account_payment_es_csb_34_1_la_caixa module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountPaymentEsCsb341LaCaixaTestCase(ModuleTestCase):
    'Test Account Payment Es Csb 34 1 La Caixa module'
    module = 'account_payment_es_csb_34_1_la_caixa'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountPaymentEsCsb341LaCaixaTestCase))
    return suite