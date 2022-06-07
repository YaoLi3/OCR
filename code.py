#!/usr/bin/env python3

from pickle import TRUE
import sys
import json
import numpy as np
import pandas as pd
import os
import re
from itertools import product
from collections import namedtuple


#####################################################################
# functions
##############################################################################
def get_value2(table_data:pd.DataFrame, key1, value1, key2):
    return table_data[table_data[key1]==value1][key2].values[0]


def get_value3(text, key2):
    return table_data[table_data['text']==text][str(key2)].values[0]


def is_value(s,pattern):
    return bool(re.search(pattern, s))


def get_value(s,pattern,x,y,r:list=(-3,3)):
    value = 'NOT FOUND'
    if ':' in s:
        string = s.split(':',1)[-1]
        if string != '':
            if is_value(string, pattern):
                value = re.match(pattern, text).group()
        else:
            for r,c in product(range(r[0],r[1]), range(r[0],r[1])):  # TODO: range
                value1 = table_data[(table_data['row']==y+r)&(table_data['col']==x+c)]
                if len(value1) > 0:
                    text = value1['text'].values[0]
                    if is_value(text):
                        value = re.match(pattern, text).group()
    else:
        # when : is not in key-value?
        pass
    return value
###########################################################
# 1. SYSTEM ID---------------------
def get_id(s):
    id_pattern = r'QD[A-Z]+[0-9]+'
    item_id = re.match(id_pattern,s)
    #item_id = item_id.group()
    return item_id


# 2. TIME----------------------------
def time_test(s):
    #time_pattern = r'[0-9\-\/\.\:]+'
    time_pattern = r'[0-9]{4}[\-\/\.\:][0-9]{1,2}[\-\/\.\:][0-9]{1,2}'
    s = s.split(' ',1)[0]
    try:
        return re.search(time_pattern, s).group()
    except AttributeError:
        print(s)
        return 'NOT FOUND'


def is_time(s):
    #time_pattern = r'[0-9]{4}[\-\/\.\:][0-9\-\/\.\:]+'
    time_pattern = r'[0-9]{4}[\-\/\.\:][0-9]{1,2}[\-\/\.\:][0-9]{1,2}'
    b = bool(re.search(time_pattern, s))
    return b


def get_time(s,x,y):
    """dataframe version"""
    time = 'NOT FOUND'
    if ':' in s:
        time_string = s.split(':',1)[-1]
        if time_string != '':
            time = time_test(time_string)
        else:
            for r,c in product(range(-4,4), range(-5,7)):  # TODO: range
                value = table_data[(table_data['row']==y+r)&(table_data['col']==x+c)]
                if len(value) > 0:
                    text = value['text'].values[0]
                    if is_time(text):
                        time = time_test(text)
    return time


# 3. DIAGNOSIS-----------------------------------
def get_diagnosis(s,x,y):
    dig = 'NOT FOUND'
    if ':' in s:
        string = s.split(':',1)[-1]
        if string != '':           
            dig = string
        else:
            for r,c in product(range(-5,5), range(-5,5)):  # TODO: range
                value = table_data[(table_data['row']==y+r)&(table_data['col']==x+c)]
                if len(value) > 0:
                    text = value['text'].values[0]
                    if '孕' in text or '妊娠' in text:
                        dig = text                   
    return dig


# 4. AGE----------------------------------------------------------------------
def is_age(s):
    if '岁' in s:
        s = s.replace('岁','')
    elif '日' in s:
        s = s.replace('日','')
    age_pattern = r'^[0-9]{1,2}$'  # TODO: 1. raw string 2. 有没有没有”岁“的
    b = bool(re.search(age_pattern, s))
    return b


def is_dob(s):
    dob_pattern = r'[0-9]{4}[\/\-][0-9]{1,2}[\/\-][0-9]{1,2}'
    b = bool(re.search(dob_pattern, s))
    return b


