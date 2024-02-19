
function abrirEditor() {
    var modal = document.getElementById("modalEditor");
    modal.style.display = "block";
}

function fecharEditor() {
    var modal = document.getElementById("modalEditor");
    modal.style.display = "none";
}


function abrirAlterarSenha() {
    var modal = document.getElementById('alterarSenhaModal');
    modal.style.display = 'block';
}

function fecharAlterarSenha() {
    var modal = document.getElementById('alterarSenhaModal');
    modal.style.display = 'none';
}

function enviarAlteracaoSenha() {
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('alterar-senha-form');

    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            const senhaAtual = document.getElementById('senha_atual').value;
            const novaSenha = document.getElementById('nova_senha').value;
            const confirmarSenha = document.getElementById('confirmar_senha').value;

            if (senhaAtual === '' || novaSenha === '' || confirmarSenha === '') {
                alert('Preencha todos os campos.');
                return;
            }

            if (novaSenha !== confirmarSenha) {
                alert('A nova senha e a confirmação da senha não coincidem.');
                return;
            }

            form.submit();
        });
    }
});
}