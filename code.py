#!/usr/bin/env python3

import sys
import json
import numpy as np
import pandas as pd
import os
import re
from itertools import product


# class Entry:
#     def __init__(self, row, col, x, y, text):
#         self.row = row
#         self.col = col
#         self.x = x
#         self.y = y
#         self.text = text

#     @property
#     def x(self):
#         return self.x

#     @property
#     def y(self):
#         return self.y

#     @property
#     def row(self):
#         return self.row

#     @property
#     def col(self):
#         return self.col

#     @property
#     def text(self):
#         return self.text


# class Sheet:
#     def __init__(self, qid) -> None:
#         self.line_data = None
#         self.key_value = None

#         self.id = qid  # QDxxxxx

#         # single pages or multi
#         self.single = True

#         self.table = None  # grid
#         # or nested dictionary


#         # header
#         # body
#         self.body_coor = [topx,topy,lowx,lowy]
#         # footer
    
#     def save_table(self):
#         self.key_value.to_csv(f'{self.id}.csv', index=False)

#     def set_if_single_page(self, t):
#         self.single = t

#     #def get_entry(self, row, col):
#     #    """when table is an array"""
#     #    return self.table[row, col]

#     def get_entry(self, row, col):
#         """when table is a DataFrame"""
#         try:
#             return self.table[self.table['row']==row and self.table['col']==col].values[0]
#         except ValueError:
#             print('need to update this method')





def if_multi_pages(d):
    texts = list(d.keys())
    if texts.count('姓名') > 1 or texts.count('性别') > 1:
        return True 




#####################################################################
# functions
##############################################################################
def time_test(s):
    time_pattern = r'[0-9\-\/\.\:]+'
    return re.match(time_pattern, s).group()
    # time = re.match(time_pattern, s)
    # if time is not None:
    #     return time.group()
    # else:
    #     return 'NOT FOUND'
    # b = ''
    # for i in s:
    #  if i.isdigit() or i in ['/','-','.',':',' ']:
    #      b = b + i
    #  if not (i.isdigit() or i in ['/','-','.',':',' ']):
    #      break
    # return b


def is_time(s):
    #time_pattern = r'[0-9]{4}[\-\/\.][0-9]{1,2}'
    time_pattern = r'[0-9\-\/\.\:]+'
    b = bool(re.search(time_pattern, s))
    return b


# def get_time(e):
#     time = 'NOT FOUND'
#     if ':' in e.text:
#         time_string = e.text.split(':')
#         # when time_value is in the same entry with the time_key
#         if len(time_string) > 1:
#             time = time_test(time_string)
#            # return time
#         else:
#         # if time_value is not in the same entry as the time_key, find if it's in the next row (same/close column)
#             # for i in range(3):
#             #     for j in range(3):
#             #         next_entry = Sheet.get_entry(e.row+i, e.col+j)
#             #         if next_entry is not None:
#             #             if is_time(next_entry.text):
#             #                 time = time_test(next_entry.text)
#             #                 return time
#             #         else:
#             #             continue
#             for r,c in product(range(3), range(3)):
#                 next_entry = Sheet.get_entry(e.row+r, e.col+c)
#                 if next_entry is not None and is_time(next_entry.text):
#                     time = time_test(next_entry.text)
#                     break
#     return time


def get_time(s):
    time = 'NOT FOUND'
    if ':' in s:
        time_string = s.split(':',1)[-1]
        # when time_value is in the same entry with the time_key
        #if len(time_string) > 1:
        if time_string != '':
            print(is_time(time_string))
            time = time_test(time_string)
            print(time)
        else:
            for r,c in product(range(3), range(3)):
                print(r,c)
    return time


def get_xitongid(sheet):
    return sheet.id

def get_diagnosis():
    pass


def get_id(s):
    id_pattern = r'QD[A-Z]+[0-9]+'
    item_id = re.match(id_pattern,s)
    item_id = item_id.group()
    return item_id


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
                #group = group.append(pre.iloc[[j]])
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
        key_name = key_pair[0]
        i = key_pair[1]
        a = table_data[table_data['text'].str.contains(i,regex=True)]['text']
        if len(a) != 0:
            a = table_data[table_data['text'].str.contains(i,regex=True)]['text'].values[0]   
            if '时间' in a:
                print(get_time(a))
        else:
            if key_name == '全人群系统项目编号':
                kvalue = kvalue.append({'k': key_name, 'values': prefix}, ignore_index=True)
            elif key_name == '检验项目':
                kvalue = kvalue.append({'k': key_name, 'values': proj}, ignore_index=True)
            else:
                kvalue = kvalue.append({'k':key_name,'values':'NOT FOUND'},ignore_index=True)
            continue

    #     split = a.find(':')
    #     if split != -1:
    #         value = a[split+1:]
    #         if '时间' in a:
    #             value = time_test(value)
    #         elif '检验项目' in a:
    #             value = '血糖'
    #         kvalue = kvalue.append({'k': key_name, 'values': value}, ignore_index=True)
    #     else:
    #         y = table_data[table_data['text']==a]['row'].values[0]
    #         x = table_data[table_data['text']==a]['col'].values[0]
    #         value = table_data[(table_data['row']==y)&(table_data['col']>x)]
    #         print(key_name)
    #         print(value)
    #         value.sort_values('col')
    #         try:
    #             value = value['text'].iloc[0]
    #         except IndexError:
    #             kvalue = kvalue.append({'k':key_name,'values':'NOT FOUND'},ignore_index=True)
    #             continue
    #             #y1 = y+1
    #             #value = table_data[table_data['row']==y1]
    #             #print(value)
    #         kvalue = kvalue.append({'k':key_name,'values':value},ignore_index=True)
    # return kvalue


