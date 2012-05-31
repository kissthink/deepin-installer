#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012~2013 Deepin, Inc.
#               2012~2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk
import gio
import glib

NONE_CALLBACK=lambda *args:None

class CopyUtil():
    '''copy files,most stolen from fmd/fsutils'''
    def __init__(self):
        self.job_queue=[]
        self.is_run=False
        self.cancel=gio.Cancellable()
        self.filelist=[]
        self.target=None
        self.source=None

    def get_target_gfile(self,target_path):
        self.target=gio.File(target_path)
        target_type=self.target.query_info("standard::type",gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS).get_file_type()
        if target_type==gio.FILE_TYPE_DIRECTORY:
            return self.target
        else:
            print "need create a directory has the same path"

    def get_source_filelist(self,source_path):
        self.source=gio.File(source_path)
        source_type=self.source.query_info("standard::type",gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS).get_file_type()
        if source_type==gio.FILE_TYPE_DIRECTORY:
            print "need insert all the path gfile object to filelist"
        else:
            self.filelist.append(self.source)

    def job_move(self,source,target):
        source.copy_async(target,self.job_done,NONE_CALLBACK,gio.FILE_COPY_NOFOLLOW_SYMLINKS,
                          cancellable=self.cancel,user_data=True)

    def job_move_dir(self,source,target):
        pass

    def job_copy(self,source,target):
        source.copy_async(target,self.job_done,NONE_CALLBACK,gio.FILE_COPY_NOFOLLOW_SYMLINKS,
                          cancellable=self.cancel,user_data=False)
    def idle(self):
        try:
            job=self.job_queue.pop(0)
        except IndexError:
            self.is_run=False
            return False

        job[0](*job[1:])
        return False

    def check_and_run(self):
        if not self.is_run:
            self.is_run=True
            glib.idle_add(self.idle)
    
    def copy(self,filelist,target):
        for f in filelist:
            fi=f.query_info("standard::type",gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS)
            tf=target.get_child(f.get_basename())
            self.push_copy_task(f,tf,fi.get_file_type())

        self.check_and_run()

    def push_copy_task(self,source,target,source_type=None):
        if not source_type:
            source_type=source.query_info("standard::type",gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS).get_file_type()
        if source_type==gio.FILE_TYPE_DIRECTORY:
            self.job_queue.append(None,source,target)
        else:
            self.job_queue.append(self.job_copy,source,target)

    def push_move_task(self,source,target,source_type=None):
        if not source_type:
            source_type=source.query_info("standard::type",gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS).get_file_type()
        if source_type==gio.FILE_TYPE_DIRECTORY:
            self.job_queue.append(self.job_move_dir,source,target)
        else:
            self.job_queue.append(self.job_move,source,target)
        
    def move(self,filelist,target):
        target_fs=target.query_info("id::filesystem").get_attribute_as_string("id::filesystem")
        for f in filelist:
            if target.equal(f.get_parent()):
                continue
            fi=f.query_info("standard::type,id::filesystem",gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS)
            source_fs=fi.get_attribute_as_string("id::filesystem")

            tf=target.get_child(f.get_basename())
            if source_fs==target_fs:
                f.move(tf,NONE_CALLBACK,gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS)
            else:
                self.push_move_task(f,tf,fi.get_file_type())
                
        self.check_and_run()        

    def cancel(self):
        pass

    #     self.src=gio.File(src)
    #     self.dst=gio.File(dst)
    #     info=self.src.query_info(gio.FILE_ATTRIBUTE_STANDARD_SIZE)
    #     self.total_num_bytes=info.get_attribute_uint64(gio.FILE_ATTRIBUTE_STANDARD_SIZE)
    #     print self.total_num_bytes

    #     self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
    #     self.window.set_size_request(400,300)
    #     self.window.set_title("Copy Util")
    #     self.window.set_position(gtk.WIN_POS_CENTER)
    #     self.vbox=gtk.VBox(False,1)
    #     self.progressbar=gtk.ProgressBar()
    #     self.progressbar.set_text("Copying......")
        
    #     self.vbox.pack_start(self.progressbar)
    #     self.window.add(self.vbox)
    #     self.window.show_all()
    #     self.window.connect("destroy",gtk.main_quit)

    # def start_copy(self):
    #     self.src.copy_async(self.dst,self.finish_copy_callback,self.progress_copy_callback,gio.FILE_COPY_OVERWRITE,glib.PRIORITY_DEFAULT,None,self.progressbar,self.progressbar)
    #     gtk.main()

    # def finish_copy_callback(self,srcfile,result,progressbar):
    #     self.src.copy_finish(result)
    #     self.progressbar.set_text("Finished Copy")
    #     self.progressbar.set_fraction(1.0)
    #     print "finish copy"

    # def progress_copy_callback(self,current_num_bytes,total_num_bytes,progressbar):
    #     total_num_bytes=self.total_num_bytes

    #     self.progressbar.set_text(str(current_num_bytes/1024)+"K/"+str(total_num_bytes/1024)+"K")
    #     self.progressbar.set_fraction(current_num_bytes/total_num_bytes)

if __name__=="__main__":
   # cu=CopyUtil("testsrc","testtarget")
   # # cu=CopyUtil("/media/cdrom/casper/filesystem.squashfs","/target")
   # cu.start_copy()
    pass
