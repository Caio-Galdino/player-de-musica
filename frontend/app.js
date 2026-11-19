// ================= comunicacao com a API =================

// faz a requisicao e devolve o JSON; se a API responder erro, lanca com a mensagem dela
async function api(method, path, body) {
    const options = { method: method, headers: {} };

    if (body !== undefined) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    const response = await fetch("/api" + path, options);

    // nem toda resposta de erro e JSON (ex.: 404 de rota inexistente vem em HTML)
    let data = null;
    try {
        data = await response.json();
    } catch (e) {
        data = null;
    }

    if (!response.ok) {
        const message = data && data.error ? data.error : "Erro " + response.status;
        throw new Error(message);
    }

    return data;
}

// monta "?title=...&artist=..." ja codificado (espacos, acentos, &, etc.)
function songQuery(song) {
    return "?" + new URLSearchParams({ title: song.title, artist: song.artist });
}

// ================= mensagens de erro =================

let errorTimer = null;

function showError(message) {
    const box = document.getElementById("error");
    box.textContent = message;
    box.hidden = false;

    // some sozinho depois de 5 segundos
    clearTimeout(errorTimer);
    errorTimer = setTimeout(clearError, 5000);
}

function clearError() {
    document.getElementById("error").hidden = true;
}

// roda uma acao e mostra o erro na tela se ela falhar
async function run(action) {
    clearError();
    try {
        await action();
    } catch (e) {
        showError(e.message);
    }
}

// ================= desenho das listas =================

// primeira letra do titulo, usada como "capa" da musica
function initial(song) {
    return song.title.charAt(0).toUpperCase();
}

// cria um elemento com classe e texto
// usa textContent (e nao innerHTML) para um titulo com "<" nao virar HTML
function createElement(tag, className, text) {
    const element = document.createElement(tag);
    element.className = className;
    if (text !== undefined) {
        element.textContent = text;
    }
    return element;
}

// buttons: lista de { label, onClick, danger }
function createSongItem(song, buttons) {
    const li = createElement("li", "song");

    li.appendChild(createElement("span", "song-cover", initial(song)));

    const info = createElement("div", "song-info");
    info.appendChild(createElement("span", "song-title", song.title));
    info.appendChild(createElement("span", "song-artist", song.artist));
    li.appendChild(info);

    li.appendChild(createElement("span", "song-duration", song.formatted_duration));

    if (buttons.length > 0) {
        const actions = createElement("div", "song-actions");
        for (const button of buttons) {
            const className = "btn btn-small" + (button.danger ? " btn-danger" : "");
            const element = createElement("button", className, button.label);
            element.addEventListener("click", () => run(button.onClick));
            actions.appendChild(element);
        }
        li.appendChild(actions);
    }

    return li;
}

// buttonsFor(song) devolve os botoes de cada musica
function renderList(listId, songs, buttonsFor, emptyText) {
    const ul = document.getElementById(listId);
    ul.replaceChildren(); // apaga o que tinha antes

    // contador ao lado do titulo do cartao
    document.getElementById(listId + "-count").textContent = songs.length;

    if (songs.length === 0) {
        ul.appendChild(createElement("li", "empty", emptyText));
        return;
    }

    for (const song of songs) {
        ul.appendChild(createSongItem(song, buttonsFor(song)));
    }
}

// ================= biblioteca =================

async function loadLibrary() {
    const search = document.getElementById("search-title").value.trim();
    let songs;

    if (search !== "") {
        songs = await api("GET", "/songs/search?" + new URLSearchParams({ title: search }));
    } else {
        const order = document.getElementById("order").value;
        songs = await api("GET", "/songs?order=" + order);
    }

    const emptyText = search !== ""
        ? "Nenhuma música com esse título."
        : "A biblioteca está vazia. Adicione uma música acima.";

    renderList("library", songs, (song) => [
        {
            label: "+ Playlist",
            onClick: async () => {
                await api("POST", "/playlist", { title: song.title, artist: song.artist });
                await loadPlayer();
            },
        },
        {
            label: "A seguir",
            onClick: async () => {
                await api("POST", "/queue", { title: song.title, artist: song.artist });
                await loadPlayer();
            },
        },
        {
            label: "Remover",
            danger: true,
            onClick: async () => {
                await api("DELETE", "/songs" + songQuery(song));
                await loadLibrary();
            },
        },
    ], emptyText);
}

// ================= player =================

function renderNowPlaying(song) {
    const cover = document.getElementById("now-cover");
    const title = document.getElementById("now-title");
    const artist = document.getElementById("now-artist");
    const duration = document.getElementById("now-duration");

    if (song === null) {
        cover.textContent = "♪";
        title.textContent = "Nada tocando";
        artist.textContent = "Adicione músicas à playlist e aperte play";
        duration.textContent = "";
        return;
    }

    cover.textContent = initial(song);
    title.textContent = song.title;
    artist.textContent = song.artist;
    duration.textContent = song.formatted_duration;
}

function renderPlayer(state) {
    renderNowPlaying(state.now_playing);

    document.getElementById("repeat").checked = state.repeat;

    renderList("playlist", state.playlist, (song) => [
        {
            label: "Remover",
            danger: true,
            onClick: async () => {
                await api("DELETE", "/playlist" + songQuery(song));
                await loadPlayer();
            },
        },
    ], "Playlist vazia.");

    // fila e historico so mostram as musicas, sem botoes
    renderList("queue", state.up_next, () => [], "Nenhuma música na fila.");
    renderList("history", state.history, () => [], "Nada tocou ainda.");
}

async function loadPlayer() {
    renderPlayer(await api("GET", "/player"));
}

// ================= eventos =================

document.getElementById("add-form").addEventListener("submit", (event) => {
    // sem isso o navegador recarrega a pagina ao enviar o formulario
    event.preventDefault();

    run(async () => {
        await api("POST", "/songs", {
            title: document.getElementById("add-title").value,
            artist: document.getElementById("add-artist").value,
            duration: Number(document.getElementById("add-duration").value),
        });
        event.target.reset();
        document.getElementById("add-title").focus();
        await loadLibrary();
    });
});

document.getElementById("search-form").addEventListener("submit", (event) => {
    event.preventDefault();
    run(loadLibrary);
});

document.getElementById("search-clear").addEventListener("click", () => {
    document.getElementById("search-title").value = "";
    run(loadLibrary);
});

document.getElementById("order").addEventListener("change", () => run(loadLibrary));

document.getElementById("btn-play").addEventListener("click", () =>
    run(async () => renderPlayer(await api("POST", "/player/play")))
);

document.getElementById("btn-next").addEventListener("click", () =>
    run(async () => renderPlayer(await api("POST", "/player/next")))
);

document.getElementById("btn-previous").addEventListener("click", () =>
    run(async () => renderPlayer(await api("POST", "/player/previous")))
);

document.getElementById("repeat").addEventListener("change", (event) =>
    run(async () => {
        const enabled = event.target.checked;
        try {
            renderPlayer(await api("PUT", "/player/repeat", { enabled: enabled }));
        } catch (e) {
            // a API recusou: volta o botao para como estava
            event.target.checked = !enabled;
            throw e;
        }
    })
);

// ================= inicio =================

run(async () => {
    await loadLibrary();
    await loadPlayer();
});
