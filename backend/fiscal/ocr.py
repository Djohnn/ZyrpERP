from decimal import Decimal


def parse_nfe_xml(xml_content: str) -> dict:
    from defusedxml.ElementTree import fromstring

    root = fromstring(xml_content)

    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

    emit = root.find('.//nfe:emit', ns)
    dest = root.find('.//nfe:dest', ns)

    supplier_data = {}
    if emit is not None:
        xnome = emit.find('nfe:xNome', ns)
        cnpj = emit.find('nfe:CNPJ', ns)
        supplier_data = {
            'name': xnome.text if xnome is not None else '',
            'cnpj': cnpj.text if cnpj is not None else '',
        }

    if not supplier_data.get('cnpj') and dest is not None:
        cnpj = dest.find('nfe:CNPJ', ns)
        supplier_data['cnpj'] = cnpj.text if cnpj is not None else ''

    dets = root.findall('.//nfe:det', ns)
    items = []
    for det in dets:
        prod = det.find('nfe:prod', ns)
        if prod is None:
            continue

        cprod = prod.find('nfe:cProd', ns)
        xprod = prod.find('nfe:xProd', ns)
        ncm = prod.find('nfe:NCM', ns)
        cfop = prod.find('nfe:CFOP', ns)
        ucom = prod.find('nfe:uCom', ns)
        qcom = prod.find('nfe:qCom', ns)
        vuncom = prod.find('nfe:vUnCom', ns)

        item = {
            'code': cprod.text if cprod is not None else '',
            'description': xprod.text if xprod is not None else '',
            'ncm': ncm.text if ncm is not None else '',
            'cfop': cfop.text if cfop is not None else '',
            'unit': ucom.text if ucom is not None else 'UN',
            'quantity': Decimal(qcom.text) if qcom is not None else Decimal('0'),
            'unit_price': Decimal(vuncom.text) if vuncom is not None else Decimal('0'),
        }
        items.append(item)

    ide = root.find('.//nfe:ide', ns)
    doc_number = ''
    doc_series = ''
    emission_date = ''
    if ide is not None:
        nf = ide.find('nfe:nNF', ns)
        serie = ide.find('nfe:serie', ns)
        dhemi = ide.find('nfe:dhEmi', ns)
        if nf is not None:
            doc_number = nf.text or ''
        if serie is not None:
            doc_series = serie.text or ''
        if dhemi is not None:
            emission_date = dhemi.text or ''

    cfop_nfe = items[0].get('cfop', '') if items else ''

    return {
        'supplier': supplier_data,
        'items': items,
        'cfop': cfop_nfe,
        'document_number': doc_number,
        'series': doc_series,
        'emission_date': emission_date,
    }
