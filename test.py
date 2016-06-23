#!/usr/bin/env python -W ignore::DeprecationWarning

import wx
import stars
import warnings

warnings.filterwarnings("ignore")

        
class TestFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,parent,-1,"test",size=(800,400))
        #test = stars.visualization.AbstractCanvas(self)
       
        
        test = stars.visualization.Maps.ShapeMap(self,layers)
        
if __name__ == "2__main__":
    app = wx.PySimpleApp()
    frame = TestFrame(None)
    frame.Show(True)
    app.MainLoop()
    
if __name__ == "__main__":
    def test_line_at_rect_liang(line_seg, rect):
        t_min = 0
        t_max = 1
      
        x1,y1 = line_seg[0]
        x2,y2 = line_seg[1]
       
        left,upper = rect[0]
        right,bottom = rect[1]
       
        if max(x1,x2) < left or min(x1,x2) > right or max(y1,y2) < bottom or min(y1,y2) > upper:
            return False
        
        dx = float(x2-x1)
        dy = float(y2-y1)
        
        P1 = -dx
        q1 = x1 - left
        r1 = q1 / P1
        
        P2 = dx
        q2 = right - x1
        r2 = q2/P2
        
        P3 = -dy
        q3 = y1- bottom
        r3 = q3/P3
        
        P4 = dy
        q4 = upper - y1
        r4 = q4/P4
       
        P_set = (P1, P2, P3, P4)
        r_set = (r1, r2, r3, r4)
       
        t1_set = [0]
        t2_set = [1]
        
        for i in range(4):
            if P_set[i] < 0:
                t1_set.append(r_set[i])
            if P_set[i] > 0:
                t2_set.append(r_set[i])
                
        t1 = max(t1_set)
        t2 = min(t2_set)
        
        return t1 < t2
                    
        
    line_seg = [(-5,3),(15,9)]
    rect = [(0,10),(10,0)]
    
    print test_line_at_rect_liang(line_seg, rect)

    line_seg = [(-8,2),(2,14)]
    print test_line_at_rect_liang(line_seg, rect)
    
    line_seg = [(1,5.0),(2,3.0)]
    rect = [(9.0, 20.43991416309013), (10.941176470588236, 18.13304721030043)]
    print test_line_at_rect_liang(line_seg, rect)
    
    line_seg = ((1, 3.0), (2, 15.0))
    rect = [(0.7563025210084034, 9.495708154506438), (1.1092436974789917, 8.63733905579399)]
    print test_line_at_rect_liang(line_seg, rect)
    
