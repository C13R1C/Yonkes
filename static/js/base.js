(function () {
    const body = document.body;
    const sidebarToggle = document.querySelector(".sidebar-toggle");
    const sidebarBackdrop = document.querySelector("[data-sidebar-backdrop]");
    const userMenu = document.querySelector("[data-user-menu]");
    const userMenuTrigger = userMenu ? userMenu.querySelector(".user-menu-trigger") : null;
    const searchForm = document.querySelector("[data-global-search]");
    const searchFeedback = document.querySelector("[data-search-feedback]");
    const sidebarLinks = document.querySelectorAll(".sidebar-link");
    const searchFilterToggle = document.querySelector("[data-toggle-search-filters]");
    const searchFilterPanel = document.querySelector("#advanced-search-filters");
    let feedbackTimer = null;

    function setSidebar(open) {
        body.classList.toggle("sidebar-open", open);

        if (sidebarToggle) {
            sidebarToggle.setAttribute("aria-expanded", String(open));
        }

        if (sidebarBackdrop) {
            sidebarBackdrop.setAttribute("aria-hidden", String(!open));
        }

        if (open) {
            const activeLink = document.querySelector(".sidebar-link.is-active") || document.querySelector(".sidebar-link");
            if (activeLink && window.matchMedia("(max-width: 1024px)").matches) {
                window.setTimeout(function () {
                    activeLink.focus({ preventScroll: true });
                }, 120);
            }
        }
    }

    function closeUserMenu() {
        if (!userMenu || !userMenuTrigger) {
            return;
        }

        userMenu.classList.remove("is-open");
        userMenuTrigger.setAttribute("aria-expanded", "false");
    }

    function showSearchFeedback(message) {
        if (!searchFeedback) {
            return;
        }

        searchFeedback.textContent = message;
        searchFeedback.classList.add("is-visible");

        window.clearTimeout(feedbackTimer);
        feedbackTimer = window.setTimeout(function () {
            searchFeedback.classList.remove("is-visible");
        }, 2600);
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", function () {
            setSidebar(!body.classList.contains("sidebar-open"));
        });
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener("click", function () {
            setSidebar(false);
        });
    }

    if (userMenu && userMenuTrigger) {
        userMenuTrigger.addEventListener("click", function (event) {
            event.stopPropagation();
            const isOpen = userMenu.classList.toggle("is-open");
            userMenuTrigger.setAttribute("aria-expanded", String(isOpen));
        });
    }

    sidebarLinks.forEach(function (link) {
        link.addEventListener("click", function () {
            if (window.matchMedia("(max-width: 1024px)").matches) {
                setSidebar(false);
            }
        });
    });


    if (searchFilterToggle && searchFilterPanel) {
        searchFilterToggle.addEventListener("click", function () {
            const collapsed = searchFilterPanel.classList.toggle("is-collapsed");
            searchFilterToggle.setAttribute("aria-expanded", String(!collapsed));
        });
    }

    if (searchForm) {
        searchForm.addEventListener("submit", function (event) {
            const input = searchForm.querySelector("input[type='search']");
            const query = input ? input.value.trim() : "";

            if (!query) {
                event.preventDefault();
                if (input) {
                    input.focus();
                }
                return;
            }

            if (input) {
                input.value = query;
            }
        });
    }

    document.addEventListener("click", function (event) {
        const dismissButton = event.target.closest("[data-dismiss-message]");

        if (!dismissButton) {
            return;
        }

        const message = dismissButton.closest(".message");
        if (message) {
            message.remove();
        }
    });

    document.addEventListener("click", function (event) {
        if (userMenu && !userMenu.contains(event.target)) {
            closeUserMenu();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            setSidebar(false);
            closeUserMenu();
        }
    });
})();
