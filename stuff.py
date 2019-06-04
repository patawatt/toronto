import pandas as pd
from time import sleep

file = "repertoire.xlsx"
xl = pd.ExcelFile(file)

df1 = pd.read_excel(xl)

memorize = df1.loc[df1['goal']=='memorize']
practice = df1.loc[df1['goal']=='practice']
learn = df1.loc[df1['goal']=='learn']

mem_sort = memorize.sort_values(by=['playcount']).reset_index(drop=True)
prac_sort = practice.sort_values(by=['playcount']).reset_index(drop=True)
learn_sort = learn.sort_values(by=['playcount']).reset_index(drop=True)

# mem_scramble = memorize.sample(frac = 1).reset_index(drop=True)
# prac_scramble = practice.sample(frac = 1).reset_index(drop=True)
# learn_scramble = learn.sample(frac = 1).reset_index(drop=True)
# total = pd.concat([mem_scramble, prac_scramble, learn_scramble]).reset_index(drop=True)

while (mem_time + mem_sort['length'][mem_count+1]) < mem_max:
    mem_time += mem_sort['length'][mem_count]
    mem_count += 1

mem_today = mem_sort[:mem_count]

while (prac_time + prac_sort['length'][prac_count+1]) < prac_max:
    prac_time += prac_sort['length'][prac_count]
    prac_count += 1

prac_today = prac_sort[:prac_count]

while (learn_time + learn_sort['length'][learn_count+1]) < learn_max:
    learn_time += learn_sort['length'][learn_count]
    learn_count += 1

learn_today = learn_sort[:learn_count]

today = pd.concat([mem_today, prac_today, learn_today]).reset_index(drop=True)
today['playcount'] += 1

final = pd.concat([today, mem_sort[mem_count+1:],prac_sort[prac_count+1:],learn_sort[learn_count+1:]]).reset_index(drop=True)

writer = pd.ExcelWriter('repertoire.xlsx')
final.to_excel(writer,'Sheet1')
writer.save()







