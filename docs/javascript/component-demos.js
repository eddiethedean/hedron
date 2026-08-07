(function () {
  "use strict";

  function reducedMotion() {
    return (
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
  }

  function delayMs(normal) {
    return reducedMotion() ? Math.min(40, normal) : normal;
  }

  function status(demo, message) {
    const node = demo.querySelector("[data-hdc-status]");
    if (node) node.textContent = message;
  }

  function trace(demo, method, path, result) {
    const node = demo.querySelector("[data-hdc-request]");
    if (!node) return;
    node.hidden = false;
    node.classList.toggle("hdc-request--deny", String(result).includes("403"));
    const code = node.querySelector("code");
    if (code) code.textContent = `${method} ${path} → ${result}`;
  }

  function initTabs(demo) {
    const tabs = Array.from(demo.querySelectorAll("[data-hdc-tab]"));
    const panels = Array.from(demo.querySelectorAll("[data-hdc-panel]"));
    function select(tab) {
      const selected = tab.dataset.hdcTab;
      for (const candidate of tabs) {
        const active = candidate === tab;
        candidate.setAttribute("aria-selected", String(active));
        candidate.tabIndex = active ? 0 : -1;
      }
      for (const panel of panels) panel.hidden = panel.dataset.hdcPanel !== selected;
    }
    for (const tab of tabs) {
      tab.addEventListener("click", () => select(tab));
      tab.addEventListener("keydown", (event) => {
        if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        let next = tabs.indexOf(tab);
        if (event.key === "ArrowRight") next = (next + 1) % tabs.length;
        if (event.key === "ArrowLeft") next = (next - 1 + tabs.length) % tabs.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = tabs.length - 1;
        tabs[next].focus();
        select(tabs[next]);
      });
    }
  }

  function setShellNavActive(demo, link) {
    for (const candidate of demo.querySelectorAll("[data-hdc-action='shell-nav']")) {
      if (candidate === link) candidate.setAttribute("aria-current", "page");
      else candidate.removeAttribute("aria-current");
    }
  }

  function initModeToggle(demo) {
    for (const toggle of demo.querySelectorAll("[data-hdc-mode-toggle]")) {
      toggle.addEventListener("click", () => {
        const mode = toggle.dataset.hdcModeToggle;
        for (const candidate of demo.querySelectorAll("[data-hdc-mode-toggle]")) {
          const active = candidate === toggle;
          candidate.setAttribute("aria-pressed", String(active));
          candidate.classList.toggle("hdc-primary", active);
        }
        for (const pane of demo.querySelectorAll("[data-hdc-mode-pane]")) {
          pane.hidden = pane.dataset.hdcModePane !== mode;
        }
        status(demo, mode === "page" ? "PAGE: full HTML document." : "FRAGMENT: region HTML only.");
      });
    }
  }

  function initPeToggle(demo) {
    for (const toggle of demo.querySelectorAll("[data-hdc-pe-toggle]")) {
      toggle.addEventListener("click", () => {
        const mode = toggle.dataset.hdcPeToggle;
        for (const candidate of demo.querySelectorAll("[data-hdc-pe-toggle]")) {
          const active = candidate === toggle;
          candidate.setAttribute("aria-pressed", String(active));
          candidate.classList.toggle("hdc-primary", active);
        }
        demo.dataset.hdcPeMode = mode;
        const app = demo.querySelector("[data-hdc-pe-app]");
        const page = demo.querySelector("[data-hdc-pe-page]");
        const resultHost = demo.querySelector("[data-hdc-form-result]");
        if (mode === "htmx") {
          if (app) app.hidden = false;
          if (page) page.hidden = true;
          if (resultHost) {
            resultHost.hidden = true;
            resultHost.innerHTML = "";
          }
        }
        status(
          demo,
          mode === "htmx"
            ? "HTMX on — submit swaps the result region."
            : "HTMX off — submit returns a full confirmation page."
        );
      });
    }
  }

  function initDemo(demo) {
    if (demo.dataset.hdcReady === "true") return;
    demo.dataset.hdcReady = "true";

    initTabs(demo);
    initModeToggle(demo);
    initPeToggle(demo);

    for (const form of demo.querySelectorAll("[data-hdc-form]")) {
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const mode = form.dataset.hdcForm || "simple";
        const path = form.dataset.hdcPath || "/demo";
        const data = new FormData(form);
        const email = String(data.get("email") || "").trim();
        const note = String(data.get("note") || "").trim();
        const errorsHost = demo.querySelector("[data-hdc-form-errors]");
        const resultHost = demo.querySelector("[data-hdc-form-result]");
        const formRegion = demo.querySelector("[data-hdc-form-region]");

        if (mode === "validate" || mode === "invite") {
          const invalid = !email || email.length < 3 || !email.includes("@");
          form.setAttribute("aria-busy", "true");
          trace(demo, "POST", path, "pending");
          window.setTimeout(() => {
            form.removeAttribute("aria-busy");
            if (invalid) {
              if (errorsHost) {
                errorsHost.hidden = false;
                errorsHost.innerHTML =
                  "<strong>Check the form</strong><ul><li>Enter a valid work email.</li></ul>";
              }
              if (resultHost) resultHost.hidden = true;
              if (formRegion) formRegion.hidden = false;
              status(demo, "Validation failed — form redisplays with errors.");
              trace(demo, "POST", path, "422 fragment");
              return;
            }
            if (errorsHost) {
              errorsHost.hidden = true;
              errorsHost.innerHTML = "";
            }
            if (formRegion) formRegion.hidden = true;
            if (resultHost) {
              resultHost.hidden = false;
              resultHost.innerHTML = `<strong>Invite sent</strong><span>Queued for ${email}.</span>`;
            }
            status(demo, `Invite accepted for ${email}.`);
            trace(demo, "POST", path, "200 fragment");
          }, delayMs(450));
          return;
        }

        if (mode === "crud-add") {
          if (!note) {
            status(demo, "Enter a note before submitting.");
            return;
          }
          const list = demo.querySelector("[data-hdc-crud-list]");
          trace(demo, "POST", path, "pending");
          window.setTimeout(() => {
            const item = document.createElement("li");
            const label = document.createElement("span");
            label.textContent = note;
            const remove = document.createElement("button");
            remove.type = "button";
            remove.className = "hdc-button";
            remove.dataset.hdcAction = "crud-delete";
            remove.textContent = "Delete";
            item.append(label, remove);
            list?.append(item);
            form.reset();
            status(demo, `Added “${note}”.`);
            trace(demo, "POST", path, "200 fragment");
          }, delayMs(400));
          return;
        }

        if (mode === "pe-submit") {
          const peMode = demo.dataset.hdcPeMode || "htmx";
          const value = note || email || "sample";
          trace(demo, "POST", path, "pending");
          window.setTimeout(() => {
            if (peMode === "full") {
              const page = demo.querySelector("[data-hdc-pe-page]");
              const app = demo.querySelector("[data-hdc-pe-app]");
              if (app) app.hidden = true;
              if (page) {
                page.hidden = false;
                page.innerHTML = `<strong>Saved</strong><span>Saved: ${value}</span>`;
              }
              status(demo, "Full-page confirmation (no fragment allowlist).");
              trace(demo, "POST", path, "200 page");
            } else {
              if (resultHost) {
                resultHost.hidden = false;
                resultHost.innerHTML = `<strong>Saved in region</strong><span>${value}</span>`;
              }
              status(demo, "HTMX swapped the declared result region.");
              trace(demo, "POST", path, "200 fragment");
            }
          }, delayMs(400));
          return;
        }

        if (typeof form.reportValidity === "function" && !form.reportValidity()) return;
        status(
          demo,
          email
            ? `Submitted ${email}. The docs returned a simulated success fragment.`
            : "Form submitted in the browser demo."
        );
        trace(demo, "POST", path, "200 fragment");
      });
    }

    const chatForm = demo.querySelector("[data-hdc-chat-form]");
    const chatField = chatForm?.querySelector("textarea[name='message']");
    for (const prompt of demo.querySelectorAll("[data-hdc-prompt]")) {
      prompt.addEventListener("click", () => {
        if (!chatField) return;
        chatField.value = prompt.dataset.hdcPrompt || "";
        chatField.dispatchEvent(new Event("input", { bubbles: true }));
        chatField.focus();
      });
    }
    chatField?.addEventListener("input", () => {
      chatField.style.height = "auto";
      chatField.style.height = `${Math.min(chatField.scrollHeight, 112)}px`;
    });
    chatField?.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" || event.shiftKey || event.isComposing) return;
      event.preventDefault();
      chatForm?.requestSubmit();
    });
    chatForm?.addEventListener("submit", (event) => {
      event.preventDefault();
      if (typeof chatForm.reportValidity === "function" && !chatForm.reportValidity()) return;
      const transcript = demo.querySelector("[data-hdc-transcript]");
      const message = String(chatField?.value || "").trim();
      if (!message || !transcript) return;

      const time = new Intl.DateTimeFormat(undefined, {
        hour: "numeric",
        minute: "2-digit",
      }).format(new Date());
      const userMessage = document.createElement("article");
      userMessage.className = "hdc-chat-message hdc-chat-user";
      const userAvatar = document.createElement("span");
      userAvatar.className = "hdc-chat-avatar";
      userAvatar.setAttribute("aria-hidden", "true");
      userAvatar.textContent = "Y";
      const userContent = document.createElement("div");
      const userLabel = document.createElement("strong");
      userLabel.textContent = "You";
      const userBody = document.createElement("p");
      userBody.textContent = message;
      const userTime = document.createElement("time");
      userTime.textContent = time;
      userContent.append(userLabel, userBody, userTime);
      userMessage.append(userAvatar, userContent);
      transcript.append(userMessage);
      chatField.value = "";
      chatField.style.height = "auto";
      transcript.scrollTop = transcript.scrollHeight;
      status(demo, "Sending message…");
      trace(demo, "POST", "/chat", "pending");

      window.setTimeout(() => {
        const reply = document.createElement("article");
        reply.className = "hdc-chat-message hdc-chat-assistant";
        const replyAvatar = document.createElement("span");
        replyAvatar.className = "hdc-chat-avatar";
        replyAvatar.setAttribute("aria-hidden", "true");
        replyAvatar.textContent = "H";
        const replyContent = document.createElement("div");
        const replyLabel = document.createElement("strong");
        replyLabel.textContent = "Hedron";
        const replyBody = document.createElement("p");
        replyBody.textContent =
          "All six deployment checks passed. The simulated rollout is healthy and ready to continue.";
        const replyTime = document.createElement("time");
        replyTime.textContent = time;
        replyContent.append(replyLabel, replyBody, replyTime);
        reply.append(replyAvatar, replyContent);
        transcript.append(reply);
        transcript.scrollTop = transcript.scrollHeight;
        status(demo, "Message delivered.");
        trace(demo, "POST", "/chat", "200 fragment");
      }, delayMs(550));
    });

    const dialog = demo.querySelector("[data-hdc-dialog]");
    dialog?.addEventListener("close", () => {
      status(demo, "Dialog closed. Focus returned to the trigger.");
      demo.querySelector('[data-hdc-action="open-dialog"]')?.focus();
    });

    demo.querySelector("[data-hdc-file]")?.addEventListener("change", (event) => {
      const files = Array.from(event.currentTarget.files || []);
      status(
        demo,
        files.length
          ? `${files.map((file) => file.name).join(", ")} selected. Server validation would run on submit.`
          : "No file selected."
      );
    });

    demo.querySelector("[data-hdc-filter]")?.addEventListener("input", (event) => {
      const query = event.currentTarget.value.trim().toLocaleLowerCase();
      const rows = Array.from(demo.querySelectorAll("[data-hdc-rows] tr"));
      let shown = 0;
      for (const row of rows) {
        row.hidden = query !== "" && !row.textContent.toLocaleLowerCase().includes(query);
        if (!row.hidden) shown += 1;
      }
      status(demo, `Showing ${shown} employee${shown === 1 ? "" : "s"}.`);
    });

    for (const input of demo.querySelectorAll("[data-hdc-dirty]")) {
      input.addEventListener("input", () => status(demo, "Unsaved changes."));
    }

    for (const link of demo.querySelectorAll("[data-hdc-page]")) {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        const page = Number(link.dataset.hdcPage || 1);
        const names = [
          ["Alpha", "Bravo", "Charlie"],
          ["Delta", "Echo", "Foxtrot"],
          ["Golf", "Hotel", "India"],
        ][page - 1];
        const content = demo.querySelector("[data-hdc-page-content]");
        if (content) {
          content.querySelector("strong").textContent = `Results ${(page - 1) * 3 + 1}–${page * 3}`;
          content.querySelector("span").textContent = names.join(" · ");
        }
        for (const candidate of demo.querySelectorAll("[data-hdc-page]")) {
          if (candidate === link) candidate.setAttribute("aria-current", "page");
          else candidate.removeAttribute("aria-current");
        }
        trace(demo, "GET", `?page=${page}`, "200 fragment");
        content?.focus?.();
      });
    }

    demo.querySelector("[data-hdc-theme-form]")?.addEventListener("submit", (event) => {
      event.preventDefault();
      const select = demo.querySelector("[data-hdc-theme]");
      const selected = select?.value || "Light";
      const swatch = demo.querySelector("[data-hdc-theme-swatch]");
      if (swatch) swatch.dataset.previewTheme = selected.toLocaleLowerCase();
      status(demo, `${selected} preview selected. A server would persist this preference.`);
      trace(demo, "POST", "/preferences/color", "204");
    });

    demo.addEventListener("click", (event) => {
      const button = event.target.closest("[data-hdc-action]");
      if (!button || !demo.contains(button)) return;
      const action = button.dataset.hdcAction;

      if (action === "count") {
        const count = demo.querySelector("[data-hdc-count]");
        if (count) count.textContent = String(Number(count.textContent || 0) + 1);
        status(demo, "Button activated.");
      }

      if (action === "refresh") {
        button.disabled = true;
        const result =
          demo.querySelector("[data-hdc-refresh-target]") || demo.querySelector("#status-card");
        const path = button.dataset.hdcPath || "/status";
        if (result) result.innerHTML = "<strong>Refreshing…</strong><span>Simulated request in progress</span>";
        trace(demo, "GET", path, "pending");
        window.setTimeout(() => {
          if (result) {
            result.innerHTML = `<strong>Service healthy</strong><span>Checked at ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</span>`;
          }
          button.disabled = false;
          trace(demo, "GET", path, "200 fragment");
        }, delayMs(550));
      }

      if (action === "refresh-notes") {
        button.disabled = true;
        const target = demo.querySelector("[data-hdc-notes-count]");
        const path = button.dataset.hdcPath || "/notes-count";
        trace(demo, "GET", path, "pending");
        window.setTimeout(() => {
          const n = Number(target?.dataset.count || 0);
          if (target) {
            target.dataset.count = String(n);
            target.innerHTML = `<strong>Notes saved: ${n}</strong><span>Allowlisted region #notes-count</span>`;
          }
          button.disabled = false;
          trace(demo, "GET", path, "200 fragment");
          status(demo, "Notes count region refreshed (still 0 until a form adds notes).");
        }, delayMs(450));
      }

      if (action === "allowlist-ok") {
        button.disabled = true;
        const target = demo.querySelector("[data-hdc-allowlist-target]");
        const path = button.dataset.hdcPath || "/status";
        trace(demo, "GET", path, "pending");
        window.setTimeout(() => {
          if (target) {
            target.innerHTML = `<strong>Allowlisted swap</strong><span>HX-Target matched #service-status</span>`;
          }
          button.disabled = false;
          status(demo, "Correct target — fragment swapped.");
          trace(demo, "GET", path, "200 fragment");
        }, delayMs(400));
      }

      if (action === "allowlist-deny") {
        button.disabled = true;
        const path = button.dataset.hdcPath || "/status";
        trace(demo, "GET", path, "pending");
        window.setTimeout(() => {
          button.disabled = false;
          status(demo, "Wrong HX-Target — server returns 403 (no swap).");
          trace(demo, "GET", path, "403 HX-Target not allowlisted");
        }, delayMs(350));
      }

      if (action === "shell-nav") {
        event.preventDefault();
        const title = button.dataset.hdcTitle || button.textContent?.trim() || "Panel";
        const detail = button.dataset.hdcDetail || "Fragment loaded into MainPanel.";
        const path = button.dataset.hdcPath || button.getAttribute("href") || "/panel";
        const panel = demo.querySelector("[data-hdc-panel-target]");
        button.setAttribute("aria-busy", "true");
        trace(demo, "GET", path, "pending");
        window.setTimeout(() => {
          if (panel) panel.innerHTML = `<strong>${title}</strong><span>${detail}</span>`;
          setShellNavActive(demo, button);
          button.removeAttribute("aria-busy");
          status(demo, `${title} loaded in the shell panel.`);
          trace(demo, "GET", path, "200 fragment");
        }, delayMs(400));
      }

      if (action === "oob-save") {
        button.disabled = true;
        const primary = demo.querySelector("[data-hdc-oob-primary]");
        const host = demo.querySelector("[data-hdc-oob-host]");
        const path = button.dataset.hdcPath || "/save";
        trace(demo, "POST", path, "pending");
        window.setTimeout(() => {
          if (primary) {
            primary.innerHTML =
              "<strong>Settings saved</strong><span>Primary region updated.</span>";
          }
          if (host) {
            host.innerHTML =
              '<span class="hdc-badge hdc-success">Saved</span><span><strong>#toast-host</strong><small>Out-of-band update</small></span>';
          }
          button.disabled = false;
          status(demo, "Primary swap + OOB host update in one response.");
          trace(demo, "POST", path, "200 fragment + OOB");
        }, delayMs(500));
      }

      if (action === "attr-host") {
        button.disabled = true;
        const host = demo.querySelector("[data-hdc-attr-host]");
        const path = button.dataset.hdcPath || "/status-attrs";
        const states = ["busy", "ready", "idle"];
        let index = 0;
        trace(demo, "GET", path, "pending");
        const timer = window.setInterval(() => {
          const state = states[index++];
          if (host) {
            host.dataset.state = state;
            const label = host.querySelector("small");
            if (label) label.textContent = `data-state=${state}`;
          }
          trace(demo, "GET", path, `200 attrs ${state}`);
          if (index === states.length) {
            window.clearInterval(timer);
            button.disabled = false;
            status(demo, "Attribute-only OOB patches applied; children unchanged.");
          }
        }, delayMs(550));
      }

      if (action === "loading-cycle") {
        button.disabled = true;
        const target = demo.querySelector("[data-hdc-loading-target]");
        const path = button.dataset.hdcPath || "/activity";
        if (target) {
          target.innerHTML =
            '<div class="hdc-loading" role="status" aria-live="polite" aria-busy="true"><i></i><span>Loading account activity…</span></div>';
        }
        trace(demo, "GET", path, "pending");
        window.setTimeout(() => {
          if (target) {
            target.innerHTML =
              '<div class="hdc-result" role="status"><strong>3 events</strong><span>Deployment, approval, and release notes.</span></div>';
          }
          button.disabled = false;
          status(demo, "Loading indicator replaced by the result fragment.");
          trace(demo, "GET", path, "200 fragment");
        }, delayMs(700));
      }

      if (action === "skeleton-cycle") {
        button.disabled = true;
        const target = demo.querySelector("[data-hdc-skeleton-target]");
        const path = button.dataset.hdcPath || "/profile";
        if (target) {
          target.setAttribute("aria-busy", "true");
          target.innerHTML =
            '<div aria-label="Loading preview"><span class="hdc-skeleton"></span><span class="hdc-skeleton"></span><span class="hdc-skeleton hdc-short"></span></div>';
        }
        trace(demo, "GET", path, "pending");
        window.setTimeout(() => {
          if (target) {
            target.removeAttribute("aria-busy");
            target.innerHTML =
              '<div class="hdc-result"><strong>Ada Lovelace</strong><span>Platform · Active</span></div>';
          }
          button.disabled = false;
          status(demo, "Skeleton replaced by loaded content.");
          trace(demo, "GET", path, "200 fragment");
        }, delayMs(700));
      }

      if (action === "fragment-refresh") {
        button.disabled = true;
        const target = demo.querySelector("[data-hdc-fragment-target]");
        const path = button.dataset.hdcPath || "/profile-fragment";
        trace(demo, "GET", path, "pending");
        window.setTimeout(() => {
          if (target) {
            target.innerHTML =
              '<span class="hdc-badge hdc-success">Saved</span><span><strong>Profile updated</strong><small>Two siblings; no Fragment wrapper.</small></span>';
          }
          button.disabled = false;
          status(demo, "Fragment response injected sibling nodes without a wrapper.");
          trace(demo, "GET", path, "200 fragment");
        }, delayMs(450));
      }

      if (action === "chart-refresh") {
        button.disabled = true;
        const target = demo.querySelector("[data-hdc-chart-panel]");
        const path = button.dataset.hdcPath || "/chart-panel";
        trace(demo, "GET", path, "pending");
        window.setTimeout(() => {
          if (target) {
            const next = Number(target.dataset.rev || 1) + 1;
            target.dataset.rev = String(next);
            target.innerHTML = `<figure class="hdc-chart"><figcaption><strong>Monthly revenue</strong><span>Fragment refresh #${next}</span></figcaption><div class="hdc-chart-art" role="img" aria-label="Sample chart refreshed"><i></i><i></i><i></i><i></i><i></i></div></figure>`;
          }
          button.disabled = false;
          status(demo, "Chart panel region refreshed.");
          trace(demo, "GET", path, "200 fragment");
        }, delayMs(500));
      }

      if (action === "toast-save") {
        button.disabled = true;
        const toast = demo.querySelector("[data-hdc-toast]");
        const path = button.dataset.hdcPath || "/copy-key";
        trace(demo, "POST", path, "pending");
        window.setTimeout(() => {
          if (toast) toast.hidden = false;
          button.disabled = false;
          status(demo, "Primary action succeeded; toast arrived via OOB host.");
          trace(demo, "POST", path, "200 fragment + OOB");
        }, delayMs(400));
      }

      if (action === "confirm-delete") {
        const confirmed = window.confirm(button.dataset.hdcConfirm || "Delete item?");
        if (!confirmed) {
          status(demo, "Delete cancelled.");
          return;
        }
        button.disabled = true;
        const row = demo.querySelector("[data-hdc-confirm-row]");
        const path = button.dataset.hdcPath || "/items/1";
        trace(demo, "DELETE", path, "pending");
        window.setTimeout(() => {
          if (row) {
            row.innerHTML =
              '<div class="hdc-result" role="status"><strong>Item deleted</strong><span>Row removed by fragment swap.</span></div>';
          }
          button.disabled = false;
          status(demo, "Confirmed — fragment removed the row.");
          trace(demo, "DELETE", path, "200 fragment");
        }, delayMs(400));
      }

      if (action === "crud-delete") {
        event.preventDefault();
        const row = button.closest("li");
        const path = button.dataset.hdcPath || "/notes/1";
        trace(demo, "DELETE", path, "pending");
        window.setTimeout(() => {
          row?.remove();
          status(demo, "Note deleted from the list region.");
          trace(demo, "DELETE", path, "200 fragment");
        }, delayMs(350));
      }

      if (action === "lazy") {
        const target = demo.querySelector("[data-hdc-lazy]");
        button.disabled = true;
        trace(demo, "GET", "/activity-feed", "pending");
        window.setTimeout(() => {
          if (target) {
            target.setAttribute("aria-busy", "false");
            target.innerHTML =
              "<strong>3 recent events</strong><span>Deployment, approval, and release notes loaded.</span>";
          }
          trace(demo, "GET", "/activity-feed", "200 fragment");
        }, delayMs(650));
      }

      if (action === "poll") {
        button.disabled = true;
        const state = demo.querySelector("[data-hdc-poll-state]");
        const detail = demo.querySelector("[data-hdc-poll-detail]");
        const updates = [
          ["Queued", "Waiting for worker"],
          ["Running", "Step 1 of 2"],
          ["Running", "Step 2 of 2"],
          ["Complete", "84 records imported; polling stopped"],
        ];
        let index = 0;
        const apply = (update) => {
          if (state) state.textContent = update[0];
          if (detail) detail.textContent = update[1];
          trace(demo, "GET", "/jobs/42", `200 ${update[0]}`);
        };
        apply(updates[index++]);
        const timer = window.setInterval(() => {
          apply(updates[index++]);
          if (index === updates.length) {
            window.clearInterval(timer);
            button.disabled = false;
            button.textContent = "Run polling demo again";
          }
        }, delayMs(700));
      }

      if (action === "more") {
        const feed = demo.querySelector("[data-hdc-feed]");
        const count = feed?.children.length || 0;
        for (const text of ["Tests passed", "Release published"]) {
          const item = document.createElement("li");
          item.textContent = text;
          feed?.append(item);
        }
        status(demo, `Added 2 events. Showing ${count + 2} events.`);
        trace(demo, "GET", `/events?after=${count}`, "200 fragment");
        if (count >= 4) {
          button.disabled = true;
          button.textContent = "All events loaded";
        }
      }

      if (action === "retry") {
        const error = demo.querySelector("[data-hdc-error]");
        button.disabled = true;
        trace(demo, "GET", "/activity", "pending");
        window.setTimeout(() => {
          if (error) {
            error.outerHTML =
              '<div class="hdc-result" role="status"><strong>Activity restored</strong><span>The retry returned a successful fragment.</span></div>';
          }
          trace(demo, "GET", "/activity", "200 fragment");
        }, delayMs(550));
      }

      if (action === "open-dialog") {
        const target = demo.querySelector("[data-hdc-dialog]");
        if (typeof target?.showModal === "function") target.showModal();
        else target?.setAttribute("open", "");
        status(demo, "Dialog opened.");
      }

      if (action === "close-dialog") {
        const target = demo.querySelector("[data-hdc-dialog]");
        if (typeof target?.close === "function") target.close();
        else target?.removeAttribute("open");
      }

      if (action === "save-editor") {
        button.disabled = true;
        status(demo, "Saving 2 changed rows…");
        trace(demo, "POST", "/allocations/changes", "pending");
        window.setTimeout(() => {
          button.disabled = false;
          status(demo, "2 rows saved. Version 8 returned by the simulated server.");
          trace(demo, "POST", "/allocations/changes", "200 version=8");
        }, delayMs(550));
      }

      if (action === "show-toast") {
        const toast = demo.querySelector("[data-hdc-toast]");
        if (toast) toast.hidden = false;
      }

      if (action === "dismiss") {
        const toast = demo.querySelector("[data-hdc-toast]");
        if (toast) toast.hidden = true;
        demo.querySelector('[data-hdc-action="show-toast"]')?.focus();
        demo.querySelector('[data-hdc-action="toast-save"]')?.focus();
      }

      if (action === "form-errors-demo") {
        button.disabled = true;
        const host = demo.querySelector("[data-hdc-form-errors]");
        const path = button.dataset.hdcPath || "/invite";
        trace(demo, "POST", path, "pending");
        window.setTimeout(() => {
          if (host) {
            host.hidden = false;
            host.innerHTML =
              "<strong>Check the form</strong><ul><li>Email is required.</li><li>Choose a billing plan.</li></ul>";
          }
          button.disabled = false;
          status(demo, "Failed POST redisplays FormErrors in the form region.");
          trace(demo, "POST", path, "422 fragment");
        }, delayMs(400));
      }
    });
  }

  function init(root) {
    for (const demo of root.querySelectorAll("[data-hedron-component-demo]")) initDemo(demo);
  }

  if (typeof document$ !== "undefined") document$.subscribe(() => init(document));
  else if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", () => init(document));
  else init(document);
})();
