#/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 09 18:48:06 2023

@author: Mattia Fanì (Los Alamos National Laboratory, US) - mattia.fani@cern.ch
Based on work of: 
    Francesco Pietropaolo (CERN)
    Serhan Tufanli (CERN)
    Chris Macias (University of Iowa, US)
    Furkan Dolek (Cukurova University, TR, and CERN)

"""

import numpy as np
import struct
import inc.settings
from inc.rawto32chn import rawto32chn

def raw_convertor_conv(fp, femb_num = 1, trigno = 0, jumbo_flag=True):
    
    inc.settings.settings()
    
    if (jumbo_flag == True):
        pkg_len = int(0x1df4/2)
    else:
        pkg_len = int(0x3fa/2)
    
    with open(fp, 'rb') as f:
        raw_data = f.read()   
        len_file = len(raw_data)
        dataNtuple =struct.unpack_from(">%dH"%(len_file//2),raw_data)
        addr = 0
        trig_i = 0

        while (trig_i < trigno):
            link_i = 0
            links_data = [np.array([], dtype=int), np.array([], dtype=int), np.array([], dtype=int),np.array([], dtype=int)]
            except_cnt = 0
            stcount=0
            while (addr <= len(dataNtuple) -  25) and (link_i < femb_num*4):
                stcount+=1
                
                pkg_cnt0 = ((((dataNtuple[addr]) << 16 )+ (dataNtuple[addr+1])) ) & 0xFFFFFFFF # << bitwise left shift, & bitwise and
                pkg_res0 = ((((dataNtuple[addr+2]) << 16 )+ (dataNtuple[addr+3])) ) & 0xFFFFFFFF
                a = addr
                for b in range(addr, len(dataNtuple)-4, 1):
                    pkg_cnt1 = ((((dataNtuple[b]) << 16 )+ (dataNtuple[b+1])) ) & 0xFFFFFFFF
                    pkg_res1 = ((((dataNtuple[b+2]) << 16 )+ (dataNtuple[b+3])) ) & 0xFFFFFFFF
                    if (pkg_cnt1 == pkg_cnt0 + 1) and (pkg_res0 == 0) and (pkg_res1 == 0):
                        addr=b
                        break 
                udp_pkg = np.array(dataNtuple[a:b], dtype = int)

                if (udp_pkg[8] == 0 ) and ( (udp_pkg[9] == 0xface) or(udp_pkg[9] == 0xfeed) ): #feed-65261, face-64206
                    links_data[link_i] = np.append(links_data[link_i] , udp_pkg[9:])
                else:
                    links_data[link_i] = np.append(links_data[link_i] , udp_pkg[8:])
                if (b-a) < pkg_len-10:
                    link_i +=1
                    except_cnt = 0
                else:
                    except_cnt = except_cnt + 1
                    if except_cnt >= 10:
                        print (f"{inc.settings.output_align}! i_binary_event={trig_i}: This is the last trigger event in the binary file")
                        # print ("                     !, This is the last tirgger event in the file, data of this event is out of format!!")
                        # print ("                     !, Please input a value < %d"%trig_i )
                        # print ("                     !, the script stop anyway")
                        #exit()
                        return
                trig_oft = b
            trig_i = trig_i + 1
        links_face_pos = []
        links_feed_pos = []
        for tmp in range(femb_num*4):
            links_face_pos.append([])
            links_feed_pos.append([])

        for i in range(len(links_data)):
            links_face_pos[i] =  np.where(links_data[i]== 0xface)[0]
            links_feed_pos[i] =  np.where(links_data[i]== 0xfeed)[0]
            links_face_pos[i] = np.sort(np.append(links_face_pos[i], links_feed_pos[i]))

        chipx2_data = [[],[],[],[]]
        for i in range(len(links_face_pos)):
            chn_data = []
            for x in range(32):
                chn_data.append([])
            for j in range(len(links_face_pos[i])-1):
                if (links_face_pos[i][j+1] - links_face_pos[i][j] == 25): 
                    onepkgdata = links_data[i][int(links_face_pos[i][j]) : int(links_face_pos[i][j]) +25 ]
                    chn_data, cycle_del =  rawto32chn(onepkgdata, chn_data)
                # else: #!!! Mattia needs to check this
                    # print (f"{inc.settings.output_align}  A sample data is not 25 words")
            chipx2_data[i] = chn_data
        femb_data = chipx2_data[0] + chipx2_data[1] + chipx2_data[2] + chipx2_data[3] 
        
        raw_data = 0
        dataNtuple = 0
        del raw_data
        del dataNtuple
        f.close()
    return femb_data