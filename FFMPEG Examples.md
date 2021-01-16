FFMPEG Examples

ffmpeg -vsync 0 -hwaccel auto -i Ad\ Astra_t00.mkv -c:a copy -c:v hevc_nvenc -rc:v vbr_hq -qmin:v 22 -qmax:v 30 -rc-lookahead 8 -weighted_pred 1 /home/movies/Ad\ Astra.mkv

ffmpeg -vsync 0 -hwaccel auto -i The\ Last\ Jedi_t00.mkv -c:a ac3 -b:a 448k -c:v hevc_nvenc -rc:v vbr_hq -qmin:v 22 -qmax:v 30 -rc-lookahead 8 -weighted_pred 1 /home/movies/The\ Last\ Jedi.mkv