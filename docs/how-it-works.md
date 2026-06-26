# How it works

Republic of Rome Online is a React web application paired with a Django backend server. The server is responsible for managing game state (the current phase, the senators in each faction, and the location of Rome's active forces), while the web application facilitates user interaction.

## Actions and effects

There are two types of game state modification:

- **Actions** are things players do, such as transferring money, attracting knights, or casting votes.
- **Effects** are non-player procedures, such as wars increasing unrest, revenue generation, or combat resolution.

Both actions and effects follow the command pattern and are centrally referenced in their respective registries.

## The action lifecycle

### 1. Availability calculation

After game state changes, the server works out which actions each player can perform. For each available action, it generates an action schema — a JSON-based description that defines:

- The type of action
- Any configuration data required
- How the action should be represented in the UI

Available actions and action schemas are only calculated once each time game state changes, then cached to the database.

### 2. Client representation

The web application uses schemas to construct UI elements such as buttons or forms. For more complex actions like attracting knights, the client receives enough information to calculate the probability of success based on real-time user input without having to contact the server.

### 3. Execution

When a player submits an action, the client sends a request containing the action type and any schema-specific data. The server then:

1. Maps the request to an action command object
2. Validates the input data
3. Modifies game state
4. Creates log entries documenting what happened

For example, a successful knight attraction updates the senator's stats (knights +1, talents −2) and creates a corresponding log entry.
