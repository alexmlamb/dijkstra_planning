import sys

from hashlib import md5

import glob
flist = glob.glob("../data/*/*log")


def string_hash(string):
    return md5(string.encode()).hexdigest()

slst = []
alst = []
allow_lst = []

action_set = {}

sa_lst = []
sa_taken = []
same_count = 0
self_taken = []

sa_s = {}

s2scr = {}

for fh in flist:
    fh = open(fh, 'r')

    last_st = None
    last_a = None

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

            #print('allowed actions', sorted(actions))

            sa = sorted(actions)
            use_tip = False
            s = string_hash(",".join(sa)) 
            if use_tip:
                s += "____" + tp_str
            slst.append(s)

            if not s in s2scr:
                s2scr[s] = []
            s2scr[s].append(d['screenshot'])

            sa_taken.append(s + "__" + d['chosen_action'])


            allow_lst.append(len(actions))

            chosen_action = d['chosen_action']
            if not chosen_action in action_set:
                action_set[chosen_action] = 0
            action_set[chosen_action] += 1

            for action in actions:
                alst.append(action)
                sa_lst.append(s + "__" + action)


            if s == last_st:
                same_count += 1
                self_taken.append(last_st + "__" + last_a)

            if last_st is not None:
                last_sa = last_st + "__" + last_a

                if not last_sa in sa_s:
                    sa_s[last_sa] = []

                sa_s[last_sa].append(s)

            last_st = s
            last_a = d['chosen_action']

print('number of transitions', len(slst))
print('number unique states', len(set(slst)))

print('number unique actions', len(set(alst)))

print('number unique state-action pairs', len(set(sa_lst)))

print('number state-action pairs taken', len(sa_taken))
print('number unique state-action pairs taken', len(set(sa_taken)))

print('average allowed actions', sum(allow_lst) * 1.0 / len(allow_lst))

print("number of self-transitions", len(self_taken))
print('number of unique self-transitions', len(set(self_taken)))

print('number of overall actions', sorted(action_set.items(), key = lambda a: a[1]))

raise Exception('done')

ndt_count = 0
for sa in sa_s:
    lst = sa_s[sa]
    if True or len(lst) > 1:
        if True or len(set(lst)) > 1:
            #print('sa', sa)
            print(sa, sorted(lst))
            ndt_count += 1

#print('num states non-deterministic', ndt_count)

lens = []
for s in s2scr:
    lens.append((s, len(s2scr[s])))

print(sorted(lens, key=lambda a: a[1]))

