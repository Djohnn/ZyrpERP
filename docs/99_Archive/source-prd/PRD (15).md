# PRD — Sistema de Gestão de Estoque e PDV

## 1. Visão geral

Sistema para pequenos/médios varejistas (ex: pet shop, mercado) que precisam de:

- Controle de estoque com suporte a fracionamento de produtos (ex: pacote de 10kg → venda por kg)
- PDV completo (venda, desconto, formas de pagamento, parcelamento)
- Controle de caixa (abertura/fechamento) com rastreabilidade por funcionário
- Devolução de produtos com reflexo automático no estoque e no caixa
- Relatórios de estoque e vendas
- Cadastro de pessoas físicas e jurídicas (clientes e fornecedores)
- Administração de funcionários com permissões

**Stack sugerida**: Python 3.12, Django 5.x, PostgreSQL (aproveitando a experiência já consolidada no projeto financeiro).

---

## 2. Apps do projeto

- `estoque` — produtos, movimentações, fracionamento, relatórios
- `pdv` — vendas, itens de venda, pagamentos, devoluções
- `caixa` — sessões de caixa, movimentações de caixa, fechamento
- `pessoas` — clientes e fornecedores (PF/PJ)
- `usuarios` — funcionários, permissões, autenticação
- `fiscal` — dados da empresa emitente, certificado digital, emissão de NF-e/NFC-e/NFS-e

---

## 3. Modelagem de dados

### 3.1 Produto e estoque

```
class Produto(models.Model):
    UNIDADE_CHOICES = [("UN", "Unidade"), ("KG", "Quilograma"), ("PCT", "Pacote")]

    nome = models.CharField(max_length=200)
    categoria = models.ForeignKey("Categoria", on_delete=models.PROTECT)
    unidade_venda = models.CharField(max_length=3, choices=UNIDADE_CHOICES)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
    estoque_atual = models.DecimalField(max_digits=10, decimal_places=3)  # suporta kg fracionado
    produto_pai = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT,
                                     related_name="produtos_filhos")
    fator_conversao = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    ativo = models.BooleanField(default=True)

    # --- Dados fiscais (para emissão de NF-e / NFC-e) ---
    ncm = models.CharField(max_length=8)  # Nomenclatura Comum do Mercosul
    cest = models.CharField(max_length=7, blank=True)  # só se sujeito a substituição tributária
    ean_gtin = models.CharField(max_length=14, blank=True)  # código de barras, "SEM GTIN" se não houver
    origem_mercadoria = models.CharField(max_length=1, choices=[
        ("0", "Nacional"), ("1", "Estrangeira - importação direta"),
        ("2", "Estrangeira - mercado interno"),
        # 3-8: demais casos de nacional/estrangeira com conteúdo de importação
    ], default="0")
    unidade_tributavel = models.CharField(max_length=6, blank=True)  # se diferente da unidade_venda
    csosn = models.CharField(max_length=3, choices=[
        ("102", "Tributada pelo Simples, sem crédito"),
        ("103", "Isenção do ICMS para faixa de receita bruta"),
        ("300", "Imune"),
        ("400", "Não tributada pelo Simples Nacional"),
        ("500", "ICMS cobrado por substituição tributária"),
    ], default="102")  # MEI/Simples usa CSOSN; regime normal usaria CST — ver seção 3.7
    aliquota_icms = models.DecimalField(max_digits=5, decimal_places=2, default=0)
```

> Exemplo: "Ração 10kg (pacote)" é o produto_pai de "Ração fracionada (kg)", com fator_conversao = 10.
> Fracionar 1 pacote gera, em uma única transação atômica:
> 
> MovimentoEstoque tipo FRACIONAMENTO_BAIXA no produto pai (-1 pacote)
> 
> MovimentoEstoque tipo FRACIONAMENTO_ENTRADA no produto filho (+10 kg)

```
class MovimentoEstoque(models.Model):
    TIPO_CHOICES = [
        ("ENTRADA", "Entrada"),
        ("SAIDA", "Saída"),
        ("FRACIONAMENTO_BAIXA", "Fracionamento - baixa"),
        ("FRACIONAMENTO_ENTRADA", "Fracionamento - entrada"),
        ("DEVOLUCAO", "Devolução"),
        ("AJUSTE", "Ajuste manual"),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=25, choices=TIPO_CHOICES)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    venda = models.ForeignKey("pdv.Venda", null=True, blank=True, on_delete=models.SET_NULL)
    devolucao = models.ForeignKey("pdv.Devolucao", null=True, blank=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey("usuarios.Funcionario", on_delete=models.PROTECT)
    data_hora = models.DateTimeField(auto_now_add=True)
    observacao = models.CharField(max_length=255, blank=True)
```

