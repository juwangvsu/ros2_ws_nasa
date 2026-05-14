sudo nmcli dev wifi rescan                                                              
sudo nmcli -f SSID,CHAN,SECURITY,SIGNAL dev wifi list | grep -i "iPhone (54"             
sudo nmcli device wifi connect "iPhone (54)" password password 