def get_age(s,x,y):
    age = 'NOT FOUND'
    age_pattern = r'[0-9]{1,2}'  # TODO: raw string
    dob_pattern = r'[0-9]{4}[\/\-][0-9]{1,2}[\/\-][0-9]{1,2}'
    if ':' in s:
        string = s.split(':',1)[-1]
        if string != '':
            # 年龄不需要判断
            age = string
        else:
            for r,c in product(range(-2,3), range(-6,10)):  # TODO: range
                value = table_data[(table_data['row']==y+r)&(table_data['col']==x+c)]
                if len(value) > 0:
                    text = value['text'].values[0]
                    if is_age(text):
                        age = re.match(age_pattern, text).group()
                        age = age+'岁'
                    elif is_dob(text):
                        try:
                            age = re.match(dob_pattern, text).group()
                        except AttributeError:
                            pass
    return age


# 5.GENDER----------------------------------------------------------------------
def is_gender(s):
    db = ['女', '男']  # TODO: 有没有识别错误的
    if s in db:
        return True
    else:
        return False


def get_gender(s,x,y):
    gender = 'NOT FOUND'
    if ':' in s:
        string = s.split(':',1)[-1]
        if string != '':

            #if is_gender(string):
            gender = string
        else:
            for r,c in product(range(-5,5), range(-5,5)):  # TODO: range
                value = table_data[(table_data['row']==y+r)&(table_data['col']==x+c)]
                if len(value) > 0:
                    text = value['text'].values[0]
                    if is_gender(text):
                        gender = text

    return gender


# 6.NAME----------------------------------------------------------------------
def is_name(s):
    name_pattern = u"^[\u4e00-\u9fa5]{2,3}$"  # TODO: 汉字。。少数民族？。。罕见字显示异常
    b = bool(re.search(name_pattern, s))
    return b


def get_name(s,x,y):
    name_pattern = u"^[\u4e00-\u9fa5]{2,3}$"
    name = 'NOT FOUND'
    if ':' in s:
        string = s.split(':',1)[-1]
        if string != '':
            name = string
            #if is_name(string):
            #    name = re.match(name_pattern, string).group()
        else:
            for r,c in product(range(-3,4), range(-5,7)):  # TODO: range
                value = table_data[(table_data['row']==y+r)&(table_data['col']==x+c)]
                if len(value) > 0:
                    text = value['text'].values[0]
                    if is_name(text):
                        name = re.match(name_pattern, text).group()
                    
    return name


# 7.科室----------------------------------------------------------------------
def is_dep(s):
    if '门诊' in s or '科别' in s or '科室' in s:
        return True
    else:
        return False


def get_dep(s,x,y):
    dep_pattern = r"[\u4e00-\u9fa5]+门诊"
    dep = 'NOT FOUND'
    if ':' in s:
        string = s.split(':',1)[-1]
        if string != '':
            if '门诊' in string and len(string) > 2:
                dep = re.search(dep_pattern, string).group()
            else:
                dep = string
            #if '产科' in string:
            #    dep = string
            #else:
            #    try:
            #        dep = re.match(dep_pattern, string).group()
            #    except AttributeError:
            #        print(s)
            #        pass
        else:
            for r,c in product(range(-5,5), range(-5,5)):  # TODO: range
                value = table_data[(table_data['row']==y+r)&(table_data['col']==x+c)]
                if len(value) > 0:
                    text = value['text'].values[0]
                    if '产科' in text:
                        dep = text
                    else:
                        try:
                            dep = re.match(dep_pattern, text).group()
                        except AttributeError:
                            pass
    return dep


# 8.sample----------------------------------------------------------------------
def get_sample(s,x,y):
    sam = 'NOT FOUND'
    sam_pattern = r'[\u4e00-\u9fa5]+'
    if ':' in s:
        string = s.split(':',1)[-1]
        if string != '':
            sam = string
        else:
            for r,c in product(range(-1,2), range(-3,4)):  # TODO: range
                value = table_data[(table_data['row']==y+r)&(table_data['col']==x+c)]
                if len(value) > 0:
                    text = value['text'].values[0]
                    if '血' in text:
                        sam = re.search(sam_pattern, text).group()
    return sam


