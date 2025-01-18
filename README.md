# quine-md5-gif

Modified the original code implemented by Rogdham to check the results with custom images.
This is a repository where the code has been modified to make it easy for anyone to run.

---

기존 Rogdham 이 구현한 코드를 일부 수정하여 custom한 이미지로 결과를 확인.
누구나 동작해보기 쉽게 코드를 수정한 레포지토리입니다.

- quine: 자기 자신의 소스코드를 입력 없이 출력하는 프로그램
- 자신의 md5sum 값과 일치하는 md5sum 값이 이미지에 포함되어 있는 파일 생성

대부분의 코드는 [Rogdham](https://github.com/Rogdham/gif-md5-hashquine)의 코드를 참고합니다.

---

## Sample

> M1 Pro(vm environment: Ubuntu 24.04LTS amd64), Elapsed 1895sec..

![](./result.gif)

결과 gif 파일의 md5sum 값이 이미지에 있는 값과 동일!!!

```bash
~/quine-md5-gif$ python3 generate.py result.gif
...
...
Temporary directory created:  tmp
Prefix data written:  tmp/prefix
Current working directory:  /Users/greendot/quine/quine-md5-gif
Bruteforcing final md5...
Target md5: cb6785f34ccd5a392deadf03598053a0
Final md5:  cb6785f34ccd5a392deadf03598053a0
Time Elapsed: 1895.69 seconds
Cleaning up...md5 collision files

md5sum result.gif
~/:quine-md5-gif$ md5sum result.gif
cb6785f34ccd5a392deadf03598053a0  result.gif
```

## Ref

- First issued
  - https://shells.aachen.ccc.de/~spq/md5.gif
    ![](https://shells.aachen.ccc.de/~spq/md5.gif)
- My first reference
  - https://github.com/Rogdham/gif-md5-hashquine
    ![](https://github.com/Rogdham/gif-md5-hashquine/blob/master/rogdham_gif_md5_hashquine.gif?raw=true)
- gif format
  - https://www.matthewflickinger.com/lab/whatsinagif/bits_and_bytes.asp

## Build

만약 Ubuntu 24.04LTS(amd64) 환경이 아닌 경우 [build fastcoll](#build-fastcoll) 를 먼저 수행하세요.

### Run

Python 3.10 이상 환경에서 확인하였습니다.

```bash
python3 generate.py result.gif
md5sum result.gif
```

### build fastcoll

기본 fastcoll은 Ubuntu 24.04LTS(amd64) 에서 빌드된 바이너리입니다.
플랫폼이 다른 경우 fastcoll을 먼저 빌드해야합니다.

```bash
# Build fastcoll
cd fastcoll
make clean
make
cp fastcoll ../fastcoll

# modify generate.py
sed -i "s/FASTCOLL_PATH = 'fastcoll_linux_amd64'/FASTCOLL_PATH = 'fastcoll'/" generate.py
```
