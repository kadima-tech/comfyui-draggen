import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "Draggen.Browser",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "DraggenRemoteMoodboardLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);

                const node = this;

                // Find widgets
                const apiKeyWidget = this.widgets.find(w => w.name === "api_key");
                const boardIdWidget = this.widgets.find(w => w.name === "moodboard_id");

                // create a container for the browser or just a simple dropdown for now?
                // Visual browser usually implies images. 
                // Let's create a button "Browse Boards" that opens a modal or fetches and shows a dropdown.

                const browseBtn = this.addWidget("button", "Load Boards", "load", async () => {
                    const key = apiKeyWidget.value;
                    if (!key) {
                        alert("Please enter an API Key first.");
                        return;
                    }

                    try {
                        const resp = await fetch(`/draggen/api/list_boards`, {
                            headers: {
                                "x-api-key": key
                            }
                        });
                        if (!resp.ok) {
                            throw new Error(await resp.text());
                        }
                        const data = await resp.json();
                        const boards = data.boards;

                        // Create/Update a dropdown widget
                        // If we want thumbnails, standard dropdown won't work well.
                        // Use a custom dialog.

                        showBoardSelector(boards, (selectedId) => {
                            boardIdWidget.value = selectedId;
                        });

                    } catch (e) {
                        alert("Failed to load boards: " + e.message);
                    }
                });

            };
        }
    },
});

function showBoardSelector(boards, onSelect) {
    // Simple modal implementation
    const dialog = document.createElement("div");
    Object.assign(dialog.style, {
        position: "fixed", top: "50%", left: "50%", transform: "translate(-50%, -50%)",
        backgroundColor: "#222", padding: "20px", borderRadius: "8px", zIndex: "10000",
        maxHeight: "80vh", overflowY: "auto", border: "1px solid #444", color: "#fff",
        display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: "10px", width: "80vw"
    });

    // Header
    const header = document.createElement("div");
    Object.assign(header.style, { gridColumn: "1 / -1", display: "flex", justifyContent: "space-between", marginBottom: "10px" });
    header.innerHTML = "<h3>Select Moodboard</h3><button id='close-draggen-modal'>X</button>";
    dialog.appendChild(header);

    boards.forEach(board => {
        const item = document.createElement("div");
        Object.assign(item.style, {
            border: "1px solid #444", padding: "10px", borderRadius: "4px", cursor: "pointer",
            textAlign: "center", backgroundColor: "#333"
        });

        // Thumbnail if available
        if (board.thumbnailUrl || board.previewImage) {
            const img = document.createElement("img");
            img.src = board.thumbnailUrl || board.previewImage;
            Object.assign(img.style, { width: "100%", height: "100px", objectFit: "cover", marginBottom: "5px" });
            item.appendChild(img);
        } else {
            // Placeholder
            const div = document.createElement("div");
            div.textContent = "No Preview";
            Object.assign(div.style, { width: "100%", height: "100px", display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "#444", marginBottom: "5px" });
            item.appendChild(div);
        }

        const name = document.createElement("div");
        name.textContent = board.name || board.id;
        name.style.fontSize = "12px";
        item.appendChild(name);

        item.onclick = () => {
            onSelect(board.id);
            document.body.removeChild(dialog);
            overlay.remove();
        };

        dialog.appendChild(item);
    });

    const overlay = document.createElement("div");
    Object.assign(overlay.style, {
        position: "fixed", top: "0", left: "0", width: "100%", height: "100%",
        backgroundColor: "rgba(0,0,0,0.5)", zIndex: "9999"
    });

    document.body.appendChild(overlay);
    document.body.appendChild(dialog);

    header.querySelector("#close-draggen-modal").onclick = () => {
        document.body.removeChild(dialog);
        overlay.remove();
    };
    overlay.onclick = () => {
        document.body.removeChild(dialog);
        overlay.remove();
    };
}
