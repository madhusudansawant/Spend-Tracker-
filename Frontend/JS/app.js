// const API_BASE_URL = "http://127.0.0.1:8000/api";

const API_BASE_URL = "https://spend-tracker-backend-7zow.onrender.com/api";

/* =========================================================
   DOM ELEMENTS
========================================================= */

const $ = (id) => document.getElementById(id);

const authSection = $("authSection");
const loginSection = $("loginSection");
const registerSection = $("registerSection");
const dashboardSection = $("dashboardSection");

const loginTab = $("loginTab");
const registerTab = $("registerTab");

const loginForm = $("loginForm");
const registerForm = $("registerForm");
const expenseForm = $("expenseForm");

const loginMessage = $("loginMessage");
const registerMessage = $("registerMessage");
const expenseMessage = $("expenseMessage");

const loginBtn = $("loginBtn");
const registerBtn = $("registerBtn");
const addExpenseBtn = $("addExpenseBtn");

const logoutBtn = $("logoutBtn");
const welcomeUser = $("welcomeUser");

const totalSpend = $("totalSpend");
const previousMonthSpend = $("previousMonthSpend");
const monthChange = $("monthChange");
const summaryMonth = $("summaryMonth");

const categoryList = $("categoryList");
const expenseList = $("expenseList");

const filterBtn = $("filterBtn");
const clearFilterBtn = $("clearFilterBtn");

const filterCategory = $("filterCategory");
const startDate = $("startDate");
const endDate = $("endDate");

const insightsSection = $("insightsSection");
const insightsList = $("insightsList");

const amountInput = $("amount");
const categoryInput = $("category");
const noteInput = $("note");
const dateInput = $("date");

const loginEmail = $("loginEmail");
const loginPassword = $("loginPassword");

const firstNameInput = $("firstName");
const lastNameInput = $("lastName");
const registerEmail = $("registerEmail");
const registerPassword = $("registerPassword");
const registerPassword2 = $("registerPassword2");


/* =========================================================
   TOKEN HELPERS
========================================================= */

function getAccessToken() {
    return localStorage.getItem("access_token");
}

function getRefreshToken() {
    return localStorage.getItem("refresh_token");
}

function saveTokens(access, refresh) {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
}

function clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_name");
}


/* =========================================================
   API REQUEST
========================================================= */

async function apiRequest(url, options = {}, retry = true) {
    const token = getAccessToken();

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {}),
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    let response;

    try {
        response = await fetch(url, {
            ...options,
            headers,
        });
    } catch (error) {
        console.error("Network error:", error);
        throw new Error("Unable to connect to the server.");
    }

    /*
       If access token expired, try refreshing it once.
    */

    if (response.status === 401 && retry && getRefreshToken()) {
        const refreshed = await refreshAccessToken();

        if (refreshed) {
            return apiRequest(url, options, false);
        }

        clearTokens();
        showLogin();

        return response;
    }

    return response;
}


/* =========================================================
   REFRESH ACCESS TOKEN
========================================================= */

async function refreshAccessToken() {
    const refresh = getRefreshToken();

    if (!refresh) {
        return false;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/auth/refresh/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    refresh,
                }),
            }
        );

        if (!response.ok) {
            clearTokens();
            return false;
        }

        const result = await response.json();

        const accessToken =
            result.access ||
            result.data?.access;

        if (!accessToken) {
            clearTokens();
            return false;
        }

        localStorage.setItem(
            "access_token",
            accessToken
        );

        return true;

    } catch (error) {
        console.error(
            "Token refresh failed:",
            error
        );

        return false;
    }
}


/* =========================================================
   LOGIN / REGISTER TABS
========================================================= */

loginTab.addEventListener("click", showLoginForm);

registerTab.addEventListener("click", showRegisterForm);


function showLoginForm() {
    loginSection.classList.remove("hidden");
    registerSection.classList.add("hidden");

    loginTab.classList.add("active");
    registerTab.classList.remove("active");

    setMessage(loginMessage, "", "");
    setMessage(registerMessage, "", "");
}


function showRegisterForm() {
    loginSection.classList.add("hidden");
    registerSection.classList.remove("hidden");

    loginTab.classList.remove("active");
    registerTab.classList.add("active");

    setMessage(loginMessage, "", "");
    setMessage(registerMessage, "", "");
}


/* =========================================================
   REGISTER
========================================================= */

registerForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        const firstName = firstNameInput.value.trim();
        const lastName = lastNameInput.value.trim();
        const email = registerEmail.value.trim();
        const password = registerPassword.value;
        const password2 = registerPassword2.value;

        if (!password || !password2) {
            setMessage(
                registerMessage,
                "Please enter both passwords.",
                "error"
            );
            return;
        }

        if (password !== password2) {
            setMessage(
                registerMessage,
                "Passwords do not match.",
                "error"
            );
            return;
        }

        registerBtn.disabled = true;
        registerBtn.textContent = "Creating account...";

        setMessage(
            registerMessage,
            "Creating account...",
            ""
        );

        try {
            const response = await fetch(
                `${API_BASE_URL}/auth/register/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        email,
                        first_name: firstName,
                        last_name: lastName,
                        password,
                        password2,
                    }),
                }
            );

            const result = await parseResponse(response);

            if (!response.ok) {
                setMessage(
                    registerMessage,
                    getErrorMessage(result),
                    "error"
                );
                return;
            }

            setMessage(
                registerMessage,
                "Account created successfully. You can now login.",
                "success"
            );

            registerForm.reset();

            setTimeout(() => {
                showLoginForm();
                loginEmail.value = email;
            }, 1000);

        } catch (error) {
            console.error(
                "Registration error:",
                error
            );

            setMessage(
                registerMessage,
                error.message ||
                    "Unable to connect to the server.",
                "error"
            );

        } finally {
            registerBtn.disabled = false;
            registerBtn.textContent = "Create Account";
        }
    }
);


/* =========================================================
   LOGIN
========================================================= */

loginForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        const email = loginEmail.value.trim();
        const password = loginPassword.value;

        loginBtn.disabled = true;
        loginBtn.textContent = "Logging in...";

        setMessage(
            loginMessage,
            "Logging in...",
            ""
        );

        try {
            const response = await fetch(
                `${API_BASE_URL}/auth/login/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        email,
                        password,
                    }),
                }
            );

            const result = await parseResponse(response);

            if (!response.ok) {
                setMessage(
                    loginMessage,
                    getErrorMessage(result),
                    "error"
                );
                return;
            }

            console.log("Login response:", result);

            const authData = result.data;

            if (
                !authData ||
                !authData.tokens
            ) {
                console.error(
                    "Unexpected login response:",
                    result
                );

                setMessage(
                    loginMessage,
                    "Login succeeded but token response is invalid.",
                    "error"
                );

                return;
            }

            const access = authData.tokens.access;
            const refresh = authData.tokens.refresh;

            if (!access || !refresh) {
                setMessage(
                    loginMessage,
                    "Login succeeded but tokens are missing.",
                    "error"
                );

                return;
            }

            saveTokens(access, refresh);

            /* Save user name */

            const user = authData.user;

            if (user) {
                const fullName = [
                    user.first_name,
                    user.last_name,
                ]
                    .filter(Boolean)
                    .join(" ")
                    .trim();

                localStorage.setItem(
                    "user_name",
                    fullName
                );
            }

            loginForm.reset();

            showDashboard();

            await loadDashboard();

        } catch (error) {
            console.error(
                "Login error:",
                error
            );

            setMessage(
                loginMessage,
                error.message ||
                    "Unable to connect to the server.",
                "error"
            );

        } finally {
            loginBtn.disabled = false;
            loginBtn.textContent = "Login";
        }
    }
);


/* =========================================================
   ADD EXPENSE
========================================================= */

expenseForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        const amount = amountInput.value;
        const category = categoryInput.value.trim();
        const note = noteInput.value.trim();
        const date = dateInput.value;

        addExpenseBtn.disabled = true;
        addExpenseBtn.textContent = "Adding...";

        setMessage(
            expenseMessage,
            "",
            ""
        );

        try {
            const response = await apiRequest(
                `${API_BASE_URL}/expenses/`,
                {
                    method: "POST",
                    body: JSON.stringify({
                        amount,
                        category,
                        note,
                        date,
                    }),
                }
            );

            const result = await parseResponse(response);

            if (!response.ok) {
                setMessage(
                    expenseMessage,
                    getErrorMessage(result),
                    "error"
                );
                return;
            }

            setMessage(
                expenseMessage,
                "Expense added successfully.",
                "success"
            );

            expenseForm.reset();

            setTodayDate();

            await loadDashboard();

        } catch (error) {
            console.error(
                "Expense error:",
                error
            );

            setMessage(
                expenseMessage,
                error.message ||
                    "Unable to save expense.",
                "error"
            );

        } finally {
            addExpenseBtn.disabled = false;
            addExpenseBtn.textContent = "Add Expense";
        }
    }
);


/* =========================================================
   DASHBOARD
========================================================= */

