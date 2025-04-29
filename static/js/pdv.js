// Variáveis globais
let itens = [];
let clienteAtual = null;
let vendaAutorizada = false;
let ultimoProduto = null;
let modalConsultaPreco, modalFinalizarVenda, modalConsultaDividas, modalPagamentoDivida, modalConfirmSemLimite, modalConsultaCliente;
let modalFechamentoCaixa;
let clienteEncontrado = null;

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar modais
    try {
        // Inicializar modais principais
        const modalConsultaPrecoEl = document.getElementById('modalConsultaPreco');
        const modalFinalizarVendaEl = document.getElementById('modalFinalizarVenda');
        const modalConsultaDividasEl = document.getElementById('modalConsultaDividas');
        const modalPagamentoDividaEl = document.getElementById('modalPagamentoDivida');
        const modalConfirmSemLimiteEl = document.getElementById('modalConfirmSemLimite');
        const modalConsultaClienteEl = document.getElementById('modalConsultaCliente');
        const modalFechamentoCaixaEl = document.getElementById('modalFechamentoCaixa');
        
        if (modalConsultaPrecoEl) {
            modalConsultaPreco = new bootstrap.Modal(modalConsultaPrecoEl);
        } else {
            console.warn("Modal de consulta de preço não encontrado no DOM");
        }
        
        if (modalFinalizarVendaEl) {
            modalFinalizarVenda = new bootstrap.Modal(modalFinalizarVendaEl);
        } else {
            console.warn("Modal de finalização de venda não encontrado no DOM");
        }
        
        if (modalConsultaDividasEl) {
            modalConsultaDividas = new bootstrap.Modal(modalConsultaDividasEl);
        } else {
            console.warn("Modal de consulta de dívidas não encontrado no DOM");
        }
        
        if (modalPagamentoDividaEl) {
            modalPagamentoDivida = new bootstrap.Modal(modalPagamentoDividaEl);
        } else {
            console.warn("Modal de pagamento de dívida não encontrado no DOM");
        }
        
        if (modalConfirmSemLimiteEl) {
            modalConfirmSemLimite = new bootstrap.Modal(modalConfirmSemLimiteEl);
        } else {
            console.warn("Modal de confirmação sem limite não encontrado no DOM");
        }
        
        if (modalConsultaClienteEl) {
            modalConsultaCliente = new bootstrap.Modal(modalConsultaClienteEl);
        } else {
            console.warn("Modal de consulta de cliente não encontrado no DOM");
        }
        
        if (modalFechamentoCaixaEl) {
            modalFechamentoCaixa = new bootstrap.Modal(modalFechamentoCaixaEl);
        } else {
            console.warn("Modal de fechamento de caixa não encontrado no DOM");
        }
    } catch (error) {
        console.error("Erro ao inicializar modais:", error);
    }
    
    // Inicializar status do caixa
    atualizarStatusCaixa();
    
    // Event listener para teclas de atalho
    document.addEventListener('keydown', function(e) {
        if (e.key === 'F2') {
            e.preventDefault();
            consultarPreco();
        } else if (e.key === 'F3') {
            e.preventDefault();
            consultarCliente();
        } else if (e.key === 'F4') {
            e.preventDefault();
            finalizarVenda();
        } else if (e.key === 'F8') {
            e.preventDefault();
            consultarDividas();
        }
    });

    // Input de produto
    const inputProduto = document.getElementById('inputProduto');
    if (inputProduto) {
        inputProduto.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                processarEntrada(e.target.value);
                e.target.value = '';
            }
        });
    }
    
    // Event listener para o campo de valor pago
    const valorPagoInput = document.getElementById('valorPago');
    if (valorPagoInput) {
        valorPagoInput.addEventListener('input', calcularTroco);
    }

    // Botões de ação rápida
    const btnConsultarPreco = document.getElementById('consultarPreco');
    const btnConsultarCliente = document.getElementById('consultarCliente');
    const btnConsultarDividas = document.getElementById('consultarDividas');
    const btnFinalizarVenda = document.getElementById('finalizarVenda');
    const btnCancelarVenda = document.getElementById('cancelarVenda');

    if (btnConsultarPreco) {
        btnConsultarPreco.addEventListener('click', consultarPreco);
    }
    
    if (btnConsultarCliente) {
        btnConsultarCliente.addEventListener('click', consultarCliente);
    }

    if (btnConsultarDividas) {
        btnConsultarDividas.addEventListener('click', consultarDividas);
    }

    if (btnFinalizarVenda) {
        btnFinalizarVenda.addEventListener('click', finalizarVenda);
    }

    const btnConfirmarVenda = document.getElementById('confirmarVenda');
    if (btnConfirmarVenda) {
        btnConfirmarVenda.addEventListener('click', confirmarVenda);
        console.log("Event listener para confirmarVenda adicionado com sucesso");
    } else {
        console.warn("Botão confirmarVenda não encontrado no DOM");
    }

    const btnBuscarDividas = document.getElementById('buscarDividas');
    if (btnBuscarDividas) {
        btnBuscarDividas.addEventListener('click', buscarDividas);
    }

    // Event listener para o método de pagamento
    const metodoPagamento = document.getElementById('metodoPagamento');
    if (metodoPagamento) {
        metodoPagamento.addEventListener('change', toggleParcelas);
    }

    // Event listener para cálculo de troco
    const valorRecebido = document.getElementById('valorRecebido');
    if (valorRecebido) {
        valorRecebido.addEventListener('input', calcularTroco);
    }

    // Reset do form de autorização quando o modal fechar
    const modalConfirmSemLimite = document.getElementById('modalConfirmSemLimite');
    if (modalConfirmSemLimite) {
        modalConfirmSemLimite.addEventListener('hidden.bs.modal', function() {
            const formAutorizacao = document.getElementById('formAutorizacao');
            if (formAutorizacao) {
                formAutorizacao.reset();
            }
            vendaAutorizada = false;
        });
    }

    // Event listeners para consulta de preço
    const inputConsultaPreco = document.getElementById('codigoConsulta');
    const btnBuscarProduto = document.getElementById('buscarProduto');

    if (inputConsultaPreco) {
        inputConsultaPreco.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                pesquisarProduto(inputConsultaPreco.value.trim());
            }
        });
    }

    if (btnBuscarProduto) {
        btnBuscarProduto.addEventListener('click', function() {
            pesquisarProduto(inputConsultaPreco.value.trim());
        });
    }

    // Event listener para pagamento de dívida
    const btnPagarDivida = document.getElementById('pagarDivida');
    if (btnPagarDivida) {
        btnPagarDivida.addEventListener('click', pagarDivida);
    }

    // Botão para confirmar pagamento de dívida
    const btnConfirmarPagamento = document.getElementById('confirmarPagamento');
    if (btnConfirmarPagamento) {
        btnConfirmarPagamento.addEventListener('click', pagarDivida);
    }

    // Botão de autorizar venda
    const btnAutorizar = document.getElementById('confirmarAutorizacao');
    if (btnAutorizar) {
        btnAutorizar.addEventListener('click', async function() {
            const username = document.getElementById('usuarioAutorizacao').value;
            const password = document.getElementById('senhaAutorizacao').value;
            
            if (!username || !password) {
                alert('Por favor, preencha usuário e senha');
                return;
            }
            
            await solicitarAutorizacao(username, password);
        });
    }

    // Event listeners para botões
    const confirmarVendaBtn = document.getElementById('confirmarVenda');
    if (confirmarVendaBtn) {
        confirmarVendaBtn.addEventListener('click', confirmarVenda);
    }
    
    const confirmarAutorizacaoBtn = document.getElementById('confirmarAutorizacao');
    if (confirmarAutorizacaoBtn) {
        confirmarAutorizacaoBtn.addEventListener('click', function() {
            const username = document.getElementById('usuarioAutorizacao').value;
            const password = document.getElementById('senhaAutorizacao').value;
            solicitarAutorizacao(username, password);
        });
    }
    
    const confirmarSemAutorizacaoBtn = document.getElementById('confirmarSemAutorizacao');
    if (confirmarSemAutorizacaoBtn) {
        confirmarSemAutorizacaoBtn.addEventListener('click', function() {
            vendaAutorizada = true;
            modalConfirmSemLimite.hide();
            modalFinalizarVenda.show();
        });
    }

    // Botão Fechar Caixa
    const btnFecharCaixa = document.getElementById('btnAbrirFecharCaixa');
    if (btnFecharCaixa) {
        btnFecharCaixa.addEventListener('click', function() {
            if (itens.length > 0) {
                Swal.fire({
                    title: 'Atenção!',
                    text: 'Existe uma venda em andamento. Finalize ou cancele a venda antes de fechar o caixa.',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
            } else {
                // Abre o modal de fechamento diretamente
                const modalEl = document.getElementById('modalFechamentoCaixa');
                if (modalEl) {
                    try {
                        const modalInstance = new bootstrap.Modal(modalEl);
                        modalInstance.show();
                    } catch (error) {
                        console.error("Erro ao abrir modal:", error);
                        alert('Ocorreu um erro ao abrir o modal de fechamento de caixa: ' + error.message);
                    }
                } else {
                    console.error("Elemento do modal não encontrado");
                    alert('Modal de fechamento de caixa não encontrado no DOM.');
                }
            }
        });
    }

    // Configurar o botão de fechar caixa no modal
    const btnFecharCaixaModal = document.getElementById('btnFecharCaixa');
    if (btnFecharCaixaModal) {
        btnFecharCaixaModal.addEventListener('click', function() {
            const valorFinal = document.getElementById('valorFinal').value;
            if (!valorFinal) {
                Swal.fire({
                    title: 'Atenção!',
                    text: 'Informe o valor final em caixa.',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
                return;
            }
            
            // Enviar requisição para fechar o caixa
            console.log("Enviando requisição para fechar o caixa com valor:", valorFinal);
            fetch('/caixa/fechar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    valor_final: parseFloat(valorFinal)
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Resposta do fechamento de caixa:", data);
                if (data.success) {
                    Swal.fire({
                        title: 'Sucesso!',
                        text: 'Caixa fechado com sucesso!',
                        icon: 'success',
                        showCancelButton: true,
                        confirmButtonText: 'Ver Relatório',
                        cancelButtonText: 'Fechar'
                    }).then((result) => {
                        // Fechar o modal
                        const modalEl = document.getElementById('modalFechamentoCaixa');
                        if (modalEl) {
                            const modal = bootstrap.Modal.getInstance(modalEl);
                            if (modal) modal.hide();
                        }
                        
                        if (result.isConfirmed && data.caixa_id) {
                            // Redirecionar para o relatório
                            console.log("Abrindo relatório do caixa ID:", data.caixa_id);
                            window.open('/caixa/relatorio/' + data.caixa_id, '_blank');
                        }
                        
                        // Recarregar a página
                        console.log("Recarregando a página...");
                        setTimeout(function() {
                            window.location.reload();
                        }, 1000);
                    });
                } else {
                    Swal.fire({
                        title: 'Erro!',
                        text: data.error || 'Não foi possível fechar o caixa.',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                }
            })
            .catch(error => {
                console.error('Erro ao fechar caixa:', error);
                Swal.fire({
                    title: 'Erro!',
                    text: 'Ocorreu um erro ao fechar o caixa.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            });
        });
    }
});

// Processamento de entrada
function processarEntrada(entrada) {
    if (!entrada.trim()) return;
    
    const match = entrada.match(/^(\d*[.,]?\d*)\*(\d+)$/);
    if (match) {
        const quantidade = parseFloat(match[1].replace(',', '.')) || 1;
        const codigo = match[2];
        adicionarProduto(codigo, quantidade);
    } else {
        adicionarProduto(entrada, 1);
    }
}

// Adicionar produto
function adicionarProduto(codigo, quantidade) {
    fetch(`/api/produtos/${codigo}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const produto = data.product;
                // Buscar promoção ativa para o produto
                fetch(`/promotions/api/promotions/active/${produto.id}`)
                    .then(async resp => {
                        let promoData = {success: false};
                        try {
                          promoData = await resp.json();
                        } catch (e) {
                          // resposta não é JSON (ex: erro 404)
                          promoData = {success: false, error: 'Resposta inválida da API de promoção'};
                        }
                        return promoData;
                    })
                    .then(promoData => {
                        let precoFinal = produto.selling_price;
                        let infoPromo = '';
                        if (promoData.success && promoData.promotion) {
                            const promo = promoData.promotion;
                            if (promo.discount_type === 'percent') {
                                precoFinal = produto.selling_price * (1 - promo.discount_value / 100);
                                infoPromo = `Promoção: -${promo.discount_value}%`;
                            } else {
                                precoFinal = Math.max(0, produto.selling_price - promo.discount_value);
                                infoPromo = `Promoção: -R$ ${promo.discount_value}`;
                            }
                        }
                        precoFinal = Math.round(precoFinal * 100) / 100;
                        const item = {
                            id: produto.id,
                            codigo: produto.code,
                            nome: produto.name,
                            quantidade: quantidade,
                            unidade: produto.unit,
                            preco: precoFinal,
                            total: quantidade * precoFinal,
                            infoPromo: infoPromo
                        };
                        // Atualizar produto atual na tela, mostrando promoção se houver
                        atualizarProdutoAtual({
                            codigo: produto.code,
                            nome: produto.name,
                            preco: precoFinal,
                            infoPromo: infoPromo
                        });
                        itens.push(item);
                        atualizarTabela();
                        atualizarTotal();
                        atualizarStatusCaixa();
                    });
            } else {
                alert('Produto não encontrado!');
            }
        })
        .catch(error => {
            console.error('Erro ao adicionar produto:', error);
            alert('Erro ao adicionar produto. Tente novamente.');
        });
}

// Atualizar tabela de itens
function atualizarTabela() {
    const tbody = document.querySelector('#itemsTable tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    itens.forEach((item, index) => {
        const tr = document.createElement('tr');
        
        tr.innerHTML = `
            <td>${item.codigo}</td>
            <td>${item.nome}</td>
            <td class="text-center">${item.quantidade.toFixed(3).replace('.', ',')}</td>
            <td>${item.unidade}</td>
            <td>R$ ${formatarValor(item.preco)}</td>
            <td>R$ ${formatarValor(item.total)}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-danger" onclick="removerItem(${index})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

// Remover item
function removerItem(index) {
    itens.splice(index, 1);
    atualizarTabela();
    atualizarTotal();
    atualizarStatusCaixa();
    
    // Se não houver mais itens, resetar produto atual
    if (itens.length === 0) {
        const nomeProduto = document.getElementById('nome-produto-atual');
        const codigoProduto = document.getElementById('codigo-produto-atual');
        const precoProduto = document.getElementById('preco-produto-atual');
        
        if (nomeProduto) nomeProduto.textContent = "Nenhum produto selecionado";
        if (codigoProduto) codigoProduto.textContent = "--";
        if (precoProduto) precoProduto.textContent = "R$ 0,00";
    } else {
        // Mostrar o último item como produto atual
        const ultimoItem = itens[itens.length - 1];
        atualizarProdutoAtual({
            codigo: ultimoItem.codigo,
            nome: ultimoItem.nome,
            preco: ultimoItem.preco
        });
    }
}

// Atualizar total
function atualizarTotal() {
    const total = itens.reduce((acc, item) => acc + item.total, 0);
    const totalElement = document.getElementById('totalVenda');
    if (totalElement) {
        totalElement.textContent = formatarValor(total);
    }
}

// Consultar preço de produto
function consultarPreco() {
    if (!modalConsultaPreco) {
        modalConsultaPreco = new bootstrap.Modal(document.getElementById('modalConsultaPreco'));
    }
    modalConsultaPreco.show();
    
    // Limpar resultados anteriores
    const resultadoConsulta = document.getElementById('resultadoConsulta');
    if (resultadoConsulta) {
        const tbody = resultadoConsulta.querySelector('tbody');
        if (tbody) tbody.innerHTML = '';
    }
    
    // Focar na caixa de pesquisa
    const codigoConsulta = document.getElementById('codigoConsulta');
    if (codigoConsulta) {
        setTimeout(() => codigoConsulta.focus(), 500);
        
        // Configurar tecla Enter
        codigoConsulta.onkeypress = function(e) {
            if (e.key === 'Enter') {
                pesquisarProduto(codigoConsulta.value.trim());
            }
        };
    }
    
    // Configurar botão de busca
    const btnBuscar = document.getElementById('buscarProduto');
    if (btnBuscar) {
        btnBuscar.onclick = function() {
            pesquisarProduto(codigoConsulta.value.trim());
        };
    }
}

// Pesquisar produto para consulta
function pesquisarProduto(termo) {
    fetch(`/api/produtos/search?q=${encodeURIComponent(termo)}`)
        .then(response => response.json())
        .then(data => {
            const resultadoConsulta = document.getElementById('resultadoConsulta');
            if (!resultadoConsulta) return;
            
            const tbody = resultadoConsulta.querySelector('tbody');
            if (!tbody) return;
            
            tbody.innerHTML = '';
            
            if (data.products && data.products.length > 0) {
                data.products.forEach(produto => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${produto.code}</td>
                        <td>${produto.name}</td>
                        <td>R$ ${formatarValor(produto.selling_price)}</td>
                        <td>${produto.stock_quantity} ${produto.unit}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="selecionarProduto('${produto.code}')">
                                <i class="fas fa-plus"></i> Adicionar
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                const tr = document.createElement('tr');
                tr.innerHTML = '<td colspan="5" class="text-center">Nenhum produto encontrado</td>';
                tbody.appendChild(tr);
            }
        })
        .catch(error => {
            console.error('Erro ao pesquisar produto:', error);
            alert('Erro ao pesquisar produto. Tente novamente.');
        });
}

// Selecionar produto do resultado da consulta
function selecionarProduto(codigo) {
    adicionarProduto(codigo, 1);
    modalConsultaPreco.hide();
}

// Consultar dívidas
function consultarDividas() {
    // Verificar se o modal está inicializado
    if (!modalConsultaDividas) {
        modalConsultaDividas = new bootstrap.Modal(document.getElementById('modalConsultaDividas'));
    }
    
    // Solicitar matrícula do cliente
    if (!modalConsultaCliente) {
        modalConsultaCliente = new bootstrap.Modal(document.getElementById('modalConsultaCliente'));
    }
    
    // Limpar campos e resultados anteriores
    const clienteMatricula = document.getElementById('clienteMatricula');
    const clienteResultado = document.getElementById('clienteResultado');
    if (clienteMatricula) clienteMatricula.value = '';
    if (clienteResultado) clienteResultado.classList.add('d-none');
    clienteEncontrado = null;
    
    // Configurar o botão de busca para o contexto de dívidas
    const buscarClienteBtn = document.getElementById('buscarCliente');
    if (buscarClienteBtn) {
        buscarClienteBtn.onclick = function() {
            buscarClienteParaDividas();
        };
    }
    
    // Configurar o evento de tecla Enter
    if (clienteMatricula) {
        clienteMatricula.onkeypress = function(e) {
            if (e.key === 'Enter') {
                buscarClienteParaDividas();
            }
        };
    }
    
    // Configurar o botão de selecionar
    const selecionarClienteBtn = document.getElementById('selecionarCliente');
    if (selecionarClienteBtn) {
        selecionarClienteBtn.onclick = function() {
            if (clienteEncontrado) {
                modalConsultaCliente.hide();
                carregarDividasDoCliente(clienteEncontrado.id);
            } else {
                alert('Nenhum cliente selecionado');
            }
        };
    }
    
    // Mostrar o modal
    modalConsultaCliente.show();
    
    // Focar no campo de matrícula
    setTimeout(() => {
        if (clienteMatricula) clienteMatricula.focus();
    }, 500);
}

function buscarClienteParaDividas() {
    const clienteMatricula = document.getElementById('clienteMatricula');
    const clienteResultado = document.getElementById('clienteResultado');
    const clienteResultadoNome = document.getElementById('clienteResultadoNome');
    const clienteResultadoLimite = document.getElementById('clienteResultadoLimite');
    
    const matricula = clienteMatricula.value.trim();
    if (!matricula) {
        alert('Digite a matrícula do cliente');
        return;
    }
    
    fetch(`/api/clientes/busca?matricula=${encodeURIComponent(matricula)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Cliente não encontrado');
            }
            return response.json();
        })
        .then(data => {
            if (data && data.customer) {
                // Exibir resultado
                clienteEncontrado = data.customer;
                clienteResultado.classList.remove('d-none');
                clienteResultadoNome.textContent = data.customer.name;
                const limite = parseFloat(data.customer.available_credit).toFixed(2);
                clienteResultadoLimite.textContent = limite;
            } else {
                clienteResultado.classList.add('d-none');
                clienteEncontrado = null;
                alert('Cliente não encontrado');
            }
        })
        .catch(error => {
            console.error('Erro ao buscar cliente:', error);
            clienteResultado.classList.add('d-none');
            clienteEncontrado = null;
            alert('Erro ao buscar cliente: ' + error.message);
        });
}

function carregarDividasDoCliente(clienteId) {
    fetch(`/api/clientes/${clienteId}/dividas`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const tbody = document.querySelector('#tabelaDividas tbody');
                tbody.innerHTML = '';
                
                data.dividas.forEach(divida => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${divida.due_date ? new Date(divida.due_date).toLocaleDateString() : '-'}</td>
                        <td>${formatarValor(divida.amount)}</td>
                        <td>${formatarValor(divida.paid_amount)}</td>
                        <td>${formatarValor(divida.remaining_amount)}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="selecionarDivida(${divida.id}, ${divida.remaining_amount})">
                                Pagar
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
                
                modalConsultaDividas.show();
            } else {
                alert(data.error || 'Erro ao buscar dívidas');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao buscar dívidas');
        });
}

// Selecionar uma dívida para pagamento
function selecionarDivida(dividaId, valorTotal) {
    // Verificar se o modal está inicializado
    if (!modalPagamentoDivida) {
        modalPagamentoDivida = new bootstrap.Modal(document.getElementById('modalPagamentoDivida'));
    }
    
    // Preencher os campos do modal de pagamento
    const dividaIdInput = document.getElementById('dividaId');
    const valorDividaSpan = document.getElementById('valorDivida');
    const valorPagamentoInput = document.getElementById('valorPagamento');
    const formaPagamentoSelect = document.getElementById('formaPagamentoDivida');
    
    if (dividaIdInput) dividaIdInput.value = dividaId;
    if (valorDividaSpan) valorDividaSpan.textContent = valorTotal.toFixed(2);
    if (valorPagamentoInput) valorPagamentoInput.value = valorTotal.toFixed(2);
    if (formaPagamentoSelect) formaPagamentoSelect.value = 'dinheiro';
    
    // Esconder o modal de consulta de dívidas e mostrar o de pagamento
    if (modalConsultaDividas) modalConsultaDividas.hide();
    modalPagamentoDivida.show();
    
    // Focar no campo de valor
    if (valorPagamentoInput) setTimeout(() => valorPagamentoInput.focus(), 500);
}

// Pagar uma dívida
function pagarDivida() {
    const dividaId = document.getElementById('dividaId')?.value;
    const valorPagamento = document.getElementById('valorPagamento')?.value;
    const formaPagamento = document.getElementById('formaPagamentoDivida')?.value;
    
    if (!dividaId || !valorPagamento || !formaPagamento) {
        alert('Dados incompletos');
        return;
    }
    
    fetch(`/api/dividas/${dividaId}/pagar`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            valor: parseFloat(valorPagamento),
            forma_pagamento: formaPagamento
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Pagamento realizado com sucesso!\n\nCupom de pagamento enviado para impressão.');
            if (modalPagamentoDivida) {
                modalPagamentoDivida.hide();
            }
        } else {
            alert(data.error || 'Erro ao realizar pagamento');
        }
    })
    .catch(error => {
        console.error('Erro ao pagar dívida:', error);
        alert('Erro ao pagar dívida');
    });
}

// Finalizar venda
async function finalizarVenda() {
    try {
        if (itens.length === 0) {
            alert('Não há itens na venda para finalizar.');
            return;
        }
        
        const total = itens.reduce((acc, item) => acc + item.total, 0);
        const modalTotal = document.getElementById('modalTotal');
        if (modalTotal) {
            modalTotal.textContent = formatarValor(total);
        }
        
        // Verificar se o modal existe e inicializá-lo se necessário
        if (!modalFinalizarVenda) {
            const modalElement = document.getElementById('modalFinalizarVenda');
            if (!modalElement) {
                console.error("Elemento modalFinalizarVenda não encontrado no DOM");
                alert("Erro ao abrir a tela de finalização. Por favor, recarregue a página.");
                return;
            }
            modalFinalizarVenda = new bootstrap.Modal(modalElement);
        }
        
        // Limpar campos do modal
        const valorPagoInput = document.getElementById('valorPago');
        if (valorPagoInput) {
            valorPagoInput.value = total;
        }
        
        // Zerar troco
        const valorTroco = document.getElementById('valorTroco');
        if (valorTroco) {
            valorTroco.textContent = '0,00';
        }
        
        // Exibir o modal
        modalFinalizarVenda.show();
    } catch (error) {
        console.error("Erro ao finalizar venda:", error);
        alert("Ocorreu um erro ao finalizar a venda. Verifique o console para mais detalhes.");
    }
}

// Calcular troco
function calcularTroco() {
    try {
        const totalVenda = itens.reduce((acc, item) => acc + item.total, 0);
        const valorPagoElement = document.getElementById('valorPago');
        const valorTrocoElement = document.getElementById('valorTroco');
        const divTrocoElement = document.getElementById('divTroco');
        
        if (!valorPagoElement || !valorTrocoElement || !divTrocoElement) {
            console.error("Elementos necessários para calcular troco não encontrados");
            return;
        }
        
        const valorPago = parseFloat(valorPagoElement.value) || 0;
        
        if (valorPago >= totalVenda) {
            const troco = valorPago - totalVenda;
            valorTrocoElement.textContent = formatarValor(troco);
            divTrocoElement.classList.remove('d-none');
        } else {
            divTrocoElement.classList.add('d-none');
        }
    } catch (error) {
        console.error("Erro ao calcular troco:", error);
    }
}

// Toggle parcelas
function toggleParcelas() {
    try {
        const formaPagamento = document.getElementById('formaPagamento');
        const divParcelas = document.getElementById('divParcelas');
        
        if (!formaPagamento || !divParcelas) {
            console.error("Elementos necessários para alternar parcelas não encontrados");
            return;
        }
        
        // Atualiza o valor do troco primeiro
        calcularTroco();
        
        // Se for crediário, mostra campo de parcelas
        if (formaPagamento.value === 'crediario') {
            divParcelas.classList.remove('d-none');
            
            // Se não há cliente selecionado, mostra alerta
            if (!window.clienteAtual) {
                alert('É necessário selecionar um cliente para venda no crediário');
                // Volta para dinheiro
                formaPagamento.value = 'dinheiro';
                divParcelas.classList.add('d-none');
            }
        } else {
            divParcelas.classList.add('d-none');
        }
    } catch (error) {
        console.error("Erro ao alternar parcelas:", error);
    }
}

// Confirmar venda
async function confirmarVenda() {
    try {
        if (itens.length === 0) {
            alert('Não há itens na venda para finalizar.');
            return;
        }
        
        const formaPagamentoElement = document.getElementById('formaPagamento');
        if (!formaPagamentoElement) {
            console.error("Elemento formaPagamento não encontrado");
            alert("Erro ao finalizar venda. Recarregue a página e tente novamente.");
            return;
        }
        
        const formaPagamento = formaPagamentoElement.value;
        const total = itens.reduce((acc, item) => acc + item.total, 0);
        
        // Se for crediário, verifica o cliente e limite
        if (formaPagamento === 'crediario') {
            // Se não tem cliente selecionado
            if (!window.clienteAtual) {
                alert('Selecione um cliente para venda no crediário');
                return;
            }
            
            // Se não está autorizada, verifica o limite
            if (!vendaAutorizada) {
                const limiteDisponivel = window.clienteAtual.credit_limit - window.clienteAtual.current_debt;
                if (limiteDisponivel < total) {
                    const msgElement = document.getElementById('msgSemLimite');
                    if (msgElement) {
                        msgElement.textContent = 
                            `O cliente ${window.clienteAtual.name} possui limite disponível de R$ ${limiteDisponivel.toFixed(2)}, ` +
                            `mas a venda atual é de R$ ${total.toFixed(2)}. Deseja autorizar mesmo assim?`;
                    }
                    
                    if (modalFinalizarVenda) {
                        modalFinalizarVenda.hide();
                    }
                    
                    if (modalConfirmSemLimite) {
                        modalConfirmSemLimite.show();
                    } else {
                        alert("Erro: Modal de confirmação não encontrado. Tente recarregar a página.");
                    }
                    return;
                }
            }
        }
        
        // Continua com a venda
        const parcelas = [];
        if (formaPagamento === 'crediario') {
            const numParcelasElement = document.getElementById('numParcelas');
            if (!numParcelasElement) {
                console.error("Elemento numParcelas não encontrado");
                alert("Erro ao processar parcelas. Recarregue a página e tente novamente.");
                return;
            }
            
            const numParcelas = parseInt(numParcelasElement.value);
            const valorParcela = total / numParcelas;
            
            console.log('Número de parcelas:', numParcelas);
            console.log('Valor por parcela:', valorParcela);
            
            for (let i = 0; i < numParcelas; i++) {
                const dataVencimento = new Date();
                dataVencimento.setMonth(dataVencimento.getMonth() + i + 1);
                
                // Garantir que o valor seja string com 2 casas decimais - conversão cuidadosa
                // Primeiro arredonda para 2 casas decimais
                const valorParcelaArredondado = Math.round(valorParcela * 100) / 100;
                // Depois converte para string com exatamente 2 casas decimais
                const valorParcelaStr = valorParcelaArredondado.toFixed(2);
                
                console.log(`Parcela ${i+1} - valor arredondado: ${valorParcelaArredondado}`);
                console.log(`Parcela ${i+1} - valor formatado: ${valorParcelaStr}, tipo: ${typeof valorParcelaStr}`);
                
                parcelas.push({
                    due_date: dataVencimento.toISOString().split('T')[0],
                    amount: valorParcelaStr,
                    installment: i + 1
                });
            }
        }
        
        const venda = {
            customer_id: window.clienteAtual ? window.clienteAtual.id : null,
            items: itens.map(item => ({
                product_id: item.id,
                quantity: parseFloat(item.quantidade),
                price: parseFloat(item.preco)
            })),
            payment_method: formaPagamento,
            authorized: vendaAutorizada,
            receivables: parcelas.map(p => ({
                ...p,
                amount: parseFloat(p.amount)
            }))
        };

        console.log('Dados da venda a enviar:', JSON.stringify(venda));
        
        // Adiciona o valor recebido se for pagamento em dinheiro
        if (formaPagamento === 'dinheiro') {
            const valorPagoElement = document.getElementById('valorPago');
            if (valorPagoElement) {
                const valorRecebido = parseFloat(valorPagoElement.value);
                if (!isNaN(valorRecebido)) {
                    venda.received_amount = valorRecebido;
                }
            }
        }
        
        const response = await fetch('/vendas/api/vendas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(venda)
        });
        
        try {
            const result = await response.json();
            
            console.log('Resposta da API:', result);
            
            if (result.success) {
                alert('Venda finalizada com sucesso!');
                // Limpa os itens
                itens = [];
                atualizarTabela();
                atualizarTotal();
                atualizarStatusCaixa();
                
                // Limpa o cliente selecionado
                window.clienteAtual = null;
                const clienteInfoElement = document.getElementById('clienteInfo');
                if (clienteInfoElement) {
                    clienteInfoElement.textContent = 'Nenhum';
                }
                
                // Limpa o produto atual
                const nomeProduto = document.getElementById('nome-produto-atual');
                const codigoProduto = document.getElementById('codigo-produto-atual');
                const precoProduto = document.getElementById('preco-produto-atual');
                
                if (nomeProduto) nomeProduto.textContent = "Nenhum produto selecionado";
                if (codigoProduto) codigoProduto.textContent = "--";
                if (precoProduto) precoProduto.textContent = "R$ 0,00";
                
                // Fecha o modal
                if (modalFinalizarVenda) {
                    modalFinalizarVenda.hide();
                }
            } else {
                exibirMensagemErro('Erro ao finalizar venda: ' + (result.error || 'Erro desconhecido'));
            }
        } catch (error) {
            console.error('Erro ao finalizar venda:', error);
            
            // Se a resposta não for JSON válido, tenta obter o texto da resposta
            try {
                const errorText = await response.text();
                console.error('Resposta de erro do servidor:', errorText);
                exibirMensagemErro('Erro ao finalizar venda. Por favor, tente novamente.');
            } catch (textError) {
                exibirMensagemErro('Erro ao finalizar venda: ' + error.message);
            }
        }
    } catch (error) {
        console.error('Erro ao finalizar venda:', error);
        exibirMensagemErro('Erro ao finalizar venda: ' + error.message);
    }
}

// Solicitar autorização
async function solicitarAutorizacao(username, password) {
    try {
        const response = await fetch('/api/vendas/autorizar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const result = await response.json();
        
        if (result.success) {
            vendaAutorizada = true;
            modalConfirmSemLimite.hide();
            confirmarVenda();
        } else {
            alert(result.error || 'Erro ao autorizar venda');
        }
    } catch (error) {
        console.error('Erro ao autorizar venda:', error);
        alert('Erro ao autorizar venda');
    }
}

// Consultar cliente pela matrícula
function consultarCliente() {
    if (!modalConsultaCliente) {
        modalConsultaCliente = new bootstrap.Modal(document.getElementById('modalConsultaCliente'));
    }
    
    // Limpar campos e resultados anteriores
    const clienteMatricula = document.getElementById('clienteMatricula');
    const clienteResultado = document.getElementById('clienteResultado');
    const clienteResultadoNome = document.getElementById('clienteResultadoNome');
    const clienteResultadoLimite = document.getElementById('clienteResultadoLimite');
    const selecionarClienteBtn = document.getElementById('selecionarCliente');
    
    if (clienteMatricula) clienteMatricula.value = '';
    if (clienteResultado) clienteResultado.classList.add('d-none');
    clienteEncontrado = null;
    
    // Configurar o botão de busca
    const buscarClienteBtn = document.getElementById('buscarCliente');
    if (buscarClienteBtn) {
        buscarClienteBtn.onclick = function() {
            buscarClientePorMatricula();
        };
    }
    
    // Configurar o evento de tecla Enter
    if (clienteMatricula) {
        clienteMatricula.onkeypress = function(e) {
            if (e.key === 'Enter') {
                buscarClientePorMatricula();
            }
        };
    }
    
    // Configurar o botão de selecionar
    if (selecionarClienteBtn) {
        selecionarClienteBtn.onclick = function() {
            selecionarClienteEncontrado();
        };
    }
    
    // Mostrar o modal
    modalConsultaCliente.show();
    
    // Focar no campo de matrícula
    setTimeout(() => {
        if (clienteMatricula) clienteMatricula.focus();
    }, 500);
    
    // Função para buscar cliente
    function buscarClientePorMatricula() {
        const matricula = clienteMatricula.value.trim();
        if (!matricula) {
            alert('Digite a matrícula do cliente');
            return;
        }
        
        fetch(`/api/clientes/busca?matricula=${encodeURIComponent(matricula)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Cliente não encontrado');
                }
                return response.json();
            })
            .then(data => {
                if (data && data.customer) {
                    // Exibir resultado
                    clienteEncontrado = data.customer;
                    clienteResultado.classList.remove('d-none');
                    clienteResultadoNome.textContent = data.customer.name;
                    const limite = parseFloat(data.customer.available_credit).toFixed(2);
                    clienteResultadoLimite.textContent = limite;
                } else {
                    clienteResultado.classList.add('d-none');
                    clienteEncontrado = null;
                    alert('Cliente não encontrado');
                }
            })
            .catch(error => {
                console.error('Erro ao buscar cliente:', error);
                clienteResultado.classList.add('d-none');
                clienteEncontrado = null;
                alert('Erro ao buscar cliente: ' + error.message);
            });
    }
    
    // Função para selecionar o cliente encontrado
    function selecionarClienteEncontrado() {
        if (!clienteEncontrado) {
            alert('Nenhum cliente selecionado');
            return;
        }
        
        // Armazenar cliente atual
        window.clienteAtual = clienteEncontrado;
        
        // Exibir informações do cliente na interface principal
        const infoCliente = document.getElementById('infoCliente');
        const nomeCliente = document.getElementById('nomeCliente');
        const limiteDisponivel = document.getElementById('limiteDisponivel');
        
        if (infoCliente && nomeCliente && limiteDisponivel) {
            infoCliente.classList.remove('d-none');
            nomeCliente.textContent = clienteEncontrado.name;
            limiteDisponivel.textContent = parseFloat(clienteEncontrado.available_credit).toFixed(2);
        }
        
        // Fechar o modal
        modalConsultaCliente.hide();
        
        // Notificar o usuário
        alert(`Cliente ${clienteEncontrado.name} selecionado com sucesso!`);
    }
}

// Controle de Status do Caixa
function atualizarStatusCaixa() {
    const statusEl = document.getElementById('caixa-status');
    if (!statusEl) return;
    
    if (itens.length === 0) {
        statusEl.textContent = 'CAIXA LIVRE';
        statusEl.classList.remove('caixa-ocupado');
        statusEl.classList.add('caixa-livre');
    } else {
        statusEl.textContent = 'CAIXA OCUPADO';
        statusEl.classList.remove('caixa-livre');
        statusEl.classList.add('caixa-ocupado');
    }
}

// Atualizar informações do produto atual
function atualizarProdutoAtual(produto) {
    if (!produto) return;

    ultimoProduto = produto;

    const nomeProduto = document.getElementById('nome-produto-atual');
    const codigoProduto = document.getElementById('codigo-produto-atual');
    const precoProduto = document.getElementById('preco-produto-atual');
    const precoPromocionalProduto = document.getElementById('preco-promocional-produto-atual');

    if (nomeProduto) nomeProduto.textContent = produto.nome;
    if (codigoProduto) codigoProduto.textContent = `Código: ${produto.codigo}`;
    if (precoProduto) precoProduto.textContent = `R$ ${formatarValor(produto.preco)}`;
    if (precoPromocionalProduto && produto.infoPromo) {
        precoPromocionalProduto.textContent = `R$ ${formatarValor(produto.precoPromocional)}`;
        precoPromocionalProduto.style.display = 'block';
    } else if (precoPromocionalProduto) {
        precoPromocionalProduto.textContent = '';
        precoPromocionalProduto.style.display = 'none';
    }
}

// Formatar valor para exibição
function formatarValor(valor) {
    return parseFloat(valor).toFixed(2).replace('.', ',');
}

// Função para exibir mensagens de erro
function exibirMensagemErro(mensagem) {
    try {
        console.error(mensagem);
        // Usar toastr para exibir mensagem de erro se disponível
        if (typeof toastr !== 'undefined') {
            toastr.error(mensagem);
        } else {
            alert(mensagem);
        }
    } catch (error) {
        console.error('Erro ao exibir mensagem de erro:', error);
        alert(mensagem);
    }
}
