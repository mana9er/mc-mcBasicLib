import csv

with open('advancement_1.18.csv', 'r', encoding='utf-8', newline='') as f:
    with open('../mcBasicLib/assets/advancement_ch.txt', 'w', encoding='utf-8') as ch_f:
        with open('../mcBasicLib/assets/advancement_en.txt', 'w', encoding='utf-8') as en_f:
            reader = csv.reader(f)
            for row in list(reader):
                en_f.write(row[1] + '\n')
                ch_f.write(row[2] + '\n')