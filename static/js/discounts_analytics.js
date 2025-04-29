$(document).ready(function() {
    function fetchDiscounts() {
        const produto = $('#filtro-produto').val();
        const startDate = $('#filtro-data-inicio').val();
        const endDate = $('#filtro-data-fim').val();
        $.ajax({
            url: '/management/analytics/api/discounts_analytics',
            method: 'GET',
            data: {
                produto: produto,
                start_date: startDate,
                end_date: endDate
            },
            success: function(response) {
                const tbody = $('#tabela-descontos tbody');
                tbody.empty();
                if (window.renderDiscountCharts) {
                    window.renderDiscountCharts(response.data);
                }
                if (response.success && response.data.length > 0) {
                    response.data.forEach(function(item) {
                        tbody.append(`
                            <tr>
                                <td>${item.data}</td>
                                <td>${item.venda_id}</td>
                                <td>${item.produto}</td>
                                <td>${item.promo_nome ? item.promo_nome : '-'}</td>
                                <td>${item.valor_original}</td>
                                <td>${item.valor_promo}</td>
                                <td>${item.diferença}</td>
                                <td>${item.desconto_percentual}</td>
                                <td>${item.operador}</td>
                            </tr>
                        `);
                    });
                } else {
                    tbody.append('<tr><td colspan="7" class="text-center">Nenhum desconto encontrado.</td></tr>');
                }
            },
            error: function() {
                alert('Erro ao buscar dados de descontos.');
            }
        });
    }

    $('#filtro-descontos').on('submit', function(e) {
        e.preventDefault();
        fetchDiscounts();
    });

    fetchDiscounts();
});
