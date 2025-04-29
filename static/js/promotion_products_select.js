// JS para busca de produtos por nome/código e seleção dinâmica
let selectedProducts = [];

function renderSelectedProducts() {
    const container = document.getElementById('selectedProducts');
    container.innerHTML = '';
    selectedProducts.forEach(prod => {
        const div = document.createElement('div');
        div.className = 'badge bg-primary m-1';
        div.innerHTML = prod.name + ' (' + prod.code + ') <span style="cursor:pointer;" data-id="' + prod.id + '">&times;</span>';
        div.querySelector('span').onclick = function(e) {
            e.stopPropagation();
            selectedProducts = selectedProducts.filter(p => p.id !== prod.id);
            renderSelectedProducts();
            updateHiddenInput();
        };
        container.appendChild(div);
    });
}

function updateHiddenInput() {
    const hidden = document.getElementById('selectedProductsInput');
    hidden.value = selectedProducts.map(p => p.id).join(',');
}

async function searchProductsPromotion(query) {
    if (!query || query.length < 3) return [];
    const resp = await fetch(`/api/products/search?q=${encodeURIComponent(query)}`);
    if (!resp.ok) return [];
    const data = await resp.json();
    if (data.success && data.products) return data.products;
if (data.success && data.data) return data.data;
return [];
}

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('productSearchInput');
    const results = document.getElementById('productSearchResults');
    input.addEventListener('input', async function() {
        const q = input.value.trim();
        if (q.length < 3) { results.innerHTML = ''; return; }
        const found = await searchProductsPromotion(q);
        results.innerHTML = '';
        found.forEach(prod => {
            if (selectedProducts.some(p => p.id === prod.id)) return;
            const li = document.createElement('li');
            li.className = 'list-group-item list-group-item-action';
            li.textContent = prod.name + ' (' + prod.code + ')';
            li.onclick = function(e) {
                e.stopPropagation();
                if (!selectedProducts.some(p => p.id === prod.id)) {
                    selectedProducts.push(prod);
                    renderSelectedProducts();
                    updateHiddenInput();
                }
                results.innerHTML = '';
                input.value = '';
                input.focus();
            };
            results.appendChild(li);
        });
    });

    // Inicializa se já há produtos selecionados (para edição)
    if (window.initialSelectedProducts) {
        window.initialSelectedProducts.forEach(prod => selectedProducts.push(prod));
        renderSelectedProducts();
        updateHiddenInput();
    }
});
