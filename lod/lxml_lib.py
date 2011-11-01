#!/usr/bin/env python
# -*- coding: utf-8 -*-

## 
## Copyright (C) 2011-2012 National library of the Netherlands, Willem Jan Faber <willemjanfaber@fe2.nl>.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139,
## USA.
##

import os 

try:
  from lxml.etree import parse
  from lxml.etree import Element
  from lxml.etree import fromstring
  #print("ok")
except ImportError:
  try:
    # Python 2.5
    from xml.etree.cElementTree.etree import parse
    from xml.etree.cElementTree.etree import Element
    from xml.etree.cElementTree.etree import fromstring

    #print("2.5")
  except ImportError:
    try:
      # Python 2.5
      from xml.etree.ElementTree.etree import parse
      from xml.etree.ElementTree.etree import Element
      from xml.etree.ElementTree.etree import fromstring
      #Eprint("2.5")
    except ImportError:
      try:
        from ElementTree.etree import parse
        from ElementTree.etree import Element
        from ElementTree.etree import fromstring
        #print("cElementTree")
      except ImportError:
        try:
          from elementtree.ElementTree.etree import parse
          from elementtree.ElementTree.etree import Element
          from elementtree.ElementTree.etree import fromstring
          #print("normal")
        except ImportError:
            #print("errr")
            os._exit(-1)

