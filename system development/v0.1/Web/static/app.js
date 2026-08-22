const messages = document.getElementById("messages");
const input = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");


const ws = new WebSocket(
    `ws://${window.location.host}/ws/chat`
);

let currentAssistant = null;
let currentThoughtStream = null;
let currentThinkingBlock = null;
let currentStats = null;
let currentMarkdown = "";
let activeTools = {};
let autoScroll = true;

ws.onopen = () => {
    console.log("Connected to GlorpCat");
};


ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    if (message.type === "thinking_delta") {
        addThinkingDelta(message.data);
    }

    else if (message.type === "content_delta") {

        // First response token means thinking has finished
        if (currentAssistant.thinkingDetails.open) {
            currentAssistant.thinkingDetails.open = false;
            currentAssistant.thinkingSummary.textContent = "Thought";
        }

        currentMarkdown += message.data;
        renderMarkdown();
    }

    else if (message.type === "done") {
        currentAssistant.thinkingDetails.open = false;
        currentAssistant.thinkingSummary.textContent = "Thought";

        currentAssistant = null;
        currentThoughtStream = null;
        currentThinkingBlock = null;
        currentStats = null;
        activeTools = {};

        sendButton.disabled = false;
    }

    else if (message.type === "tool_started") {
        addTool(message.data);
    }

    else if (message.type === "tool_finished") {
        finishTool(message.data);
    }

    else if (message.type === "response_stats") {
        renderStats(message.data);
    }

    scrollToBottom();
};

window.addEventListener(
    "wheel",
    (event) => {
        if (event.deltaY < 0) {
            autoScroll = false;
        }
    },
    { passive: true }
);


window.addEventListener("keydown", (event) => {
    if (
        event.key === "ArrowUp" ||
        event.key === "PageUp" ||
        event.key === "Home"
    ) {
        autoScroll = false;
    }
});


window.addEventListener(
    "scroll",
    () => {
        if (!autoScroll && isNearBottom()) {
            autoScroll = true;
        }
    },
    { passive: true }
);


function scrollToBottom(force = false) {
    if (!autoScroll && !force) {
        return;
    }

    window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: "auto"
    });
}

function isNearBottom() {
    const threshold = 40;

    return (
        window.innerHeight + window.scrollY >=
        document.documentElement.scrollHeight - threshold
    );
}

function enhanceCodeBlocks() {
    const blocks = currentAssistant.querySelectorAll("pre");

    blocks.forEach((pre) => {
        const code = pre.querySelector("code");

        if (!code) {
            return;
        }

        hljs.highlightElement(code);

        const languageClass = Array.from(code.classList).find(
            className => className.startsWith("language-")
        );

        const language = languageClass
            ? languageClass.replace("language-", "")
            : "text";


        const wrapper = document.createElement("div");
        wrapper.classList.add("code-block");


        const header = document.createElement("div");
        header.classList.add("code-header");


        const languageLabel = document.createElement("span");
        languageLabel.textContent = language;


        const copyButton = document.createElement("button");
        copyButton.classList.add("copy-code");
        copyButton.textContent = "Copy";


        copyButton.addEventListener("click", async () => {
            await navigator.clipboard.writeText(
                code.textContent
            );

            copyButton.textContent = "Copied";

            setTimeout(() => {
                copyButton.textContent = "Copy";
            }, 1500);
        });


        header.appendChild(languageLabel);
        header.appendChild(copyButton);


        pre.parentNode.insertBefore(wrapper, pre);

        wrapper.appendChild(header);
        wrapper.appendChild(pre);
    });
}

function renderMarkdown() {
    const html = marked.parse(currentMarkdown);

    currentAssistant.innerHTML = DOMPurify.sanitize(html);

    enhanceCodeBlocks();
}

function renderStats(stats) {
    currentStats.innerHTML = "";

    const details = document.createElement("details");
    details.classList.add("stats-details");

    const summary = document.createElement("summary");

    summary.textContent =
        `${stats.speed.generation.toFixed(1)} tok/s` +
        ` • ${stats.tokens.generated.toLocaleString()} tokens` +
        ` • ${stats.timing.overall.toFixed(1)}s`;

    const content = document.createElement("div");
    content.classList.add("stats-content");

    content.innerHTML = `
        <div class="stats-section">
            <strong>Model</strong>
            <span>Context</span>
            <span>
                ${stats.model.context_used.toLocaleString()}
                /
                ${stats.model.context_length.toLocaleString()}
                (${stats.model.context_usage.toFixed(1)}%)
            </span>

            <span>Prompt tokens</span>
            <span>${stats.tokens.prompt.toLocaleString()}</span>

            <span>Generated tokens</span>
            <span>${stats.tokens.generated.toLocaleString()}</span>

            <span>Prompt speed</span>
            <span>${stats.speed.prompt.toFixed(2)} tok/s</span>

            <span>Generation speed</span>
            <span>${stats.speed.generation.toFixed(2)} tok/s</span>

            <span>Load time</span>
            <span>${stats.timing.load.toFixed(2)} s</span>
        </div>

        <div class="stats-section">
            <strong>Timing</strong>

            <span>Thinking</span>
            <span>${stats.timing.thinking.toFixed(2)} s</span>

            <span>Generation</span>
            <span>${stats.timing.generation.toFixed(2)} s</span>

            <span>Model total</span>
            <span>${stats.timing.model_total.toFixed(2)} s</span>

            <span>Overall</span>
            <span>${stats.timing.overall.toFixed(2)} s</span>
        </div>
    `;

    details.appendChild(summary);
    details.appendChild(content);

    currentStats.appendChild(details);
}

