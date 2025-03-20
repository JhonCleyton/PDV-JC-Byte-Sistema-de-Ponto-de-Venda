// Adicionar funcionalidade de relógio dinâmico
function updateClock() {
    const now = new Date();
    const options = { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit',
        hour12: false
    };
    const formattedDateTime = now.toLocaleString('pt-BR', options);
    const clockElement = document.getElementById('current-time');
    if (clockElement) {
        clockElement.textContent = formattedDateTime;
    } else {
        console.error("Elemento 'current-time' não encontrado!");
        // Parar o intervalo se o elemento não existir para evitar erros constantes
        clearInterval(clockInterval);
    }
}

// Variável para armazenar o intervalo do relógio
let clockInterval;

// Função para iniciar o relógio
function startClock() {
    // Limpa qualquer intervalo existente para evitar duplicação
    if (clockInterval) {
        clearInterval(clockInterval);
    }
    
    // Chama uma vez imediatamente
    updateClock();
    
    // Configura para atualizar a cada segundo
    clockInterval = setInterval(updateClock, 1000);
    console.log("Relógio iniciado com sucesso!");
}

// Iniciar o relógio imediatamente
startClock();

// Variáveis globais
let itens = [];
let clienteAtual = null;
let vendaAutorizada = false;
let currentProduct = null;
let precoTotal = 0;
let formaPagamento = 'dinheiro';

// Modais
const modalConfiguracoes = new bootstrap.Modal(document.getElementById('configModal'));
const modalConsultaPreco = new bootstrap.Modal(document.getElementById('priceInquiryModal'));
const modalConsultaCliente = new bootstrap.Modal(document.getElementById('customerInquiryModal'));
const modalConsultaFiado = new bootstrap.Modal(document.getElementById('debtInquiryModal'));
const modalPagamentoFiado = new bootstrap.Modal(document.getElementById('debtPaymentModal'));
const modalPagamento = new bootstrap.Modal(document.getElementById('paymentModal'));
const modalAutorizacao = new bootstrap.Modal(document.getElementById('authorizationModal'));
const modalRetiradaCaixa = new bootstrap.Modal(document.getElementById('withdrawalModal'));

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Iniciar o relógio
    startClock();
    
    // Eventos para o campo de entrada de produto
    const produtoInput = document.getElementById('product-input');
    produtoInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            processarEntrada(e.target.value);
            e.target.value = '';
        }
    });

    // Eventos para teclas de atalho
    document.addEventListener('keydown', function(e) {
        if (e.key === 'F1') {
            e.preventDefault();
            produtoInput.focus();
        } else if (e.key === 'F2') {
            e.preventDefault();
            abrirConsultaPreco();
        } else if (e.key === 'F3') {
            e.preventDefault();
            abrirConsultaCliente();
        } else if (e.key === 'F4') {
            e.preventDefault();
            finalizarVenda();
        }
    });

    // Botões de ação
    document.getElementById('btn-search-customer').addEventListener('click', function() {
        buscarClientePDV(document.getElementById('customer-input').value);
    });
    document.getElementById('btn-finish-sale').addEventListener('click', finalizarVenda);
    document.getElementById('btn-cancel-sale').addEventListener('click', cancelarVenda);
    
    // Botões de atalho
    document.getElementById('btn-config-toggle').addEventListener('click', abrirConfiguracoes);
    document.getElementById('btn-price-inquiry').addEventListener('click', abrirConsultaPreco);
    document.getElementById('btn-customer-inquiry').addEventListener('click', abrirConsultaCliente);
    document.getElementById('btn-debt-inquiry').addEventListener('click', abrirConsultaFiado);
    
    // Botões das modais
    document.getElementById('btn-search-price').addEventListener('click', buscarProdutoPreco);
    document.getElementById('btn-search-customer-modal').addEventListener('click', buscarClienteModal);
    document.getElementById('btn-search-debt').addEventListener('click', buscarDividas);
    document.getElementById('btn-confirm-debt-payment').addEventListener('click', pagarDivida);
    document.getElementById('btn-confirm-payment').addEventListener('click', confirmarPagamento);
    document.getElementById('btn-authorize-sale').addEventListener('click', abrirAutorizacao);
    document.getElementById('btn-confirm-authorization').addEventListener('click', autorizarVenda);
    document.getElementById('btn-save-config').addEventListener('click', salvarConfiguracoes);
    
    // Botão de retirada de caixa
    document.getElementById('btn-withdrawal').addEventListener('click', abrirRetiradaCaixa);
    document.getElementById('btn-confirm-withdrawal').addEventListener('click', confirmarRetiradaCaixa);
    
    // Eventos para campos específicos
    const paymentMethod = document.getElementById('payment-method');
    paymentMethod.addEventListener('change', togglePagamentoFields);
    
    const receivedAmount = document.getElementById('received-amount');
    receivedAmount.addEventListener('input', calcularTroco);
    
    // Iniciar com foco no campo de produto
    produtoInput.focus();
    
    // Carregar configurações salvas
    carregarConfiguracoes();
});