async function loadDashboard() {
    /*
       Summary and expenses are independent requests,
       so load them at the same time.
    */

    await Promise.all([
        loadSummary(),
        loadExpenses(),
    ]);
}


/* =========================================================
   SUMMARY
========================================================= */

async function loadSummary() {
    try {
        const now = new Date();

        const year = now.getFullYear();
        const month = now.getMonth() + 1;

        const response = await apiRequest(
            `${API_BASE_URL}/summary/?year=${year}&month=${month}`
        );

        const result = await parseResponse(response);

        if (!response.ok) {
            console.error(
                "Summary error:",
                result
            );
            return;
        }

        const summary = result.data;

        if (!summary) {
            console.error(
                "Invalid summary response:",
                result
            );
            return;
        }

        totalSpend.textContent =
            formatCurrency(summary.total_spend);

        previousMonthSpend.textContent =
            formatCurrency(
                summary.previous_month_total
            );

        monthChange.textContent =
            `${summary.month_over_month_change}%`;

        summaryMonth.textContent =
            new Date(
                year,
                month - 1
            ).toLocaleString(
                "en-IN",
                {
                    month: "long",
                    year: "numeric",
                }
            );

        renderCategories(
            summary.spend_by_category
        );

        renderInsights(
            summary.category_insights
        );

    } catch (error) {
        console.error(
            "Summary error:",
            error
        );
    }
}


/* =========================================================
   EXPENSES
========================================================= */

async function loadExpenses(filters = {}) {
    try {
        const params = new URLSearchParams();

        if (filters.category) {
            params.set(
                "category",
                filters.category
            );
        }

        if (filters.start_date) {
            params.set(
                "start_date",
                filters.start_date
            );
        }

        if (filters.end_date) {
            params.set(
                "end_date",
                filters.end_date
            );
        }

        const queryString = params.toString();

        const url = queryString
            ? `${API_BASE_URL}/expenses/?${queryString}`
            : `${API_BASE_URL}/expenses/`;

        const response = await apiRequest(url);

        const result = await parseResponse(response);

        if (!response.ok) {
            console.error(
                "Expenses error:",
                result
            );
            return;
        }

        renderExpenses(
            result.data
        );

    } catch (error) {
        console.error(
            "Expenses error:",
            error
        );
    }
}


/* =========================================================
   RENDER CATEGORIES
========================================================= */

function renderCategories(categories = []) {
    if (!categories.length) {
        categoryList.innerHTML = `
            <p class="empty-state">
                No expenses this month.
            </p>
        `;
        return;
    }

    categoryList.innerHTML = categories
        .map(
            (category) => `
                <div class="category-item">
                    <span class="category-name">
                        ${escapeHtml(category.category)}
                    </span>

                    <span class="category-amount">
                        ${formatCurrency(category.total)}
                    </span>
                </div>
            `
        )
        .join("");
}


/* =========================================================
   RENDER EXPENSES
========================================================= */

function renderExpenses(expenses = []) {
    if (!expenses.length) {
        expenseList.innerHTML = `
            <p class="empty-state">
                No expenses found.
            </p>
        `;
        return;
    }

    expenseList.innerHTML = expenses
        .map(
            (expense) => `
                <div class="expense-item">

                    <div class="expense-left">

                        <span class="expense-category">
                            ${escapeHtml(expense.category)}
                        </span>

                        <span class="expense-note">
                            ${escapeHtml(
                                expense.note || "No note"
                            )}
                        </span>

                        <span class="expense-date">
                            ${formatDate(expense.date)}
                        </span>

                    </div>

                    <span class="expense-amount">
                        ${formatCurrency(expense.amount)}
                    </span>

                </div>
            `
        )
        .join("");
}


/* =========================================================
   INSIGHTS
========================================================= */

function renderInsights(insights = []) {
    if (!insights.length) {
        insightsSection.classList.add("hidden");
        return;
    }

    insightsSection.classList.remove("hidden");

    insightsList.innerHTML = insights
        .map(
            (insight) => `
                <div class="insight">

                    <strong>
                        ${escapeHtml(insight.category)}
                    </strong>

                    <p>
                        ${escapeHtml(insight.message)}
                    </p>

                </div>
            `
        )
        .join("");
}


/* =========================================================
   FILTERS
========================================================= */

filterBtn.addEventListener(
    "click",
    async () => {
        await loadExpenses({
            category: filterCategory.value.trim(),
            start_date: startDate.value,
            end_date: endDate.value,
        });
    }
);


clearFilterBtn.addEventListener(
    "click",
    async () => {
        filterCategory.value = "";
        startDate.value = "";
        endDate.value = "";

        await loadExpenses();
    }
);