### 3.2 Venda, item de venda e pagamento

```
class Venda(models.Model):
    STATUS_CHOICES = [("FINALIZADA", "Finalizada"), ("CANCELADA", "Cancelada")]

    numero = models.CharField(max_length=20, unique=True)
    vendedor = models.ForeignKey("usuarios.Funcionario", on_delete=models.PROTECT)
    cliente = models.ForeignKey("pessoas.Pessoa", null=True, blank=True, on_delete=models.SET_NULL)
    caixa_sessao = models.ForeignKey("caixa.CaixaSessao", on_delete=models.PROTECT)
    desconto_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="FINALIZADA")
    data_hora = models.DateTimeField(auto_now_add=True)

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey("estoque.Produto", on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    devolvido = models.BooleanField(default=False)

class Pagamento(models.Model):
    FORMA_CHOICES = [
        ("DINHEIRO", "Dinheiro"),
        ("CREDITO", "Cartão de crédito"),
        ("DEBITO", "Cartão de débito"),
        ("PIX", "Pix"),
    ]

    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="pagamentos")
    forma = models.CharField(max_length=10, choices=FORMA_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    parcelas = models.PositiveSmallIntegerField(default=1)  # só relevante se CREDITO
```

> Uma venda pode ter mais de um Pagamento (ex: parte em dinheiro, parte no cartão).

### 3.3 Devolução

```
class Devolucao(models.Model):
    FORMA_REEMBOLSO_CHOICES = [
        ("DINHEIRO", "Dinheiro"),
        ("ESTORNO_CARTAO", "Estorno no cartão"),
        ("ESTORNO_PIX", "Estorno via Pix"),
    ]

    item_venda = models.ForeignKey(ItemVenda, on_delete=models.PROTECT, related_name="devolucoes")
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    motivo = models.CharField(max_length=255)
    forma_reembolso = models.CharField(max_length=15, choices=FORMA_REEMBOLSO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey("usuarios.Funcionario", on_delete=models.PROTECT)
    data_hora = models.DateTimeField(auto_now_add=True)
```

**Regra de negócio ao salvar uma **`**Devolucao**` (dentro de uma transação):

1. Cria `MovimentoEstoque` tipo `DEVOLUCAO` (reentrada do produto no estoque)
2. Marca `ItemVenda.devolvido = True` (ou cria controle de devolução parcial se quantidade < total do item)
3. Se `forma_reembolso == DINHEIRO`: cria `MovimentoCaixa` tipo `SANGRIA`, com motivo `"Devolução: {produto} - {motivo}"`, vinculado à sessão de caixa aberta no momento
4. Se `forma_reembolso` for cartão ou Pix: **não** gera movimento de caixa físico — gera um registro de "estorno pendente" para conferência (não impacta o saldo em dinheiro do fechamento)

### 3.4 Caixa

```
class CaixaSessao(models.Model):
    STATUS_CHOICES = [("ABERTO", "Aberto"), ("FECHADO", "Fechado")]

    funcionario_abertura = models.ForeignKey("usuarios.Funcionario", on_delete=models.PROTECT,
                                              related_name="caixas_abertos")
    funcionario_fechamento = models.ForeignKey("usuarios.Funcionario", null=True, blank=True,
                                                on_delete=models.SET_NULL, related_name="caixas_fechados")
    valor_abertura = models.DecimalField(max_digits=10, decimal_places=2)
    valor_fechamento_informado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ABERTO")
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)

class MovimentoCaixa(models.Model):
    TIPO_CHOICES = [("VENDA", "Venda"), ("SANGRIA", "Sangria"), ("SUPRIMENTO", "Suprimento")]

    caixa_sessao = models.ForeignKey(CaixaSessao, on_delete=models.CASCADE, related_name="movimentos")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    forma_pagamento = models.CharField(max_length=10, choices=Pagamento.FORMA_CHOICES, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=255, blank=True)
    venda = models.ForeignKey(Venda, null=True, blank=True, on_delete=models.SET_NULL)
    devolucao = models.ForeignKey(Devolucao, null=True, blank=True, on_delete=models.SET_NULL)
    data_hora = models.DateTimeField(auto_now_add=True)
```

