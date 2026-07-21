from rest_framework import serializers


class FiscalStatusSerializer(serializers.Serializer):
    sale_id = serializers.UUIDField()
    fiscal_status = serializers.CharField(source='status')
    attempt = serializers.IntegerField(source='attempt_number')
    protocol = serializers.CharField(allow_blank=True)
    pdf_url = serializers.CharField(source='pdf_key', allow_blank=True)
    xml_url = serializers.CharField(source='xml_key', allow_blank=True)
    error_detail = serializers.CharField(allow_blank=True)


class FiscalRequestSerializer(serializers.Serializer):
    sale_id = serializers.UUIDField()
    status = serializers.CharField(read_only=True)
    attempt = serializers.IntegerField(read_only=True)


class ReceiptFiscalValidateSerializer(serializers.Serializer):
    receipt_id = serializers.UUIDField()
    cfop = serializers.CharField(required=False, allow_blank=True)
    issues = serializers.ListField(read_only=True)
    warnings = serializers.ListField(read_only=True)
    requires_attention = serializers.BooleanField(read_only=True)
    created = serializers.BooleanField(read_only=True)
    document_id = serializers.UUIDField(read_only=True, allow_null=True)


class OCRXmlSerializer(serializers.Serializer):
    xml_content = serializers.CharField(write_only=True)
    supplier = serializers.DictField(read_only=True)
    items = serializers.ListField(read_only=True)
    cfop = serializers.CharField(read_only=True)
    document_number = serializers.CharField(read_only=True)
    series = serializers.CharField(read_only=True)
    emission_date = serializers.CharField(read_only=True)
