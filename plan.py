'''

Get: 
    graph of s --> next_state_lst, (s1,s2) --> action_set.  

'''


from data import get_graph, encode
from dijkstra import dijkstra, backtrack
import random
import math
import numpy

def pick_goal(state_counts, state_dists):
    states = list(state_counts.keys())
    scores = []

    for state in states:

        if not state in state_dists:
            score = 0.0
        elif state_dists[state] == 0 or state_dists[state] > 100:
            score = 0.0
        else:
            score = (1.0 / (1.0 + math.sqrt(state_counts[state]))) * (1.0 / max(1, state_dists[state]))
        scores.append(score)
 
    scores = numpy.array(scores)

    if scores.sum() < 1e-3:
        #print('planning failure - no goals found')
        return None, -1

    scores = scores / (scores.sum())


    goal_idx = numpy.random.choice(numpy.arange(len(states)), p=scores)
    goal = states[goal_idx]

    steps_to_goal = state_dists[goal]


    return goal, steps_to_goal

def pick_action(action_counts, allowed_actions): 

    scores = []

    for action in allowed_actions: 
        if not action in action_counts:
            action_counts[action] = 0
        score = 1.0 / (1.0 + math.sqrt(action_counts[action]))
        scores.append(score)

    scores = numpy.array(scores)

    if scores.sum() < 1e-3:
        return random.choice(allowed_actions)

    scores = scores/scores.sum()

    score_idx = numpy.random.choice(numpy.arange(len(allowed_actions)), p=scores)

    action = allowed_actions[score_idx]

    return action


# Either picks a goal or picks an action randomly from set of allowable actions.  
# If goal=None or steps_to_goal=0, act randomly and then set a new goal and steps_to_goal.  
# Otherwise, follow to the goal and reduce steps_to_goal by 1.  

def get_action(screenshot, page_navigation_actions, direct_ui_actions, state_dict, action_id, config):

    allowed_actions = page_navigation_actions + direct_ui_actions

    start_state = encode(allowed_actions)

    state_counts = state_dict['state_counts']
    action_counts = state_dict['action_counts']
    graph = state_dict['graph']
    inv = state_dict['inv']

    goal = state_dict['goal']
    steps_to_goal = state_dict['steps_to_goal']

    if config['rare_action_policy']:
        chosen_action = pick_action(action_counts, allowed_actions)
        return chosen_action, state_dict

    opt_acts, opt_dists, _ = dijkstra(graph, start_state)


    if opt_dists[config['home_state']] > 1000:
        #print('cannot find route home!  Should trigger reset to VM?')
        state_dict['no_way_home'] = True
    else:
        state_dict['no_way_home'] = False

    #Did we hit goal, not have goal, or run out of steps?  
    if goal is None or goal == start_state or steps_to_goal <= 0 or not (start_state in graph.keys()):

        if goal == start_state:
            state_dict['hit_goal'] += 1

        #random action and find a new goal.  
        chosen_action = pick_action(action_counts, allowed_actions)

        goal, steps_to_goal = pick_goal(state_counts, opt_dists)
        steps_to_goal += config['extra_plan_steps']

        state_dict['goal'] = goal
        state_dict['steps_to_goal'] = steps_to_goal


    else:

        if goal in opt_acts and opt_dists[goal] <= steps_to_goal:
            plan_seq = backtrack(opt_acts, start_state, goal)
            #print('planned sequence to goal', plan_seq)
            chosen_action = random.choice(inv[(plan_seq[0], plan_seq[1])])
            state_dict['plan_acts'] += 1
            #print('action to execute', chosen_action)
        else:
            
            chosen_action = pick_action(action_counts, allowed_actions)
            state_dict['goal'] = None
            state_dict['steps_to_goal'] = -1
            state_dict['plan_fail'] += 1

        state_dict['steps_to_goal'] -= 1

    return chosen_action, state_dict

def simulate_env(graph, inv, state, action, config):
    assert type(action) is str

    default = config['home_state']

    if not state in graph:
        return default

    next_lst = []

    next_states = graph[state]
    for ns in next_states:
        for inv_action in inv[(state, ns)]:
            if inv_action == action:
                next_lst.append(ns)

    if len(next_lst) >= 1:
        return random.choice(next_lst)
    else:
        return default

def init_state_dict(graph, inv):

    state_counts = {}
    action_counts = {}

    for s in graph.keys():
        state_counts[s] = 0

    for alst in inv.values():
        for a in alst:
            action_counts[a] = 0

    state_dict = {}
    state_dict['state_counts'] = state_counts
    state_dict['action_counts'] = action_counts
    state_dict['graph'] = graph
    state_dict['goal'] = None
    state_dict['steps_to_goal'] = -1
    state_dict['inv'] = inv
    state_dict['plan_acts'] = 0
    state_dict['plan_fail'] = 0
    state_dict['hit_goal'] = 0
    state_dict['no_way_home'] = False

    return state_dict

if __name__ == "__main__":

    config = {}
    config['extra_plan_steps'] = 1.0  #This is how many extra steps we give the model to reach a plan.  
    config['p_reset_nowayhome'] = 0.1 #If we can't find a path to home state, then we hard-reset with this probability.  
    config['home_state'] = '03e5f372b4c1fb6059b95ea61365de30'
    config['rare_action_policy'] = False # Just act by sampling rarely-taken actions, with no planning

    graph, inv, allowed_actions = get_graph()

    state_dict = init_state_dict(graph, inv)

    start_state = config['home_state']

    print('start', start_state)
    print('re-encode', encode(allowed_actions[start_state]))
    assert start_state == encode(allowed_actions[start_state])

    random_policy = False

    for j in range(0, 2000000):

        if random_policy:
            action = random.choice(allowed_actions[start_state])
            no_route_home = False
        else:
            action, state_dict = get_action(screenshot=None, page_navigation_actions=allowed_actions[start_state], direct_ui_actions=[], state_dict=state_dict, action_id=None, config=config)

        if j % 100 == 0:
            print(j, start_state, action)
            print('steps-to-goal', state_dict['steps_to_goal'])
        start_state = simulate_env(graph, inv, start_state, action, config)

        if state_dict['no_way_home'] and random.uniform(0,1) < config['p_reset_nowayhome']:
            start_state = config['home_state']

        if not start_state in state_dict['state_counts']:
            state_dict['state_counts'][start_state] = 0
        state_dict['state_counts'][start_state] += 1

        if not action in state_dict['action_counts']:
            state_dict['action_counts'][action] = 0
        state_dict['action_counts'][action] += 1

    print('number planned actions', state_dict['plan_acts'])
    print('number of goal-hits', state_dict['hit_goal'])
    print('number of planning-fails', state_dict['plan_fail'])

    num_visited = 0
    for state in state_dict['state_counts']:
        if state_dict['state_counts'][state] >= 1:
            num_visited += 1
    print('number visited states', num_visited)

    num_actions = 0
    for action in state_dict['action_counts']:
        if state_dict['action_counts'][action] > 0:
            num_actions += 1

    print('num actions visited', num_actions)




