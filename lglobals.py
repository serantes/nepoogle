#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#***************************************************************************
#*   nepoogle - globals library.                                           *
#*                                                                         *
#*   Copyright (C) 2011-2012 Ignacio Serantes <kde@aynoa.net>              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 2 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU General Public License for more details.                          *
#*                                                                         *
#*   You should have received a copy of the GNU General Public License     *
#*   along with this program; if not, write to the                         *
#*   Free Software Foundation, Inc.,                                       *
#*   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.         *
#***************************************************************************

import gettext, locale, os, sys

import PyKDE4.kdecore as kdecore

from PyKDE4.soprano import Soprano

#BEGIN lglobals.py

PROGRAM_URL = sys.argv[0]
PROGRAM_NAME = os.path.basename(sys.argv[0])
PROGRAM_BASENAME = os.path.splitext(PROGRAM_NAME)[0]
PROGRAM_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
PROGRAM_VERSION_VERSION = 'v0.9.4git'
PROGRAM_VERSION_DATE = '2012-xx-xx'
PROGRAM_AUTHOR_NAME = 'Ignacio Serantes'
PROGRAM_AUTHOR_EMAIL = 'kde@aynoa.net'
PROGRAM_HTML_POWERED = "<hr>--<br /><b>Powered by</b> <em>%(name)s</em> <b>%(version)s</b> released (%(date)s)" \
                        % {'name': PROGRAM_NAME, \
                            'version': PROGRAM_VERSION_VERSION, \
                            'date': PROGRAM_VERSION_DATE \
                            }

gettext.bindtextdomain(PROGRAM_NAME, '') #'/path/to/my/language/directory')
gettext.textdomain(PROGRAM_NAME)
_ = gettext.gettext
#gettext.translation(PROGRAM_NAME, languages=['es']).install()

SLEEP_NO_SLEEP = 0
SLEEP_AFTER_UPDATE_DBUS = 1.5
SLEEP_AFTER_UPDATE = 0.5

ONTOLOGY_ALTLABEL = "nao:altLabel"
ONTOLOGY_COMMENT = "nie:comment"
ONTOLOGY_COPIED_FROM = "ndo:copiedFrom"
ONTOLOGY_DEPICTION = "nfo:depiction"
ONTOLOGY_DESCRIPTION = "nao:description"
ONTOLOGY_FULLNAME = "nco:fullname"
ONTOLOGY_IDENTIFIER = "nao:identifier"
ONTOLOGY_LANGUAGE = "nie:language"
ONTOLOGY_LINK = "nao:isRelated"
ONTOLOGY_MUSIC_ALBUM_COVER = "nmm:artwork"
ONTOLOGY_NUMERIC_RATING = "nao:numericRating"
ONTOLOGY_PREFLABEL = "nao:prefLabel"
ONTOLOGY_SUBJECT = "nie:subject"
ONTOLOGY_SYMBOL = "nao:hasSymbol"
ONTOLOGY_SYMBOL_CONTACT = "nco:photo"
ONTOLOGY_TITLE = "nie:title"
ONTOLOGY_TYPE_CONTACT = "nco:Contact"
ONTOLOGY_TYPE_IMAGE = "nfo:Image"
ONTOLOGY_TYPE_MUSIC_ALBUM = "nmm:MusicAlbum"
ONTOLOGY_TYPE_TAG = "nao:Tag"

DO_NOT_USE_NEPOMUK = False
USE_INTERNAL_RESOURCE = False
USE_INTERNAL_RESOURCE_FOR_MAIN_TYPE = (False or DO_NOT_USE_NEPOMUK)

INTERNAL_RESOURCE = (USE_INTERNAL_RESOURCE or DO_NOT_USE_NEPOMUK)
INTERNAL_RESOURCE_FORCED_IN_CONSOLE = (USE_INTERNAL_RESOURCE or DO_NOT_USE_NEPOMUK)
INTERNAL_RESOURCE_IN_PLAYLIST = (USE_INTERNAL_RESOURCE or DO_NOT_USE_NEPOMUK)
INTERNAL_RESOURCE_IN_RESULTS_LIST = (USE_INTERNAL_RESOURCE or DO_NOT_USE_NEPOMUK)

PYKDE4_VERSION_STR = kdecore.versionString().split(" ")[0].strip()

SYSTEM_ENCODING = locale.getpreferredencoding()
if (SYSTEM_ENCODING == ""):
    SYSTEM_ENCODING = 'UTF-8' # Forcing UTF-8.