def find_section(ts):
    topx = 0; topy = 0; lowx = 0; lowy = 0
    sub_topxs = []; sub_topys = []; sub_lowxs = []; sub_lowys = []
    for t in ts:
        if t.text in ['参考区间', '参考值', '单位']:
            sub_topxs.append(t.x)
            sub_topys.append(t.y)
            topx = t.x+1; topy = t.y+1
        if "备注" in t.text or '检验者' in  t.text or '检验医' in t.text:
            sub_lowxs.append(t.x)
            sub_lowys.append(t.y)
            lowx = t.x-1; lowy = t.y-1
    #topx = sorted(sub_topxs, reverse=True)[0]
    #topy = sorted(sub_topys, reverse=True)[0]
    #lowx = sorted(sub_lowxs)[0]
    #lowy = sorted(sub_lowys)[0]
    return topx,topy,lowx,lowy


def sort_section_col(ts, topy, lowy): # sort by x value
    sub_ts = []
    for t in ts:
        if t.y < lowy and t.y > topy and not re.search(r"备注", t.text):
            #if not re.search(r"备注", t.text):
            sub_ts.append(t)
    sss = sorted(sub_ts, key=lambda x:x.x)
    return sss


def detect_col(sss, rcor=7, ccor=10):
    test = {}
    n = 1
    test[n] = []
    for i in range(1, len(sss)):
        start_y = sss[0].y
        ct = sss[i]; lt = sss[i-1]
        #print(lt.text, lt.row, lt.y)
        test[n].append(lt)
        x_change = ct.x - lt.x
        y_change = ct.y - start_y
        if x_change > row_inter*rcor and y_change < col_inter*ccor:
            #print('----------')
            n += 1
            test[n] = []
    return test


def match_row(test, range_cor=2):
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
    return data


def get_value(l3, sub_name):
    for t,v in l3.items():
        if t in sub_name:
            return v
        


if __name__ == '__main__':
    imagejson_filename = sys.argv[1]
    name = get_id(os.path.basename(imagejson_filename))
    headerjson_filename = sys.argv[2]
    prefix = sys.argv[3]
    # proj=sys.argv[4]
    proj='血糖'

    # loading image json
    image_data, row_inter, col_inter = loading_json_content(imagejson_filename)
    print(f'min row {row_inter}, min col {col_inter}')
    # construct image json to a table data
    col_data = get_column_ids(image_data,col_inter)
    #print(col_data.head())
    row_data = get_row_ids(image_data,row_inter)
    table_data = merge_row_col(col_data,row_data)

    item_id = imagejson_filename.split("/")[-1]
    id_pattern = r'QD[A-Z]+[0-9]+'
    item_id = re.match(id_pattern,item_id)
    item_id = item_id.group()
    old_row = 0
    line_data = []
    with open(f"{prefix}.table.txt", 'w') as f:
        for i,line in table_data.iterrows():
            if old_row == line['row']:
                index_col = line['col']
                line_data.append(line['text'])
            else:
                #print(line_data)
                f.writelines(f'{line_data}\n')
                old_row += 1
                line_data = []
                line_data.append(line['text'])
    table_data.to_csv(f"{prefix}.table.csv",encoding='utf_8_sig',header=True,index=False)


    ###########
    # find target key-values
    headers = load_header(headerjson_filename)
    get_target_data(headers,table_data, name, proj)
    #kvalue = get_target_data(headers,table_data, name, proj)
    ###########
    # save csv
    #kvalue = kvalue.T
    #print(kvalue)
    #kvalue.to_csv(f"{prefix}.csv",encoding='utf_8_sig',header=False)

    # ts = []
    # for text in table_data['text']:
    #     t = Entry(table_data[table_data['text']==text]['row'].values[0], \
    #         table_data[table_data['text']==text]['col'].values[0], \
    #             table_data[table_data['text']==text]['x'].values[0], \
    #                 table_data[table_data['text']==text]['y'].values[0], \
    #                     text)
    #     ts.append(t)


    # ts = sorted(ts, key=lambda x: (x.x, x.y))
    # x1,y1,x2,y2 = find_section(ts)
    # l1 = sort_section_col(ts, y1, y2)
    # l2 = detect_col(l1)
    # l3 = match_row(l2)
    # for kp in headers:
    #     v = get_value(l3, kp[1])
    #     if v is not None:
    #         print(f'{kp[0]}\t{v}')

