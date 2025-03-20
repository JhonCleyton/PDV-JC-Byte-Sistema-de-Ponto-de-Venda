# PDV JC Byte - Sistema de Ponto de Venda

<div align="center">
  <img src="static/logo.jpg" alt="Logo JC Byte" width="200"/>
  <h3>Desenvolvido por JC Byte - Soluções em Tecnologia</h3>
</div>

## 📋 Sobre o Sistema

O PDV JC Byte é um sistema completo de Ponto de Venda (PDV) desenvolvido para atender às necessidades de empresas de pequenos portes iniciando seus trabalhos. Com uma interface moderna e intuitiva, o sistema oferece todas as funcionalidades necessárias para gerenciar vendas, estoque, clientes e finanças de forma eficiente e segura.

> **⚠️ IMPORTANTE:**  
> Para personalizar o sistema com sua identidade visual, substitua os arquivos de imagem na pasta `static` com sua própria logo, mantendo os mesmos nomes e formatos dos arquivos originais:
> - `logo.jpg` - Logo principal usada no README e em várias partes do sistema
> - `logo1.png` - Logo alternativa usada em algumas interfaces
> - `logo2.png` - Logo secundária 
> - `logo_merc.png` - Logo usada nas interfaces de mercado
> - `logo_mercado.jpeg` - Logo complementar
>
> Certifique-se de manter os mesmos formatos de arquivo para garantir compatibilidade com todo o sistema.

### 🌟 Principais Funcionalidades

- **Gestão de Vendas**
  - Registro rápido de vendas com código de barras
  - Múltiplas interfaces PDV (Professional, Modern e Standard)
  - Impressão de cupons com nome do operador
  - Múltiplas formas de pagamento (dinheiro, cartão de crédito, débito, PIX)
  - Parcelamento de vendas e controle de crédito
  - Confirmação de saída para evitar perda de vendas
  - Relógio em tempo real integrado

- **Controle de Estoque**
  - Cadastro de produtos com código de barras
  - Controle de entrada e saída automático
  - Alertas de estoque baixo
  - Gestão de fornecedores
  - Registro de notas fiscais de entrada
  - Controle de custos e preços de venda

- **Gestão Financeira**
  - Contas a pagar e receber com controle de vencimentos
  - Controle de caixa com abertura e fechamento
  - Relatórios detalhados de caixa incluindo pagamentos de dívidas
  - Suporte a retiradas de caixa com aprovação
  - Relatórios financeiros completos
  - Controle de parcelas e pagamentos

- **Gestão de Clientes**
  - Cadastro completo com matrícula automática
  - Histórico detalhado de compras
  - Controle de crédito e limite por cliente
  - Gestão de inadimplência
  - Emissão de comprovantes de pagamento de dívidas

- **Dashboard e Análises**
  - Dashboard com atualizações em tempo real
  - Relatórios detalhados de vendas
  - Análise de desempenho diário e mensal
  - Exportação para Excel
  - Gráficos e visualizações dinâmicas

- **Gestão de Usuários**
  - Controle de acesso por níveis (admin, gerente, vendedor)
  - Registro de operações por usuário
  - Identificação do operador nos cupons fiscais
  - Autenticação segura

## 🚀 Tecnologias Utilizadas

- **Backend:**
  - Python 3.11+
  - Flask Framework
  - SQLAlchemy ORM
  - Flask-Login para autenticação
  - Flask-Migrate para migrações
  - Flask-Cors para integração com frontends
  - Celery para processamento assíncrono (opcional)

- **Frontend:**
  - HTML5, CSS3, JavaScript
  - Bootstrap 5
  - jQuery e AJAX para requisições assíncronas
  - Charts.js para gráficos e visualizações
  - QR Code para pagamentos via PIX

- **Impressão e Documentos:**
  - Reportlab e FPDF para geração de PDFs
  - Integração com impressoras térmicas
  - SumatraPDF para visualização e impressão
  - Suporte a múltiplos métodos de impressão

- **Banco de Dados:**
  - SQLite (padrão para instalações locais)
  - Suporte a PostgreSQL para instalações em rede
  - Migrações automáticas de banco de dados

