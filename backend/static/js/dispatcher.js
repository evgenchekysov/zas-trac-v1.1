function renderTest() {

    const tickets = [
        {id: 1, status: "NEW"},
        {id: 2, status: "IN_PROGRESS"},
        {id: 3, status: "PAUSED"}
    ];

    renderTickets(tickets);

}

function switchTab(tab) {

    document.getElementById("tickets-view")
        .classList.toggle("hidden", tab !== "tickets");

    document.getElementById("timeline-view")
        .classList.toggle("hidden", tab !== "timeline");

    document.getElementById("btn-tickets")
        .classList.toggle("text-blue-600", tab === "tickets");

    document.getElementById("btn-timeline")
        .classList.toggle("text-blue-600", tab === "timeline");
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}


function formatStatus(status) {

    const map = {
        NEW: "Новая",
        IN_PROGRESS: "В работе",
        PAUSED: "Пауза",
        DONE: "Завершена",
        CLOSED: "Закрыта"
    };

    return map[status] || status;
}


function statusColor(status) {

    const map = {
        NEW: "text-blue-500",
        IN_PROGRESS: "text-green-600",
        PAUSED: "text-yellow-600",
        DONE: "text-gray-500",
        CLOSED: "text-red-600"
    };

    return map[status] || "";
}

// ===== LOAD =====



async function load() {

    const token = localStorage.getItem("token");

    if (!token) {
        console.log("NO TOKEN");
        return;
    }

    const res = await fetch("/tickets/", {
        headers: {
            Authorization: "Bearer " + token
        }
    });

    const data = await res.json();

    if (!Array.isArray(data)) {
        console.error("API error:", data);
        return;
    }

    renderTickets(data);
    renderTimeline(data);
}


// ===== TICKETS =====
function renderTickets(tickets) {

    const container = document.getElementById("tickets");
    container.innerHTML = "";

    tickets.forEach(t => {

        const el = document.createElement("div");
        el.className = "bg-white p-4 rounded shadow";

        el.innerHTML = `
            <div class="flex justify-between items-center">

                <div>
                    <div class="font-bold">#${t.id}</div>
                    <div class="text-sm font-semibold
                        ${statusColor(t.status)}">
                        ${formatStatus(t.status)}
                    </div>
                </div>

                <div class="flex gap-2">

                    <button onclick="join(${t.id})"
                        class="bg-slate-500 text-white px-2 rounded">
                        JOIN
                    </button>

                    <button onclick="assign(${t.id})"
                        class="bg-purple-600 text-white px-2 rounded">
                        ASSIGN
                    </button>

                    <button onclick="start(${t.id})"
                        class="bg-blue-500 text-white px-2 rounded">
                        START
                    </button>

                    <button onclick="stop()"
                        class="bg-yellow-500 text-white px-2 rounded">
                        STOP
                    </button>

                    <button onclick="done(${t.id})"
                        class="bg-green-600 text-white px-2 rounded">
                        DONE
                    </button>

                    <button onclick="closeTicket(${t.id})"
                        class="bg-red-600 text-white px-2 rounded">
                        CLOSE
                    </button>

                </div>

            </div>
`;

        container.appendChild(el);
    });
}


// ===== TIMELINE =====
function renderTimeline(tickets) {

    const container = document.getElementById("timeline");
    container.innerHTML = "";

    const users = {};

    tickets.forEach(t => {
        (t.sessions || []).forEach(s => {

            if (!users[s.user_id]) {
                users[s.user_id] = 0;
            }

            users[s.user_id]++;
        });
    });

    Object.keys(users).forEach(user => {

        const el = document.createElement("div");
        el.className = "bg-white p-3 rounded shadow";

        el.innerHTML = `
            <div class="font-bold">${user}</div>
            <div class="text-sm">Сессий: ${users[user]}</div>
        `;

        container.appendChild(el);
    });
}


// ===== ACTIONS =====
async function start(id) {
    await fetch(`/tickets/${id}/start`, { method: "POST",
        headers: { Authorization: "Bearer " + localStorage.getItem("token") }
    });
    load();
}

async function join(id) {
    await fetch(`/tickets/${id}/join`, { method: "POST",
        headers: { Authorization: "Bearer " + localStorage.getItem("token") }
    });
    load();
}

async function stop() {
    await fetch(`/sessions/stop`, { method: "POST",
        headers: { Authorization: "Bearer " + localStorage.getItem("token") }
    });
    load();
}

async function done(id) {
    await fetch(`/tickets/${id}/done`, { method: "POST",
        headers: { Authorization: "Bearer " + localStorage.getItem("token") }
    });
    load();
}


async function closeTicket(id) {
    await fetch(`/tickets/${id}/close`, {
        method: "POST",
        headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
        }
    });

    load();
}


async function assign(id) {

    const userId = prompt("Введите ID исполнителя");

    if (!userId) return;

    await fetch(`/tickets/${id}/assign`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token")
        },
        body: JSON.stringify([userId])
    });

    load();
}
    

// ===== INIT =====
load();
setInterval(load, 5000);


//renderTest();
