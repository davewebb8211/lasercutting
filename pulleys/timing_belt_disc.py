#! /usr/bin/env python
'''
Copyright (C) 2007 Aaron Spike  (aaron @ ekips.org)
Copyright (C) 2007 Tavmjong Bah (tavmjong @ free.fr)
Copyright (C) 2011 Dave Webb    (davewebb8211 @ gmail.com)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''

## TODO: connect segments


import inkex
import simplestyle, sys
from math import *
import gettext
_ = gettext.gettext

def inv(angle):
    return tan(angle) - angle

def point_on_involute(radius, parameter):
    x = radius * cos(pi * parameter) + radius * parameter * pi * sin(pi * parameter)
    y = radius * sin(pi * parameter) - radius * parameter * pi * cos(pi * parameter)
    return (x, y)

def point_on_circle(radius, angle):
    x = radius * cos(angle)
    y = radius * sin(angle)
    return (x, y)

def rotate_point(point, angle):
    x = cos(angle) * point[0] - sin(angle) * point[1]
    y = sin(angle) * point[0] + cos(angle) * point[1]
    return (x, y)

def mm2px(in_mm):
	""" convert mm -> userunit """
	in_pixel = inkex.unittouu("%fmm" % in_mm)
	return in_pixel

def points_to_svgd(p):
    svgd = ''
    for x in p:
        svgd += 'L%.3f,%.3f' % (mm2px(x[0]), mm2px(x[1]))
    return svgd

class Disc(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("-t", "--teeth",
                        action="store", type="int",
                        dest="teeth", default=24,
                        help="Number of teeth")
        self.OptionParser.add_option("-b", "--belt",
                        action="store", type="string",
                        dest="belt", default="T2.5",
                        help="Belt type (T2.5, T5, T10, T20)")
        self.OptionParser.add_option("--axle",
                        action="store", type="float",
                        dest="axle", default=6.0,
                        help="Diameter of axle (mm)")
        self.OptionParser.add_option("--axletype",
                        action="store", type="int",
                        dest="axletype", default=0,
                        help="Type of axle")
        self.OptionParser.add_option("-n", "--neutral",
                        action="store", type="inkbool", 
                        dest="neutral", default=False,
                        help="Draw the neutral axis")

    def effect(self):
        teeth = self.options.teeth
        belt = self.options.belt
        axletype = self.options.axletype
        axle = self.options.axle
        neutralcircle = self.options.neutral

        two_pi = 2.0 * pi

        centers = [(float(x) * two_pi / float(teeth) ) for x in range(teeth) ]
        psi = two_pi / float(teeth)
        
        # always for T-belts
        gamma = radians(50.0)
        
        
        # get br and hg from dictionary
        br_se = {'T2.5': 1.75, 'T5': 2.96, 'T10': 6.02, 'T20': 11.65}
        hg_se = {'T2.5': 0.75, 'T5': 1.25, 'T10': 2.60, 'T20':  5.20}

        br_n  = {'T2.5': 1.83, 'T5': 3.32, 'T10': 6.57, 'T20': 12.60}
        hg_n  = {'T2.5': 1.00, 'T5': 1.95, 'T10': 3.40, 'T20':  6.00}
        
        rb_   = {'T2.5': 0.20, 'T5': 0.40, 'T10': 0.60, 'T20':  0.80}
        rt_   = {'T2.5': 0.30, 'T5': 0.60, 'T10': 0.80, 'T20':  1.20}
        
        a_    = {'T2.5': 0.3,  'T5': 0.5,  'T10': 1.0 , 'T20':  1.5}
        
        d_ = { 'T2.5' : {   10:  8.05, 
                            11:  8.85, 
                            12:  9.60,
                            13: 10.40,
                            14: 11.20,
                            15: 12.00,
                            16: 12.80, 
                            17: 13.60, 
                            18: 14.40,
                            19: 15.20,
                            20: 16.00,
                            22: 17.60,
                            25: 19.95,
                            28: 22.35,
                            32: 25.55,
                            36: 28.75,
                            40: 31.90,
                            48: 38.30,
                            60: 47.85,
                            72: 57.40,
                            84: 66.95,
                            96: 76.50}, 
               'T5'   : {   10: 16.05, 
                            11: 17.65,
                            12: 19.25,
                            13: 20.85,
                            14: 22.45,
                            15: 24.05,
                            16: 25.60, 
                            17: 27.20, 
                            18: 28.80,
                            19: 30.40,
                            20: 32.00,
                            22: 35.25,
                            25: 39.95,
                            28: 44.75,
                            32: 51.10,
                            36: 57.45,
                            40: 63.85,
                            48: 76.55,
                            60: 95.65,
                            72: 114.75,
                            84: 133.90,
                            96: 153.00},
               'T10'  : {   12: 38.5,
                            13: 41.55,
                            14: 44.70,
                            15: 47.90,
                            16: 51.10, 
                            17: 54.25, 
                            18: 57.45,
                            19: 60.65,
                            20: 63.80,
                            22: 70.20,
                            25: 79.75,
                            28: 89.25,
                            32: 102.00,
                            36: 114.75,
                            40: 127.45,
                            48: 152.95,
                            60: 191.15,
                            72: 229.30,
                            84: 267.50,
                            96: 305.70},
               'T20'  : {   15: 95.65,
                            16: 102.00, 
                            17: 108.35, 
                            18: 114.75,
                            19: 121.10,
                            20: 127.45,
                            22: 140.20,
                            25: 159.30,
                            28: 178.40,
                            32: 203.85,
                            36: 229.35,
                            40: 254.80,
                            48: 305.70,
                            60: 382.10,
                            72: 458.50,
                            84: 534.90,
                            96: 611.30}}
        
        a = a_[belt]
        
        rb = rb_[belt]
        rt = rb_[belt]
        
        if teeth <= 20:
            # Form SE
            br = br_se[belt]
            hg = hg_se[belt]
        else:
            br = br_n[belt]
            hg = hg_n[belt]
        
        try:
            d = d_[belt][teeth]
            r0 = d / 2.0 - a        
        except:
            inkex.errormsg(_("No definitions in standard for %d teeth with belt %s. Can't continue" % (teeth, belt)))
            exit(-1)
        
        # Do some sanity checkts:
        
        if (axle >= (2.0 * r0) - 2.0 * hg - 2.0):
            inkex.errormsg(_("The rest ring between the root circle (%fmm) "
                             "and the axle (%fmm) is less than 1.0 mm. Can't continue" % (2.0 * r0 - hg, axle)))
            exit(-1)
            
        
        phi = asin((br / 2.0) / r0)         

        x1, y1 = r0 - hg, 0
        x2, y2 = r0 - hg, br/2.0 - tan(gamma/2.0) * (r0 * cos(phi) - (r0 - hg))
        
        # between x1 and x2
        t = rb * tan(radians(45.0) - gamma/4.0)
        x12, y12 = x1, y2 - t
        x231, y231 = x2 + t * sin(radians(90.0) - gamma/2.0), y2 + t * cos(radians(90.0) - gamma/2.0)
        
        
        
        x3, y3 = r0 * cos(phi), br/2.0
        
        
                
        # move to start point
        path = 'M%.3f,%.3f' % (mm2px(x3), mm2px(-y3))

        # rotate tooth
        for c in centers[0:1]:
            points = []
        
            p_tmp = [rotate_point   ((x231,-y231), c), 
                     rotate_point   ((x2  ,-y2  ), c), 
                     rotate_point   ((x12 ,-y12 ), c),
                     rotate_point   ((x2  , y2  ), c), 
                     point_on_circle(        r0  , c + phi)]
            points.extend( p_tmp )
            
            
            # straight lines
            path += points_to_svgd(points)
            
            # segment to next ...
            (x4, y4) = point_on_circle(r0, c + psi - phi  )
            path += 'A%f,%f %f 0,1 %f,%f' % (mm2px(r0), mm2px(r0), 0, mm2px(x4), mm2px(y4))
            






























        #######################


#        involute_right = []
#        involute_left  = []
#
#        # Addendum
#        # (Kopfhoehe)
#        ha = 1.1 * module
#
#        # Dedendum
#        # (Fusshoehe)
#        hf = 1.2 * module
#
#        # Pitch circle
#        # (Waelzkreishalbmesser)
#        rw = (module * float(teeth)) / 2.0
#
#        # Outer circle
#        # (Kopfkreishalbmesser)
#        ra = rw + ha
#
#        # Base circle
#        # (Grundkreishalbmesser (Abwickelkreis der Evolvente))
#        rb = rw * cos(alpha)
#
#        # Root circle
#        # (Fusskreishalbmesser)
#        rf = rw - hf
#
#        # Fillet radius
#        # (Fusskreis-Rundungs-Halbmesser)
#        rr = rb - rf
#
#        # Half of angular width of tooth
#        # (Zahndicken-Halbwinkel)
#        psi = (pi)/(2.0 * float(teeth))
#
#        # Angle at outside circle
#        # (Profilwinkel am Kopfzylinder)
#        alpha_at = acos(rb / ra)
#
#        # Half of angular width at base circle
#        # (Grunddicken-Halbwinkel)
#        psi_b = psi + inv(alpha)
#
#        # Half of angular width at outer circle
#        # (Zahndicken-Halbwinkel am Kopfkreis)
#        psi_a = psi + inv(alpha) - inv(alpha_at)
#
#        # Angular width of fillet
#        # (Zahnfuss-Rundungs-Winkel)
#        psi_r = rr / rb
#        
#        ## check if base circle is > root circle
#        fillet = False
#        if rb > rf:
#            fillet = True
#
#
#        # find parameter t on outer circle (Kopfkreis)
#        t = 0.0
#        step = 0.1
#        while 1 == 1:
#            (x, y) = point_on_involute(rb, t)
#            dist = sqrt(x**2 + y**2)
#
#            if abs(dist-ra) < 0.001:
#                break
#
#            if dist < ra:
#                t += step
#            else:
#                t -= step
#                step = step/2.0
#
#        t_on_ra = t
#        
#        # find parameter t on root circle (f no fillet is used)
#        sign_flag = True    # plus = True, minus = False
#        if fillet == False:
#            # base circle is smaller than root circle
#
#            t = 0.0
#            step = 0.1
#            
#            count = 0
#            
#            while True:
#                (x, y) = point_on_involute(rb, t)
#                dist = sqrt(x**2 + y**2)
#                
#                if abs(dist-rf) < 0.001:
#                    break
#                
##                inkex.errormsg(_("count = %d, t = %f, step = %f, dist = %f; rf = %f" % (count, t, step, dist, rf)))
#                
#                if dist < rf:
#                    t += step
#                    if sign_flag == True:
#                        step = step/2.0
#                        sign_flag = False
#                        
#                else:
#                    t -= step
#                
#                    if sign_flag == False:
#                        step = step/2.0
#                        sign_flag = True
#                
#                count = count + 1
#                if count > 100:
#                    break
#            
#            t_inner = t
#                
#        else:
#            # Have a fillet and then start the involute at the base circle
#            t_inner = 0.0
#
#
#        # create left and right involute in x,y coordinates
#        t = t_inner
#        stop_next = 0
#        while 1 == 1:
#            (x, y) = point_on_involute(rb, t)
#
#            inv_tmp = [(x,y)]
#            involute_right.extend(inv_tmp)
#            inv_tmp = [(x, -y)]
#            involute_left.extend(inv_tmp)
#
#            t = t + 0.01
#
#            if stop_next == 1:
#            	break
#
#            if t > t_on_ra:
#                t = t_on_ra
#                stop_next = 1
#
#
#        ## (0) start point
#        p = involute_right[0]
#        path = 'M%.3f,%.3f' % (mm2px(p[0]), mm2px(p[1]))
#        
#        
#        # rotate tooth
#        for c in centers: #[0:10]:
##            inkex.errormsg(_("c = %f" % (c)))
#
#            ####################
#            # create one tooth #
#            ####################
#    
#            ## (1) involute_right segment
#            points = []
#            for p in involute_right[1:]:
#                points.extend([rotate_point(p, c)])
#    
#            path += points_to_svgd(points)
#    
#    
#            ## (2) circle on outside circle
#            # (Kreisbogen auf dem Kopfkreis (ra))
#            (x, y) = point_on_circle(ra, c + psi_b + psi_a)
#            path += 'A%f,%f -60 0,1 %f,%f' % (mm2px(ra), mm2px(ra), mm2px(x), mm2px(y))
#    
#            ## (3) involute_left segment
#            points = []
#            for p in reversed(involute_left[:-1]):
#                p = rotate_point(p, 2 * psi_b + c)
#                points.extend([p])
#    
#            path += points_to_svgd(points)
#    
#
#            if fillet == True:
#                ## (4) Fillet to root circle
#                # (Rundung zum Fusskreis)            
#                (x, y) = point_on_circle(rf, c + 2 * psi_b + psi_r)
#                path += 'A%f,%f 0 0,0 %f,%f' % (mm2px(rr), mm2px(rr), mm2px(x), mm2px(y))
#                
#    
#                ## (5) circle on root circle
#                # (Kreis auf dem Fusskreis (rf))
#                (x, y) = point_on_circle(rf, c + 4 * psi - psi_r)
#                path += 'A%f,%f 0 0,0 %f,%f' % (mm2px(rf), mm2px(rf), mm2px(x), mm2px(y))
#    
#                ## (5) Second fillet at root circle
#                # (zweite Rundung im Fusskreis)
#                (x, y) = point_on_circle(rb, c + 4 * psi)   
#                path += 'A%f,%f -60 0,0 %f,%f' % (mm2px(rr), mm2px(rr), mm2px(x), mm2px(y))
#            else:
#                # only circle on root circle
#                (tmp_x, tmp_y) = p
#                (x, y) = point_on_involute(rb, t_inner)
#                (x, y) = rotate_point((x, y), c + 4 * psi)
#                
#                ## simples: only segment on root circle
##                path += 'A%f,%f -60 0,0 %f,%f' % (mm2px(rf), mm2px(rf), mm2px(x), mm2px(y))    
#
#                ## advanced: ellepsis
##                dist = sqrt((tmp_x - x)**2 + (tmp_y - y)**2)
##                path += 'A%f,%f %f 0,0 %f,%f' % (mm2px(dist/1.5), mm2px(dist/2.0), degrees(c + 2 * psi ) - 90.0, mm2px(x), mm2px(y))               
#                
#                ## most advanced: 3 circles with tangential match
#                rounding = 0.25
#                
#                # get tangent of involute                                
#                (x1, y1) = rotate_point(involute_left[0], 2 * psi_b + c)
#                (x2, y2) = rotate_point(involute_left[1], 2 * psi_b + c)
#                (dx1, dy1) = (x2 - x1, y2 - y1)                
#                l1 = sqrt(dx1**2 + dy1**2)
#                (dx1, dy1) = (dx1/l1, dy1/l1)   # normalised
#                (x3, y3) = (x1 - (dy1 * rounding), y1 + (dx1 * rounding))
#                l2 = sqrt(x3**2 + y3**2)
#                scale = (l2-rounding)/(l2)
#                (x4, y4) = (x3 * scale, y3 * scale)
#              
##                path += 'L%.3f,%.3f' % (mm2px(x3), mm2px(y3))
#                path += 'A%f,%f %f 0,0 %f,%f' % (mm2px(rounding), mm2px(rounding), 0, mm2px(x4), mm2px(y4))
#                
#                # next point
#                (x1, y1) = rotate_point(involute_right[0], 4 * psi + c)
#                (x2, y2) = rotate_point(involute_right[1], 4 * psi + c)
#                (dx1, dy1) = (x2 - x1, y2 - y1)                
#                l1 = sqrt(dx1**2 + dy1**2)
#                (dx1, dy1) = (dx1/l1, dy1/l1)   # normalised
#                (x3, y3) = (x1 + (dy1 * rounding), y1 - (dx1 * rounding))
#                l2 = sqrt(x3**2 + y3**2)
#                scale = (l2-rounding)/(l2)
#                (x4, y4) = (x3 * scale, y3 * scale)
#                
#
#                rounding2 = sqrt(x4**2 + y4**2)
##                path += 'L%.3f,%.3f' % (mm2px(x3), mm2px(y3))
#                path += 'A%f,%f %f 0,1 %f,%f' % (mm2px(rounding2), mm2px(rounding2), 0, mm2px(x4), mm2px(y4))
#
#
#                path += 'A%f,%f %f 0,0 %f,%f' % (mm2px(rounding), mm2px(rounding), 0, mm2px(x1), mm2px(y1))
#




        ## close path
#        path += 'z'

#        inkex.errormsg(_("path = (%s)" % path))


        ##############################
        # embed path in SVG document #
        ##############################

        ## Create a new layer.
        ## Embed gear in group to make animation easier:
        ## Translate group, Rotate path.
#        t = 'translate(' + str( self.view_center[0] ) + ',' + str( self.view_center[1] ) + ')'
        t = 'translate(' + str( 0.0 ) + ',' + str( 0.0 ) + ')'
        g_attribs = {inkex.addNS('label','inkscape'):'Gear' + str( teeth ),
                     'transform':t }
        g = inkex.etree.SubElement(self.current_layer, 'g', g_attribs)

        # Create SVG Path for gear
        style = { 'stroke'       : '#000000',
        		  'fill'         : 'none',
        		  'stroke-width' : '0.1' }
        gear_attribs = {'style':simplestyle.formatStyle(style), 'd':path}
        gear = inkex.etree.SubElement(g, inkex.addNS('path','svg'), gear_attribs )

#        
#        # Axle
        axle_attribs = {'style':simplestyle.formatStyle(style)}
        
        circ = inkex.etree.Element(inkex.addNS('circle','svg'), axle_attribs)
        circ.set('cx',      str(mm2px(0)))
        circ.set('cy',      str(mm2px(0)))
        circ.set('r',       str(mm2px(axle/2.0)))

        g.append(circ)
#
#
#        # Adding a circles
        style = { 'stroke'          : '#ff0000',
                  'fill'            : 'none',
                  'stroke-width'    : '0.1',
                  'stroke-dasharray': '3, 0.5, 0.5, 0.5' }
        circ_attribs = {'style':simplestyle.formatStyle(style)}

        radiuslist = []
        
#        radiuslist.extend([r0])
        
        if neutralcircle:
            radiuslist.extend([d/2.0])
#        if pitchcircle:
#            radiuslist.extend([rw])
#        if basecircle:
#            radiuslist.extend([rb])
#        if rootcircle:
#            radiuslist.extend([rf])
#        
        for radius in radiuslist:
            circ = inkex.etree.Element(inkex.addNS('circle','svg'), circ_attribs)
            circ.set('cx',      str(mm2px(0)))
            circ.set('cy',      str(mm2px(0)))
            circ.set('r',       str(mm2px(radius)))

            g.append(circ)

if __name__ == '__main__':
    e = Disc()
    e.affect()


# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
