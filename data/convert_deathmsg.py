import csv

with open('deathmsg_1.21.2_rep.csv', 'r', encoding='utf-8', newline='') as f:
    with open('../mcBasicLib/assets/deathmsg_zh-cn.txt', 'w', encoding='utf-8') as ch_f:
        with open('../mcBasicLib/assets/deathmsg_en.txt', 'w', encoding='utf-8') as en_f:
            reader = csv.reader(f)
            for row in list(reader):
                ch_f.write(row[1] + '\n')
                en_f.write(row[2] + '\n')