// Funções para configurações
function abrirConfiguracoes() {
    modalConfiguracoes.show();
}

function salvarConfiguracoes() {
    // Obter valores
    const tema = document.getElementById('config-theme').value;
    const corPrimaria = document.querySelector('.color-option.selected')?.getAttribute('data-color') || '#2563eb';
    const mensagem = document.getElementById('config-message').value;
    const corMensagem = document.getElementById('config-message-color').value;
    
    // Salvar no localStorage
    const config = {
        tema,
        corPrimaria,
        mensagem,
        corMensagem
    };
    localStorage.setItem('pdvConfig', JSON.stringify(config));
    
    // Aplicar configurações
    aplicarConfiguracoes(config);
    
    // Fechar modal
    modalConfiguracoes.hide();
    
    // Mostrar confirmação
    mostrarMensagem('Configurações salvas com sucesso!', 'success');
}

function carregarConfiguracoes() {
    // Verificar se existem configurações salvas
    const configSalva = localStorage.getItem('pdvConfig');
    if (configSalva) {
        const config = JSON.parse(configSalva);
        
        // Preencher campos do modal
        document.getElementById('config-theme').value = config.tema;
        document.querySelectorAll('.color-option').forEach(option => {
            if (option.getAttribute('data-color') === config.corPrimaria) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
        document.getElementById('config-message').value = config.mensagem;
        document.getElementById('config-message-color').value = config.corMensagem;
        
        // Aplicar configurações
        aplicarConfiguracoes(config);
    }
    
    // Adicionar evento para seleção de cores
    document.querySelectorAll('.color-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.color-option').forEach(o => o.classList.remove('selected'));
            this.classList.add('selected');
        });
    });
}

function aplicarConfiguracoes(config) {
    // Aplicar tema
    document.body.className = `tema-${config.tema}`;
    
    // Aplicar cor primária (usando variáveis CSS)
    document.documentElement.style.setProperty('--primary-color', config.corPrimaria);
    
    // Aplicar mensagem destacada
    const mensagemDestacada = document.getElementById('highlighted-message');
    if (mensagemDestacada) {
        mensagemDestacada.textContent = config.mensagem;
        mensagemDestacada.className = `pdv-message-highlighted pdv-message-${config.corMensagem}`;
    }
}

// Funções de processamento
function processarEntrada(entrada) {
    // Verificar se o formato é quantidade*código
    if (entrada.includes('*')) {
        const parts = entrada.split('*');
        const quantidade = parseFloat(parts[0]);
        const codigo = parts[1];
        
        if (!isNaN(quantidade) && quantidade > 0) {
            buscarProduto(codigo, quantidade);
        } else {
            alert('Quantidade inválida');
        }
    } else {
        // Código simples, quantidade 1
        buscarProduto(entrada, 1);
    }
}