# 10. main table section----------------------------------------------------------------------
def find_section(table_data, row_inter, col_inter):
    print(table_data.head())
    top_indice = []; low_indice = []
    table_data = table_data.reset_index(drop=True)
    print(table_data.head())
    for t in table_data['text']:
        if t in ['参考区间', '参考值', '单位']:
            df = table_data[table_data['text']==t].sort_values('y', ascending=False)
            top_indice.append(df.index[0])
        if "备注" in t or '检验者' in t or '检验医' in t:
            df = table_data[table_data['text']==t].sort_values('y')
            low_indice.append(df.index[0])
    top = max(top_indice)+1  #TODO:
    low = min(low_indice)
    sub_table_data = table_data.iloc[top:low]
    sub_table_data = sub_table_data.reset_index()
    
    # update row & col id
    row = 0; col = 0
    rcor = 10; ccor = 10
    sub_table_data = sub_table_data.sort_values('x')
    sub_table_data = sub_table_data.reset_index(drop=True)
    print(sub_table_data)
    for i in sub_table_data.index[:-1]:
        start_y = sub_table_data['y'].iloc[0]
        x_change = sub_table_data['x'].iloc[i+1] - sub_table_data['x'].iloc[i]
        y_change = sub_table_data['y'].iloc[i+1] - start_y 
        if x_change > row_inter*rcor and y_change < col_inter*ccor:  # i is the last column, i+1 changes to next column
            sub_table_data['col'].iloc[i] = col
            col += 1
            sub_table_data['col'].iloc[i+1] = col
    sub_table_data = sub_table_data.sort_values(by=['col','y'])
    for col in set(sub_table_data['col']):
        print(sub_table_data[sub_table_data['col']==col])

    '''
    data = {}
    v1 = sorted(test[1], key=lambda x: x.y)
    v3 = sorted(test[3], key=lambda x: x.y)
    for i in v1:
        for j in v3:
            if abs(i.y-j.y) <= row_inter*range_cor:
                #print(i.text, j.text)
                data[i.text] = j.text
            #if abs(i.row-j.row) == 1:
                #print(i.text, j.text)
    
    for t,v in l3.items():
        if t in sub_name:
            return v
    '''


######################################################
# loading raw json
def robust(item,list,limit_b,limit_e):
    mean = np.mean(list)
    if item > mean-limit_e and item < mean+limit_b:
        result = True
    else:
        result = False
    return result


def loading_json_content(imagejson_filename):
    test = json.load(open(imagejson_filename,encoding='UTF-8'))
    TextDetections = test['TextDetections'].copy()
    pre = pd.DataFrame(columns = ['text','x','y','col','row'])
    h_list = []
    w_list = []
    for i in range(len(TextDetections)):
        text = TextDetections[i]['DetectedText']
        x = TextDetections[i]['ItemPolygon']['X']
        y = TextDetections[i]['ItemPolygon']['Y']
        h = TextDetections[i]['ItemPolygon']['Height']
        h_list.append(h)
        w = TextDetections[i]['ItemPolygon']['Width']
        w_list.append(w)
        pre = pre.append({'text':text,'x':x,'y':y,'col':1,'row':1},ignore_index=True)
    h_list.sort()
    w_list.sort()
    row_limit = h_list[0]/2
    col_limit = w_list[0]/2
    return pre, row_limit, col_limit


# assign col id by merging close item in one col
def get_column_ids(pre, column_SD):
    pre1 = pre[['text','x','y','col']].copy()
    pre1 =pre1.sort_values('x')
    tre = 0
    col = 0
    for i in range(len(pre1)):
        if i != 0:
            i = tre
            col += 1
        pre1['col'].iloc[i] = col
        if i == len(pre1)-1:
                break
        #group = pre.iloc[[i]]
        xi = pre1.iloc[i]['x']
        jug = list([xi])
        for j in range(i+1,len(pre1)):
            xj = pre1.iloc[j]['x']
            tre = j
            if robust(xj,jug,column_SD,column_SD):
                pre1['col'].iloc[j] = col
                jug.append(xj)
            else:
                break
    return pre1


# assign row id by merging close item in one row
def get_row_ids(pre, row_SD):
    pre2 = pre[['text','x','y','row']].copy()
    pre2 = pre2.sort_values('y')
    tre = 0
    row = 0
    for i in range(len(pre2)):
        if i != 0:
            i = tre
            row += 1
        pre2['row'].iloc[i] = row
        if i == len(pre2)-1:
                break
        yi = pre2.iloc[i]['y']
        jug = list([yi])
        for j in range(i+1,len(pre2)):
            yj = pre2.iloc[j]['y']
            tre = j
            if robust(yj,jug,row_SD,row_SD):
                pre2['row'].iloc[j] = row
                jug.append(yj)
            else:
                break
    return pre2


