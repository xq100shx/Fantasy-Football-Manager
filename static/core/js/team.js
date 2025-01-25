const pitch = document.getElementById("pitch");
const playerModal = document.getElementById("playerModal");
const playerSearch = document.getElementById("playerSearch");
const playerList = document.getElementById("playerList");
const formationSelect = document.getElementById("formationSelect");
let selectedCard = null;

// Placeholder for players fetched from the database
const players = [
  { id: 1, name: "John Doe", photo: "{% static 'core/img/phplayer.jpg' %}" },
  { id: 2, name: "Jane Smith", photo: "{% static 'core/img/phplayer.jpg' %}" },
  { id: 3, name: "Mike Johnson", photo: "{% static 'core/img/phplayer.jpg' %}" },
];

// Function to generate formation dynamically
function generateFormation(formationRows) {
  //add the goalkeeper to the formation rows
  formationRows.unshift(1);
  const formation = [];
  const rowHeight = 100 / (formationRows.length + 1); // Divide pitch height evenly
  formationRows.reverse().forEach((playersInRow, rowIndex) => {
    const top = rowHeight * (rowIndex + 1); // Calculate vertical placement
    const colWidth = 100 / (playersInRow + 1); // Distribute players evenly horizontally
    for (let i = 1; i <= playersInRow; i++) {
      formation.push({
        top: `${top}%`,
        left: `${colWidth * i}%`,
      });
    }
  });

  return formation;
}

// Function to create a player card
function createPlayerCard(name = "", position = {}, clubLogoUrl = "") {
  const card = document.createElement("div");
  card.classList.add("player-card");
  card.style.top = position.top;
  card.style.left = position.left;
  card.innerHTML = `
    <img src="{% static 'core/img/placeholder150x150.png'%}" alt="Player">
    <div class="player-info"><p>${name || "Empty"}</p></div>
  `;
  card.addEventListener("click", () => {
    selectedCard = card;
    openModal();
  });
  return card;
}

// Function to render formation on the pitch
function renderFormation(formation) {
  pitch.innerHTML = "";
  formation.forEach((pos) => {
    const playerCard = createPlayerCard("", pos, "");
    pitch.appendChild(playerCard);
  });
}

// Open modal for player selection
function openModal() {
  playerModal.style.display = "block";
  playerSearch.value = "";
  renderPlayerList(players);
}

// Close modal
function closeModal() {
  playerModal.style.display = "none";
}

// Render player list in the modal
function renderPlayerList(playerListData) {
  playerList.innerHTML = "";
  playerListData.forEach((player) => {
    const li = document.createElement("li");
    li.classList.add("list-group-item");
    li.textContent = player.name;
    li.addEventListener("click", () => selectPlayer(player));
    playerList.appendChild(li);
  });
}

// Select a player and update the card
function selectPlayer(player) {
  if (selectedCard) {
    selectedCard.querySelector("img").src = player.photo;
    selectedCard.querySelector(".player-info p").textContent = player.name;
    closeModal();
  }
}
playerSearch.addEventListener('input', () => {
    const searchValue = playerSearch.value.toLowerCase();
    const filteredPlayers = players.filter(player =>
        player.name.toLowerCase().includes(searchValue)
    );
    renderPlayerList(filteredPlayers);
});
// Handle formation selection change
formationSelect.addEventListener("change", () => {
  const selectedFormation = formationSelect.value;
  let formation;

  switch (selectedFormation) {
    case "4-4-2":
      formation = generateFormation([4, 4, 2]);
      break;
    case "4-3-3":
      formation = generateFormation([4, 3, 3]);
      break;
    case "3-5-2":
      formation = generateFormation([3, 5, 2]);
      break;
    case "5-3-2":
      formation = generateFormation([5, 3, 2]);
      break;
    default:
      formation = generateFormation([4, 4, 2]);
  }

  renderFormation(formation);
});

// Default formation on page load
const defaultFormation = generateFormation([4, 4, 2]);
renderFormation(defaultFormation);