function mostrarMensagem(texto, tipo = 'info') {
    // Criar o elemento de mensagem
    const mensagem = document.createElement('div');
    mensagem.className = `alert alert-${tipo}`;
    mensagem.textContent = texto;
    
    // Verificar se o container de mensagens existe, se não, criar
    let container = document.getElementById('mensagens');
    if (!container) {
        container = document.createElement('div');
        container.id = 'mensagens';
        container.className = 'mensagens-container';
        // Adicionar estilos para posicionar as mensagens
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // Adicionar ao container de mensagens
    container.appendChild(mensagem);
    
    // Remover após 3 segundos
    setTimeout(() => {
        mensagem.remove();
    }, 3000);
}

// Funções relacionadas a produtos
function buscarProduto(codigo, quantidade) {
    fetch(`/api/produtos/${codigo}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Produto não encontrado');
        }
        return response.json();
    })
    .then(produto => {
        adicionarProduto(produto, quantidade);
    })
    .catch(error => {
        mostrarMensagem('Produto não encontrado', 'danger');
    });
}

function adicionarProduto(produto, quantidade) {
    // Calcular preço
    const precoTotal = produto.preco * quantidade;
    
    // Verificar se o produto já está na lista
    const index = itens.findIndex(item => item.produto.id === produto.id);
    
    if (index !== -1) {
        // Produto já existe, atualizar quantidade
        itens[index].quantidade += quantidade;
        itens[index].precoTotal += precoTotal;
    } else {
        // Novo produto
        itens.push({
            produto: produto,
            quantidade: quantidade,
            precoTotal: precoTotal
        });
    }
    
    // Atualizar exibição
    atualizarTabelaProdutos();
    atualizarTotal();
    
    // Exibir produto atual
    currentProduct = produto;
    document.getElementById('current-product-name').textContent = produto.nome;
    document.getElementById('current-product-price').textContent = `R$ ${produto.preco.toFixed(2)}`;
    document.getElementById('current-product-code').textContent = `Código: ${produto.codigo}`;
}

function atualizarTabelaProdutos() {
    const tbody = document.getElementById('product-list');
    tbody.innerHTML = '';
    
    itens.forEach((item, index) => {
        const tr = document.createElement('tr');
        
        // Ordem
        const tdOrder = document.createElement('td');
        tdOrder.textContent = index + 1;
        tr.appendChild(tdOrder);
        
        // Código
        const tdCode = document.createElement('td');
        tdCode.textContent = item.produto.codigo;
        tr.appendChild(tdCode);
        
        // Nome
        const tdName = document.createElement('td');
        tdName.textContent = item.produto.nome;
        tr.appendChild(tdName);
        
        // Quantidade
        const tdQuantity = document.createElement('td');
        tdQuantity.textContent = item.quantidade;
        tr.appendChild(tdQuantity);
        
        // Preço unitário
        const tdUnitPrice = document.createElement('td');
        tdUnitPrice.textContent = `R$ ${item.produto.preco.toFixed(2)}`;
        tr.appendChild(tdUnitPrice);
        
        // Preço total
        const tdTotalPrice = document.createElement('td');
        tdTotalPrice.textContent = `R$ ${item.precoTotal.toFixed(2)}`;
        tr.appendChild(tdTotalPrice);
        
        // Ações
        const tdActions = document.createElement('td');
        
        // Botão excluir
        const btnDelete = document.createElement('button');
        btnDelete.innerHTML = '<i class="fas fa-trash"></i>';
        btnDelete.className = 'btn btn-sm btn-danger';
        btnDelete.addEventListener('click', () => removerProduto(index));
        tdActions.appendChild(btnDelete);
        
        tr.appendChild(tdActions);
        
        tbody.appendChild(tr);
    });
}

function removerProduto(index) {
    itens.splice(index, 1);
    atualizarTabelaProdutos();
    atualizarTotal();
}

function atualizarTotal() {
    precoTotal = itens.reduce((total, item) => total + item.precoTotal, 0);
    document.getElementById('total-amount').textContent = `R$ ${precoTotal.toFixed(2)}`;
}

// Funções relacionadas a consultas
function abrirConsultaPreco() {
    modalConsultaPreco.show();
    document.getElementById('price-inquiry-input').value = '';
    document.getElementById('price-inquiry-input').focus();
}

function buscarProdutoPreco() {
    const codigo = document.getElementById('price-inquiry-input').value;
    
    if (!codigo) {
        alert('Informe o código do produto');
        return;
    }
    
    fetch(`/api/produtos/${codigo}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Produto não encontrado');
        }
        return response.json();
    })
    .then(produto => {
        document.getElementById('price-inquiry-result').innerHTML = `
            <div class="alert alert-info">
                <p><strong>${produto.nome}</strong></p>
                <p>Código: ${produto.codigo}</p>
                <p class="text-success font-weight-bold">Preço: R$ ${produto.preco.toFixed(2)}</p>
                <p>Estoque: ${produto.estoque} unidades</p>
            </div>
        `;
    })
    .catch(error => {
        document.getElementById('price-inquiry-result').innerHTML = `
            <div class="alert alert-danger">
                Produto não encontrado
            </div>
        `;
    });
}

