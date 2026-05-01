// Placeholder JS — sera remplacé à l'étape 12 du plan.

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("ping-btn");
    const out = document.getElementById("ping-result");

    btn.addEventListener("click", async () => {
        out.textContent = "Chargement…";
        try {
            const res = await fetch("/api/health");
            const data = await res.json();
            out.textContent = JSON.stringify(data, null, 2);
        } catch (err) {
            out.textContent = "Erreur : " + err.message;
        }
    });
});
