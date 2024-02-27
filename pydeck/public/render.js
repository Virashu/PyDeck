"use strict";

const root = document.getElementById("root");
var deck_config;
var buttons = [];
var updatePending = false;

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


var baseRows = 3;
var baseCols = 5;
var baseButtons = [];
for (let i = 0; i < baseRows; i++) {
  for (let j = 0; j < baseCols; j++) {
    baseButtons.push(new Button(`${i}:${j}`, `${i}:${j}`));
  }
}

/* Order
 *
 * 1. Get buttons, images, state, config
 * 2. Render buttons
 * 3. Handle clicks
 * 4. Update icons, states, etc.
 * 
*/



function deck_click(button_id) {
  console.log("click!");
  fetch(`http://${config.address}:${config.port}/api/event`, {
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

function renderScreen() {
  let rendered = `
    <div class="deck">
      <div class="deck-button-container">
        ${buttons.map((b) => b.render()).join("")}
      </div>
    </div>
  `;
  root.innerHTML = rendered;
}

const fetchButtons = () => {
  fetch(`http://${config.address}:${config.port}/api/buttons`)
    .then((res) => res.json())
    .then((res) => {
      buttons = res.buttons.map((button) =>
        new Button(button.id, button.text)
      );
      updatePending = true;
    })
}

const init = async () => {
  fetchButtons();
  fetch(`http://${config.address}:${config.port}/api/config`, {
    'Access-Control-Allow-Origin': '*',
  })
    .then((res) => res.json())
    .then((res) => {
      let css_vars = document.documentElement.style;
      css_vars.setProperty("--deck-rows", res.dimensions.rows);
      css_vars.setProperty("--deck-columns", res.dimensions.cols);
      updatePending = true;
    })
}

const initTest = () => {
  buttons = baseButtons;
  let css_vars = document.documentElement.style;
  css_vars.setProperty("--deck-rows", baseRows);
  css_vars.setProperty("--deck-columns", baseCols);
  updatePending = true;
}

init();
renderScreen();

setInterval(() => {
  fetchButtons();
  if (updatePending) {
    updatePending = false;
    renderScreen();
  }
}, 100);
