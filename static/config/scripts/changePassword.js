function showStep(etapa) {
    // Ocultar todos os formulários
    document.getElementById('etapa1-form').classList.add('hidden');
    document.getElementById('etapa2-form').classList.add('hidden');
    document.getElementById('etapa3-form').classList.add('hidden');

    // Mostrar o formulário da etapa especificada
    document.getElementById(etapa).classList.remove('hidden');
}

showStep('{{ etapa }}');

function checkCode() {
    var codigoInserido = document.getElementById('codigo').value; // Obtém o código inserido pelo usuário
    var codigoGerado = '{{ codigo }}'; // Obtém o código gerado pelo servidor
    if (codigoInserido === codigoGerado) {
        // Código correto, redirecione o usuário para a próxima etapa
        showStep('etapa3-form');
    } else {
        // Código incorreto, exiba uma mensagem de erro (você pode usar alert, exibir uma mensagem na página, etc.)
        alert('Código incorreto. Tente novamente.');
    }
}