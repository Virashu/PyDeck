"use strict";
/* Order
 *
 * 1. Get buttons, images, state, config
 * 2. Render buttons
 * 3. Handle clicks
 * 4. Update icons, states, etc.
 * 
*/

const clientConfig = config;
const HOST = `http://${clientConfig.address}:${clientConfig.port}`;

const nav = `
  <div class="nav-fixed">
    <button onclick="changePage('deck')">Deck</button>
    <button onclick="changePage('settings')">Settings</button>
  </div>
`;

var updatePending = false;
var deckConfig;

class Button {
  constructor(id, text) {
    [this.row, this.col] = id;
    this.id = `${this.row}:${this.col}`;
    this.text = text;
  }

  /* Render the button
   * @returns {string}
  **/
  render() {
    return `
      <div
        class="deck-button"
        style="grid-column: ${this.col + 1}; grid-row: ${this.row + 1};"
        onclick="deck_click('${this.id}')"
      >
        ${this.text}
      </div>
    `;
  }

  renderHtml() {
    divElement = document.createElement("div");
    divElement.classList.add("deck-button");
    divElement.style.gridColumn = this.col + 1;
    divElement.style.gridRow = this.row + 1;
    divElement.innerHTML = this.text;

    divElement.onclick = () => {
      deck_click(this.id);
    }

    return divElement;
  }
}

class PageDeck {
  constructor() {
    this.buttons = [];
  }

  async init() {
    this.buttons = await fetchButtons();
  }

  async update() {
    // Check if config changed
    // Check if buttons changed
    // Fetch everything

    this.buttons = await fetchButtons();
  }

  render() {
    let rendered = `
      <div class="deck">
        <div class="deck-button-container" style="--deck-rows: ${deckConfig.deck.rows}; --deck-columns: ${deckConfig.deck.cols};">
          ${this.buttons.map((b) => b.render()).join("")}
        </div>
      </div>
    `;
    return rendered;
  }
}

async function fetchActionsNames() {
  let response = await fetch(`${HOST}/api/actions_list`);
  if (!response.ok) {
    console.error("Failed to fetch actions");
    return [];
  }

  let data = await response.json();
  return data;
}

class PageSettings {
  constructor() {
    this.actions_list = [];
  }

  async init() {
    this.actions_list = await fetchActionsNames();
  }

  async update() {
    this.actions_list = await fetchActionsNames();
  }

  render() {
    return `
      <div class="settings">
        <h1>Settings</h1>
        <ul>
          ${this.actions_list.map((action) => `<li>${action}</li>`).join("")}
        </ul>
      </div>
    `;
  }
}

function deck_click(button_id) {
  fetch(`${HOST}/api/event`, {
    method: "POST",
    headers: {
      'Accept': '*',
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: "click",
      data: {
        button_id,
      },
    }),
  });
}

var root = document.getElementById("root");

function render(page) {
  root.innerHTML = page.render();
}

async function fetchButtons() {
  let response = await fetch(`${HOST}/api/buttons`);
  if (!response.ok) {
    console.error("Failed to fetch buttons");
    return [];
  }

  let data = await response.json();
  let buttons = data.buttons.map((button) =>
    new Button(button.id, button.text)
  );
  updatePending = true;
  return buttons;
}

async function fetchConfig() {
  let response = await fetch(`${HOST}/api/config`);
  let data = await response.json();
  return data;
}

async function init() {
  deckConfig = await fetchConfig();

  root.innerHTML = nav;
  let newRoot = document.createElement("div");
  newRoot.classList.add("container");
  root.appendChild(newRoot);

  root = newRoot;

  updatePending = true;
}

init();

const pages = {
  "deck": new PageDeck(),
  "settings": new PageSettings(),
}

var currentPage = "deck";

function changePage(newPage) {
  console.log(newPage);
  if (newPage === currentPage) return;
  if (!pages[newPage]) return;
  currentPage = newPage;
  pages[currentPage].init();

  requestUpdate();
}

function requestUpdate() {
  updatePending = true;
}

function update() {
  let page = pages[currentPage];
  if (!page) return;
  page.update();

  if (updatePending) {
    updatePending = false;
    render(page);
  }
}

update();
setInterval(update, 500);