function abrirConsultaCliente() {
    modalConsultaCliente.show();
    document.getElementById('customer-inquiry-input').value = '';
    document.getElementById('customer-inquiry-input').focus();
}

function buscarClienteModal() {
    const matricula = document.getElementById('customer-inquiry-input').value;
    
    if (!matricula) {
        alert('Informe a matrícula do cliente');
        return;
    }
    
    fetch(`/api/clientes/${matricula}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Cliente não encontrado');
        }
        return response.json();
    })
    .then(cliente => {
        document.getElementById('customer-inquiry-result').innerHTML = `
            <div class="alert alert-info">
                <p><strong>${cliente.nome}</strong></p>
                <p>Matrícula: ${cliente.matricula}</p>
                <p>Departamento: ${cliente.departamento}</p>
                <p>Limite de crédito: R$ ${cliente.limite_credito.toFixed(2)}</p>
                <p>Saldo devedor: R$ ${cliente.saldo_devedor.toFixed(2)}</p>
                <p>Crédito disponível: R$ ${(cliente.limite_credito - cliente.saldo_devedor).toFixed(2)}</p>
            </div>
        `;
    })
    .catch(error => {
        document.getElementById('customer-inquiry-result').innerHTML = `
            <div class="alert alert-danger">
                Cliente não encontrado
            </div>
        `;
    });
}

function buscarClientePDV(matricula) {
    if (!matricula) {
        alert('Informe a matrícula do cliente');
        return;
    }
    
    fetch(`/api/clientes/${matricula}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Cliente não encontrado');
        }
        return response.json();
    })
    .then(cliente => {
        clienteAtual = cliente;
        
        document.getElementById('customer-info').classList.remove('d-none');
        document.getElementById('customer-name').textContent = cliente.nome;
        document.getElementById('customer-id').textContent = cliente.matricula;
        document.getElementById('customer-department').textContent = cliente.departamento;
        document.getElementById('customer-balance').textContent = `R$ ${(cliente.limite_credito - cliente.saldo_devedor).toFixed(2)}`;
        
        document.getElementById('customer-input').value = '';
    })
    .catch(error => {
        alert('Cliente não encontrado');
    });
}

function abrirConsultaFiado() {
    modalConsultaFiado.show();
    document.getElementById('debt-inquiry-input').value = '';
    document.getElementById('debt-inquiry-input').focus();
}