KDE4_CONFIG_PATH = unicode(kdecore.KStandardDirs().locate("config", ""), SYSTEM_ENCODING).split(":")[0].strip()
KDE4_DATA_PATH = unicode(kdecore.KStandardDirs().locate("data", ""), SYSTEM_ENCODING).split(":")[0].strip()

NEPOOGLE_CONFIG_FILE = KDE4_CONFIG_PATH + PROGRAM_NAME + ".rc"
NEPOOGLE_DATA_PATH = KDE4_DATA_PATH + PROGRAM_NAME + "/"
NEPOOGLE_DOWNLOADS_PATH = NEPOOGLE_DATA_PATH + "downloads/"

USE_NEW_INFERENCE_METHOD = (PYKDE4_VERSION_STR > "4.8.7")
if USE_NEW_INFERENCE_METHOD:
    DEFAULT_ENGINE = 1
    SOPRANO_QUERY_LANGUAGE = Soprano.Query.QueryLanguageSparqlNoInference

else:
    DEFAULT_ENGINE = 1
    SOPRANO_QUERY_LANGUAGE = Soprano.Query.QueryLanguageSparql
    USE_INTERNAL_RESOURCE_FOR_MAIN_TYPE = True

NEXIF_METERING_MODE = [_("Unknown"), _("Average"), _("CenterWeightedAverage"), _("Spot"), _("MultiSpot"), _("Pattern"), _("Partial"), _("Other")]
NEXIF_WHITE_BALANCE = [_("Unknown"), _("Automatic"), _("Manual")]

