@echo off

if exist Singkong-new.jar ( 
  copy /Y Singkong.jar Singkong-backup.jar
  move /Y Singkong-new.jar Singkong.jar
)
