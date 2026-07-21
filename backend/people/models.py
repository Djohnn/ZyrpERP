import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from tenancy.managers import TenantManager
from tenancy.models import TenantScopedModel, TimeStampedModel


def digits_only(value):
    return re.sub(r'\D', '', value or '')


class PeopleModel(TimeStampedModel, TenantScopedModel):
    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True


class Person(PeopleModel):
    TYPE_CHOICES = [('PF', 'Pessoa física'), ('PJ', 'Pessoa jurídica')]

    person_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    name = models.CharField(max_length=200)
    trade_name = models.CharField(max_length=200, blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.trade_name = self.trade_name.strip()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PersonRole(PeopleModel):
    ROLE_CHOICES = [
        ('customer', 'Cliente'),
        ('supplier', 'Fornecedor'),
        ('carrier', 'Transportador'),
        ('contact', 'Contato'),
    ]
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['person', 'role'], name='uniq_person_role'),
        ]

    def save(self, *args, **kwargs):
        if self.person_id and self.person.tenant_id != self.tenant_id:
            raise ValidationError('Person must belong to the same tenant.')
        return super().save(*args, **kwargs)


class PersonDocument(PeopleModel):
    TYPE_CHOICES = [('CPF', 'CPF'), ('CNPJ', 'CNPJ'), ('IE', 'Inscrição Estadual')]
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    value = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'document_type', 'value'],
                condition=Q(is_active=True),
                name='uniq_active_document_per_tenant',
            ),
        ]

    def save(self, *args, **kwargs):
        if self.person_id and self.person.tenant_id != self.tenant_id:
            raise ValidationError('Person must belong to the same tenant.')
        self.value = digits_only(self.value)
        return super().save(*args, **kwargs)


class PersonAddress(PeopleModel):
    TYPE_CHOICES = [('fiscal', 'Fiscal'), ('delivery', 'Entrega'), ('billing', 'Cobrança')]
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    street = models.CharField(max_length=200)
    number = models.CharField(max_length=30, blank=True, default='')
    complement = models.CharField(max_length=100, blank=True, default='')
    district = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=8, blank=True, default='')
    country = models.CharField(max_length=2, default='BR')
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.person_id and self.person.tenant_id != self.tenant_id:
            raise ValidationError('Person must belong to the same tenant.')
        self.postal_code = digits_only(self.postal_code)
        self.state = self.state.strip().upper()
        return super().save(*args, **kwargs)


class PersonContact(PeopleModel):
    TYPE_CHOICES = [('email', 'E-mail'), ('phone', 'Telefone')]
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='contacts')
    contact_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    value = models.CharField(max_length=254)
    label = models.CharField(max_length=50, blank=True, default='')
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.person_id and self.person.tenant_id != self.tenant_id:
            raise ValidationError('Person must belong to the same tenant.')
        raw = self.value.strip()
        self.value = raw.lower() if self.contact_type == 'email' else digits_only(raw)
        return super().save(*args, **kwargs)


class ConsentRecord(PeopleModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='consents')
    purpose = models.CharField(max_length=100)
    granted = models.BooleanField()
    source = models.CharField(max_length=50, blank=True, default='')
    recorded_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.person_id and self.person.tenant_id != self.tenant_id:
            raise ValidationError('Person must belong to the same tenant.')
        return super().save(*args, **kwargs)
