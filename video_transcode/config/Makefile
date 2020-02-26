all: video-transcode video-transcode.service
.PHONY: all video-transcode install uninstall clean

service_dir=/etc/systemd/system
awk_script='BEGIN {FS="="; OFS="="}{if ($$1=="ExecStart") {$$2=exec_path} if (substr($$1,1,1) != "\#") {print $$0}}'

video-transcode.service: video-transcode/event_loop.py
# awk is needed to replace the absolute path of rpi2mqtt executable in the .service file
	awk -v exec_path=$(shell which video-transcode) $(awk_script) video-transcode.service.template > video-transcode.service

install: $(service_dir) rpi2mqtt.service
	cp video-transcode.service $(service_dir)

uninstall:
	-systemctl stop rpi2mqtt
	-rm -r $(service_dir)/video-transcode.service

clean:
	-rm video-transcode.service