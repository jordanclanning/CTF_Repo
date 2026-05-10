function checkCode() {
    const input = document.getElementById("code").value;
    const result = document.getElementById("result");

    // ❌ Client-side access control (insecure by design)
    const gateCode = "OPS-GATE-ALPHA-2026";

    if (input === gateCode) {
        result.innerText = "Access granted.\n\nSummit{Client_Side_Logic_Is_Not_Security}";
    } else {
        result.innerText = "Access denied.";
    }
}