function sendMessage() {
    const text = input.value.trim();

    if (!text) {
        return;
    }

    addUserMessage(text);
    createAssistantMessage();

    autoScroll = true;

    ws.send(JSON.stringify({
        message: text
    }));

    input.value = "";
    sendButton.disabled = true;

    scrollToBottom(true);
}

function addThinkingDelta(text) {
    if (!currentThinkingBlock) {
        currentThinkingBlock = document.createElement("div");
        currentThinkingBlock.classList.add("thinking");

        currentThoughtStream.appendChild(
            currentThinkingBlock
        );
    }

    currentThinkingBlock.textContent += text;
}

function addUserMessage(text) {
    const element = document.createElement("div");

    element.classList.add(
        "message",
        "user-message"
    );

    element.textContent = text;

    messages.appendChild(element);
}


function createAssistantMessage() {
    currentMarkdown = "";
    const container = document.createElement("div");

    container.classList.add(
        "message",
        "assistant-message"
    );


    const thinkingDetails = document.createElement("details");
    thinkingDetails.classList.add("thinking-container");
    thinkingDetails.open = true;


    const thinkingSummary = document.createElement("summary");
    thinkingSummary.textContent = "Thinking...";


    currentThoughtStream = document.createElement("div");
    currentThoughtStream.classList.add("thought-stream");


    thinkingDetails.appendChild(thinkingSummary);
    thinkingDetails.appendChild(currentThoughtStream);


    currentAssistant = document.createElement("div");
    currentAssistant.classList.add("assistant-content");

    currentStats = document.createElement("div");
    currentStats.classList.add("response-stats");


    container.appendChild(thinkingDetails);
    container.appendChild(currentAssistant);
    container.appendChild(currentStats);

    messages.appendChild(container);


    currentAssistant.thinkingDetails = thinkingDetails;
    currentAssistant.thinkingSummary = thinkingSummary;

    currentThinkingBlock = null;
    activeTools = {};
}

function addTool(data) {
    // End the current reasoning block.
    // Any reasoning after this tool gets a new block.
    currentThinkingBlock = null;

    const tool = document.createElement("div");
    tool.classList.add("tool");

    const status = document.createElement("span");
    status.classList.add("tool-status");
    status.textContent = "●";

    const name = document.createElement("span");
    name.classList.add("tool-name");
    name.textContent = getToolLabel(data.name);

    const details = document.createElement("div");
    details.classList.add("tool-details");

    if (data.arguments) {
        details.textContent = getToolDetails(
            data.name,
            data.arguments
        );
    }

    tool.appendChild(status);
    tool.appendChild(name);

    if (details.textContent) {
        tool.appendChild(details);
    }

    currentThoughtStream.appendChild(tool);

    activeTools[data.name] = tool;
}
function finishTool(data) {
    const tool = activeTools[data.name];

    if (!tool) {
        return;
    }

    const status = tool.querySelector(".tool-status");

    status.textContent = "✓";

    const time = document.createElement("span");
    time.classList.add("tool-time");
    time.textContent = `${data.elapsed.toFixed(2)}s`;

    tool.appendChild(time);

    delete activeTools[data.name];
}

function getToolLabel(name) {
    const labels = {
        search_text: "Searched the web",
        search_news: "Searched news",
        get_collections: "Checked document collections",
        query_collection: "Searched documents",
        sequentialthinking: "Used sequential thinking"
    };

    return labels[name] || name;
}

function getToolDetails(name, args) {
    if (
        name === "search_text" ||
        name === "search_news"
    ) {
        return args.query || "";
    }

    if (name === "query_collection") {
        return args.query || args.collection || "";
    }

    return "";
}

sendButton.addEventListener(
    "click",
    sendMessage
);


input.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();

            sendMessage();
        }
    }
);