function buscarDividas() {
    const matricula = document.getElementById('debt-inquiry-input').value;
    
    if (!matricula) {
        alert('Informe a matrícula do cliente');
        return;
    }
    
    fetch(`/api/clientes/${matricula}/dividas`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Cliente não encontrado ou sem dívidas');
        }
        return response.json();
    })
    .then(dividas => {
        if (dividas.length === 0) {
            document.getElementById('debt-inquiry-result').innerHTML = `
                <div class="alert alert-success">
                    Cliente não possui dívidas pendentes
                </div>
            `;
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Data</th>
                            <th>Valor</th>
                            <th>Ação</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        dividas.forEach(divida => {
            const data = new Date(divida.data_venda).toLocaleDateString('pt-BR');
            html += `
                <tr>
                    <td>${divida.id}</td>
                    <td>${data}</td>
                    <td>R$ ${divida.valor_total.toFixed(2)}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="abrirPagamentoFiado(${divida.id}, ${divida.valor_total})">
                            Pagar
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        document.getElementById('debt-inquiry-result').innerHTML = html;
    })
    .catch(error => {
        document.getElementById('debt-inquiry-result').innerHTML = `
            <div class="alert alert-danger">
                ${error.message}
            </div>
        `;
    });
}

function abrirPagamentoFiado(id, valor) {
    document.getElementById('debt-payment-amount').value = valor.toFixed(2);
    
    // Armazenar o ID da dívida para uso posterior
    document.getElementById('debt-payment-amount').dataset.debtId = id;
    
    modalPagamentoFiado.show();
    modalConsultaFiado.hide();
}

function pagarDivida() {
    const debtId = document.getElementById('debt-payment-amount').dataset.debtId;
    const valorPagamento = parseFloat(document.getElementById('debt-payment-amount').value.replace(',', '.')) || 0;
    const formaPagamento = document.getElementById('debt-payment-method').value;
    
    if (isNaN(valorPagamento) || valorPagamento <= 0) {
        alert('Valor de pagamento inválido');
        return;
    }
    
    // Enviar requisição para o servidor
    fetch('/api/dividas/pagar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: debtId,
            valor: valorPagamento,
            forma_pagamento: formaPagamento
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao processar pagamento');
        }
        return response.json();
    })
    .then(result => {
        alert('Pagamento realizado com sucesso!');
        modalPagamentoFiado.hide();
        
        // Atualizar tabela de dívidas
        const matricula = document.getElementById('debt-inquiry-input').value;
        if (matricula) {
            buscarDividas();
        }
    })
    .catch(error => {
        alert(`Erro: ${error.message}`);
    });
}

// Funções relacionadas à venda
function finalizarVenda() {
    if (itens.length === 0) {
        alert('Não há itens na venda');
        return;
    }
    
    // Resetar campos
    document.getElementById('received-amount').value = '';
    document.getElementById('change-amount').textContent = 'R$ 0,00';
    document.getElementById('payment-method').value = 'dinheiro';
    togglePagamentoFields();
    
    // Exibir info do cliente se houver
    if (clienteAtual) {
        document.getElementById('fiado-customer-info').classList.remove('d-none');
        document.getElementById('fiado-customer-name').textContent = clienteAtual.nome;
        document.getElementById('fiado-customer-id').textContent = clienteAtual.matricula;
        document.getElementById('fiado-customer-balance').textContent = `R$ ${(clienteAtual.limite_credito - clienteAtual.saldo_devedor).toFixed(2)}`;
    } else {
        document.getElementById('fiado-customer-info').classList.add('d-none');
    }
    
    modalPagamento.show();
}

function togglePagamentoFields() {
    const metodo = document.getElementById('payment-method').value;
    const campoValorRecebido = document.getElementById('received-amount-group');
    const campoTroco = document.getElementById('change-group');
    
    if (metodo === 'dinheiro') {
        campoValorRecebido.classList.remove('d-none');
        campoTroco.classList.remove('d-none');
    } else {
        campoValorRecebido.classList.add('d-none');
        campoTroco.classList.add('d-none');
    }
    
    // Mostrar botão de autorização apenas se for fiado
    const botaoAutorizar = document.getElementById('btn-authorize-sale');
    
    if (metodo === 'fiado') {
        if (!clienteAtual) {
            alert('Selecione um cliente para venda fiado');
            document.getElementById('payment-method').value = 'dinheiro';
            togglePagamentoFields();
            return;
        }
        
        botaoAutorizar.classList.remove('d-none');
    } else {
        botaoAutorizar.classList.add('d-none');
    }
}

function calcularTroco() {
    const valorRecebido = parseFloat(document.getElementById('received-amount').value.replace(',', '.')) || 0;
    const troco = valorRecebido - precoTotal;
    
    document.getElementById('change-amount').textContent = `R$ ${troco.toFixed(2)}`;
    
    if (troco < 0) {
        document.getElementById('change-amount').classList.add('text-danger');
    } else {
        document.getElementById('change-amount').classList.remove('text-danger');
    }
}

function abrirAutorizacao() {
    document.getElementById('authorization-code').value = '';
    
    modalPagamento.hide();
    modalAutorizacao.show();
}

function autorizarVenda() {
    const codigo = document.getElementById('authorization-code').value;
    
    if (!codigo) {
        alert('Informe o código de autorização');
        return;
    }
    
    fetch('/api/autorizar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            codigo: codigo
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Código de autorização inválido');
        }
        return response.json();
    })
    .then(result => {
        vendaAutorizada = true;
        alert('Venda autorizada com sucesso!');
        modalAutorizacao.hide();
        modalPagamento.show();
    })
    .catch(error => {
        alert(`Erro: ${error.message}`);
    });
}

function confirmarPagamento() {
    // Verificar método de pagamento
    formaPagamento = document.getElementById('payment-method').value;
    
    // Validar pagamento fiado
    if (formaPagamento === 'fiado' && !vendaAutorizada) {
        alert('Esta venda precisa de autorização. Clique em "Autorizar" e informe o código.');
        return;
    }
    
    // Validar pagamento em dinheiro
    if (formaPagamento === 'dinheiro') {
        const valorRecebido = parseFloat(document.getElementById('received-amount').value.replace(',', '.')) || 0;
        if (isNaN(valorRecebido) || valorRecebido < precoTotal) {
            alert('Valor recebido insuficiente');
            return;
        }
    }
    
    // Preparar dados da venda
    const venda = {
        itens: itens.map(item => ({
            produto_id: item.produto.id,
            quantidade: item.quantidade,
            preco_unitario: item.produto.preco
        })),
        forma_pagamento: formaPagamento,
        cliente_id: clienteAtual ? clienteAtual.id : null
    };
    
    // Enviar requisição para o servidor
    fetch('/api/vendas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(venda)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao processar venda');
        }
        return response.json();
    })
    .then(result => {
        alert('Venda finalizada com sucesso!');
        modalPagamento.hide();
        
        // Limpar tudo
        itens = [];
        clienteAtual = null;
        precoTotal = 0;
        vendaAutorizada = false;
        
        // Atualizar interface
        atualizarTabelaProdutos();
        atualizarTotal();
        document.getElementById('customer-info').classList.add('d-none');
        document.getElementById('current-product-name').textContent = '';
        document.getElementById('current-product-price').textContent = '';
        document.getElementById('current-product-code').textContent = '';
        
        // Focar no campo de produto
        document.getElementById('product-input').focus();
    })
    .catch(error => {
        alert(`Erro: ${error.message}`);
    });
}

function cancelarVenda() {
    if (confirm('Tem certeza que deseja cancelar a venda?')) {
        itens = [];
        clienteAtual = null;
        precoTotal = 0;
        vendaAutorizada = false;
        
        // Atualizar interface
        atualizarTabelaProdutos();
        atualizarTotal();
        document.getElementById('customer-info').classList.add('d-none');
        document.getElementById('current-product-name').textContent = '';
        document.getElementById('current-product-price').textContent = '';
        document.getElementById('current-product-code').textContent = '';
        
        // Focar no campo de produto
        document.getElementById('product-input').focus();
    }
}

// Função para abrir o modal de retirada de caixa
function abrirRetiradaCaixa() {
    // Limpar campos
    document.getElementById('withdrawal-amount').value = '';
    document.getElementById('withdrawal-reason').value = '';
    document.getElementById('withdrawal-password').value = '';
    
    // Carregar autorizadores
    carregarAutorizadores();
    
    // Exibir modal
    modalRetiradaCaixa.show();
}

// Função para carregar lista de autorizadores (gerentes e admins)
function carregarAutorizadores() {
    fetch('/caixa/autorizadores')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const select = document.getElementById('withdrawal-authorizer');
                // Limpar opções existentes
                select.innerHTML = '<option value="">Selecione um autorizador</option>';
                
                // Adicionar opções
                data.autorizadores.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = user.name;
                    select.appendChild(option);
                });
            } else {
                mostrarMensagem(`Erro ao carregar autorizadores: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            mostrarMensagem(`Erro na requisição: ${error}`, 'error');
        });
}

// Função para confirmar retirada de caixa
function confirmarRetiradaCaixa() {
    const valor = document.getElementById('withdrawal-amount').value.trim();
    const motivo = document.getElementById('withdrawal-reason').value.trim();
    const autorizadorId = document.getElementById('withdrawal-authorizer').value;
    const senha = document.getElementById('withdrawal-password').value;
    
    // Validação básica
    if (!valor || isNaN(parseFloat(valor.replace(',', '.')))) {
        mostrarMensagem('Digite um valor válido para a retirada', 'error');
        return;
    }
    
    if (!motivo) {
        mostrarMensagem('Informe o motivo da retirada', 'error');
        return;
    }
    
    if (!autorizadorId) {
        mostrarMensagem('Selecione um autorizador', 'error');
        return;
    }
    
    if (!senha) {
        mostrarMensagem('Digite a senha do autorizador', 'error');
        return;
    }
    
    // Preparar dados para enviar
    const dados = {
        valor: parseFloat(valor.replace(',', '.')),
        motivo: motivo,
        autorizador_id: autorizadorId,
        senha: senha
    };
    
    // Enviar solicitação
    fetch('/caixa/retirada', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarMensagem('Retirada registrada com sucesso!', 'success');
            modalRetiradaCaixa.hide();
        } else {
            mostrarMensagem(`Erro: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        mostrarMensagem(`Erro na requisição: ${error}`, 'error');
    });
}
