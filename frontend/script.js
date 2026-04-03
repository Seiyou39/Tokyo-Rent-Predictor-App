console.log("JS LOADED");
const form = document.getElementById("form");
const result = document.getElementById("result");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
        area: parseFloat(document.getElementById("area").value),
        walk: parseFloat(document.getElementById("walk").value),
        age: parseFloat(document.getElementById("age").value),
        floor: parseFloat(document.getElementById("floor").value),
        rooms: parseFloat(document.getElementById("rooms").value),
        ward: document.getElementById("ward").value,
        layout_type: document.getElementById("layout_type").value
    };

    result.innerText = "预测中...";

    const res = await fetch("/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    const json = await res.json();

    result.innerText = "预测租金: ¥" + Math.round(json.predicted_rent);
});