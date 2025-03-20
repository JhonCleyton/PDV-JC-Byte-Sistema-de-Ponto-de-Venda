// Função para exibir diálogo personalizado de confirmação
function exibirDialogoSaida() {
    return new Promise((resolve) => {
        // Criar overlay
        const overlay = document.createElement('div');
        overlay.className = 'dialogo-overlay';
        
        // Criar modal
        const modal = document.createElement('div');
        modal.className = 'dialogo-modal';
        
        // Conteúdo do modal
        modal.innerHTML = `
            <div class="dialogo-header">
                <h3>Atenção</h3>
            </div>
            <div class="dialogo-body">
                <div class="dialogo-icone">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="dialogo-mensagem">
                    <p>Tem certeza que deseja sair desta página?</p>
                    <p>As alterações não salvas serão perdidas.</p>
                </div>
            </div>
            <div class="dialogo-footer">
                <button class="dialogo-btn dialogo-btn-secundario" id="dialogo-cancelar">Cancelar</button>
                <button class="dialogo-btn dialogo-btn-primario" id="dialogo-confirmar">Confirmar</button>
            </div>
        `;
        
        // Adicionar ao documento
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        
        // Animação de entrada
        setTimeout(() => {
            overlay.style.opacity = '1';
            modal.style.transform = 'translateY(0)';
        }, 10);
        
        // Event listeners
        document.getElementById('dialogo-cancelar').addEventListener('click', () => {
            fecharDialogo();
            resolve(false);
        });
        
        document.getElementById('dialogo-confirmar').addEventListener('click', () => {
            fecharDialogo();
            resolve(true);
        });
        
        // Função para fechar o diálogo
        function fecharDialogo() {
            modal.style.transform = 'translateY(-20px)';
            overlay.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(overlay);
            }, 300);
        }
    });
}

// Função para interceptar tentativas de sair da página
async function interceptarSaida(event) {
    // Verificar se o caixa está aberto (variável global)
    if (window.caixaAberto) {
        // Se este for o evento beforeunload
        if (event.type === 'beforeunload') {
            // Mensagem para navegadores que ignoram preventDefault
            const mensagem = 'Tem certeza que deseja sair? As alterações podem não ser salvas.';
            event.returnValue = mensagem;
            return mensagem;
        } else {
            // Para outros eventos (cliques em links, etc)
            event.preventDefault();
            const confirmar = await exibirDialogoSaida();
            if (confirmar) {
                // Se for um link, navegar para o href
                if (event.currentTarget.href) {
                    window.location.href = event.currentTarget.href;
                }
                // Se for um formulário, enviar
                else if (event.currentTarget.tagName === 'FORM') {
                    event.currentTarget.submit();
                }
            }
        }
    }
}

// Inicialização quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Sobrescrever o comportamento padrão para todos os links que saem da página
    const links = document.querySelectorAll('a[href]:not([href^="#"]):not([target="_blank"])');
    
    links.forEach(link => {
        link.addEventListener('click', interceptarSaida);
    });
    
    // Para formulários
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', interceptarSaida);
    });
    
    // Sobrescrever o comportamento nativo do beforeunload para mostrar um modal estilizado
    // Isso só funciona para cliques específicos, não para fechamento de aba/navegador
    window.addEventListener('beforeunload', interceptarSaida);
});
