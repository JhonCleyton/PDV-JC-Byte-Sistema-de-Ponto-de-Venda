# PDV JC Byte - Interface PyQt

O PDV JC Byte agora conta com uma interface gráfica própria desenvolvida com PyQt5, oferecendo uma experiência mais integrada e moderna.

## Principais Características

1. **Interface Nativa**: Janela própria do sistema, sem depender de navegadores externos
2. **Detecção de IP Automática**: Identifica o IP da rede automaticamente para facilitar o acesso de outros dispositivos
3. **Design Consistente**: Mantém a identidade visual do PDV com o tema dourado e logo personalizado
4. **Inicialização Simplificada**: Inicia o servidor Flask e a interface gráfica com um único comando

## Requisitos

Para utilizar o PDV com interface PyQt, é necessário instalar as seguintes dependências:

```
PyQt5==5.15.9
PyQt5-Qt5==5.15.2
PyQt5-sip==12.12.1
PyQtWebEngine==5.15.6
PyQtWebEngine-Qt5==5.15.2
```

Estas dependências já foram adicionadas ao arquivo `requirements.txt` e serão instaladas automaticamente pelo script de inicialização.

## Como Iniciar

Existem duas maneiras de iniciar o PDV com a interface PyQt:

### 1. Usando o script BAT (Recomendado)

Execute o arquivo `iniciar_pdv_qt.bat` com um duplo clique. Este script:
- Verifica se as dependências do PyQt estão instaladas
- Instala as dependências, se necessário
- Inicia a aplicação PyQt

### 2. Diretamente pelo Python

```
python iniciar_pdv_qt.py
```

## Funcionamento

Quando iniciado, o aplicativo:

1. Inicia o servidor Flask em uma thread separada
2. Detecta automaticamente o IP da máquina na rede
3. Abre uma janela com o logo do PDV e a interface web incorporada
4. Exibe o endereço utilizado na barra de status (ex: http://192.168.1.100:5000)

Se não for encontrado um IP de rede, o sistema utilizará automaticamente `localhost:5000`.

## Personalizações

O código do arquivo `iniciar_pdv_qt.py` pode ser facilmente personalizado para ajustar:

- Dimensões da janela
- Cores e estilos
- Elementos visuais adicionais
- Comportamento da aplicação

## Resolução de Problemas

Se você encontrar problemas ao executar a aplicação:

1. **Erro de dependências**: Execute manualmente `pip install PyQt5 PyQtWebEngine`
2. **Servidor não inicia**: Verifique se o Flask está instalado e funcionando corretamente
3. **Problemas de rede**: Verifique se o IP detectado está correto na barra de status

Para qualquer outro problema, consulte a documentação ou entre em contato com o suporte.