**Fechamento de caixa (agregação de **`**MovimentoCaixa**`**)**:

```
Vendas do dia:
  Cartão crédito  = soma(tipo=VENDA, forma=CREDITO)
  Cartão débito   = soma(tipo=VENDA, forma=DEBITO)
  Dinheiro        = soma(tipo=VENDA, forma=DINHEIRO)
  Pix             = soma(tipo=VENDA, forma=PIX)
  Total bruto     = soma de todas as formas

Saídas do caixa:
  Sangrias (motivo)  = lista de MovimentoCaixa tipo=SANGRIA
  Suprimentos        = lista de MovimentoCaixa tipo=SUPRIMENTO

Saldo esperado em dinheiro = vendas em dinheiro - sangrias em dinheiro + suprimentos em dinheiro
Diferença de caixa = valor_fechamento_informado - saldo esperado

Estornos pendentes (cartão/Pix) = lista à parte, não entra no saldo físico
```

### 3.5 Pessoas

```
class Pessoa(models.Model):
    TIPO_CHOICES = [("FISICA", "Pessoa física"), ("JURIDICA", "Pessoa jurídica")]
    PAPEL_CHOICES = [("CLIENTE", "Cliente"), ("FORNECEDOR", "Fornecedor"), ("AMBOS", "Cliente e fornecedor")]

    tipo = models.CharField(max_length=8, choices=TIPO_CHOICES)
    papel = models.CharField(max_length=10, choices=PAPEL_CHOICES)
    nome_razao_social = models.CharField(max_length=200)
    cpf_cnpj = models.CharField(max_length=18, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    ativo = models.BooleanField(default=True)
```

### 3.6 Funcionários e permissões

```
class Funcionario(models.Model):
    CARGO_CHOICES = [("ADMIN", "Administrador"), ("VENDEDOR", "Vendedor")]

    usuario = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    cargo = models.CharField(max_length=10, choices=CARGO_CHOICES)
    ativo = models.BooleanField(default=True)
```

> Recomendação: usar Groups/Permissions nativos do Django em vez de reinventar um sistema de permissões — cobre "pode abrir caixa", "pode dar desconto", "pode cancelar venda", "pode gerenciar estoque" via permissões customizadas por model/ação.

### 3.7 Dados fiscais (empresa emitente, certificado, notas)

> Você definiu: empresa MEI e emissão de NF-e (produtos), NFC-e (consumidor final) e NFS-e (serviços). SAT foi removido do escopo — é um sistema específico de São Paulo, e como a operação é em Goiás não se aplica. Dois pontos importantes antes do modelo:
> 
> CRT do MEI: desde 01/04/2025, toda NF-e/NFC-e de MEI é obrigada a informar o Código de Regime Tributário 4 (MEI). É diferente do CRT 1 (Simples Nacional comum) — se o campo vier errado, a SEFAZ rejeita a nota.
> 
> NFC-e não pode mais ir para CNPJ: pelo Ajuste SINIEF nº 11/2025, a partir de 05/01/2026 a NFC-e passou a ser exclusiva para consumidor final pessoa física (CPF). Se o sistema vender para uma pessoa jurídica no PDV, a nota tem que ser NF-e (modelo 55), não NFC-e. Isso significa que o tipo de documento fiscal deve ser decidido pelo tipo de pessoa do cliente na venda, não fixo por produto.

```
class Empresa(models.Model):
    CRT_CHOICES = [
        ("1", "Simples Nacional"),
        ("2", "Simples Nacional - excesso de sublimite"),
        ("3", "Regime Normal"),
        ("4", "MEI"),
    ]

    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200, blank=True)
    cnpj = models.CharField(max_length=18, unique=True)
    inscricao_estadual = models.CharField(max_length=20, blank=True)  # obrigatória p/ NF-e/NFC-e
    inscricao_municipal = models.CharField(max_length=20, blank=True)  # obrigatória p/ NFS-e
    crt = models.CharField(max_length=1, choices=CRT_CHOICES, default="4")
    codigo_municipio_ibge = models.CharField(max_length=7)
    uf = models.CharField(max_length=2)
    logradouro = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    cep = models.CharField(max_length=9)
    ambiente_nfe = models.CharField(max_length=10, choices=[
        ("HOMOLOGACAO", "Homologação"), ("PRODUCAO", "Produção")
    ], default="HOMOLOGACAO")

class CertificadoDigital(models.Model):
    TIPO_CHOICES = [("A1", "A1 - arquivo"), ("A3", "A3 - token/cartão")]

    empresa = models.OneToOneField(Empresa, on_delete=models.CASCADE, related_name="certificado")
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES, default="A1")
    arquivo_criptografado = models.BinaryField()  # .pfx/.p12, nunca em texto puro
    senha_criptografada = models.BinaryField()    # nunca a senha em texto puro no banco
    validade_inicio = models.DateField()
    validade_fim = models.DateField()
    ativo = models.BooleanField(default=True)
```

