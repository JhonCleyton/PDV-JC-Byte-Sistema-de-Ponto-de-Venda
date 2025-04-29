function formatReal(valor) {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}
let graficoClientes = null;
async function carregarClientes() {
    const start = document.getElementById('clientes-data-inicio').value;
    const end = document.getElementById('clientes-data-fim').value;
    const params = new URLSearchParams({ start_date: start, end_date: end });
    const resp = await fetch(`/vendas/api/analytics/clientes?${params.toString()}`);
    const data = await resp.json();
    if (!data.success) {
        alert('Erro ao carregar análise de clientes: ' + (data.error || ''));
        return;
    }
    // Gráfico
    if (graficoClientes) graficoClientes.destroy();
    const ctx = document.getElementById('grafico-clientes').getContext('2d');
    graficoClientes = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.clientes.labels,
            datasets: [{
                label: 'Total Comprado',
                data: data.clientes.valores,
                backgroundColor: '#198754'
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
    // Tabela
    const tbody = document.querySelector('#tabela-clientes tbody');
    tbody.innerHTML = '';
    data.clientes.detalhes.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${item.nome}</td><td>${item.qtd}</td><td>${formatReal(item.total)}</td>`;
        tbody.appendChild(tr);
    });
}
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('filtros-clientes').addEventListener('submit', function(e) {
        e.preventDefault();
        carregarClientes();
    });
    document.getElementById('btn-export-clientes').addEventListener('click', function() {
        const start = document.getElementById('clientes-data-inicio').value;
        const end = document.getElementById('clientes-data-fim').value;
        const params = new URLSearchParams({ start_date: start, end_date: end });
        window.location.href = `/vendas/api/analytics/clientes/export?${params.toString()}`;
    });
    carregarClientes();
});
