"use strict";

// @ts-ignore (external)
const clientConfig = config;

const HOST = `http://${clientConfig.address}:${clientConfig.port}`;
const nav = `
  <div class="nav-fixed">
    <button onclick="changePage('deck')">Deck</button>
    <button onclick="changePage('settings')">Settings</button>
  </div>
`;

/**
 * @template T
 * @typedef {{ [x: string]: T }} Dict<T>
 */

/**
 * @typedef {Dict<Button>} ButtonDict
 * @typedef {Dict<HTMLElement>} HTMLButtonDict
 * @typedef {{
 *   deck: {
 *     rows: number,
 *     cols: number,
 *   }
 * }} DeckConfig
 * @typedef {{
 *   id: [number, number];
 *   text: string;
 *   text_align: string;
 *   font_family: string;
 *   font_size: string;
 * }} JSONButton
 */

/**
 * @interface Page
 * @prop {boolean} pending_render
 * @method {(): Promise<void>} init
 * @method {(): Promise<void>} update
 * @method {(): HTMLElement} render
 */

/*
 * @typedef {object} Page
 * @property {boolean} pending_render
 */
/*
 * @method
 * @name Page#init
 * @returns {Promise<void>}
 */
/*
 * @method
 * @name Page#update
 * @returns {Promise<void>}
 */
/*
 * @method
 * @name Page#render
 * @returns {HTMLElement}
 */

/** @type {DeckConfig} */
var deckConfig;

/** @type {HTMLElement} */
// @ts-ignore
var root = document.getElementById("root");

class Button {
  /** @type {number} */
  row;
  /** @type {number} */
  col;
  /** @type {string} */
  id_str;
  /** @type {string} */
  text;
  /**
   * @param {[number, number]} id_arr
   * @param {string} text
   */
  constructor(id_arr, text) {
    [this.row, this.col] = id_arr;
    this.id_str = `${this.row}:${this.col}`;
    this.text = text;
  }
  /**
   * @returns {HTMLDivElement}
   */
  renderHtml() {
    let divElement = document.createElement("div");
    divElement.classList.add("deck-button");
    divElement.style.gridColumn = `${this.col + 1}`;
    divElement.style.gridRow = `${this.row + 1}`;
    divElement.innerHTML = this.text;
    divElement.onclick = () => {
      deck_click(this.id_str);
    };
    return divElement;
  }
}

/**
 * @param {number} rows
 * @param {number} cols
 * @returns {ButtonDict}
 */
function createBlankButtons(rows, cols) {
  /** @type {ButtonDict} */
  var res = {};
  for (var y = 0; y < rows; y++) {
    for (var x = 0; x < cols; x++) {
      let id_str = `${y}:${x}`;
      res[id_str] = new Button([y, x], "&nbsp;?");
    }
  }
  return res;
}

/**
 * @implements {Page}
 */
class PageLoading {
  /**
   * @type {boolean}
   */
  pending_render;
  /**
   *
   */
  constructor() {}
  /**
   * @returns {Promise<void>}
   */
  async init() {}
  /**
   * @returns {Promise<void>}
   */
  async update() {}
  /**
   * @returns {HTMLDivElement}
   */
  render() {
    return document.createElement("div");
  }
}

/**
 * @implements {Page}
 */
class PageDeck {
  rootEl;
  container;
  /**
   * @type {ButtonDict}
   */
  buttons;
  /**
   * @type {{ [x: string]: string; }}
   */
  button_hashes;
  /**
   * @type {{ [x: string]: HTMLElement; }}
   */
  rendered;
  /**
   * @type {boolean}
   */
  pending_render;
  /**
   * @type {DeckConfig}
   */
  prev_config;

