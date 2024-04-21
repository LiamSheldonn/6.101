"""
6.101 Lab 5:
Recipes
"""

import pickle
import sys

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def atomic_ingredient_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    out = {}
    for item in recipes:
        if item[0] == "atomic":
            out[item[1]] = item[2]
    return out


def compound_ingredient_possibilities(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """

    out = {}
    for item in recipes:
        if item[0] == "compound":
            if item[1] in out:
                out[item[1]].append(item[2])
            else:
                out[item[1]] = [item[2]]

    return out


def lowest_cost(recipes, food_item, forbiddens=None):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    return cheapest_flat_recipe(recipes, food_item, forbiddens, return_cost=True)


def scaled_flat_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    if flat_recipe is not None:
        out = {}
        for k in flat_recipe:
            out[k] = flat_recipe[k] * n
        return out
    else:
        return None


def add_flat_recipes(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        add_flat_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    out = {}
    for recipe in flat_recipes:
        for k in recipe:
            if k in out:
                out[k] += recipe[k]
            else:
                out[k] = recipe[k]
    return out


def price_from_flatlist(flat_list, atomic_dict):
    return sum(atomic_dict[k] * flat_list[k] for k in flat_list) if flat_list else None


def cheapest_flat_recipe(recipes, food_item, forbiddens=None, return_cost=False):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    comp_dict = compound_ingredient_possibilities(recipes)
    atomic_dict = atomic_ingredient_costs(recipes)
    if forbiddens:
        forbidden_set = set(forbiddens)
    else:
        forbidden_set = set()

    def recursive_helper(food_item):
        if food_item in forbidden_set:
            # print(f'Item {food_item} in forbiddens.')
            return None
        elif food_item in atomic_dict:
            out = {food_item: 1}
            # print(f'At atomic item {food_item}. Returning {out}.')
            return out
        elif food_item in comp_dict:
            all_recipes = []
            for recipe in comp_dict[food_item]:
                out = {}
                for ing, amount in recipe:
                    subdict = recursive_helper(ing)
                    if subdict:
                        subdict_scaled = scaled_flat_recipe(subdict, amount)
                        out = add_flat_recipes([out, subdict_scaled])
                    else:
                        print("Current recipe not valid.")
                        out = None
                        break
                if out:
                    all_recipes.append(out)
            if all_recipes:
                costs = [
                    price_from_flatlist(recipe, atomic_dict) for recipe in all_recipes
                ]
                min_cost_recipe = all_recipes[costs.index(min(costs))]
                # print(f'At compound item {food_item}. Returning {min_cost_recipe}.')
                return min_cost_recipe
            else:
                print(f"No valid recipes for {food_item}.")
                return None

        else:
            # print(f'Item {food_item} not in recipebook.')
            return None

    least = recursive_helper(food_item)
    return price_from_flatlist(least, atomic_dict) if return_cost else least


def combined_flat_recipes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes for a certain ingredient, compute and return a list of flat
    recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """
    new = []
    if len(flat_recipes) == 1:
        new = flat_recipes[0]
    else:
        combined = combined_flat_recipes(flat_recipes[1:])
        for recipe in combined:
            for item in flat_recipes[0]:
                new.append(add_flat_recipes([item, recipe]))
    return new


def all_flat_recipes(recipes, food_item, forbiddens=None):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    comp_dict = compound_ingredient_possibilities(recipes)
    atomic_dict = atomic_ingredient_costs(recipes)
    if forbiddens:
        forbidden_set = set(forbiddens)
    else:
        forbidden_set = set()

    def recursive_helper(food_item):
        if food_item in forbidden_set:
            # print(f'Item {food_item} in forbiddens.')
            return None
        elif food_item in atomic_dict:
            out = [{food_item: 1}]
            # print(f'At atomic item {food_item}. Returning {out}.')
            return out
        elif food_item in comp_dict:
            real_flats = []
            for recipe in comp_dict[food_item]:
                full_flat_rec_list = []
                for ing, amount in recipe:
                    flat_recipes = recursive_helper(ing)
                    if flat_recipes:
                        flat_rec_scaled = [
                            scaled_flat_recipe(flat, amount)
                            for flat in flat_recipes
                            if flat
                        ]
                        full_flat_rec_list.append(flat_rec_scaled)
                    else:
                        # print('Current recipe not valid.')
                        full_flat_rec_list = None
                        break
                if full_flat_rec_list:
                    combined = combined_flat_recipes(full_flat_rec_list)
                    real_flats = real_flats + combined
            # print(f'At compound item {food_item}. Returning {real_flats}.')
            return real_flats

        else:
            # print(f'Item {food_item} not in recipebook.')
            return None

    out = recursive_helper(food_item)
    return out if out else []


if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)

    # print(sum(atomic_ingredient_costs(example_recipes).values()))
    # c = 0
    # comp_pos_list = compound_ingredient_possibilities(example_recipes)
    # for item in comp_pos_list:
    #     if len(comp_pos_list[item])>1:
    #         c+=1
    # print(c)

    cookie_recipes = [
        ("compound", "cookie sandwich", [("cookie", 2), ("ice cream scoop", 3)]),
        ("compound", "cookie", [("chocolate chips", 3)]),
        ("compound", "cookie", [("sugar", 10)]),
        ("atomic", "chocolate chips", 200),
        ("atomic", "sugar", 5),
        ("compound", "ice cream scoop", [("vanilla ice cream", 1)]),
        ("compound", "ice cream scoop", [("chocolate ice cream", 1)]),
        ("atomic", "vanilla ice cream", 20),
        ("atomic", "chocolate ice cream", 30),
    ]
    print(all_flat_recipes(cookie_recipes, "cookie sandwich"))
    # print(lowest_cost(cookie_recipes, 'cookie sandwich'))
    # dairy_recipes_2 = [
    # ('compound', 'milk', [('cow', 2), ('milking stool', 1)]),
    # ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    # ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    # ('atomic', 'milking stool', 5),
    # ('atomic', 'cutting-edge laboratory', 1000),
    # ('atomic', 'time', 10000),
    # ]
    # print(lowest_cost(dairy_recipes_2, 'cheese'))
    # soup = {
    #     "carrots": 5,
    #     "celery": 3,
    #     "broth": 2,
    #     "noodles": 1,
    #     "chicken": 3,
    #     "salt": 10
    #     }
    # # print(scaled_flat_recipe(soup, 3))
    # carrot_cake = {
    #     "carrots": 5,
    #     "flour": 8,
    #     "sugar": 10,
    #     "oil": 5,
    #     "eggs": 4,
    #     "salt": 3
    #     }
    # bread = {"flour": 10, "sugar": 3, "oil": 3, "yeast": 15, "salt": 5}
    # grocery_list = [soup, carrot_cake, bread]
    # print(add_flat_recipes(grocery_list))
    # dairy_recipes = [
    # ('compound', 'milk', [('cow', 2), ('milking stool', 1)]),
    # ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    # ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    # ('atomic', 'milking stool', 5),
    # ('atomic', 'cutting-edge laboratory', 1000),
    # ('atomic', 'time', 10000),
    # ('atomic', 'cow', 100),
    # ]
    # print(cheapest_flat_recipe(dairy_recipes, 'cheese', ['cow']))

    # cake_recipes = [{"cake": 1}, {"gluten free cake": 1}]
    # icing_recipes = [{"vanilla icing": 1}, {"cream cheese icing": 1}]
    # topping_recipes = [{"sprinkles": 20}]
    # print(combined_flat_recipes([cake_recipes, icing_recipes, topping_recipes]))
