sudo nmcli dev wifi rescan                                                              
sudo nmcli -f SSID,CHAN,SECURITY,SIGNAL dev wifi list | grep -i vsu@2026_5G             
sudo nmcli device wifi connect vsu@2026_5G password vsu@2026 
