document.addEventListener('DOMContentLoaded', function () {
    const toggleTabButton = document.getElementById('toggleTab');
    const tab = document.getElementById('tab');

    toggleTabButton.addEventListener('click', function () {
        tab.classList.toggle('hidden');
    });
});


function abrirEditor() {
    var modal = document.getElementById("modalEditor");
    modal.style.display = "block";
}

function fecharEditor() {
    var modal = document.getElementById("modalEditor");
    modal.style.display = "none";
}
function salvarEdicao() {
    var novoNome = document.getElementById('nome').value;
    var novoEmail = document.getElementById('email').value;
    var novoCurso = document.getElementById('curso').value;
    var novoSemestre = document.getElementById('semestre').value;

    // Envie os dados atualizados para o servidor
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/atualizar_perfil', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send('nome=' + novoNome + '&email=' + novoEmail + '&curso=' + novoCurso + '&semestre=' + novoSemestre);

    xhr.onload = function () {
        if (xhr.status === 200) {
            // Sucesso, você pode adicionar feedback ao usuário se desejar
            alert('Perfil atualizado com sucesso.');
            document.getElementById('nomePerfil').textContent = novoNome;
            document.getElementById('emailPerfil').textContent = novoEmail;
            document.getElementById('cursoPerfil').textContent = novoCurso;
            document.getElementById('semestrePerfil').textContent = novoSemestre;
        } else {
            // Lidar com erros, se houver
            alert('Erro ao atualizar o perfil.');
        }

        // Oculte o editor
        document.getElementById('editor-form').style.display = 'none';
    };
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
    
        form.addEventListener('submit', function (event) {
            event.preventDefault();
    
            const senhaAtual = document.getElementById('senha_atual').value;
            const novaSenha = document.getElementById('nova_senha').value;
            const confirmarSenha = document.getElementById('confirmar_senha').value;
    
            // Realize validações apropriadas aqui (por exemplo, verificar se as senhas coincidem)
            if (senhaAtual === '' || novaSenha === '' || confirmarSenha === '') {
                alert('Preencha todos os campos.');
                return;
            }
    
            if (novaSenha !== confirmarSenha) {
                alert('A nova senha e a confirmação da senha não coincidem.');
                return;
            }
    
            // Se as validações passarem, envie o formulário
            form.submit();
        });
    });
    fecharAlterarSenha();
}