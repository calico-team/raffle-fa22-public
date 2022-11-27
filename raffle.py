import pandas as pd
import random

# Name of the column in raffle.csv whose values we will match with tickets.csv
# It doesn't need to be emails-- can be any string pretty much (ensure values match with values of below col)
RANKING_IDENTIFIER_COL = "Registration Email"
# Values in this col (zero indexed) in tickets.csv should match up with the values in the column above in raffle.csv
TICKET_IDENTIFIER_COL_IDX = 0
# The column index in tickets.csv that gives the number of tickets for that row
TICKET_COUNT_COL_IDX = 1
# When we make the preference grid, google sheets starts each option with the question name
PRIZE_COL_STARTS_WITH = "Raffle Prizes Ranking"
TICKET_CSV = "ticket-counts-test2.csv"
INVENTORY_CSV = "raffle-prizes-test2.csv"
PREFERENCES_CSV = "rankings-test2.csv"


def get_dist():
    df = pd.read_csv(TICKET_CSV)
    dist = dict()
    total = 0
    for index, row in df.iterrows():
        dist[row[TICKET_IDENTIFIER_COL_IDX]] = row[TICKET_COUNT_COL_IDX]
        total += row[TICKET_COUNT_COL_IDX]
    return dist, total


def rand_dist(dist, total):
    selected = random.randint(0, total - 1)  # inclusive
    so_far = 0
    for key in dist:
        so_far += dist[key]
        if so_far > selected:
            return key

    print("Error! Nothing found!")
    print(dist)
    print(total)
    print(selected)


# returns the key (identifier) of the person drawn
def draw_ticket(dist, total):
    key = rand_dist(dist, total)
    new_total = total - dist[key]
    del dist[key]  # remove the person
    return key, new_total


def get_inventory():
    df = pd.read_csv(INVENTORY_CSV)
    inventory = dict()

    for index, row in df.iterrows():
        inventory[row[0]] = row[1]

    return inventory


# returns false if failed
def remove_inventory(inventory, prize_name):
    if prize_name in inventory:
        if inventory[prize_name] == 0:
            return False
        inventory[prize_name] -= 1
        return True
    return False


# Returns a mapping of identifiers -> prize preferences (which are rank -> prize name)
def get_preferences():
    df = pd.read_csv(PREFERENCES_CSV)

    # prize_id to prize name
    prizes = dict()

    col: str = ""
    i = 0
    prize_id = 0
    start_col = None
    end_col = None
    name_col = None
    for col in df.columns:
        if col == RANKING_IDENTIFIER_COL:
            name_col = i
        if col.startswith(PRIZE_COL_STARTS_WITH):
            if start_col is None:
                start_col = i
            prize = col[col.index("[") + 1:col.index("]")]  # get prize name
            prizes[prize_id] = prize
            prize_id += 1
            end_col = i + 1
        i += 1

    people = dict()

    for index, row in df.iterrows():
        prize_id = 0
        ranks = dict()
        i = 0
        curr_name = ""
        curr_dict = dict()
        for value in row:
            # value is a ranking of that column's prize
            if i == name_col:
                ranks[value] = dict()
                curr_name = value
            if start_col <= i < end_col:
                # one of the prize columns
                curr_dict[value] = prizes[prize_id]
                prize_id += 1
            i += 1
        # assign people to their ranking preferences
        people[curr_name] = curr_dict

    return people


def main():

    # you did this
    with open('seed.txt', 'r') as seed_file:
        seed = seed_file.read()
    random.seed(seed)

    # main logic
    dist, total = get_dist()
    inventory = get_inventory()
    prefs = get_preferences()
    while len(dist) > 0:  # for each person
        person, total = draw_ticket(dist, total)
        if person not in prefs:
            print(f"{person} did not submit a preference form")
            continue
        person_prefs = prefs[person]
        # assuming we have preferences from 1 to max
        prize_get = False
        for i in range(1, 999):
            if i not in person_prefs:
                # didn't fill out all ranks, assume don't want anything
                break
            selected_prize = person_prefs[i]
            if remove_inventory(inventory, selected_prize):
                print(f"{person} drew {selected_prize}. {inventory[selected_prize]} remain...")
                prize_get = True
                break
        if not prize_get:
            print(person, "No prize left or prize not wanted")


if __name__ == "__main__":
    main()
    print("Finished")
