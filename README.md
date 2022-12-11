# stenocaptioner

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stenocaptioner)
[![Downloads](https://pepy.tech/badge/stenocaptioner)](https://pepy.tech/project/stenocaptioner)

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

### Options

```sh
stenocaptioner --help
usage: stenocaptioner [-h] [--language LANGUAGE] [--model-type {tiny,base,small,medium,large}] [--text-color TEXT_COLOR] [--background-color BACKGROUND_COLOR]
                      [--contour-color CONTOUR_COLOR] [--contour-width CONTOUR_WIDTH] [--font FONT] [--fontsize FONTSIZE] [--fadein-duration FADEIN_DURATION]
                      [--fadeout-duration FADEOUT_DURATION] [--save-text] [--load-text LOAD_TEXT] [--letter-effect {none,typing,arrive,cascade}] [--side-margin SIDE_MARGIN]
                      [--bottom-margin BOTTOM_MARGIN]
                      url

positional arguments:
  url                   URL of the video.

options:
  -h, --help            show this help message and exit
  --language LANGUAGE   Language of the text.
  --model-type {tiny,base,small,medium,large}
                        Whisper model type.
  --text-color TEXT_COLOR
                        Color of the text.
  --background-color BACKGROUND_COLOR
                        Color of the background.
  --contour-color CONTOUR_COLOR
                        Color of the contour.
  --contour-width CONTOUR_WIDTH
                        Width of the contour.
  --font FONT           Font name.
  --fontsize FONTSIZE   Font size.
  --fadein-duration FADEIN_DURATION
                        Duration of the fade-in effect.
  --fadeout-duration FADEOUT_DURATION
                        Duration of the fade-out effect.
  --save-text           Save the transcribed text.
  --load-text LOAD_TEXT
                        Load the transcribed text.
  --letter-effect {none,typing,arrive,cascade}
                        Effect of the letters.
  --side-margin SIDE_MARGIN
                        Margin of the text from the side of the video. It is expressed as a ratio of the width of the image.
  --bottom-margin BOTTOM_MARGIN
                        Margin of the text from the bottom of the video. It is expressed as a ratio of the height of the image.

```

### Original video

![demo_org](https://raw.githubusercontent.com/neka-nat/stenocaptioner/master/assets/demo_org.gif)

### Basic Result

![result_basic](https://raw.githubusercontent.com/neka-nat/stenocaptioner/master/assets/result_basic.gif)

### Background color

```sh
stenocaptioner https://www.youtube.com/watch?v=ldybnuFxdiQ --language ja --background-color blue
```

![result_bg_color_blue](https://raw.githubusercontent.com/neka-nat/stenocaptioner/master/assets/result_bg_color_blue.gif)

### Contour

```sh
stenocaptioner https://www.youtube.com/watch?v=ldybnuFxdiQ --language ja --contour-color black
```

![result_contour](https://raw.githubusercontent.com/neka-nat/stenocaptioner/master/assets/result_contour.gif)

### Font

Download https://fontfree.me/3132.

```sh
stenocaptioner https://www.youtube.com/watch?v=ldybnuFxdiQ --language ja --font ./gomarice_mukasi_mukasi.ttf
```

![result_font](https://raw.githubusercontent.com/neka-nat/stenocaptioner/master/assets/result_font.gif)

### Effect (typing)

```sh
stenocaptioner https://www.youtube.com/watch?v=ldybnuFxdiQ --language ja --letter-effect typing
```

![result_typing](https://raw.githubusercontent.com/neka-nat/stenocaptioner/master/assets/result_typing.gif)

### Effect (arrive)

```sh
stenocaptioner https://www.youtube.com/watch?v=ldybnuFxdiQ --language ja --letter-effect arrive
```

![result_arrive](https://raw.githubusercontent.com/neka-nat/stenocaptioner/master/assets/result_arrive.gif)

### Effect (cascade)

```sh
stenocaptioner https://www.youtube.com/watch?v=ldybnuFxdiQ --language ja --letter-effect cascade
```

![result_cascade](https://raw.githubusercontent.com/neka-nat/stenocaptioner/master/assets/result_cascade.gif)
