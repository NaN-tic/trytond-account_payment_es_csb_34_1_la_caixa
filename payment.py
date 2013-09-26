# This file is part of account_payment_es_csb_34_1_la_caixa module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
import logging
try:
    from retrofix import Record, write, c34_1_la_caixa as c34_1_lc
except ImportError:
    message = ('Unable to import retrofix library.\n'
               'Please install it before install this module.')
    logging.getLogger('account_payment_es_csb_34_1_la_caixa').error(message)
    raise Exception(message)

__all__ = [
    'Journal',
    'Group',
    ]
__metaclass__ = PoolMeta


class Journal:
    __name__ = 'account.payment.journal'
    csb34_11_lc_type = fields.Selection([
            ('transfer', 'Transfers'),
            ('check', 'Checks'),
            ('promissory_note', 'Promissory Notes'),
            ('certified_payment', 'Certified Payments'),
            ], 'Type of CSB 34 payment')
    csb34_11_lc_text1 = fields.Char('Line 1', help=(u'Enter text and/or '
            'select a field of the invoice to include as a description in the '
            'letter. Allowed values are: ${name}, ${bank_account}, '
            '${invoices}, ${amount}, ${communication}, ${date}, '
            '${maturity_date}, ${create_date}, ${date_created}, ${concept}.'))
    csb34_11_lc_text2 = fields.Char('Line 2', help=(u'Enter text and/or '
            'select a field of the invoice to include as a description in the '
            'letter. Allowed values are: ${name}, ${bank_account}, '
            '${invoices}, ${amount}, ${communication}, ${date}, '
            '${maturity_date}, ${create_date}, ${date_created}, ${concept}.'))
    csb34_11_lc_text3 = fields.Char('Line 3', help=(u'Enter text and/or '
            'select a field of the invoice to include as a description in the '
            'letter. Allowed values are: ${name}, ${bank_account}, '
            '${invoices}, ${amount}, ${communication}, ${date}, '
            '${maturity_date}, ${create_date}, ${date_created}, ${concept}.'))
    csb34_11_lc_add_date = fields.Boolean('Add Date', help=('Check it if you '
            'want to add the 910 data type in the file to include the payment '
            'date.'))

    @classmethod
    def __setup__(cls):
        super(Journal, cls).__setup__()
        if ('csb34_1_lc', 'CSB 34-1 La Caixa') not in cls.process_method.selection:
            cls.process_method.selection.extend([
                    ('csb34_1_lc', 'CSB 34-1 La Caixa'),
                    ])
        cls._error_messages.update({
                'dear_sir': ('Dear Sir'),
                'payement_ref': ('Payment ref.'),
                'total': ('Total:'),
                })

    @staticmethod
    def default_csb34_11_lc_type():
        return 'transfer'

    @staticmethod
    def default_csb34_11_lc_not_to_the_order():
        return True

    @staticmethod
    def default_csb34_11_lc_barred():
        return True

    @classmethod
    def default_csb34_11_lc_text1(cls):
        return '%s %s' % (cls.raise_user_error('dear_sir',
            raise_exception=False), ' ${name},')

    @classmethod
    def default_csb34_11_lc_text2(cls):
        return '%s %s' % (cls.raise_user_error('payement_ref',
            raise_exception=False), ' ${communication}')

    @classmethod
    def default_csb34_11_lc_text3(cls):
        return '%s %s' % (cls.raise_user_error('total',
            raise_exception=False), ' ${amount}')

    @staticmethod
    def default_csb34_11_lc_add_date():
        return True


