
function showModal(id) {
    var modal = document.getElementById(`modalEditor-${id}`);
    modal.style.display = "block";
}

function closeModal(id) {
    var modal = document.getElementById(`modalEditor-${id}`);
    modal.style.display = "none";
}


function showChangePassword() {
    var modal = document.getElementById('alterarSenhaModal');
    modal.style.display = 'block';
}

function closeChangePassword() {
    var modal = document.getElementById('alterarSenhaModal');
    modal.style.display = 'none';
}

function changePassword() {
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('alterar-senha-form');

    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            const oldPassword = document.getElementById('senha_atual').value;
            const newPassword = document.getElementById('nova_senha').value;
            const confirmPassword = document.getElementById('confirmar_senha').value;

            if (oldPassword === '' || newPassword === '' || confirmPassword === '') {
                alert('Preencha todos os campos.');
                return false;
            }

            if (newPassword !== confirmPassword) {
                alert('A nova senha e a confirmação da senha não coincidem.');
                return;
            }

            form.submit();
        });
    }
});
}