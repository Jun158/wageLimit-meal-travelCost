import pandas as pd
import re
from datetime import datetime

def wageLimit(subslry, travelPattern, wagetype, tmpWageDic):
    if wagetype in travelPattern:
        pass
    else:
        wageAmount = 0; moreThan10K = 0; MaybelessThan10K = ""; holdamount = 0; holdamount2 = 0
        flag = False
        for char in subslry:
            if char in ["⑴", "⑵", "⑶", "⑷", "⑸", "⑹", "⑺", "⑻", "⑼", "⑽"]: char = ""
            if char in ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]: char = ""
            if char.isdigit():
                MaybelessThan10K += char
            elif char=="万":
                try:
                    moreThan10K = int(MaybelessThan10K)*10000
                    MaybelessThan10K = ""
                except Exception as e:
                    continue
            elif char=="円":
                flag = False
                if MaybelessThan10K: wageAmount = (int(moreThan10K) + int(MaybelessThan10K))    
                else: wageAmount = (int(moreThan10K))
                tmpWageDic[wagetype].append(wageAmount)
                if holdamount: tmpWageDic[wagetype].append(holdamount)
                if holdamount2: tmpWageDic[wagetype].append(holdamount2)
                wageAmount = 0
                moreThan10K = 0
                MaybelessThan10K = ""
            elif char=="～":
                if MaybelessThan10K:
                    if wagetype=="時給":
                        pass
                    elif wagetype=="年収":
                        if int(MaybelessThan10K)<10000:
                            MaybelessThan10K = int(MaybelessThan10K)*10000
                    else:
                        try:
                            if len(MaybelessThan10K)<4:
                                MaybelessThan10K = int(MaybelessThan10K)*10000
                        except ValueError:
                            tmpWageDic[wagetype].append("NULL")
                    if moreThan10K: holdamount = (int(moreThan10K) + int(MaybelessThan10K))
                    else: holdamount = MaybelessThan10K
                elif moreThan10K:
                    holdamount2 = moreThan10K
                if not re.search("～\d+", subslry):
                    tmpWageDic[wagetype].append("NULL")
                    tmpWageDic[wagetype].append("NULL")
                wageAmount = 0
                moreThan10K = 0
                MaybelessThan10K = ""    
            else:
                holdamount = 0
                holdamount2 = 0
                if flag: tmpWageDic[wagetype].pop(); flag = False
                MaybelessThan10K = ""

def travelcost(slry, travelPattern, columnsdic):
    subslry = re.split(travelPattern, slry)[1]
    if subslry=="":
        columnsdic["交通費"] = "一部支給"
    elif re.search(r"規定|別途|一部", subslry):
        columnsdic["交通費"] = "一部支給"
    elif re.search(r"全額|実費|完全", subslry):
        columnsdic["交通費"] = "全額支給"
    else:
        columnsdic["交通費"] = "一部支給"

