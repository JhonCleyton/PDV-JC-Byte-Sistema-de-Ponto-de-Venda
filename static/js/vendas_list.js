// Função para abrir o modal de edição de tipo de venda
function openEditTypeModal(saleId, currentType) {
    document.getElementById('edit-sale-id').value = saleId;
    document.getElementById('edit-payment-method').value = currentType;
    const modal = new bootstrap.Modal(document.getElementById('editTypeModal'));
    modal.show();
}

// Função para salvar o novo tipo de venda
async function saveEditType() {
    const saleId = document.getElementById('edit-sale-id').value;
    const newType = document.getElementById('edit-payment-method').value;
    if (!saleId || !newType) return;
    try {
        const response = await fetch(`/vendas/api/sales/update_type/${saleId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ payment_method: newType })
        });
        const data = await response.json();
        if (data.success) {
            location.reload();
        } else {
            alert(data.error || 'Erro ao atualizar tipo de venda.');
        }
    } catch (err) {
        alert('Erro ao atualizar tipo de venda.');
        console.error(err);
    }
}

// Função para renderizar tabela de vendas
function renderVendasTable(sales) {
    const tbody = document.getElementById('tbody-vendas');
    tbody.innerHTML = '';
    sales.forEach(sale => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${sale.id}</td>
            <td>${sale.date}</td>
            <td>${sale.customer}</td>
            <td>R$ ${sale.total.toFixed(2)}</td>
            <td>${sale.payment_method}</td>
            <td>${renderStatusBadge(sale.status)}</td>
            <td>
                <div class="btn-group">
                    <button type="button" class="btn btn-sm btn-outline-secondary" onclick="viewSale(${sale.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-warning" onclick="openEditTypeModal(${sale.id}, '${sale.payment_method}')">
                        <i class="bi bi-pencil"></i> Editar Tipo
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="deleteSale(${sale.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderStatusBadge(status) {
    if (status === 'concluída') return '<span class="badge bg-success">Concluída</span>';
    if (status === 'pendente') return '<span class="badge bg-warning">Pendente</span>';
    if (status === 'cancelada') return '<span class="badge bg-danger">Cancelada</span>';
    return status;
}

function renderPaginacao(pages, pageAtual) {
    const paginacao = document.getElementById('paginacao-vendas');
    paginacao.innerHTML = '';
    if (pages <= 1) return;
    for (let i = 1; i <= pages; i++) {
        const li = document.createElement('li');
        li.className = 'page-item' + (i === pageAtual ? ' active' : '');
        li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        li.addEventListener('click', function(e) {
            e.preventDefault();
            carregarVendas(i);
        });
        paginacao.appendChild(li);
    }
}

async function carregarVendas(page = 1) {
    const startDate = document.getElementById('filtro-data-inicio').value;
    const endDate = document.getElementById('filtro-data-fim').value;
    const paymentMethod = document.getElementById('filtro-pagamento').value;
    const perPage = document.getElementById('filtro-per-page').value;
    const params = new URLSearchParams({
        page,
        per_page: perPage,
        start_date: startDate,
        end_date: endDate,
        payment_method: paymentMethod
    });
    try {
        const resp = await fetch(`/vendas/api/sales/list?${params.toString()}`);
        const data = await resp.json();
        if (data.success) {
            renderVendasTable(data.sales);
            renderPaginacao(data.pages, page);
        } else {
            alert('Erro ao carregar vendas: ' + (data.error || ''));
        }
    } catch (err) {
        alert('Erro ao carregar vendas.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const saveTypeBtn = document.getElementById('save-type-btn');
    if (saveTypeBtn) {
        saveTypeBtn.addEventListener('click', saveEditType);
    }
    // Filtros e paginação
    document.getElementById('filtros-venda').addEventListener('submit', function(e) {
        e.preventDefault();
        carregarVendas(1);
    });
    // Carrega vendas ao abrir a página
    carregarVendas(1);
});
