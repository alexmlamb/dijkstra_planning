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
        elif state_dists[state] == 0 or state_dists[state] > 10:
            score = 0.0
        else:
            score = (1.0 / (1 + math.sqrt(state_counts[state]))) * (1.0 / max(1, state_dists[state]))
        scores.append(score)
 
    scores = numpy.array(scores)

    if scores.sum() < 1e-3:
        print('planning failure - no goals found')
        return None, -1

    scores = scores / (scores.sum())


    goal_idx = numpy.random.choice(numpy.arange(len(states)), p=scores)
    goal = states[goal_idx]

    steps_to_goal = state_dists[goal]


    return goal, steps_to_goal

def pick_action(allowable_actions, action_counts): 
    return random.choice(allowable_actions)


# Either picks a goal or picks an action randomly from set of allowable actions.  
# If goal=None or steps_to_goal=0, act randomly and then set a new goal and steps_to_goal.  
# Otherwise, follow to the goal and reduce steps_to_goal by 1.  

def get_action(screenshot, page_navigation_actions, direct_ui_actions, state_dict, action_id):

    allowed_actions = page_navigation_actions + direct_ui_actions

    start_state = encode(allowed_actions)

    state_counts = state_dict['state_counts']
    action_counts = state_dict['action_counts']
    graph = state_dict['graph']
    inv = state_dict['inv']

    goal = state_dict['goal']
    steps_to_goal = state_dict['steps_to_goal']

    opt_acts, opt_dists, _ = dijkstra(graph, start_state)



    #Did we hit goal, not have goal, or run out of steps?  
    if goal is None or goal == start_state or steps_to_goal <= 0 or not (start_state in graph.keys()):
        #random action and find a new goal.  
        chosen_action = random.choice(allowed_actions)

        goal, steps_to_goal = pick_goal(state_counts, opt_dists)

        state_dict['goal'] = goal
        state_dict['steps_to_goal'] = steps_to_goal

    else:
        print('try to hit goal', goal, 'in steps', steps_to_goal)
        #return action for goal and decrement steps to goal.  
        if goal in opt_acts and opt_dists[goal] <= steps_to_goal + 1:
            plan_seq = backtrack(opt_acts, start_state, goal)
            print('planned sequence to goal', plan_seq)
            chosen_action = random.choice(inv[(plan_seq[0], plan_seq[1])])
            state_dict['plan_acts'] += 1
            print('action to execute', chosen_action)
        else:
            chosen_action = random.choice(allowed_actions)
            state_dict['goal'] = None
            state_dict['steps_to_goal'] = -1

        state_dict['steps_to_goal'] -= 1


    return chosen_action, state_dict

def simulate_env(graph, inv, state, action):
    assert type(action) is str
    default = '03e5f372b4c1fb6059b95ea61365de30'

    if not state in graph:
        return default

    next_states = graph[state]
    for ns in next_states:
        for inv_action in inv[(state, ns)]:
            if inv_action == action:
                return ns
    
    #print('no successor found from', state, action, 'reset to start')
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

    return state_dict

if __name__ == "__main__":

    graph, inv, allowed_actions = get_graph()

    state_dict = init_state_dict(graph, inv)

    #Follow a data-collection loop and pretend that the graph is the true dynamics.  

    start_state = '03e5f372b4c1fb6059b95ea61365de30'

    print('start', start_state)
    print('re-encode', encode(allowed_actions[start_state]))
    assert start_state == encode(allowed_actions[start_state])

    #Initially get it to take random action, then try to get it to reach a goal.  
    #action, state_dict = get_action(screenshot=None, page_navigation_actions=allowed_actions[start_state], direct_ui_actions=[], state_dict=state_dict, action_id=None)

    for j in range(0, 2000000):
        
        if True:
            action = random.choice(allowed_actions[start_state])
        else:
            action, state_dict = get_action(screenshot=None, page_navigation_actions=allowed_actions[start_state], direct_ui_actions=[], state_dict=state_dict, action_id=None)

        print(j, start_state, action)
        print('steps-to-goal', state_dict['steps_to_goal'])
        start_state = simulate_env(graph, inv, start_state, action)

        if not start_state in state_dict['state_counts']:
            state_dict['state_counts'][start_state] = 0
        state_dict['state_counts'][start_state] += 1

    print('number planned actions', state_dict['plan_acts'])

    num_visited = 0
    for state in state_dict['state_counts']:
        if state_dict['state_counts'][state] >= 1:
            num_visited += 1
    print('number visited states', num_visited)

if False:

    graph, inv = get_graph()

    #start = '03e5f372b4c1fb6059b95ea61365de30'

    paths, dist, _ = dijkstra(graph, start)

    print(dist)

    #goal = '8f8b4ff07b75d46c05fe290433222130'
    #goal = '03e5f372b4c1fb6059b95ea61365de30'
    goal = 'e838873f7a0e6d0d8465cf31408fd9ef'

    p = backtrack(paths, start, goal)

    print('plan from', start, 'to', goal)

    print(p[0])
    for j in range(0, len(p)-1):
        print(inv[(p[j], p[j+1])], p[j+1])