/* =========================================================
   LOGOUT
========================================================= */

logoutBtn.addEventListener(
    "click",
    () => {
        clearTokens();

        welcomeUser.textContent = "";

        loginForm.reset();

        showLogin();
    }
);


/* =========================================================
   SHOW DASHBOARD
========================================================= */

function showDashboard() {
    authSection.classList.add("hidden");
    dashboardSection.classList.remove("hidden");

    logoutBtn.classList.remove("hidden");

    const userName =
        localStorage.getItem("user_name");

    welcomeUser.textContent =
        userName
            ? `Welcome, ${userName}`
            : "Welcome";
}


/* =========================================================
   SHOW LOGIN
========================================================= */

function showLogin() {
    authSection.classList.remove("hidden");
    dashboardSection.classList.add("hidden");

    logoutBtn.classList.add("hidden");

    showLoginForm();
}


/* =========================================================
   MESSAGE
========================================================= */

function setMessage(
    element,
    message,
    type = ""
) {
    element.textContent = message;

    element.className = "message";

    if (type) {
        element.classList.add(type);
    }
}


/* =========================================================
   PARSE API RESPONSE
========================================================= */

async function parseResponse(response) {
    const contentType =
        response.headers.get("content-type");

    if (
        contentType &&
        contentType.includes("application/json")
    ) {
        return await response.json();
    }

    return {};
}


/* =========================================================
   FORMAT CURRENCY
========================================================= */

const currencyFormatter =
    new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
        }
    );


function formatCurrency(amount) {
    return currencyFormatter.format(
        Number(amount || 0)
    );
}


/* =========================================================
   FORMAT DATE
========================================================= */

function formatDate(dateString) {
    if (!dateString) {
        return "No date";
    }

    const date = new Date(
        `${dateString}T00:00:00`
    );

    if (Number.isNaN(date.getTime())) {
        return "Invalid date";
    }

    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric",
        }
    );
}


/* =========================================================
   TODAY DATE
========================================================= */

function setTodayDate() {
    const today = new Date();

    const year =
        today.getFullYear();

    const month =
        String(
            today.getMonth() + 1
        ).padStart(2, "0");

    const day =
        String(
            today.getDate()
        ).padStart(2, "0");

    dateInput.value =
        `${year}-${month}-${day}`;
}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHtml(value) {
    const div =
        document.createElement("div");

    div.textContent =
        value ?? "";

    return div.innerHTML;
}


/* =========================================================
   ERROR MESSAGE
========================================================= */

function getErrorMessage(data) {
    if (!data) {
        return "Something went wrong.";
    }

    if (typeof data === "string") {
        return data;
    }

    if (data.message) {
        return data.message;
    }

    if (data.detail) {
        return data.detail;
    }

    if (data.errors) {
        const errors =
            Object.values(data.errors)
                .flat();

        if (errors.length) {
            return errors.join(" ");
        }
    }

    /*
       DRF example:

       {
           "email": [
               "Enter a valid email address."
           ]
       }
    */

    const fieldErrors =
        Object.values(data)
            .filter(
                (value) =>
                    Array.isArray(value)
            )
            .flat();

    if (fieldErrors.length) {
        return fieldErrors.join(" ");
    }

    return "Something went wrong.";
}


/* =========================================================
   PASSWORD VISIBILITY TOGGLE
========================================================= */
function setupPasswordToggles() {
    const toggleBtns = document.querySelectorAll('.toggle-password');
    
    // SVG code for Eye (Show)
    const iconEye = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
    
    // SVG code for Eye-Off (Hide)
    const iconEyeOff = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"></path><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"></path><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"></path><line x1="2" y1="2" x2="22" y2="22"></line></svg>`;

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Find the input field that comes right before the button
            const input = this.previousElementSibling;
            
            // Toggle type between 'password' and 'text'
            if (input.type === 'password') {https://spend-tracker-backend-7zow.onrender.com/
                input.type = 'text';
                this.innerHTML = iconEyeOff;
                this.setAttribute('aria-label', 'Hide password');
            } else {
                input.type = 'password';
                this.innerHTML = iconEye;
                this.setAttribute('aria-label', 'Show password');
            }
        });
    });
}




/* =========================================================
   INITIALIZE APP
========================================================= */
async function initializeApp() {
    setTodayDate();
    setupPasswordToggles(); // <-- Add this line here

    if (getAccessToken()) {
        showDashboard();
        await loadDashboard();
    } else {
        showLogin();
    }
}

initializeApp();

