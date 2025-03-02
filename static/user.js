document.addEventListener("DOMContentLoaded", () => {
    const submitQuestionForm = document.getElementById("submit-question");

    if (submitQuestionForm) {
        submitQuestionForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const name = document.getElementById("name").value;
            const age = document.getElementById("age").value;
            const question = document.getElementById("question").value;

            fetch("http://127.0.0.1:5000/submit-question", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, age, question })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    alert("✅ Question submitted successfully!");
                    window.location.href = "/"; // Redirect to homepage after submission
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("⚠️ Failed to submit question. Try again.");
            });
        });
    }
});
