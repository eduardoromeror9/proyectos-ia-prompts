// Minimal UI interactions — sidebar toggle & input auto-resize

const sidebar = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");
const openBtn = document.getElementById("openSidebar");
const closeBtn = document.getElementById("closeSidebar");
const chatInput = document.querySelector(".chat-input");
const sendBtn = document.querySelector(".btn-send");

function openSidebar() {
  sidebar.classList.add("open");
  sidebarOverlay.classList.add("visible");
}

function closeSidebar() {
  sidebar.classList.remove("open");
  sidebarOverlay.classList.remove("visible");
}

openBtn?.addEventListener("click", openSidebar);
closeBtn?.addEventListener("click", closeSidebar);
sidebarOverlay?.addEventListener("click", closeSidebar);

// Auto-resize textarea
chatInput?.addEventListener("input", () => {
  chatInput.style.height = "auto";
  chatInput.style.height = Math.min(chatInput.scrollHeight, 200) + "px";

  const hasText = chatInput.value.trim().length > 0;
  sendBtn.disabled = !hasText;
});

// Enter to submit (Shift+Enter for newline) — UI only, no send logic
chatInput?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (chatInput.value.trim()) {
      chatInput.value = "";
      chatInput.style.height = "auto";
      sendBtn.disabled = true;
    }
  }
});
