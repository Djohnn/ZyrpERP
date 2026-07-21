import logging
from decimal import Decimal

import requests

from fiscal.ports import CancelResult, EmitResult, FiscalProvider, QueryResult

logger = logging.getLogger(__name__)

CFOP_PADRAO = '5102'
PAYMENT_METHOD_MAP = {
    'cash': '01',
    'card_external': '03',
    'card_integrated': '03',
    'pix': '17',
}


def _as_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return float(Decimal(str(value)))


class PlugNotasAdapter(FiscalProvider):
    BASE_URL = 'https://api.plugnotas.com.br'

    def __init__(self, api_key: str = ''):
        self.api_key = api_key

    def _headers(self):
        return {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
        }

    def _build_emit_payload(self, emitter, document, items, payments):
        payload = {
            'idIntegracao': str(document.idempotency_key),
            'natureza': 'VENDA',
            'emitente': {
                'cpfCnpj': emitter.cpf_cnpj,
                'inscricaoEstadual': getattr(emitter, 'ie', '') or '',
            },
            'itens': [
                {
                    'codigo': str(item['product'].sku),
                    'descricao': item['product'].name[:120],
                    'ncm': item.get('ncm', ''),
                    'cfop': document.cfop or CFOP_PADRAO,
                    'unidade': item.get('unidade', 'UN'),
                    'quantidade': _as_float(item['quantity']),
                    'valorUnitario': {
                        'comercial': _as_float(item['unit_price']),
                        'tributavel': _as_float(item['unit_price']),
                    },
                    'valor': _as_float(item['line_total']),
                    'tributos': {
                        'icms': {
                            'origem': item.get('origem', '0'),
                            'cst': item.get('cst_icms', '00'),
                            'baseCalculo': {'modalidadeDeterminacao': 0, 'valor': 0},
                            'aliquota': _as_float(item.get('aliquota_icms', 0)),
                            'valor': 0,
                        },
                        'pis': {
                            'cst': item.get('cst_pis', '99'),
                            'baseCalculo': {'valor': 0, 'quantidade': 0},
                            'aliquota': 0,
                            'valor': 0,
                        },
                        'cofins': {
                            'cst': item.get('cst_cofins', '07'),
                            'baseCalculo': {'valor': 0},
                            'aliquota': 0,
                            'valor': 0,
                        },
                    },
                }
                for item in items
            ],
            'pagamentos': [
                {
                    'aVista': True,
                    'meio': PAYMENT_METHOD_MAP.get(payment.get('method'), '01'),
                    'valor': _as_float(payment['amount']),
                }
                for payment in payments
            ],
        }
        recipient = getattr(document, 'recipient', None)
        if recipient:
            payload['destinatario'] = {
                'cpfCnpj': recipient['cpf_cnpj'],
                'razaoSocial': recipient['name'],
                'endereco': recipient['address'],
            }
        return [payload]

    def emit(self, tenant, emitter, document, items, payments):
        response = requests.post(
            f'{self.BASE_URL}/nfce',
            headers=self._headers(),
            json=self._build_emit_payload(emitter, document, items, payments),
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        provider_id = data.get('idNota') or data.get('id') or ''
        logger.info('NFC-e emission requested: %s', provider_id)
        return EmitResult(provider_document_id=provider_id, raw_response=data)

    def query(self, tenant, provider_document_id: str):
        response = requests.get(
            f'{self.BASE_URL}/nfce/{provider_document_id}/resumo',
            headers=self._headers(),
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return QueryResult(
            status=data.get('status', 'PROCESSANDO'),
            protocol=data.get('protocolo'),
            xml_url=data.get('xml') or data.get('xmlUrl'),
            pdf_url=data.get('pdf') or data.get('pdfUrl'),
            error_reason=data.get('motivo') or data.get('erro'),
        )

    def cancel(self, tenant, provider_document_id: str):
        response = requests.post(
            f'{self.BASE_URL}/nfce/{provider_document_id}/cancelamento',
            headers=self._headers(),
            json={},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return CancelResult(success=True, protocol=data.get('protocolo'))
