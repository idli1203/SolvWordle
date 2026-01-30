from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Input, Button, DataTable, Label
from textual.reactive import reactive
from textual import work
import logic

class WordleCell(Static):
    """A single cell in the Wordle grid. Click to toggle color."""

    # 0=Gray, 1=Yellow, 2=Green
    color_state = reactive(0)

    def render(self):
        return f"{self.id[-1]}" # For debug, just shows col index? No, we set content manually.

    def on_click(self):
        # Cycle 0 -> 1 -> 2 -> 0
        self.color_state = (self.color_state + 1) % 3
        self.update_style()

    def update_style(self):
        self.remove_class("gray", "yellow", "green")
        if self.color_state == 0:
            self.add_class("gray")
        elif self.color_state == 1:
            self.add_class("yellow")
        elif self.color_state == 2:
            self.add_class("green")

    def set_letter(self, letter):
        self.update(letter.upper())

class WordleApp(App):
    CSS_PATH = "wordle.tcss"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()

        # LEFT: Game Grid + Input
        with Container(id="game-container"):
            with Vertical():
                # Challenge: We need 6 rows of 5 cells
                for r in range(6):
                    with Horizontal(classes="row"):
                        for c in range(5):
                            yield WordleCell(id=f"cell-{r}-{c}", classes="cell")

                yield Input(placeholder="Type guess here...", id="guess_input")
                yield Button("Calculate Entropy", id="calc_btn", variant="primary")

        # RIGHT: Assistant
        with Container(id="sidebar"):
            with Vertical(id="stats-panel"):
                yield Label("Candidates: ??", id="candidate_count")

            yield DataTable(id="suggestions_table")

        yield Footer()

    def on_mount(self):
        self.active_turn = 0  # Initialize turn counter
        self.query_one("#candidate_count").update("Loading Matrix... Please Wait...")
        # Run loading in background so UI shows up instantly
        self.load_solver()

        # Setup Table
        table = self.query_one(DataTable)
        table.add_columns("Entropy", "Word")

    @work(exclusive=True, thread=True)
    def load_solver(self):
        # This takes ~2 seconds
        self.solver = logic.WordleSolver()
        # Update UI back on main thread (textual handles this thread-safety usually, but call_from_thread is safer for heavy updates)
        self.call_from_thread(self.on_solver_loaded)

    def on_solver_loaded(self):
        self.query_one("#candidate_count").update(f"Candidates: {len(self.solver.candidate_indices)}")
        self.notify("Solver Ready!", severity="information")
        # Suggest first word immediately
        self.update_suggestions()

    def on_button_pressed(self, event):
        if event.button.id == "calc_btn":
            self.run_turn()

    @work(exclusive=True, thread=True)
    def update_suggestions(self):
        # Run entropy calculation in background
        if not hasattr(self, 'solver') or self.solver is None:
            return

        # Top 15 is plenty for TUI
        results = self.solver.get_best_guesses(top_k=15)
        self.call_from_thread(self.update_table, results)

    def update_table(self, results):
        table = self.query_one(DataTable)
        table.clear()
        for entropy, word in results:
            table.add_row(f"{entropy:.4f}", word)

    def run_turn(self):
        """
        1. Read the Input (Guess Word).
        2. Read the Grid (Colors).
        3. Update Solver.
        """
        if not hasattr(self, 'solver'):
            self.notify("Solver still loading...", severity="warning")
            return

        if self.active_turn >= 6:
            self.notify("Game Over! Reset to play again.", severity="error")
            return

        inp = self.query_one(Input)
        guess = inp.value.lower().strip()

        if len(guess) != 5:
            self.notify("Word must be 5 letters!", severity="error")
            return

        if guess not in self.solver.guesses:
            self.notify("Not a valid word!", severity="error")
            return

        # 2. Get Colors for this guess
        # We need to look at the "Active Row" or let user specify pattern?
        # Current design: User can click cells freely.
        # Strategy: Find the row that matches the typed guess letters?
        # OR: Just look at the grid. Assuming user filled the top available row.

        # Simple version: We need to know which row we are on.
        # Let's count how many turns we've played based on solver candidates? No.
        # Let's add an explicit 'active_turn' counter to the class.
        r = self.active_turn

        # Construct pattern string from the grid cells at row r
        pattern_str = ""
        for c in range(5):
             cell = self.query_one(f"#cell-{r}-{c}", WordleCell)
             # Update letter
             cell.set_letter(guess[c])
             # Read color
             pattern_str += str(cell.color_state)

        # 3. Update Solver
        self.solver.update_candidates(guess, pattern_str)
        self.query_one("#candidate_count").update(f"Candidates: {len(self.solver.candidate_indices)}")

        if len(self.solver.candidate_indices) == 1:
            idx = self.solver.candidate_indices[0]
            ans = self.solver.answers[idx]
            self.notify(f"SOLVED! The word is: {ans.upper()}", severity="information", timeout=10)

        # 4. Next Turn
        self.active_turn += 1
        inp.value = ""
        inp.focus()

        # 5. Get new suggestions
        self.update_suggestions()


if __name__ == "__main__":
    app = WordleApp()
    app.run()
