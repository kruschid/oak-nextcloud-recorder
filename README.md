# oak-nextcloud-recorder

## Installation with Docker:

```sh
# oak
sudo curl -fL https://docs.luxonis.com/install_dependencies.sh | bash
# docker
sudo curl -fsSL https://get.docker.com -o get-docker.sh | bash
sudo usermod -aG docker $USER
echo "Log out and log back in to use docker without sudo"
exit

# oak recorder
git clone https://github.com/kruschid/oak-nextcloud-recorder.git
docker build -t oak-recorder .
```

## How to run

```sh
docker run -d \
  --restart unless-stopped \
  --privileged \
  -v /dev/bus/usb:/dev/bus/usb \
  --device-cgroup-rule='c 189:* rmw' \
  --name oak-recorder \
  oak-recorder
```
