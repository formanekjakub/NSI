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