def get_wage_main(slry):
    tmpWageDic = {'時給': [], '日給': [], '月給': [], '月収': [], '月額': [], '年収': []}
    columnsdic = {'時給下限': '', '時給上限': '', '日給下限': '', '日給上限': '', '月給下限': '', '月給上限': '', '年収下限': '', '年収上限': '', '交通費': '', '賄い有無': ''}
    travelPattern = r"交通費|交費|交"; pattern = r"(時給|日給|月給|月収|月額|年収|交通費|交費|交)"; meals = r"賄|まかない"; tildeword = r"以上"

    if re.search(travelPattern, slry): travelcost(slry, travelPattern, columnsdic)
    if re.search(meals, slry): columnsdic["賄い有無"] = "1"

    if slry.isdigit() and len(slry)<6: slry = slry+"円"
    
    hourMonthDaylyDic = {"1時間": "時給", 
                         "月収": "月給", 
                         "月額": "月給",
                         "想定月給": "例",
                         "想定月収": "例",
                         "想定月額": "例",
                         "目安": "例",
                         "日収": "日給", 
                         "日当": "日給",
                         "1稼働：": "日給",
                         "年俸制": "年収"}
    [slry := slry.replace(keyword, hourMonthDaylyDic[keyword]) for keyword in hourMonthDaylyDic.keys() if keyword in slry]

    exceptionPatternList = [r"場合.*(月給|月収|月額)\d*万\d*円",
                            r"時給\d+円×実働\d+時間＝日給\d+円",
                            r"日給\d+円×\d+日勤務＝月給\d+円",
                            r"手当\d+万\d+円",
                            r"手当\d+\.?\d*?万?円",
                            r"年収例.*就職\d*年目.*?\d*万円",
                            r"交通費.*?(月給\d*円|\d*円/月)",
                            r"月給例月給\d+円",
                            r"初勤務手当て\d*円支給",
                            r"約\d+\.?\d*?万?円?～\d+\.?\d*?万?円",
                            r"約\d+\.?\d*?万円",
                            r"月給例…\d+万\d+円～",
                            r"時給\d+円×\d+h×月\d+日",
                            r"月給例】日給\d*万\d*円×月\d*日⇒月給\d*万\d*円",
                            r"＋[一-龥ぁ-んァ-ン]*(\d+万?円|\d+万?円?～\d+万?円)＋",
                            r"残業代\d*\.?\d*?万?円",
                            r"\(.*?[一-龥ぁ-んァ-ン]*?\)",
                            r"※\d*[一-龥ぁ-んァ-ン]*当たり\d*",
                            r"褒賞金平均(\d*万?円|\d*万?円?～\d*万?円)",
                            r"祝金(\d*万?円|\d*万?円?～\d*万?円)",
                            r"年目月給\d+(\.\d+)*万円",
                            r"\d+×\d+×\d+＝\d+円",
                            r"\d+円?～\d+円×\d+\.?\d*?h×\d+日＝\d+円?～\d+円",
                            r"\d+\.?\d*?万?円?～\d+\.?\d*?万?円×\d+時間×\d+日＝\d+\.?\d*?万?円?～\d+\.?\d*?万?円", 
                            r"\d+円×\d+時間×\d+日 ＝\d+円",
                            r"上限\d*万円",
                            r"交通費.*?(月給\d*円|\d*円/月)",
                            r"\d*円×\d*\.\d*h×\d*日＝\d*円",
                            r"月給例】 月給\d*～\d*万円",
                            r"\d*円×実働\d*h×\d*日＝\d*円",
                            r"\d*円×\d*ｈ?h?×\d*日＝\d*円",
                            r"\d*円×\d*\.\d*時間×\d*日＝\d*円",
                            r"\d*円×\d*時間\d*分×\d*日＝\d*円",
                            r"\d*円×1日\d*h×月\d*日＝\d*円",
                            r"\d*円×週\d*\.\d*時間×\d*週間＝\d*円",
                            r"\d*円×\d*ｈ×\d*日＝\d*円",
                            r"\d*円×\d*:\d*×\d*日＝\d*円",
                            r"\d*円×実働\d*時間×\d*日＝\d+万?\d*?円",
                            r"\d*円×\d*h×\d*日＝\d*円",
                            r"\d*円×実働×\d*日＝\d*円",
                            r"\d+円×\d+時間\d+分 ×\d+日＝\d+円",
                            r"時給\d+円×\d+時間×月\d+日＝\d+円",
                            r"\d+\.?\d*?万?円?～\d+\.?\d*?万?円×\d*\.?\d*?ｈ×\d+日＝\d+\.?\d*?万?円?～\d+\.?\d*?万?円",
                            r"\d+円×\d+\.?\d*?時間\d*?分?×\d+日＝\d+万?\d*?円",
                            r"\d+円×\d+h×\d+日＝\d+万?\d*?円",
                            r"時給換算時給\d+円",
                            r"×\d+%=約?\d+万?\d*?円",
                            r"1年後に?\d+万?\d*?円",
                            r"1か月後に?\d+万?\d*?円",
                            r"支度金?\d+万?\d*?円?～?\d+万?\d*?円",
                            r"\d+円×\d+時間\d+分",
                            r"時給\d+円×",
                            r"固定.*?\d+円.*?超過分別途支給",
                            r"例.*?\d+\.?\d*?万?円?～\d+\.?\d*?万?円",
                            r"例.*?\d*\.?\d*?万?円",
                            r"交通費支給有.*?月給\d*\.?\d*?万?円",
                            r"年収（残業含まず）：\d+万円～",
                            r"\d+円×\d+\.?\d+時間×月\d+日＝\d+円",
                            r"＝\d+円",
                            r"\d+( |　| )円",
                            r"時給( |　| )\d+"]
    for exceptionPattern in exceptionPatternList:
        match = re.findall(exceptionPattern, slry)
        [slry := slry.replace(i, "") for i in match if match]
    
    if len(slry)==6 and slry[-1]!="円": slry = slry+"円"
    elif len(slry)==7 and slry[-1]=="～": slry = slry[:-1] + "円"

    exceptionPattern = r"（.*?）"
    match = re.findall(exceptionPattern, slry)
    if match:
        for i in match:
            submatch = re.sub(r"\d+", "~_~_", i)
            slry = slry.replace(i, submatch)

    exceptionPattern = r"\(.*\d+万?\d*円.*\)"
    match = re.findall(exceptionPattern, slry)
    [slry := slry.replace(i, "~_~_") for i in match if match]

    exceptionPattern = r"(時給\d+)～[^\d+]"
    match = re.findall(exceptionPattern, slry)
    if match: slry = slry.replace(match[0], match[0]+"円")

    exceptionPatternList = [r"(月給\d+万)～[^\d+]",
                            r"\d+円～\d{4,}(?!円)"]
    for exceptionPattern in exceptionPatternList:
        match = re.findall(exceptionPattern, slry)
        [slry := slry.replace(i, i+"円") for i in match if match]

    exceptionPattern = r"((時給\d+円以上)時給\d+～\d+円)"
    match = re.findall(exceptionPattern, slry)
    if match: slry = slry.replace(match[0][1], "")

    exceptionPattern = r"\d{5,}?円?～\d{5,}?円/月|\d{1,}?万円?～\d{1,}?万円/月|\d{5,}?円/月|\d{1,}?万円/月"
    match = re.findall(exceptionPattern, slry)
    if match: slry = [slry.replace(i, "月給"+i) for i in match][0]

    exceptionPattern = r"(平均給与例)(時給|日給|日収|月給|月収|月額|年収)(\d*\.?\d?万?円)"
    match = re.findall(exceptionPattern, slry)
    if match: match = "".join(match[0][0:]); slry = slry.replace(match, "")
    
    exceptionPattern = r'月給\d+\.\d+万円～\d+\.\d+万円'
    match = re.search(exceptionPattern, slry)
    if match:
        new_slry = re.sub(r'月給\d+\.\d+万円', '月給'+str(int(float(match.group().split('～')[0].replace('月給', '').replace('万円', '')) * 10000)), match.group())
        new_slry = re.sub(r"\d+\.\d+万円", str(int(float(match.group().split("～")[1].replace("万円", "")) * 10000)) + "円", new_slry)
        new_slry = re.sub(r'(\d+)円～(\d+)円', r'\1～\2円', new_slry)
        slry = slry.replace(match.group(), new_slry)

    exceptionPattern = r'月給\d+\.\d+～\d+万円'
    match = re.search(exceptionPattern, slry)
    if match:
        new_slry = re.sub(r'\d+\.\d+', str(int(float(match.group().split('～')[0].replace('月給', '')) * 10000)), match.group())
        new_slry = re.sub(r'\d+万円', str(int(float(match.group().split('～')[1].replace('万円', '')) * 10000)) + '円', new_slry)
        slry = slry.replace(match.group(), new_slry)

    exceptionPattern = r"月給\d+～\d+\.?\d*万円"
    match = re.search(exceptionPattern, slry)
    if match:
        new_slry = re.sub(r"\d+\.?\d*", str(int(float(match.group().split("～")[0].replace("月給", "")) * 10000)), match.group())
        new_slry = re.sub(r"\d+万円", str(int(float(match.group().split("～")[1].replace("万円", "")) * 10000)) + "円", new_slry)
        new_slry = re.sub(r"(\d+)円～(\d+)円", r"\1～\2円", new_slry)
        slry = slry.replace(match.group(), new_slry)

    exceptionPattern = r'月給\d+\.\d+万円～'
    match = re.search(exceptionPattern, slry)
    if match:
        new_slry = re.sub(r'月給\d+\.\d+万', match.group().split('.')[0] + str(int(match.group().split('.')[1].replace('万円', '').replace('～', '')) * 1000), match.group())
        slry = slry.replace(match.group(), new_slry)

    salary_index = df.columns.get_loc('salary')
    if False in ([i in df.columns for i in columnsdic.keys()]):
        columnlist = []
        for i in columnsdic:
            columnlist.insert(0, i)
        for column in columnlist:
            df.insert(salary_index + 1, column, "")

    match1 = re.findall(pattern, slry)
    if match1:
        checkSlry = slry.split(match1[0])
        if "円" in checkSlry[0]:
            checkSlry[0] = "時給" + checkSlry[0]
            slry = checkSlry[0] + match1[0] + "".join(checkSlry[1:])
    elif not match1:
        if "円" in slry:
            slry = "時給" + slry
            
    match1 = re.findall(pattern, slry)
    if match1:
        match2 = match1.copy()
        match2.pop(0)
        match2 += ["|~|~"]
    else:
        match1 = ['時給']
        match2 = ['|~|~']

    for wageTypeBegin, wageTypeEnd in zip(match1, match2):
        slry = wageTypeBegin.join(slry.split(wageTypeBegin)[1:])
        if wageTypeEnd: subslry = slry.split(wageTypeEnd)[0]
        else: subslry = slry
        if re.search(tildeword, subslry): subslry = subslry.replace(tildeword, "～")
        try:
            wageLimit(subslry, travelPattern, wageTypeBegin, tmpWageDic)
        except Exception as e:
            print(count[0])
            print("An error occurred for slry:", slry)
            print("An error occurred for subslry:", subslry)
            print("An error occurred for match1:", match1)
            print(f"Error message: {e} at line {e.__traceback__.tb_lineno}")

    for i in range(len(tmpWageDic)):
        wagetype = list(tmpWageDic.keys())[i]
        concatenated_value = tmpWageDic['月給'] + tmpWageDic['月収'] + tmpWageDic['月額']
        tmpWageDic['月給'] = concatenated_value
        if wagetype=="月収" or wagetype=="月額": wagetype="月給"
        value = tmpWageDic[wagetype]
        while "" in value:
            value.remove("")
        value = [x for x in value if not (isinstance(x, int) and x <= 895 and x >= 0)]
        if value:
            value = [int(item) if isinstance(item, str) and item != "NULL" else item for item in value]
            if "NULL" in value:
                value = [item for item in value if item != 'NULL']
                if value:
                    lowerkeyword = wagetype + "下限"
                    columnsdic[lowerkeyword] = min(value)
            elif min(value) == max(value):
                lowerkeyword = wagetype + "下限"
                columnsdic[lowerkeyword] = min(value)
            else:
                lowerkeyword = wagetype + "下限"
                columnsdic[lowerkeyword] = min(value)
                upperkeyword = wagetype + "上限"
                columnsdic[upperkeyword] = max(value)    
    # insert values
    for i, key, value in zip(range(len(columnsdic)), columnsdic.keys(), columnsdic.values()):
        df.at[count[0],key] = value
    count[0]+=1


# main
tgt = "TW_2024-01-15.tsv"
file_extention = tgt[-3:]
if file_extention == "csv": delimiter=','
elif file_extention == "tsv": delimiter='\t'
else: delimiter=''
df=pd.read_csv(tgt, delimiter=delimiter)
df['salary'] = df['salary'].astype("string").str.replace("、", "").str.replace(",", "").str.replace("〜", "～").str.replace("：", ":").str.replace("~", "～").str.replace(" ", "").str.replace("，", "")
count = [0]
df['salary'].apply(get_wage_main)

df.to_csv("output.csv")