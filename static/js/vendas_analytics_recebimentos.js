function formatReal(valor) {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}
let graficoRecebimentos = null;
async function carregarRecebimentos() {
    const start = document.getElementById('recebimentos-data-inicio').value;
    const end = document.getElementById('recebimentos-data-fim').value;
    const params = new URLSearchParams({ start_date: start, end_date: end });
    const resp = await fetch(`/vendas/api/analytics/recebimentos?${params.toString()}`);
    const data = await resp.json();
    if (!data.success) {
        alert('Erro ao carregar análise de recebimentos: ' + (data.error || ''));
        return;
    }
    // Gráfico
    if (graficoRecebimentos) graficoRecebimentos.destroy();
    const ctx = document.getElementById('grafico-recebimentos').getContext('2d');
    graficoRecebimentos = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.recebimentos.labels,
            datasets: [{
                data: data.recebimentos.valores,
                backgroundColor: ['#198754', '#0d6efd', '#ffc107', '#dc3545', '#6610f2']
            }]
        },
        options: { responsive: true }
    });
    // Tabela
    const tbody = document.querySelector('#tabela-recebimentos tbody');
    tbody.innerHTML = '';
    data.recebimentos.detalhes.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${item.forma}</td><td>${item.qtd}</td><td>${formatReal(item.total)}</td>`;
        tbody.appendChild(tr);
    });
}
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('filtros-recebimentos').addEventListener('submit', function(e) {
        e.preventDefault();
        carregarRecebimentos();
    });
    document.getElementById('btn-export-recebimentos').addEventListener('click', function() {
        const start = document.getElementById('recebimentos-data-inicio').value;
        const end = document.getElementById('recebimentos-data-fim').value;
        const params = new URLSearchParams({ start_date: start, end_date: end });
        window.location.href = `/vendas/api/analytics/recebimentos/export?${params.toString()}`;
    });
    carregarRecebimentos();
});