> Segurança do certificado — não é opcional: o certificado + senha permitem emitir notas fiscais válidas em nome da empresa. Nunca salvar arquivo ou senha em texto puro no banco. Usar criptografia simétrica (ex: django-cryptography ou Fernet do pacote cryptography) com a chave de criptografia guardada fora do banco (variável de ambiente / secrets manager), nunca versionada no repositório. Prever alerta automático (ex: e-mail) quando faltarem 30/15/7 dias para o vencimento do certificado — nota fiscal não emite com certificado vencido.

```
class NotaFiscal(models.Model):
    TIPO_CHOICES = [
        ("NFE", "NF-e (produto)"),
        ("NFCE", "NFC-e (consumidor final)"),
        ("NFSE", "NFS-e (serviço)"),
    ]
    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"), ("AUTORIZADA", "Autorizada"),
        ("REJEITADA", "Rejeitada"), ("CANCELADA", "Cancelada"),
    ]

    tipo = models.CharField(max_length=5, choices=TIPO_CHOICES)
    venda = models.ForeignKey("pdv.Venda", null=True, blank=True, on_delete=models.PROTECT)
    numero = models.PositiveIntegerField()
    serie = models.CharField(max_length=3, default="1")
    chave_acesso = models.CharField(max_length=44, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDENTE")
    protocolo_autorizacao = models.CharField(max_length=50, blank=True)
    xml_retorno = models.TextField(blank=True)
    motivo_rejeicao = models.CharField(max_length=255, blank=True)
    data_emissao = models.DateTimeField(auto_now_add=True)
```

**Regra de decisão do tipo de documento na venda**: ao finalizar a venda, o sistema escolhe automaticamente entre NF-e e NFC-e com base no `cliente.tipo`:

- `cliente` é pessoa física (ou venda sem cliente identificado) → **NFC-e**
- `cliente` é pessoa jurídica → **NF-e** (a NFC-e não pode mais ser emitida pra CNPJ desde 05/01/2026)

**Sobre o provedor de emissão**: dá pra emitir direto pela SEFAZ (mais barato, mais complexo — exige webservices SOAP/assinatura XML própria) ou por um provedor homologado (Focus NFe, por exemplo — você já tem familiaridade disso do GestUP). Um provedor cobre NF-e/NFC-e/NFS-e numa API só, o que simplifica bastante a integração.

### 3.8 Fluxo detalhado de emissão da nota fiscal

1. **Venda finalizada no PDV** — o `MovimentoCaixa` de venda já foi registrado; a nota fiscal é um passo seguinte e não deve travar o fechamento da venda em si (ver ponto sobre contingência abaixo).
2. **Monta o XML fiscal**: para cada `ItemVenda`, busca os dados fiscais do `Produto` (NCM, CSOSN, alíquotas etc.) e os dados da `Empresa` (CNPJ, IE, CRT). Decide o tipo de documento: `cliente.tipo == JURIDICA` → NF-e; caso contrário → NFC-e.
3. **Verifica o certificado**: antes de assinar, checa se `CertificadoDigital.ativo` e se `validade_fim` ainda não passou. Certificado vencido bloqueia a emissão — o sistema deve avisar isso de forma clara pro operador, não só falhar silenciosamente.
4. **Assina o XML** com o certificado descriptografado em memória (nunca gravar o arquivo decifrado em disco).
5. **Envia para emissão** — via provedor homologado (ex: Focus NFe) ou direto pelos webservices da SEFAZ.
6. **Resposta da SEFAZ**:
  - **Autorizada**: grava `chave_acesso`, `protocolo_autorizacao`, status `AUTORIZADA`; gera o PDF do DANFE (NF-e) ou DANFCE (NFC-e) e vincula à `Venda`.
  - **Rejeitada**: grava `motivo_rejeicao`, status `REJEITADA`; a venda continua valenda no caixa, mas fica sinalizada como "nota pendente de correção" até reenviar.

