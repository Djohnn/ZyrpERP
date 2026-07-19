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
