const button = document.getElementById("askButton");

button.addEventListener("click", async () => {

    const message = document.getElementById("message").value;

    const passportReceived =
        document.querySelector('input[name="passport"]:checked').value === "received";

    const response = await fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            passport_received: passportReceived,
            message: message
        })
    });

    const data = await response.json();

    document.getElementById("answer").textContent = data.answer;
});