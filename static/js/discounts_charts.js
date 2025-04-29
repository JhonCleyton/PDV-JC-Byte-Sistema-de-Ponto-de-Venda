// Gráficos analíticos de descontos usando Chart.js
$(document).ready(function() {
    function renderDiscountCharts(data) {
        // Limpa área de gráficos
        $('#discount-charts').empty();
        if (!data || data.length === 0) {
            $('#discount-charts').append('<div class="text-center text-muted">Nenhum dado para gráficos.</div>');
            return;
        }
        // Layout flex para gráficos lado a lado
        $('#discount-charts').append('<div id="charts-flex" style="display:flex;gap:20px;justify-content:center;"></div>');
        // 1. Descontos por produto
        let produtos = {};
        data.forEach(item => {
            if (!produtos[item.produto]) produtos[item.produto] = 0;
            produtos[item.produto] += parseFloat(item.diferença.replace('R$','').replace(',','.'));
        });
        let prodLabels = Object.keys(produtos);
        let prodValues = Object.values(produtos);
        let prodDiv = $('<div style="flex:1;max-width:400px;text-align:center;"></div>');
        prodDiv.append('<h6>Desconto Total por Produto</h6>');
        let ctx1 = $('<canvas width="400" height="260"></canvas>')[0].getContext('2d');
        prodDiv.append(ctx1.canvas);
        $('#charts-flex').append(prodDiv);
        new Chart(ctx1, {
            type: 'bar',
            data: { labels: prodLabels, datasets: [{ label: 'Desconto Total (R$)', data: prodValues, backgroundColor: '#007bff' }] },
            options: { responsive: false, plugins: { legend: { display: false } } }
        });
        // 2. Descontos por operador
        let operadores = {};
        data.forEach(item => {
            if (!operadores[item.operador]) operadores[item.operador] = 0;
            operadores[item.operador] += parseFloat(item.diferença.replace('R$','').replace(',','.'));
        });
        let opLabels = Object.keys(operadores);
        let opValues = Object.values(operadores);
        let opDiv = $('<div style="flex:1;max-width:400px;text-align:center;"></div>');
        opDiv.append('<h6>Desconto Total por Operador</h6>');
        let ctx2 = $('<canvas width="400" height="260"></canvas>')[0].getContext('2d');
        opDiv.append(ctx2.canvas);
        $('#charts-flex').append(opDiv);
        new Chart(ctx2, {
            type: 'bar',
            data: { labels: opLabels, datasets: [{ label: 'Desconto Total (R$)', data: opValues, backgroundColor: '#28a745' }] },
            options: { responsive: false, plugins: { legend: { display: false } } }
        });
    }
    // Hook para integração com discounts_analytics.js
    window.renderDiscountCharts = renderDiscountCharts;
});
