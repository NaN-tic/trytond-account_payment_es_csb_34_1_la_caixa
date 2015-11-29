#!/usr/bin/env python
# This file is part of the account_payment_es_csb_34_1_la_caixa module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.tests.test_tryton import test_view, test_depends
import trytond.tests.test_tryton
import unittest


class AccountPaymentEsCSB341LaCaixaTestCase(unittest.TestCase):
    '''Test Account Payment ES CSB 34-1 La Caixa module'''

    def setUp(self):
        trytond.tests.test_tryton.install_module(
            'account_payment_es_csb_34_1_la_caixa')

    def test0005views(self):
        'Test views'
        test_view('account_payment_es_csb_34_1_la_caixa')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountPaymentEsCSB341LaCaixaTestCase))
    return suite
