const step1 = document.getElementById('step1-form');
const step2 = document.getElementById('step2-form');
const step3 = document.getElementById('step3-form');
let stepSelected = document.getElementById('{{ step }}')

function showStep() {
    step1.classList.add('hidden');
    step2.classList.add('hidden');
    step3.classList.add('hidden');

    stepSelected.classList.remove('hidden');
}

function checkCode() {
    var codigoInserido = document.getElementById('code_user').value;
    var codigoGerado = '{{ code }}';
    if (codigoInserido === codigoGerado) {
        showStep(step3);
    } else {
        alert('Código incorreto. Tente novamente.');
    }
}

showStep();