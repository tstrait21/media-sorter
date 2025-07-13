import PyInstaller.__main__

if __name__ == "__main__":
    PyInstaller.__main__.run([
        'src/media_sorter/main.py',
        '--onefile',
        '--name=media-sorter',
        '--distpath=./dist',
        '--workpath=./build',
    ])