# merge row and col info
def merge_row_col(pre1,pre2):
    pre0 =pd.merge(pre1,pre2)
    pre0 = pre0.sort_values(by=['row','col'])
    pre0 = pre0[['row','col','x','y','text']].copy()
    pre0 = pre0.sort_values(by=['row','col'])
    pre0['text'] = pre0['text'].astype('str_')
    return pre0


######################################################
def load_header(headerjson_filename):
    keys = json.load(open(headerjson_filename,encoding='UTF-8'))
    return keys


######################################################
def get_target_data(headers,table_data, prefix, proj):
    table_data = table_data.reset_index()
    kvalue = pd.DataFrame(columns=['k','values'])


    for key_pair in headers:
    # loop starts
        key_name = key_pair[0]; sub_keys = key_pair[1]
        targets = table_data[table_data['text'].str.contains(sub_keys,regex=True)]['text']
        value = 'NOT FOUND'

        # when there's multiple entries meet the condition
        if len(targets) > 0:  
            target = targets.values[0]
            y = get_value2(table_data, 'text', target, 'row')
            x = get_value2(table_data, 'text', target, 'col')
            if key_name == '采集时间':  #if '采集时间' in target:  
                value = get_time(target,x,y)
            elif '年龄' == key_name:  #elif '生日' in target or '年龄' in target:
                value = get_age(target,x,y)
            elif key_name == '性别': 
                for t in targets:
                    y = get_value2(table_data, 'text', t, 'row')
                    x = get_value2(table_data, 'text', t, 'col')
                    value = get_gender(t,x,y)
            elif key_name == '科室':
                for t in targets:
                    if is_dep(t):
                        y = get_value2(table_data, 'text', t, 'row')
                        x = get_value2(table_data, 'text', t, 'col')
                        value = get_dep(t,x,y)
            elif key_name == '姓名':
                value = get_name(target,x,y)
                #for t in targets:
                #    y = get_value2(table_data, 'text', t, 'row')
                #    x = get_value2(table_data, 'text', t, 'col')
                #    value = get_name(t, x, y)
                    #if value == 'NOT FOUND':
                    #    try:
                    #        value = re.search(u"^[\u4e00-\u9fa5]{2,3}$", prefix).group()
                    #    except AttributeError:
                    #        value = 'NOT FOUND'
            elif key_name == '临床诊断':
                value = get_diagnosis(target, x, y)
            elif key_name == '样本类型':
                value = get_sample(target, x, y)
            else:
                split = target.find(':')
                if split != -1:
                    value = target[split+1:]
                else:
                    value = table_data[(table_data['row']==y)&(table_data['col']>x)]
                    value.sort_values('col')
                    try:
                        value = value['text'].iloc[0]
                    except IndexError:
                        value = 'NOT FOUND'

        # fixed values
        if key_name == '全人群系统项目编号':
            value = prefix
        elif key_name == '检验项目':
            value = proj

        kvalue = kvalue.append({'k':key_name,'values':value},ignore_index=True)
    # loop ends
    return kvalue


if __name__ == '__main__':
    imagejson_filename = sys.argv[1]
    headerjson_filename = sys.argv[2]
    prefix = sys.argv[3]
    proj=sys.argv[4]
    name = get_id(os.path.basename(imagejson_filename))
    if name is None:
        name = prefix
    else:
        name=name.group()


    # loading image json
    image_data, row_inter, col_inter = loading_json_content(imagejson_filename)
    # construct image json to a table data
    col_data = get_column_ids(image_data,col_inter)
    row_data = get_row_ids(image_data,row_inter)
    table_data = merge_row_col(col_data,row_data)
    find_section(table_data, row_inter, col_inter)
    '''
    table_data.to_csv(f"{prefix}.table.csv",encoding='utf_8_sig',header=True,index=False)


    ###########
    # find target key-values
    headers = load_header(headerjson_filename)
    get_target_data(headers,table_data, name, proj)
    kvalue = get_target_data(headers,table_data, name, proj)
    ###########
    # save csv
    kvalue = kvalue.T
    kvalue.to_csv(f"{prefix}.csv",encoding='utf_8_sig',header=False)
    '''

