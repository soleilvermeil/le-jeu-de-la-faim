import copy
import os
from typing import List, TypeVar, Any
import pandas as pd  # only for logging
from .engine import game
from .shared import utils
from .agents import BaseAgent


# Define the type of the agent
Agent = TypeVar("Agent", bound=BaseAgent)


# TODO: Combine this with the same function from BaseAgent
def __messages2str(messages: List[str]) -> str:
    """
    Returns a string representation of a list of messages.
    """
    # Naive conversion of list of messages to a string
    messages = "\n".join(messages)

    # Removes all newline characters at the start and end of each message
    messages = messages.strip("\n")

    # Removes all triple newline characters with double
    messages = messages.replace("\n\n\n", "\n\n")

    # Return
    return messages


# TODO: Put this in a similar place as __messages2str
def __str2border(s: str, total_length: int = 80) -> str:
    """
    Returns a string with a border around it.
    """
    return f"{s:-<{total_length-1}}"


def __save_txt(game_, state_history) -> None:
    """
    Save the game log to a text file.
    """
    os.makedirs("logs", exist_ok=True)
    debug_messages = []
    for state in state_history:
        debug_messages.append(__messages2str(state["debug"]["messages"]))
        debug_messages.append("")
    with open(os.path.join("logs", f"log_{game_.id}.txt"), "w", encoding="utf8") as f:
        f.write(__messages2str(debug_messages) + "\n")


def __save_tsv(game_, state_history) -> None:
    """
    Save the full state history to a TSV file. Each row corresponds to a given
    point in time in the game, times the number of characters in the game.
    """
    os.makedirs("logs", exist_ok=True)
    data = {}
    for state in state_history:
        game_state = state["game"]
        for character in list(state["characters"].keys()):
            character_state = state["characters"][character]

            flattened_game_state = utils.flatten_dict({"game": game_state})
            flattened_game_state = utils.transform_dict_values(
                dct=flattened_game_state,
                transformations=[
                    (list, lambda x: "<list>"),
                    (str, lambda x: x if "\n" not in x else "<str>")
                ]
            )
            flattened_character_state = utils.flatten_dict({"character": character_state})
            flattened_character_state = utils.transform_dict_values(
                dct=flattened_character_state,
                transformations=[
                    (list, lambda x: "<list>"),
                    (str, lambda x: x if "\n" not in x else "<str>")
                ]
            )

            combined_state = {**flattened_game_state, **flattened_character_state}

            if not data:
                for key in combined_state.keys():
                    data[key] = [combined_state[key]]
            else:
                for key in combined_state.keys():
                    data[key].append(combined_state[key])
    df = pd.DataFrame(data)
    df.to_csv(os.path.join("logs", f"log_{game_.id}.tsv"), sep="\t", index=False, encoding="utf8")


def __return_leaderboard(game_, state_history) -> pd.DataFrame:

    # Define the leaderboard, where keys are name of the characters and values
    # are their final rank in the game (1 for the winner, 2 for the
    # second place, etc.)
    leaderboard = {
        "game_id": [],
        "character_name": [],
        "rank": [],
    }

    # Check each state to get the alive characters, in reverse order
    for state in reversed(state_history):

        alive_characters = state["game"]["state"]["alive_characters"]
        number_of_entries_in_leaderboard = len(leaderboard["character_name"])

        for character in alive_characters:
            if character not in leaderboard["character_name"]:
                leaderboard["game_id"].append(game_.id)
                leaderboard["character_name"].append(character)
                leaderboard["rank"].append(number_of_entries_in_leaderboard + 1)

    # Save the leaderboard to a TSV file
    # os.makedirs("logs", exist_ok=True)
    df = pd.DataFrame(leaderboard)
    # df.to_csv(os.path.join("logs", f"leaderboard_{game_.id}.tsv"), sep="\t", index=False, encoding="utf8")
    return df


def api(
    agents: List[Agent],
    map_name: str | None = None,
    verbose: bool = False,
    save_txt: bool = False,
    save_tsv: bool = False,
    return_leaderboard: bool = False,
) -> None | dict[str, Any]:

    # Check that all agents are unique
    names = [agent.name for agent in agents]
    assert len(names) == len(utils.unique(names)), "All agents must have unique names."

    # Create the game object
    game_ = game.Game(character_names=[agent.name for agent in agents], map_name=map_name)

    # Start the game
    game_.start_game()

    # Define the state and the state history
    state = {}
    state_history = []

    while not state or len(state["game"]["state"]["alive_characters"]) > 1:

        # Get the current state of the game
        state = game_.get_state_of_game()

        # Save the state
        state_history.append(copy.deepcopy(state))

        # Print the public messages
        if verbose:
            print(__str2border(""))
            print(__messages2str(state["debug"]["messages"]))
            print(__str2border(""))

        # Send to all agents the state of the game
        for agent in agents:

            # If character has been dead last turn, skip
            if len(state_history) >= 2 and not state_history[-2]["characters"][agent.name]["state"]["alive"]:
                continue

            # Communicate the state of the game to the agent
            agent.give_state_of_game(state)

        # If only a single character is left, exit the loop
        if len(state["game"]["state"]["alive_characters"]) == 1:
            break

        # Ask each agent to make a decision
        for agent in agents:

            # Check if still alive. If dead, do only inform about the death
            # if it has not been done already. If still alive, ask for a
            # decision.
            if not state["characters"][agent.name]["state"]["alive"]:
                if len(state_history) >= 2 and state_history[-2]["characters"][agent.name]["state"]["alive"]:
                    agent.inform_death()
                continue
            else:
                action = agent.interrogate()
                # print(f"{agent.name} decided to {action}.")

            # Send the decision to the game
            game_.set_action(agent.name, action)

        # Update the game once all agents have made their decisions
        game_.update_game()

    # Print the winner
    if verbose:
        print("Game over! Winner is " + utils.smart_join(lst=[c.name for c in game_.get_alive_characters()], sep=", ", last_sep=" and ") + "!")

    values_to_return: dict[str, Any] = {}

    # Save the game log
    if save_txt:
        __save_txt(game_, state_history)

    # Save the full state history
    if save_tsv:
        __save_tsv(game_, state_history)

    # Save the leaderboard
    if return_leaderboard:
        leaderboard = __return_leaderboard(game_, state_history)
        values_to_return["leaderboard"] = leaderboard

    # Return
    return None if not values_to_return else values_to_return
