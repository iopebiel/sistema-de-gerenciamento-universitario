const step1 = document.getElementById('step1-form');
const step2 = document.getElementById('step2-form');
const step3 = document.getElementById('step3-form');
const step =

function showStep() {
    step1.classList.add('hidden');
    step2.classList.add('hidden');
    step3.classList.add('hidden');

    console.log(step)
    step.classList.remove('hidden');
}

function checkCode() {
    var codigoInserido = document.getElementById('codigo').value;
    var codigoGerado = {codigo}; 
    if (codigoInserido === codigoGerado) {
        showStep(step3);
    } else {
        alert('Código incorreto. Tente novamente.');
    }
}

showStep();