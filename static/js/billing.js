function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(";").shift();
    }
    return "";
}

function showAlert(message, type) {
    const alert = document.getElementById("billing-alert");
    alert.className = `alert alert-${type}`;
    if (Array.isArray(message)) {
        const list = document.createElement("ul");
        list.className = "mb-0";
        message.forEach((item) => {
            const listItem = document.createElement("li");
            listItem.textContent = item;
            list.appendChild(listItem);
        });
        alert.replaceChildren(list);
        return;
    }
    alert.textContent = message;
}

function humanizeFieldName(fieldName) {
    return fieldName
        .replaceAll("_", " ")
        .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function flattenErrors(errorData, prefix = "") {
    if (!errorData) {
        return [];
    }

    if (typeof errorData === "string") {
        return [prefix ? `${humanizeFieldName(prefix)}: ${errorData}` : errorData];
    }

    if (Array.isArray(errorData)) {
        return errorData.flatMap((item) => flattenErrors(item, prefix));
    }

    if (typeof errorData === "object") {
        return Object.entries(errorData).flatMap(([field, value]) => {
            const fieldPrefix = prefix ? `${prefix}.${field}` : field;
            return flattenErrors(value, fieldPrefix);
        });
    }

    return [String(errorData)];
}

function formatApiErrors(data) {
    const detail = data?.detail || data;
    const messages = flattenErrors(detail);
    if (messages.length === 0) {
        return ["Unable to generate invoice. Please check the form and try again."];
    }
    return messages;
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
}

function collectItems() {
    return Array.from(document.querySelectorAll(".product-row")).map((row) => ({
        product_id: row.querySelector(".product-id").value,
        quantity: Number(row.querySelector(".quantity").value),
    }));
}

function collectDenominations() {
    return Array.from(document.querySelectorAll(".denomination-count")).map((input) => ({
        value: Number(input.dataset.value),
        count: Number(input.value || 0),
    }));
}

function createRowFromTemplate() {
    const firstRow = document.querySelector(".product-row");
    const row = firstRow.cloneNode(true);
    row.querySelector(".product-id").value = "";
    row.querySelector(".quantity").value = "1";
    return row;
}

document.addEventListener("click", (event) => {
    if (event.target.id === "add-row") {
        document.getElementById("product-rows").appendChild(createRowFromTemplate());
    }

    if (event.target.classList.contains("remove-row")) {
        const rows = document.querySelectorAll(".product-row");
        if (rows.length > 1) {
            event.target.closest(".product-row").remove();
        }
    }
});

document.getElementById("billing-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const customerEmail = document.getElementById("customer_email").value.trim();
    if (!isValidEmail(customerEmail)) {
        showAlert("Customer Email: Enter a valid email address.", "danger");
        document.getElementById("customer_email").focus();
        return;
    }

    const payload = {
        customer_email: customerEmail,
        paid_amount: document.getElementById("paid_amount").value,
        items: collectItems(),
        denominations: collectDenominations(),
    };

    try {
        const response = await fetch("/api/invoices/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) {
            showAlert(formatApiErrors(data), "danger");
            return;
        }
        window.location.href = `/invoices/${data.id}/`;
    } catch (error) {
        showAlert("Unable to generate invoice. Please try again.", "danger");
    }
});
