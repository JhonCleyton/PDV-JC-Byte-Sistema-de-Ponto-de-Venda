// Funções utilitárias
function formatReal(valor) {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

// Gráficos Chart.js
let graficoVendasDia = null;
let graficoPagamentos = null;

async function carregarDashboard() {
    const start = document.getElementById('dashboard-data-inicio').value;
    const end = document.getElementById('dashboard-data-fim').value;
    const params = new URLSearchParams({ start_date: start, end_date: end });
    const resp = await fetch(`/vendas/api/analytics/dashboard?${params.toString()}`);
    const data = await resp.json();
    if (!data.success) {
        alert('Erro ao carregar dashboard: ' + (data.error || ''));
        return;
    }
    document.getElementById('dashboard-faturamento').textContent = formatReal(data.faturamento_total);
    document.getElementById('dashboard-num-vendas').textContent = data.num_vendas;
    document.getElementById('dashboard-ticket-medio').textContent = formatReal(data.ticket_medio);

    // Gráfico de vendas por dia
    if (graficoVendasDia) graficoVendasDia.destroy();
    const ctx1 = document.getElementById('grafico-vendas-dia').getContext('2d');
    graficoVendasDia = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: data.vendas_por_dia.labels,
            datasets: [{
                label: 'Vendas',
                data: data.vendas_por_dia.valores,
                backgroundColor: '#0d6efd'
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });

    // Gráfico de formas de pagamento
    if (graficoPagamentos) graficoPagamentos.destroy();
    const ctx2 = document.getElementById('grafico-pagamentos').getContext('2d');
    graficoPagamentos = new Chart(ctx2, {
        type: 'pie',
        data: {
            labels: data.formas_pagamento.labels,
            datasets: [{
                data: data.formas_pagamento.valores,
                backgroundColor: ['#198754', '#0d6efd', '#ffc107', '#dc3545', '#6610f2']
            }]
        },
        options: { responsive: true }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('dashboard-filtros').addEventListener('submit', function(e) {
        e.preventDefault();
        carregarDashboard();
    });
    document.getElementById('btn-export-dashboard').addEventListener('click', function() {
        const start = document.getElementById('dashboard-data-inicio').value;
        const end = document.getElementById('dashboard-data-fim').value;
        const params = new URLSearchParams({ start_date: start, end_date: end });
        window.location.href = `/vendas/api/analytics/dashboard/export?${params.toString()}`;
    });
    carregarDashboard();
});
