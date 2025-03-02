document.addEventListener("DOMContentLoaded", () => {
    const qaList = document.getElementById("qa-list");
    const topQuestioners = document.getElementById("top-questioners");
    const topAnswerers = document.getElementById("top-answerers");

    // ✅ Function to update the Q&A list (Groups multiple answers under one question)
    function updateQAList(qaPairs) {
        if (!qaPairs || !Array.isArray(qaPairs) || qaPairs.length === 0) {
            qaList.innerHTML = `<p class="text-center text-gray-600">No questions available.</p>`;
            return;
        }

        qaList.innerHTML = qaPairs.map(qa => `
            <div class="overflow-hidden rounded-3xl bg-white shadow-lg transition-all hover:shadow-xl">
                <div class="p-6">
                    <div class="mb-4">
                        <h3 class="text-xl font-semibold text-gray-900">Question</h3>
                        <p class="mt-2 text-gray-700">${qa.question}</p>
                        <p class="mt-2 text-sm text-gray-500">
                            Asked by <strong>${qa.name}</strong> (Age: ${qa.age})
                        </p>
                    </div>

                    ${qa.answers && qa.answers.length > 0 ? `
                        <div class="border-t border-gray-100 pt-4">
                            <h3 class="text-xl font-semibold text-gray-900">Answers</h3>
                            ${qa.answers.map(ans => `
                                <div class="mt-2 p-3 rounded-lg bg-gray-100">
                                    <p class="text-gray-700">${ans.answer}</p>
                                    <p class="mt-1 text-sm text-gray-500">
                                        Answered by <strong>${ans.answerer_name || "Anonymous"}</strong> 
                                        (Age: ${ans.answerer_age || "Unknown"})
                                    </p>
                                </div>
                            `).join("")}
                        </div>
                    ` : `<p class="mt-4 text-sm font-medium text-red-500">
                        This question hasn't been answered yet.
                    </p>`}
                </div>
            </div>
        `).join("");
    }

    // ✅ Function to update the leaderboard correctly
    function updateLeaderboard(data) {
        console.log("Leaderboard Data:", data); // Debugging: Check if leaderboard data is correct

        // Top Questioners
        if (data.questioners && data.questioners.length > 0) {
            topQuestioners.innerHTML = data.questioners.map(q => `
                <li class="flex items-center justify-between rounded-full bg-red-50 px-4 py-2">
                    <span class="font-medium text-gray-900">${q.name}</span>
                    <span class="text-sm text-red-500">${q.count} questions</span>
                </li>
            `).join("");
        } else {
            topQuestioners.innerHTML = `<p class="text-gray-600">No top questioners yet.</p>`;
        }

        // Top Answerers
        if (data.answerers && data.answerers.length > 0) {
            topAnswerers.innerHTML = data.answerers.map(a => `
                <li class="flex items-center justify-between rounded-full bg-blue-50 px-4 py-2">
                    <span class="font-medium text-gray-900">${a.name}</span>
                    <span class="text-sm text-blue-500">${a.count} answers</span>
                </li>
            `).join("");
        } else {
            topAnswerers.innerHTML = `<p class="text-gray-600">No top answerers yet.</p>`;
        }
    }

    // ✅ Fetch Data from Backend
    function fetchData() {
        fetch("http://127.0.0.1:5000/get-questions")
            .then(response => response.json())
            .then(data => {
                console.log("Received Questions Data:", data); // Debugging
                updateQAList(data.questions || []);  // ✅ Prevents errors when no questions exist
            })
            .catch(error => console.error("Error loading questions:", error));

        fetch("http://127.0.0.1:5000/get-leaderboard")
            .then(response => response.json())
            .then(data => {
                console.log("Received Leaderboard Data:", data); // Debugging
                updateLeaderboard(data);
            })
            .catch(error => console.error("Error loading leaderboard:", error));
    }

    // Refresh every 5 seconds
    setInterval(fetchData, 5000);
    fetchData(); // Initial fetch
});