7. **Contingência (SEFAZ fora do ar)**: o PDV não pode parar de vender porque a SEFAZ caiu. Prever um modo de contingência (nota fica com status `PENDENTE` e é reenviada automaticamente depois, dentro do prazo legal) — isso é padrão em qualquer PDV de varejo real.
8. **Cancelamento**: se a venda inteira for cancelada dentro do prazo legal (geralmente até 24h para NFC-e, regras variam por estado), dispara evento de cancelamento na SEFAZ. **Devolução parcial de um item não cancela a nota inteira** — normalmente exige emissão de uma nota de entrada de devolução separada, então isso precisa ser tratado à parte do fluxo de `Devolucao` já modelado (ver ponto em aberto).

---

## 4. Fluxo de venda com devolução (referência)

1. Abertura de caixa (funcionário + valor inicial)
2. Venda no PDV: itens (com fracionamento se aplicável), desconto, forma(s) de pagamento
3. Cliente solicita devolução de um item específico
4. Reembolso conforme forma de pagamento original:
  - Dinheiro → sangria imediata no caixa
  - Cartão → estorno na operadora (não afeta caixa físico no dia)
  - Pix → devolução via Pix (não afeta caixa físico)

5. Reentrada do produto no estoque (`MovimentoEstoque` tipo DEVOLUCAO)
6. Registro no caixa com motivo detalhado
7. Fechamento de caixa consolidado por forma de pagamento, com sangrias e estornos pendentes destacados

---

## 5. Relatórios

- **Estoque completo**: todos os produtos e quantidades atuais
- **Produtos zerados**: produtos com `estoque_atual <= 0`
- **Vendas por produto**: histórico e quantidade vendida de um produto específico
- **Fechamento de caixa**: detalhado por forma de pagamento, sangrias e estornos pendentes

---

## 6. Sprints

| Sprint | Escopo |
| --- | --- |
| 0 | Setup do projeto, apps (estoque, pdv, caixa, pessoas, usuarios) |
| 1 | Modelo Produto + Categoria + CRUD básico |
| 2 | MovimentoEstoque + lógica de fracionamento (produto_pai/fator_conversao) |
| 3 | Relatórios de estoque (geral, zerados, vendas por produto) |
| 4 | Pessoa (PF/PJ) + fornecedores/clientes |
| 5 | Funcionario + grupos/permissões + admin |
| 6 | CaixaSessao — abertura/fechamento básico (sem venda ainda) |
| 7 | PDV — Venda/ItemVenda/Pagamento, desconto, parcelamento |
| 8 | Devolucao + reentrada no estoque + reflexo no caixa |
| 9 | Relatório de fechamento de caixa completo |
| 10 | Empresa (dados do emitente) + CertificadoDigital (upload/criptografia + alerta de vencimento) |
| 11 | Campos fiscais no Produto (NCM, CEST, CSOSN, origem, etc.) |
| 12 | Integração de emissão (NF-e/NFC-e, decisão automática por tipo de cliente) via provedor homologado |
| 13 | NFS-e (se aplicável a serviços) |
| 14 | Ajustes finos, permissões refinadas, testes |

---

## 7. Pontos em aberto para próximas sessões

- Definir se devolução parcial de quantidade (ex: devolver 1kg de 2kg fracionados) precisa de controle mais granular no `ItemVenda`
- Definir regra de cancelamento de venda completa (diferente de devolução de item)
- Definir se have integração real com maquineta de cartão/Pix ou se o registro de estorno é apenas manual/informativo
- Definir formato de emissão de cupom/nota (se necessário nesta fase)
- Confirmar se o negócio presta serviços (justifica NFS-e) ou é só venda de produto
- Escolher provedor de emissão (ex: Focus NFe) e mapear diferenças de contrato entre NF-e/NFC-e/NFS-e
- Definir estratégia de guarda da chave de criptografia do certificado (variável de ambiente vs. secrets manager)
- Definir como tratar o lado fiscal da devolução parcial (nota de entrada de devolução separada da nota original)