  constructor() {
    this.rootEl = document.createElement("div");
    this.rootEl.classList.add("deck");
    this.container = document.createElement("div");
    this.container.classList.add("deck-button-container");
    this.rootEl.appendChild(this.container);
  }
  /**
   * @returns {void}
   */
  update_size() {
    this.container.style.setProperty("--deck-rows", `${deckConfig.deck.rows}`);
    this.container.style.setProperty("--deck-cols", `${deckConfig.deck.cols}`);
  }
  /**
   * @returns {Promise<void>}
   */
  async init() {
    this.buttons = createBlankButtons(clientConfig.rows, clientConfig.cols);
    this.button_hashes = {};
    this.rendered = {};
    for (let id in this.buttons) {
      this.button_hashes[id] = JSON.stringify(this.buttons[id]);
    }
    let buttons = await JSONToButtons(await fetchButtonsJSON());
    buttons.forEach((button) => {
      this.button_hashes[button.id_str] = JSON.stringify(button);
      this.buttons[button.id_str] = button;
    });
    let to_append = [];
    for (let id in this.buttons) {
      let button = this.buttons[id];
      this.rendered[id] = button.renderHtml();
      to_append.push(this.rendered[id]);
    }
    this.container.replaceChildren(...to_append);
    this.pending_render = true;
    this.update_size();
  }
  /**
   * @returns {Promise<void>}
   */
  async update() {
    if (deckConfig != this.prev_config) {
      this.prev_config = deckConfig;
      this.update_size();
      await this.init();
      return;
    }
    let new_buttons = await JSONToButtons(await fetchButtonsJSON());
    new_buttons.forEach((button) => {
      let id_str = button.id_str;
      let hash = JSON.stringify(button);
      if (this.button_hashes[id_str] !== hash) {
        this.button_hashes[id_str] = hash;
        this.buttons[id_str] = button;
        this.rendered[id_str].innerHTML = button.renderHtml().innerHTML;
        this.pending_render = true;
      }
    });
  }
  /**
   * @returns {HTMLElement}
   */
  render() {
    return this.rootEl;
  }
}

/**
 * @param {string} str
 * @returns {HTMLElement}
 */
function textToEl(str) {
  let wrapper = document.createElement("div");
  wrapper.innerHTML = str;
  // @ts-ignore
  return wrapper.firstChild;
}

/**
 * @returns {Promise<Array<string>>}
 */
async function fetchActionsNames() {
  let response = await fetch(`${HOST}/api/actions_list`);
  if (!response.ok) {
    console.error("Failed to fetch actions");
    return [];
  }
  let data = await response.json();
  return data;
}

/**
 * @implements {Page}
 */
class PageSettings {
  actions_list;
  /**
   * @type {boolean}
   */
  pending_render;
  /**
   *
   */
  constructor() {
    this.actions_list = [];
  }
  /**
   * @returns {Promise<void>}
   */
  async init() {
    this.actions_list = await fetchActionsNames();
    this.pending_render = true;
  }
  /**
   * @returns {Promise<void>}
   */
  async update() {
    this.actions_list = await fetchActionsNames();
    this.pending_render = true;
  }
  /**
   * @returns {HTMLElement}
   */
  render() {
    let s = `
      <div class="settings">
        <h1>Settings</h1>
        <ul>
          ${this.actions_list.map((action) => `<li>${action}</li>`).join("")}
        </ul>
      </div>
    `;
    return textToEl(s);
  }
}

/** @type {Dict<Page>} */
var pages = {
  loading: new PageLoading(),
  deck: new PageDeck(),
  settings: new PageSettings(),
};

var currentPage = "loading";

/**
 * @param {string} button_id
 * @returns {void}
 */
function deck_click(button_id) {
  fetch(`${HOST}/api/event`, {
    method: "POST",
    headers: {
      Accept: "*",
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type: "click",
      data: {
        button_id,
      },
    }),
  });
}

/**
 * @returns {Promise<Array<JSONButton>>}
 */
async function fetchButtonsJSON() {
  let response = await fetch(`${HOST}/api/buttons`);
  if (!response.ok) {
    console.error("Failed to fetch buttons");
    return [];
  }
  let data = await response.json();
  return data;
}

/**
 * @param {Array<JSONButton>} data
 * @returns {Array<Button>}
 */
function JSONToButtons(data) {
  return data.map((button) => new Button(button.id, button.text));
}

/**
 * @returns {Promise<DeckConfig>}
 */
async function fetchDeckConfig() {
  let response = await fetch(`${HOST}/api/config`);
  let data = await response.json();
  return data;
}

/**
 * @returns {void}
 */
function render() {
  let page = pages[currentPage];
  root.replaceChildren(page.render());
}

/** @returns {Promise<void>} */
async function init() {
  deckConfig = await fetchDeckConfig();
  root.innerHTML = nav;
  let newRoot = document.createElement("div");
  newRoot.classList.add("container");
  root.appendChild(newRoot);
  root = newRoot;
  await changePage("deck");
}

init();

/**
 * @param {string} newPage
 * @returns {Promise<void>}
 */
async function changePage(newPage) {
  if (newPage === currentPage) return;
  if (pages[newPage] === undefined) return;
  currentPage = newPage;
  await pages[currentPage].init();
}

/** @returns {Promise<void>} */
async function update() {
  let page = pages[currentPage];
  if (!page) {
    console.error("Page is None");
    return;
  }
  await page.update();
  if (page.pending_render) {
    page.pending_render = false;
    render();
  }
}

update();
setInterval(update, 100);
