// static/script.js

async function deleteData(id) {
    if (!confirm(`Opravdu chcete smazat záznam #${id}?`)) return;
    try {
        const resp = await fetch(`/api/data/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        });

        if (!resp.ok) {
            const err = await resp.json();
            alert(`Chyba při mazání: ${err.error || err.message}`);
            return;
        }

        // Option A: remove the row in-place:
        document.getElementById(`row-${id}`).remove();

        // Option B: fully reload the page to re-fetch sorted data:
        // window.location.reload();
    }
    catch (e) {
        console.error(e);
        alert('Neznámá chyba při mazání.');
    }
}

async function deleteAllData(id) {
    if (!confirm(`Opravdu chcete smazat všechny záznamy?`)) return;
    try {
        const resp = await fetch(`/api/delete_all`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        });

        if (!resp.ok) {
            const err = await resp.json();
            alert(`Chyba při mazání: ${err.error || err.message}`);
            return;
        }
        window.location.reload();
    }
    catch (e) {
        console.error(e);
        alert('Neznámá chyba při mazání.');
    }
}

// static/script.js
document.addEventListener('DOMContentLoaded', () => {
  const thresholdInput = document.getElementById('threshold');
  const setBtn         = document.getElementById('setThresholdBtn');
  const statusMsg      = document.getElementById('thresholdStatus');

  setBtn.addEventListener('click', async () => {
    const val = parseInt(thresholdInput.value, 10);
    if (isNaN(val)) {
      statusMsg.textContent = 'Zadejte platné číslo.';
      statusMsg.classList.add('error');
      return;
    }

    try {
      // ← point at the correct URL
      const res = await fetch('/api/threshold', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ threshold: val })
      });

      const data = await res.json();
      if (res.ok) {
        statusMsg.textContent = `Práh nastaven: ${data.threshold}`;
        statusMsg.classList.remove('error');
        statusMsg.classList.add('success');
      } else {
        statusMsg.textContent = `Chyba: ${data.error || 'něco se pokazilo'}`;
        statusMsg.classList.add('error');
      }
    } catch (err) {
      statusMsg.textContent = 'Server nedostupný.';
      statusMsg.classList.add('error');
    }
  });
});

