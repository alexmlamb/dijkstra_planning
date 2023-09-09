import sys

from hashlib import md5

import glob
flist = glob.glob("../data/*/*log")


def string_hash(string):
    return md5(string.encode()).hexdigest()

def encode(allowed_actions):
    return string_hash(",".join(allowed_actions))

def get_graph():

    slst = []
    alst = []
    allow_lst = []

    allowed_actions = {}

    action_set = {}

    sa_lst = []
    sa_taken = []
    same_count = 0
    self_taken = []

    sa_s = {}

    s2scr = {}

    spair2a = {}
    s2ns = {}

    state_count = {}
    action_count = {}

    for fh in flist:
        fh = open(fh, 'r')

        last_st = None
        last_a = None

        #print('---------------------')
        for line in fh:
            try:
                d = eval(line)
                actions = d['actions']

            except:
                actions = None


            if actions is not None:
        
                tipe = d['tip_events']


                if len(tipe) > 0:
                    tp_lst = []
                    for tp in tipe:
                        tp_lst.append(tp['TestCaseName'] + "__" + tp['CompletionKind'])
                    tp_str = '____'.join(sorted(list(set(tp_lst))))
                else:
                    tp_str = "____"


                sa = sorted(actions)
                use_tip = False
                s = string_hash(",".join(sa)) 
                if use_tip:
                    s += "____" + tp_str
                slst.append(s)


                allowed_actions[s] = sorted(actions)

                #print(s)
                #print(d['chosen_action'])

                if not s in state_count:
                    state_count[s] = 0
                state_count[s] += 1

                if not d['chosen_action'] in action_count:
                    action_count[d['chosen_action']] = 0
                action_count[d['chosen_action']] += 1
            
                if not s in s2scr:
                    s2scr[s] = []
                s2scr[s].append(d['screenshot'])

                sa_taken.append(s + "__" + d['chosen_action'])


                allow_lst.append(len(actions))

                for action in actions:
                    alst.append(action)
                    sa_lst.append(s + "__" + action)

                    action_set[action] = True

                if s == last_st:
                    same_count += 1
                    self_taken.append(last_st + "__" + last_a)

                if last_st is not None:
                    if not last_st in s2ns:
                        s2ns[last_st] = []
                    s2ns[last_st].append(s)

                    if not (last_st, s) in spair2a:
                        spair2a[(last_st, s)] = []
                    spair2a[(last_st, s)].append(last_a)

                    last_sa = last_st + "__" + last_a

                    if not last_sa in sa_s:
                        sa_s[last_sa] = []

                    sa_s[last_sa].append(s)

                last_st = s
                last_a = d['chosen_action']

    for key in spair2a:
        spair2a[key] = list(set(spair2a[key]))
    for key in s2ns:
        s2ns[key] = list(set(s2ns[key]))

    return s2ns, spair2a, allowed_actions

