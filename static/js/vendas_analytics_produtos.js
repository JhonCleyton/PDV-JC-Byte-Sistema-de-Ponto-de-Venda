function formatReal(valor) {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}
let graficoProdutos = null;
let detalhesProdutosCache = [];
async function carregarProdutos() {
    const start = document.getElementById('produtos-data-inicio').value;
    const end = document.getElementById('produtos-data-fim').value;
    const params = new URLSearchParams({ start_date: start, end_date: end });
    const resp = await fetch(`/vendas/api/analytics/produtos?${params.toString()}`);
    const data = await resp.json();
    if (!data.success) {
        alert('Erro ao carregar análise de produtos: ' + (data.error || ''));
        return;
    }
    // Gráfico
    if (graficoProdutos) graficoProdutos.destroy();
    const ctx = document.getElementById('grafico-produtos').getContext('2d');
    graficoProdutos = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.produtos.labels,
            datasets: [{
                label: 'Quantidade Vendida',
                data: data.produtos.valores,
                backgroundColor: '#0d6efd'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Quantidade: ' + context.parsed.y;
                        }
                    }
                }
            }
        }
    });
    // Tabela
    detalhesProdutosCache = data.produtos.detalhes;
    renderTabelaProdutos();
}

function renderTabelaProdutos() {
    const tbody = document.querySelector('#tabela-produtos tbody');
    tbody.innerHTML = '';
    const select = document.getElementById('produtos-por-pagina');
    let qtd = select ? select.value : '25';
    let lista;
    if (qtd === 'all') {
        lista = detalhesProdutosCache;
    } else {
        lista = detalhesProdutosCache.slice(0, parseInt(qtd));
    }
    lista.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${item.nome}</td><td>${item.qtd}</td><td>${formatReal(item.total)}</td>`;
        tbody.appendChild(tr);
    });
}
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('filtros-produtos').addEventListener('submit', function(e) {
        e.preventDefault();
        carregarProdutos();
    });
    document.getElementById('btn-export-produtos').addEventListener('click', function() {
        const start = document.getElementById('produtos-data-inicio').value;
        const end = document.getElementById('produtos-data-fim').value;
        const params = new URLSearchParams({ start_date: start, end_date: end });
        window.location.href = `/vendas/api/analytics/produtos/export?${params.toString()}`;
    });
    document.getElementById('produtos-por-pagina').addEventListener('change', function() {
        renderTabelaProdutos();
    });
    carregarProdutos();
});
