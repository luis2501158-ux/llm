const modeField = document.querySelector('#mode');
const textField = document.querySelector('#text');
const submitButton = document.querySelector('#submit');
const resultField = document.querySelector('#result');
const historyList = document.querySelector('#history');
const refreshButton = document.querySelector('#refresh');

async function fetchHistory() {
  try {
    const response = await fetch('/api/history');
    if (!response.ok) {
      throw new Error('No se pudo cargar el historial');
    }
    const entries = await response.json();
    historyList.innerHTML = entries.map(entry => {
      return `<li><strong>${entry.mode}</strong> — <span>${new Date(entry.created_at).toLocaleString()}</span><br><em>${entry.prompt}</em><p>${entry.result}</p></li>`;
    }).join('');
  } catch (error) {
    historyList.innerHTML = `<li class="error">${error.message}</li>`;
  }
}

async function submitRequest() {
  const mode = modeField.value;
  const text = textField.value.trim();
  if (!text) {
    resultField.textContent = 'Por favor ingresa un texto o una idea.';
    return;
  }

  resultField.textContent = 'Procesando...';
  submitButton.disabled = true;

  try {
    const response = await fetch('/api/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode, text }),
    });

    if (!response.ok) {
      const payload = await response.json();
      throw new Error(payload.detail || 'Error en la petición');
    }

    const data = await response.json();
    resultField.textContent = data.result;
    fetchHistory();
  } catch (error) {
    resultField.textContent = `Error: ${error.message}`;
  } finally {
    submitButton.disabled = false;
  }
}

submitButton.addEventListener('click', submitRequest);
refreshButton.addEventListener('click', fetchHistory);
window.addEventListener('load', fetchHistory);
