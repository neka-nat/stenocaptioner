# stenocaptioner

Automatic subtitling tool using whisper.

## Installation

### Ubuntu

```sh
sudo apt-get -y install imagemagick fonts-vlgothic
```

You will also need to modify the ImageMagick configuration file to comment out the following policy.

```
sudo vi /etc/ImageMagick-6/policy.xml
  <!--
  <policy domain="path" pattern="@*" rights="none">
  -->
```

Install with pip.

```sh
pip install git+https://github.com/openai/whisper.git
pip install stenocaptioner
```

## Usage

You can give the url of youtube video as an argument.

```sh
stenocaptioner https://www.youtube.com/watch?v=A6GG65TAEYo --language ja --text-color red
```

![demo](assets/demo.png)