class Group:
    __name__ = 'account.payment.group'

    def map_message(self, receipt, message=''):
        """
        Evaluates an expression and returns its value
        @param recibo: Order line data
        @param message: The expression to be evaluated
        @return: Computed message (string)
        """
        for field in receipt.iterkeys():
            value = str(receipt[field]).decode('utf-8')
            message = message.replace('${' + field + '}', value)
        return message

    def set_devault_csb34_1_lc_payment_values(self):
        values = self.set_default_csb34_payment_values()
        values['add_date'] = values['payment_journal'].csb34_11_lc_add_date
        values['csb34_11_lc_type'] = values['payment_journal'].csb34_11_lc_type
        for receipt in values['receipts']:
            if values['csb34_11_lc_type'] != 'transfer':
                receipt['bank_account'] = ''.zfill(17)
                if values['send_type'] == 'mail':
                    receipt['bank_account'] += '1'
                elif values['send_type'] == 'certified_mail':
                    receipt['bank_account'] += '2'
                else:
                    receipt['bank_account'] += '3'
                if values['not_to_the_order']:
                    receipt['bank_account'] += '1'
                else:
                    receipt['bank_account'] += '0'
                if values['barred']:
                    receipt['bank_account'] += '9'
                else:
                    receipt['bank_account'] += '0'
            receipt['message_101'] = self.map_message(receipt,
                    values['payment_journal'].csb34_11_lc_text1)
            receipt['message_102'] = self.map_message(receipt,
                    values['payment_journal'].csb34_11_lc_text2)
            receipt['message_103'] = self.map_message(receipt,
                    values['payment_journal'].csb34_11_lc_text3)
            if values['add_date']:
                (year, month, day) = str(values['payment_date']).split('-')
                receipt['date'] = day + month + year
        return values

    @classmethod
    def process_csb34_1_lc(cls, group):
        def set_ordering_header_record():
            record = Record(c34_1_lc.ORDERING_HEADER_RECORD)
            record.record_code = '03'
            record.operation_code = '62'
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.data_number = '001'
            record.send_date = values['payment_date']
            record.creation_date = values['creation_date']
            record.account = values['bank_account']
            record.charge_detail = 'false'  # or 'true'
            return write([record])

        def set_ordering_header_002_record():
            record = Record(c34_1_lc.ORDERING_HEADER_002_RECORD)
            record.record_code = '03'
            record.operation_code = '62'
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.data_number = '002'
            record.name = values['name']
            return write([record])

        def set_ordering_header_003_record():
            record = Record(c34_1_lc.ORDERING_HEADER_003_RECORD)
            record.record_code = '03'
            record.operation_code = '62'
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.data_number = '003'
            record.address = values['street']
            return write([record])

        def set_ordering_header_004_record():
            record = Record(c34_1_lc.ORDERING_HEADER_004_RECORD)
            record.record_code = '03'
            record.operation_code = '62'
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.data_number = '004'
            record.city = values['city']
            return write([record])

        def set_national_header_record():
            record = Record(c34_1_lc.NATIONAL_HEADER_RECORD)
            record.record_code = '04'
            record.operation_code = '56'
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            return write([record])

        def set_detail_001_record():
            record = Record(c34_1_lc.DETAIL_001_RECORD)
            record.record_code = '06'
            record.operation_code = values['csb34_11_lc_type']
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.recipient_nif = receipt['vat_number']
            record.data_number = '010'
            record.amount = receipt['amount']
            record.bank_account = receipt['bank_account']  # receipt['data']
            record.cost = receipt['cost']
            record.concept = receipt['concept']
            record.direct_payment = receipt['direct_payment']
            return write([record])

        def set_detail_002_record():
            record = Record(c34_1_lc.DETAIL_002_RECORD)
            record.record_code = '06'
            record.operation_code = values['csb34_11_lc_type']
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.recipient_nif = receipt['vat_number']
            record.data_number = '011'
            record.name = receipt['name']
            return write([record])

        def set_detail_003_record():
            record = Record(c34_1_lc.DETAIL_003_RECORD)
            record.record_code = '06'
            record.operation_code = values['csb34_11_lc_type']
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.recipient_nif = receipt['vat_number']
            record.data_number = '012'
            record.street = receipt['street']
            return write([record])

        def set_detail_004_record():
            record = Record(c34_1_lc.DETAIL_004_RECORD)
            record.record_code = '06'
            record.operation_code = values['csb34_11_lc_type']
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.recipient_nif = receipt['vat_number']
            record.data_number = '013'
            record.street2 = receipt['street2']
            return write([record])

        def set_detail_005_record():
            record = Record(c34_1_lc.DETAIL_005_RECORD)
            record.record_code = '06'
            record.operation_code = values['csb34_11_lc_type']
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.recipient_nif = receipt['vat_number']
            record.data_number = '014'
            record.zip_city = '%s%s' % (receipt['zip'], receipt['city'])
            return write([record])

        def set_detail_006_record():
            record = Record(c34_1_lc.DETAIL_006_RECORD)
            record.record_code = '06'
            record.operation_code = values['csb34_11_lc_type']
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.recipient_nif = receipt['vat_number']
            record.data_number = '015'
            record.country_code = receipt['country_code']
            record.state = receipt['state']
            return write([record])

        def set_detail_007_record():
            record = Record(c34_1_lc.DETAIL_007_RECORD)
            record.record_code = '06'
            record.operation_code = values['csb34_11_lc_type']
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.recipient_nif = receipt['vat_number']
            record.data_number = '016'
            record.concept = receipt['concept']
            return write([record])

        def set_detail_101_record():
            record = Record(c34_1_lc.DETAIL_101_RECORD)
            record.record_code = '06'
            record.operation_code = values['csb34_11_lc_type']
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.recipient_nif = receipt['vat_number']
            record.data_number = '101'
            record.message = receipt['message_101']
            return write([record])

        def set_detail_102_record():
            record = Record(c34_1_lc.DETAIL_102_RECORD)
            record.record_code = '06'
            record.operation_code = values['csb34_11_lc_type']
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.recipient_nif = receipt['vat_number']
            record.data_number = '102'
            record.message = receipt['message_102']
            return write([record])

        def set_detail_103_record():
            record = Record(c34_1_lc.DETAIL_103_RECORD)
            record.record_code = '06'
            record.operation_code = values['csb34_11_lc_type']
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.recipient_nif = receipt['vat_number']
            record.data_number = '103'
            record.message = receipt['message_103']
            return write([record])

        def set_detail_910_record():
            record = Record(c34_1_lc.DETAIL_910_RECORD)
            record.record_code = '06'
            record.operation_code = values['csb34_11_lc_type']
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.recipient_nif = receipt['vat_number']
            record.data_number = '910'
            record.message = receipt['date']
            return write([record])

        def set_national_footer_record():
            record = Record(c34_1_lc.NATIONAL_FOOTER_RECORD)
            record.record_code = '08'
            record.operation_code = '56'
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.amount = values['amount']
            record.payment_line_count = str(values['payment_count'])
            record.record_count = str(values['detail_record_count'])
            return write([record])

        def set_ordering_footer_record():
            record = Record(c34_1_lc.ORDERING_FOOTER_RECORD)
            record.record_code = '09'
            record.operation_code = '62'
            record.nif = values['vat_number']
            record.suffix = values['suffix']
            record.amount = values['amount']
            record.payment_line_count = str(values['payment_count'])
            record.record_count = str(values['record_count'])
            return write([record])

        values = Group.set_devault_csb34_1_lc_payment_values(group)
        text = set_ordering_header_record() + '\r\n'
        values['record_count'] += 1
        text += set_ordering_header_002_record() + '\r\n'
        values['record_count'] += 1
        text += set_ordering_header_003_record() + '\r\n'
        values['record_count'] += 1
        text += set_ordering_header_004_record() + '\r\n'
        values['record_count'] += 1
        text += set_national_header_record() + '\r\n'
        values['record_count'] += 1
        values['detail_record_count'] += 1
        for receipt in values['receipts']:
            text += set_detail_001_record() + '\r\n'
            values['record_count'] += 1
            values['detail_record_count'] += 1
            text += set_detail_002_record() + '\r\n'
            values['record_count'] += 1
            values['detail_record_count'] += 1
            if receipt['street']:
                text += set_detail_003_record() + '\r\n'
                values['record_count'] += 1
                values['detail_record_count'] += 1
            if 'street2' in receipt and receipt['street2']:
                text += set_detail_004_record() + '\r\n'
                values['record_count'] += 1
                values['detail_record_count'] += 1
            if receipt['zip'] or receipt['city']:
                text += set_detail_005_record() + '\r\n'
                values['record_count'] += 1
                values['detail_record_count'] += 1
            if values['csb34_11_lc_type'] != 'transfer' \
                    and values['send_type'] in ('mail', 'certified_mail'):
                text += set_detail_006_record() + '\r\n'
                values['record_count'] += 1
                values['detail_record_count'] += 1
                if values['payroll_check']:
                    text += set_detail_007_record() + '\r\n'
                    values['record_count'] += 1
                    values['detail_record_count'] += 1
                text += set_detail_101_record() + '\r\n'
                values['record_count'] += 1
                values['detail_record_count'] += 1
                text += set_detail_102_record() + '\r\n'
                values['record_count'] += 1
                values['detail_record_count'] += 1
                text += set_detail_103_record() + '\r\n'
                values['record_count'] += 1
                values['detail_record_count'] += 1
                if values['add_date']:
                    text += set_detail_910_record() + '\r\n'
                    values['record_count'] += 1
                    values['detail_record_count'] += 1
            values['payment_count'] += 1
        values['detail_record_count'] += 1
        text += set_national_footer_record() + '\r\n'
        values['record_count'] += 2
        text += set_ordering_footer_record() + '\r\n'
        group.attach_file(text)
