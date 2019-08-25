all: rpi2mqtt rpi2mqtt.service
.PHONY: all rpi2mqtt install uninstall clean

service_dir=/etc/systemd/system
awk_script='BEGIN {FS="="; OFS="="}{if ($$1=="ExecStart") {$$2=exec_path} if (substr($$1,1,1) != "\#") {print $$0}}'

rpi2mqtt: rpi2mqtt/event_loop.py setup.py
	pip install .

rpi2mqtt.service: rpi2mqtt/event_loop.py
# awk is needed to replace the absolute path of rpi2mqtt executable in the .service file
	awk -v exec_path=$(shell which rpi2mqtt) $(awk_script) rpi2mqtt.service.template > rpi2mqtt.service

install: $(service_dir) $(conf_dir) schedulerd.service scheduler.conf.yml
	cp rpi2mqtt.service $(service_dir)

uninstall:
	-systemctl stop mydaemond
	-rm -r $(service_dir)/rpi2mqtt.service

clean:
	-rm rpi2mqtt.service