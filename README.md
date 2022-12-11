# stenocaptioner

Automatic subtitling tool using whisper.

## Dependencies

* [whisper](https://github.com/openai/whisper)
* [moviepy](https://github.com/Zulko/moviepy)
* [youtube_dl](https://github.com/ytdl-org/youtube-dl)

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
stenocaptioner https://www.youtube.com/watch?v=ldybnuFxdiQ --language ja
```

### Original video

![demo_org](assets/demo_org.gif)

### Basic Result

![result_basic](assets/result_basic.gif)

### Background color

![result_bg_color_blue](assets/result_bg_color_blue.gif)

### Contour

![result_contour](assets/result_contour.gif)

### Font

https://fontfree.me/3132

![result_font](assets/result_font.gif)

### Effect (typing)

![result_typing](assets/result_typing.gif)

### Effect (arrive)

![result_arrive](assets/result_arrive.gif)

### Effect (cascade)

![result_cascade](assets/result_cascade.gif)