SCRIPT_IMAGE_VIEWER = "<script type=\"text/javascript\">function getObjectXY(o){var x,y;c=o;if(o.offsetParent){x=y=0;do{x+=o.offsetLeft;if(o.style.borderLeftWidth!='')x+=parseInt(o.style.borderLeftWidth);else o.style.borderLeftWidth='0px';y+=o.offsetTop;if(o.style.borderTopWidth!='')y+=parseInt(o.style.borderTopWidth);else o.style.borderTopWidth='0px';}while(o=o.offsetParent);}return [x-parseInt(c.style.borderLeftWidth),y-parseInt(c.style.borderLeftWidth)];}function retInt(s,f){if(typeof s=='number')return s;var result=s.indexOf(f);return parseInt(s.substring(0,(result!=-1)?result:s.length));}function getMouseXY(e){var x=0,y=0;if(!e)e=window.event;if(e.pageX||e.pageY){x=e.pageX;y=e.pageY;}else if(e.clientX||e.clientY){x=e.clientX+document.body.scrollLeft+document.documentElement.scrollLeft;y=e.clientY+document.body.scrollTop+document.documentElement.scrollTop;}return [x,y];}function mouseWheel(){var s=this;var w=function(e,o,d){};s.wheelHandler=function(e){var d=0;if(!e)e=window.event;if(e.wheelDelta)d=e.wheelDelta/120;else if(e.detail)d=-e.detail/3;if(e.preventDefault)e.preventDefault();e.returnValue=false;if(d)w(e,this,d);};s.init=function(o,c){if(o.addEventListener)o.addEventListener('DOMMouseScroll',this.wheelHandler,false);o.onmousewheel=this.wheelHandler;w=c;};this.setCallback=function(c){w=c;}}function viewer(args){var s=this;s.outerFrame=null;var i=null,imageSource=null,parent=null,replace=null,preLoader=null;var frame=['400px','400px',true];var zoomFactor='10%';var m='300%';i=args['image']?args['image']:null;imageSource=args['imageSource']?args['imageSource']:null;parent=args['parent']?args['parent']:null;replace=args['replace']?args['replace']:null;preLoader=args['preLoader']?args['preLoader']:null;frame=args['frame']?args['frame']:['400px','400px',true];zoomFactor=args['zoomFactor']?args['zoomFactor']:'10%';m=args['maxZoom']?args['maxZoom']:'300%';s.frameElement=s.f=null;var oW,oH,l=0;var lm=null,sp=5;var mo=null;s.getFrameDimension=function(){return [s.f.clientWidth,s.f.clientHeight];};s.setDimension=function(w,h){i.width=Math.round(w);i.height=Math.round(h);};s.getDimension=function(){return [i.width,i.height];};s.setPosition=function(x,y){i.style.left=(Math.round(x)+'px');i.style.top=(Math.round(y)+'px');};s.getPosition=function(){return [retInt(i.style.left,'px'),retInt(i.style.top,'px')];};s.setMouseCursor=function(){var d=s.getDimension();var fd=s.getFrameDimension();var c='crosshair';if(d[0]>fd[0]&&d[1]>fd[1])c='move';else if(d[0]>fd[0])c='e-resize';else if(d[1]>fd[1])c='n-resize';i.style.cursor=c;};s.maxZoomCheck=function(w,h){if(typeof w=='undefined'||typeof h=='undefined'){var t=s.getDimension();w=t[0],h=t[1];}if(typeof m=='number'){return((w/oW)>m||(h/oH)>m);}else if(typeof m=='object'){return(w>m[0]||h>m[1]);}};s.fitToFrame=function(w,h){if(typeof w=='undefined'||typeof h=='undefined'){w=oW,h=oH;}var fd=s.getFrameDimension(),nW,nH;nW=fd[0];nH=Math.round((nW*h)/w);if(nH>(fd[1])){nH=fd[1];nW=Math.round((nH*w)/h);}return [nW,nH];};s.getZoomLevel=function(){return l;};s.zoomTo=function(nl,x,y){var fd=s.getFrameDimension();if(nl<0||x<0||y<0||x>=fd[0]||y>=fd[1])return false;var d=s.fitToFrame(oW,oH);for(var n=nl;n>0;n--)d[0]*=zoomFactor,d[1]*=zoomFactor;var cW=i.width,cH=i.height;var p=s.getPosition();p[0]-=((x-p[0])*((d[0]/cW)-1)),p[1]-=((y-p[1])*((d[1]/cH)-1));p=s.centerImage(d[0],d[1],p[0],p[1]);if(!s.maxZoomCheck(d[0],d[1])){l=nl;s.setDimension(d[0],d[1]);s.setPosition(p[0],p[1]);s.setMouseCursor();}else return false;return true;};s.centerImage=function(w,h,x,y){if(typeof w=='undefined'||typeof h=='undefined'){var t=s.getDimension();w=t[0],h=t[1];};if(typeof x=='undefined'||typeof y=='undefined'){var t=s.getPosition();x=t[0],y=t[1];}var fd=s.getFrameDimension();if(w<=fd[0])x=Math.round((fd[0] - w)/2);if(h<=fd[1])y=Math.round((fd[1] - h)/2);if(w>fd[0]){if(x>0)x=0;else if((x+w)<fd[0])x=fd[0]-w;}if(h>fd[1]){if(y>0)y=0;else if((y+h)<fd[1])y=fd[1]-h;}return [x,y];};s.relativeToAbsolute=function(x,y){if(x<0||y<0||x>=s.f.clientWidth||y>=s.f.clientHeight)return null;return [x-retInt(i.style.left,'px'),y-retInt(i.style.top,'px')];};s.reset=function(){var d=s.fitToFrame(oW,oH);var p=s.centerImage(d[0],d[1],0,0);s.setDimension(d[0],d[1]);s.setPosition(p[0],p[1]);l=0;};s.moveBy=function(x,y){var p=s.getPosition();p=s.centerImage(i.width,i.height,p[0]+x,p[1]+y);s.setPosition(p[0],p[1]);};s.hide=function(){if(s.outerFrame)s.outerFrame.style.display='none';else s.f.style.display='none';};s.show=function(){if(s.outerFrame)s.outerFrame.style.display='block';else s.f.style.display='block';};s.onload=null;s.onmousewheel=function(e,o,direction){s.f.focus();if(!e)e=window.event,e.returnValue=false;else if(e.preventDefault)e.preventDefault();if((l+direction)>=0){var mp=getMouseXY(e);var fp=getObjectXY(s.f);s.zoomTo(l+direction,mp[0]-fp[0],mp[1]-fp[1]);}};s.onmousemove=function(e){if(!e)e=window.event,e.returnValue=false;else if(e.preventDefault)e.preventDefault();var mp=getMouseXY(e);var p=s.getPosition();p[0]+=(mp[0]-lm[0]),p[1]+=(mp[1]-lm[1]);lm=mp;p=s.centerImage(i.width,i.height,p[0],p[1]);s.setPosition(p[0],p[1]);};s.onmouseup_or_out=function(e){if(!e)e=window.event,e.returnValue=false;else if(e.preventDefault)e.preventDefault();i.onmousemove=i.onmouseup=i.onmouseout=null;i.onmousedown=s.onmousedown;};s.onmousedown=function(e){s.f.focus();if(!e)e=window.event,e.returnValue=false;else if(e.preventDefault)e.preventDefault();lm=getMouseXY(e);i.onmousemove=s.onmousemove;i.onmouseup=i.onmouseout=s.onmouseup_or_out;};s.onkeypress=function(e){var k;if(window.event)e=window.event,k=e.keyCode,e.returnValue=false;else if(e.which)k=e.which,e.preventDefault();k=String.fromCharCode(k);var p=s.getPosition();var LEFT='a',UP='w',RIGHT='d',DOWN='s',CENTER_IMAGE='c',ZOOMIN='=',ZOOMOUT='-';if(k==LEFT)p[0]+=sp;else if(k==UP)p[1]+=sp;else if(k==RIGHT)p[0]-=sp;else if(k==DOWN)p[1]-=sp;else if(k==CENTER_IMAGE||k=='C')s.reset();else if(k==ZOOMIN||k=='+'||k=='x'||k=='X')s.zoomTo(l+1,s.f.clientWidth/2,s.f.clientHeight/2);else if((k==ZOOMOUT||k=='z'||k=='Z')&&l>0)s.zoomTo(l-1,s.f.clientWidth/2,s.f.clientHeight/2);if(k==LEFT||k==UP||k==RIGHT||k==DOWN){p=s.centerImage(i.width,i.height,p[0],p[1]);s.setPosition(p[0],p[1]);sp+=2;}};s.onkeyup=function(e){sp=5;};s.setZoomProp=function(nZF,nMZ){if(nZF==null)zoomFactor=10;zoomFactor=1+retInt(nZF,'%')/100;if(typeof nMZ=='string')m=retInt(nMZ,'%')/100;else if(typeof nMZ=='object'&&nMZ!=null){m[0]=retInt(nMZ[0],'px');m[1]=retInt(nMZ[1],'px');}else m='300%';};s.setFrameProp=function(newFrameProp){s.f.style.width=newFrameProp[0];s.f.style.height=newFrameProp[1];};s.initImage=function(){i.style.maxWidth=i.style.width=i.style.maxHeight=i.style.height=null;oW=i.width;oH=i.height;var d=s.fitToFrame(oW,oH);s.setDimension(d[0],d[1]);if(frame[2]==true)s.f.style.width=(Math.round(d[0])+'px');if(frame[3]==true)s.f.style.height=(Math.round(d[1])+'px');var p=s.centerImage(d[0],d[1],0,0);s.setPosition(p[0],p[1]);s.setMouseCursor();mo=new mouseWheel();mo.init(i,s.onmousewheel);i.onmousedown=s.onmousedown;s.f.onkeypress=s.onkeypress;s.f.onkeyup=s.onkeyup;if(viewer.onload!=null)viewer.onload(s);if(s.onload!=null)s.onload();};s.preInitImage=function(){if(preLoader!=null){i.style.left=((s.f.clientWidth-i.width)/2)+'px';i.style.top=((s.f.clientHeight-i.height)/2)+'px';}i.onload=s.initImage;i.src=imageSource;};s.setNewImage=function(newImageSource,newPreLoader){if(typeof newImageSource=='undefined')return;imageSource=newImageSource;if(typeof newPreLoader!=='undefined')preLoader=newPreLoader;if(preLoader!=null){i.onload=s.preInitImage;i.src=preLoader;return;}i.onload=s.initImage;i.src=imageSource;};s.setZoomProp(zoomFactor,m);s.frameElement=s.f=document.createElement('div');s.f.style.width=frame[0];s.f.style.height=frame[1];s.f.style.border=\"0px solid #000\";s.f.style.margin=\"0px\";s.f.style.padding=\"0px\";s.f.style.overflow=\"hidden\";s.f.style.position=\"relative\";s.f.style.zIndex=2;s.f.tabIndex=1;if(i!=null){if(parent !=null){i.parentNode.removeChild(i);parent.appendChild(s.f);}else if(replace !=null){i.parentNode.removeChild(i);replace.parentNode.replaceChild(s.f,replace);}else i.parentNode.replaceChild(s.f,i);i.style.margin=i.style.padding=\"0\";i.style.borderWidth=\"0px\";i.style.position='absolute';i.style.zIndex=3;s.f.appendChild(i);if(imageSource!=null)s.preInitImage();else s.initImage();}else{if(parent!=null)parent.appendChild(s.f);else if(replace!=null)replace.parentNode.replaceChild(s.f,replace);i=document.createElement('img');i.style.position='absolute';i.style.zIndex=3;s.f.appendChild(i);s.setNewImage(imageSource);}};viewer.onload=null;</script>\n"

#END lglobals.py
