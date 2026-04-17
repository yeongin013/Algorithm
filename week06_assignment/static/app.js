async function runCheck() {
  const textA = document.getElementById("textA").value;
  const textB = document.getElementById("textB").value;
  const btn = document.getElementById("checkBtn");

  btn.disabled = true;
  btn.textContent = "Checking...";

  try {
    const res = await fetch("/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text_a: textA, text_b: textB }),
    });

    if (!res.ok) {
      alert("Server error: " + res.status);
      return;
    }

    const data = await res.json();
    renderResults(data);
  } catch (err) {
    alert("Request failed: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Check";
  }
}

function renderResults(data) {
  document.getElementById("similarity").textContent = data.similarity + "%";
  document.getElementById("lcsLength").textContent = data.lcs_length;
  document.getElementById("lcsString").textContent = data.lcs || "(empty)";

  renderDiff("diffA", data.diff_a);
  renderDiff("diffB", data.diff_b);

  document.getElementById("results").classList.remove("hidden");
}

/**
 * Render diff tokens into the target element using safe DOM methods.
 * Consecutive tokens of the same type are grouped into a single <span>.
 */
function renderDiff(elementId, tokens) {
  const container = document.getElementById(elementId);
  container.textContent = "";

  if (!tokens || tokens.length === 0) {
    const em = document.createElement("em");
    em.textContent = "(empty)";
    container.appendChild(em);
    return;
  }

  let i = 0;
  while (i < tokens.length) {
    const type = tokens[i].type;
    let text = "";
    while (i < tokens.length && tokens[i].type === type) {
      text += tokens[i].char;
      i++;
    }
    const span = document.createElement("span");
    span.className = type;
    span.textContent = text;
    container.appendChild(span);
  }
}
