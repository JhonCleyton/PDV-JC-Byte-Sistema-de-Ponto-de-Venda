function formatReal(valor) {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}
let graficoComparativo = null;
async function carregarComparativo() {
    const start1 = document.getElementById('comparativo-data-inicio1').value;
    const end1 = document.getElementById('comparativo-data-fim1').value;
    const start2 = document.getElementById('comparativo-data-inicio2').value;
    const end2 = document.getElementById('comparativo-data-fim2').value;
    const params = new URLSearchParams({ start_date1: start1, end_date1: end1, start_date2: start2, end_date2: end2 });
    const resp = await fetch(`/vendas/api/analytics/comparativo?${params.toString()}`);
    const data = await resp.json();
    if (!data.success) {
        alert('Erro ao carregar comparativo: ' + (data.error || ''));
        return;
    }
    // Gráfico
    if (graficoComparativo) graficoComparativo.destroy();
    const ctx = document.getElementById('grafico-comparativo').getContext('2d');
    graficoComparativo = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Faturamento', 'Vendas', 'Ticket Médio'],
            datasets: [
                {
                    label: data.periodos[0].label,
                    data: [data.periodos[0].faturamento, data.periodos[0].vendas, data.periodos[0].ticket_medio],
                    backgroundColor: '#0d6efd'
                },
                {
                    label: data.periodos[1].label,
                    data: [data.periodos[1].faturamento, data.periodos[1].vendas, data.periodos[1].ticket_medio],
                    backgroundColor: '#198754'
                }
            ]
        },
        options: { responsive: true }
    });
    // Tabela
    const tbody = document.querySelector('#tabela-comparativo tbody');
    tbody.innerHTML = '';
    data.periodos.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${p.label}</td><td>${p.vendas}</td><td>${formatReal(p.faturamento)}</td><td>${formatReal(p.ticket_medio)}</td>`;
        tbody.appendChild(tr);
    });
}
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('filtros-comparativo').addEventListener('submit', function(e) {
        e.preventDefault();
        carregarComparativo();
    });
    document.getElementById('btn-export-comparativo').addEventListener('click', function() {
        const start1 = document.getElementById('comparativo-data-inicio1').value;
        const end1 = document.getElementById('comparativo-data-fim1').value;
        const start2 = document.getElementById('comparativo-data-inicio2').value;
        const end2 = document.getElementById('comparativo-data-fim2').value;
        const params = new URLSearchParams({ start_date1: start1, end_date1: end1, start_date2: start2, end_date2: end2 });
        window.location.href = `/vendas/api/analytics/comparativo/export?${params.toString()}`;
    });
    carregarComparativo();
});
