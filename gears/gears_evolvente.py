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

class Gears(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("-t", "--teeth",
                        action="store", type="int",
                        dest="teeth", default=24,
                        help="Number of teeth")
        self.OptionParser.add_option("-m", "--module",
                        action="store", type="float",
                        dest="module", default=1.0,
                        help="Module (A scaling factor used in metric gears with units in millimeters whose effect is to enlarge the gear tooth size. Common values: 1, 2, 4)")
        self.OptionParser.add_option("-a", "--alpha",
                        action="store", type="float",
                        dest="alpha", default=20.0,
                        help="Pressure Angle (common values: 14.5, 20, 25 degrees)")
        self.OptionParser.add_option("--axle",
                        action="store", type="float",
                        dest="axle", default=6.0,
                        help="Diameter of axle (mm)")
        self.OptionParser.add_option("--axletype",
                        action="store", type="int",
                        dest="axletype", default=0,
                        help="Type of axle")
        self.OptionParser.add_option("-o", "--outercircle",
                        action="store", type="inkbool", 
                        dest="outercircle", default=False,
                        help="Draw the outer circle")
        self.OptionParser.add_option("-p", "--pitchcircle",
                        action="store", type="inkbool", 
                        dest="pitchcircle", default=True,
                        help="Draw the pitch circle (recommended for aligning gears)")
        self.OptionParser.add_option("-b", "--basecircle",
                        action="store", type="inkbool", 
                        dest="basecircle", default=False,
                        help="Draw the base circle")
        self.OptionParser.add_option("-r", "--rootcircle",
                        action="store", type="inkbool", 
                        dest="rootcircle", default=False,
                        help="Draw the root circle")

    def effect(self):
        teeth = self.options.teeth
        module = self.options.module
        alpha = radians(self.options.alpha)  
        axle = self.options.axle
        outercircle = self.options.outercircle
        pitchcircle = self.options.pitchcircle
        basecircle = self.options.basecircle
        rootcircle = self.options.rootcircle

        two_pi = 2.0 * pi

        centers = [(float(x) * two_pi / float( teeth) ) for x in range( teeth ) ]

        involute_right = []
        involute_left  = []

        # Addendum
        # (Kopfhoehe)
        ha = 1.1 * module

        # Dedendum
        # (Fusshoehe)
        hf = 1.2 * module

        # Pitch circle
        # (Waelzkreishalbmesser)
        rw = (module * float(teeth)) / 2.0

        # Outer circle
        # (Kopfkreishalbmesser)
        ra = rw + ha

        # Base circle
        # (Grundkreishalbmesser (Abwickelkreis der Evolvente))
        rb = rw * cos(alpha)

        # Root circle
        # (Fusskreishalbmesser)
        rf = rw - hf

        # Fillet radius
        # (Fusskreis-Rundungs-Halbmesser)
        rr = rb - rf

        # Half of angular width of tooth
        # (Zahndicken-Halbwinkel)
        psi = (pi)/(2.0 * float(teeth))

        # Angle at outside circle
        # (Profilwinkel am Kopfzylinder)
        alpha_at = acos(rb / ra)

        # Half of angular width at base circle
        # (Grunddicken-Halbwinkel)
        psi_b = psi + inv(alpha)

        # Half of angular width at outer circle
        # (Zahndicken-Halbwinkel am Kopfkreis)
        psi_a = psi + inv(alpha) - inv(alpha_at)

        # Angular width of fillet
        # (Zahnfuss-Rundungs-Winkel)
        psi_r = rr / rb
        
        ## check if base circle is > root circle
        fillet = False
        if rb > rf:
            fillet = True


        # find parameter t on outer circle (Kopfkreis)
        t = 0.0
        step = 0.1
        while 1 == 1:
            (x, y) = point_on_involute(rb, t)
            dist = sqrt(x**2 + y**2)

            if abs(dist-ra) < 0.001:
                break

            if dist < ra:
                t += step
            else:
                t -= step
                step = step/2.0

        t_on_ra = t
        
        # find parameter t on root circle (f no fillet is used)
        sign_flag = True    # plus = True, minus = False
        if fillet == False:
            # base circle is smaller than root circle

            t = 0.0
            step = 0.1
            
            count = 0
            
            while True:
                (x, y) = point_on_involute(rb, t)
                dist = sqrt(x**2 + y**2)
                
                if abs(dist-rf) < 0.001:
                    break
                
#                inkex.errormsg(_("count = %d, t = %f, step = %f, dist = %f; rf = %f" % (count, t, step, dist, rf)))
                
                if dist < rf:
                    t += step
                    if sign_flag == True:
                        step = step/2.0
                        sign_flag = False
                        
                else:
                    t -= step
                
                    if sign_flag == False:
                        step = step/2.0
                        sign_flag = True
                
                count = count + 1
                if count > 100:
                    break
            
            t_inner = t
                
        else:
            # Have a fillet and then start the involute at the base circle
            t_inner = 0.0


        # create left and right involute in x,y coordinates
        t = t_inner
        stop_next = 0
        while 1 == 1:
            (x, y) = point_on_involute(rb, t)

            inv_tmp = [(x,y)]
            involute_right.extend(inv_tmp)
            inv_tmp = [(x, -y)]
            involute_left.extend(inv_tmp)

            t = t + 0.01

            if stop_next == 1:
            	break

            if t > t_on_ra:
                t = t_on_ra
                stop_next = 1


        ## (0) start point
        p = involute_right[0]
        path = 'M%.3f,%.3f' % (mm2px(p[0]), mm2px(p[1]))
        
        
        # rotate tooth
        for c in centers: #[0:10]:
#            inkex.errormsg(_("c = %f" % (c)))

            ####################
            # create one tooth #
            ####################
    
            ## (1) involute_right segment
            points = []
            for p in involute_right[1:]:
                points.extend([rotate_point(p, c)])
    
            path += points_to_svgd(points)
    
    
            ## (2) circle on outside circle
            # (Kreisbogen auf dem Kopfkreis (ra))
            (x, y) = point_on_circle(ra, c + psi_b + psi_a)
            path += 'A%f,%f -60 0,1 %f,%f' % (mm2px(ra), mm2px(ra), mm2px(x), mm2px(y))
    
            ## (3) involute_left segment
            points = []
            for p in reversed(involute_left[:-1]):
                p = rotate_point(p, 2 * psi_b + c)
                points.extend([p])
    
            path += points_to_svgd(points)
    

            if fillet == True:
                ## (4) Fillet to root circle
                # (Rundung zum Fusskreis)            
                (x, y) = point_on_circle(rf, c + 2 * psi_b + psi_r)
                path += 'A%f,%f 0 0,0 %f,%f' % (mm2px(rr), mm2px(rr), mm2px(x), mm2px(y))
                
    
                ## (5) circle on root circle
                # (Kreis auf dem Fusskreis (rf))
                (x, y) = point_on_circle(rf, c + 4 * psi - psi_r)
                path += 'A%f,%f 0 0,0 %f,%f' % (mm2px(rf), mm2px(rf), mm2px(x), mm2px(y))
    
                ## (5) Second fillet at root circle
                # (zweite Rundung im Fusskreis)
                (x, y) = point_on_circle(rb, c + 4 * psi)   
                path += 'A%f,%f -60 0,0 %f,%f' % (mm2px(rr), mm2px(rr), mm2px(x), mm2px(y))
            else:
                # only circle on root circle
                (tmp_x, tmp_y) = p
                (x, y) = point_on_involute(rb, t_inner)
                (x, y) = rotate_point((x, y), c + 4 * psi)
                
                ## simples: only segment on root circle
#                path += 'A%f,%f -60 0,0 %f,%f' % (mm2px(rf), mm2px(rf), mm2px(x), mm2px(y))    

                ## advanced: ellepsis
#                dist = sqrt((tmp_x - x)**2 + (tmp_y - y)**2)
#                path += 'A%f,%f %f 0,0 %f,%f' % (mm2px(dist/1.5), mm2px(dist/2.0), degrees(c + 2 * psi ) - 90.0, mm2px(x), mm2px(y))               
                
                ## most advanced: 3 circles with tangential match
                rounding = 0.25
                
                # get tangent of involute                                
                (x1, y1) = rotate_point(involute_left[0], 2 * psi_b + c)
                (x2, y2) = rotate_point(involute_left[1], 2 * psi_b + c)
                (dx1, dy1) = (x2 - x1, y2 - y1)                
                l1 = sqrt(dx1**2 + dy1**2)
                (dx1, dy1) = (dx1/l1, dy1/l1)   # normalised
                (x3, y3) = (x1 - (dy1 * rounding), y1 + (dx1 * rounding))
                l2 = sqrt(x3**2 + y3**2)
                scale = (l2-rounding)/(l2)
                (x4, y4) = (x3 * scale, y3 * scale)
              
#                path += 'L%.3f,%.3f' % (mm2px(x3), mm2px(y3))
                path += 'A%f,%f %f 0,0 %f,%f' % (mm2px(rounding), mm2px(rounding), 0, mm2px(x4), mm2px(y4))
                
                # next point
                (x1, y1) = rotate_point(involute_right[0], 4 * psi + c)
                (x2, y2) = rotate_point(involute_right[1], 4 * psi + c)
                (dx1, dy1) = (x2 - x1, y2 - y1)                
                l1 = sqrt(dx1**2 + dy1**2)
                (dx1, dy1) = (dx1/l1, dy1/l1)   # normalised
                (x3, y3) = (x1 + (dy1 * rounding), y1 - (dx1 * rounding))
                l2 = sqrt(x3**2 + y3**2)
                scale = (l2-rounding)/(l2)
                (x4, y4) = (x3 * scale, y3 * scale)
                

                rounding2 = sqrt(x4**2 + y4**2)
#                path += 'L%.3f,%.3f' % (mm2px(x3), mm2px(y3))
                path += 'A%f,%f %f 0,1 %f,%f' % (mm2px(rounding2), mm2px(rounding2), 0, mm2px(x4), mm2px(y4))


                path += 'A%f,%f %f 0,0 %f,%f' % (mm2px(rounding), mm2px(rounding), 0, mm2px(x1), mm2px(y1))


        ## close path
        path += 'z'

#        inkex.errormsg(_("path = (%s)" % path))


        ##############################
        # embed path in SVG document #
        ##############################

        ## Create a new layer.
        ## Embed gear in group to make animation easier:
        ## Translate group, Rotate path.
        t = 'translate(' + str( self.view_center[0] ) + ',' + str( self.view_center[1] ) + ')'
        g_attribs = {inkex.addNS('label','inkscape'):'Gear' + str( teeth ),
                     'transform':t }
        g = inkex.etree.SubElement(self.current_layer, 'g', g_attribs)

        # Create SVG Path for gear
        style = { 'stroke'       : '#000000',
        		  'fill'         : 'none',
        		  'stroke-width' : '0.1' }
        gear_attribs = {'style':simplestyle.formatStyle(style), 'd':path}
        gear = inkex.etree.SubElement(g, inkex.addNS('path','svg'), gear_attribs )
        
        # Axle
        axle_attribs = {'style':simplestyle.formatStyle(style)}
        
        circ = inkex.etree.Element(inkex.addNS('circle','svg'), axle_attribs)
        circ.set('cx',      str(mm2px(0)))
        circ.set('cy',      str(mm2px(0)))
        circ.set('r',       str(mm2px(axle)))

        g.append(circ)


        # Adding a circles
        style = { 'stroke'       : '#ff0000',
                  'fill'         : 'none',
                  'stroke-width' : '0.1' }
        circ_attribs = {'style':simplestyle.formatStyle(style)}

        radiuslist = []
        
        if outercircle:
            radiuslist.extend([ra])
        if pitchcircle:
            radiuslist.extend([rw])
        if basecircle:
            radiuslist.extend([rb])
        if rootcircle:
            radiuslist.extend([rf])
        
        for radius in radiuslist:
            circ = inkex.etree.Element(inkex.addNS('circle','svg'), circ_attribs)
            circ.set('cx',      str(mm2px(0)))
            circ.set('cy',      str(mm2px(0)))
            circ.set('r',       str(mm2px(radius)))

            g.append(circ)

if __name__ == '__main__':
    e = Gears()
    e.affect()


# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
