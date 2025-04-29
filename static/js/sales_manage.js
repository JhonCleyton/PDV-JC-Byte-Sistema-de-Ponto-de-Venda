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
        const response = await fetch(`/api/sales/update_type/${saleId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ payment_method: newType })
        });
        const data = await response.json();
        if (data.success) {
            // Atualiza a lista de vendas
            filterSales();
            bootstrap.Modal.getInstance(document.getElementById('editTypeModal')).hide();
        } else {
            alert(data.error || 'Erro ao atualizar tipo de venda.');
        }
    } catch (err) {
        alert('Erro ao atualizar tipo de venda.');
        console.error(err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const saveTypeBtn = document.getElementById('save-type-btn');
    if (saveTypeBtn) {
        saveTypeBtn.addEventListener('click', saveEditType);
    }
});