## 💻 Requisitos do Sistema

- Python 3.11 ou superior
- Navegador web moderno (Chrome, Firefox, Edge)
- 4GB de RAM (mínimo)
- 500MB de espaço em disco
- Windows 10/11 (suporte principal)
- Impressora térmica para cupons (opcional)

## 🔄 Arquitetura do Sistema

O PDV JC Byte utiliza uma arquitetura baseada em MVC (Model-View-Controller) com os seguintes componentes:

- **Models**: Define a estrutura do banco de dados e as entidades do sistema
- **Routes**: Implementa os endpoints da API e a lógica de negócios
- **Templates**: Interface de usuário renderizada no servidor
- **Utils**: Utilitários e funções auxiliares para impressão e processamento

O sistema é modular e organizado por funcionalidades:
- Autenticação e controle de acesso
- Gestão de produtos e categorias
- Vendas e PDV
- Gestão financeira (contas a pagar/receber)
- Controle de caixa
- Relatórios e dashboards
- Configurações do sistema

## 🛠️ Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/JhonCleyton/pdv-jcbyte.git
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o sistema:
   - Dê duplo clique em `iniciar_pdv.bat`, ou
   - Execute via terminal:
     ```bash
     python app.py
     ```

## 📱 Acesso ao Sistema

- **Local:** http://localhost:5000
- **Rede:** http://[IP-DA-MÁQUINA]:5000
- **Usuário padrão:** admin
- **Senha padrão:** admin

## 🔒 Segurança e Backup

- Autenticação de usuários com senha criptografada
- Controle de permissões por perfil de usuário
- Registro detalhado de atividades
- Backup automático de dados
- Proteção contra SQL Injection e ataques comuns
- Validação de entrada em todos os formulários

## 🔄 Correções e Melhorias Recentes

- **Relógio em Tempo Real**: Implementação de atualização automática do relógio no PDV.
- **Nome do Operador no Cupom**: Inclusão do nome do operador nos cupons fiscais para melhor controle.
- **Dashboard com Atualizações**: Sistema de atualização automática dos dados do dashboard.
- **Registro de Pagamentos de Dívidas**: Melhoria no relatório de caixa para exibir corretamente pagamentos de dívidas.
- **Diálogo de Confirmação**: Implementação de diálogo de confirmação para evitar saídas acidentais do PDV.
- **Compatibilidade com Métodos de Pagamento**: Correções para suportar diferentes métodos de pagamento nos relatórios.

## 📊 Recursos Adicionais

- Impressão de cupons fiscais personalizáveis
- Exportação de relatórios em PDF/Excel
- Backup automático configurável
- Suporte a múltiplos usuários simultâneos
- Interface responsiva para diferentes dispositivos
- Notificações de estoque baixo e contas a vencer
- Integração com APIs externas

## 🔄 Atualizações

O sistema recebe atualizações regulares com:
- Novas funcionalidades baseadas em feedback dos usuários
- Melhorias de desempenho e otimizações
- Correções de bugs e problemas relatados
- Atualizações de segurança e compatibilidade

## 📞 Suporte e Contato

### Desenvolvedor
**Jhon Cleyton**
- 🌐 [GitHub](https://github.com/JhonCleyton)
- 📷 [Instagram](https://instagram.com/jhon97cleyton)
- 📧 Email: tecnologiajcbyte@gmail.com
- 📱 WhatsApp: (73) 99854-7885

### Empresa
**JC Byte - Soluções em Tecnologia**
- 🏢 Especializada em soluções tecnológicas para empresas
- 💡 Desenvolvimento de sistemas personalizados
- 🔧 Suporte técnico especializado
- 📈 Consultoria em TI

## 📄 Licença

Este software é propriedade da JC Byte - Soluções em Tecnologia.
Todos os direitos reservados.

---

<div align="center">
  <p>Desenvolvido por JC Byte - Soluções em Tecnologia</p>
  <p>&copy; 2025 JC Byte - Soluções em Tecnologia. Todos os direitos reservados.</p>
</div>
